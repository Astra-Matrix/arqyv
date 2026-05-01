"""
Live search runner — executes off the Qt main thread.

Strategy:
  1. Parse query: type keyword → ext list | ".ext" → exact ext | text → LIKE
  2. Query SQLite synchronously (raw sqlite3, no async overhead).
  3. If DB has < MIN_DB_RESULTS, supplement with a time-boxed filesystem walk.
  4. Stream results in batches via Qt signals so the UI updates while scanning.

Cancellation: caller passes a threading.Event; the runner checks it frequently
and exits early. Stale results are discarded on the UI side by sequence number.
"""

from __future__ import annotations

import os
import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

# ── Type map (natural-language keyword → extensions) ──────────────────────────

_TYPE_MAP: dict[str, list[str]] = {
    "video":    [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv", ".m4v",
                 ".ts", ".mpg", ".mpeg", ".3gp", ".rmvb", ".divx"],
    "audio":    [".mp3", ".flac", ".wav", ".aac", ".ogg", ".opus", ".m4a", ".wma",
                 ".alac", ".aiff", ".ape", ".dsf"],
    "image":    [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif",
                 ".svg", ".heic", ".heif", ".raw", ".cr2", ".nef", ".arw"],
    "document": [".pdf", ".docx", ".doc", ".txt", ".md", ".rtf", ".odt",
                 ".xlsx", ".xls", ".ods", ".pptx", ".ppt", ".odp", ".csv"],
    "archive":  [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".zst"],
    "code":     [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json",
                 ".yaml", ".toml", ".rs", ".go", ".java", ".cpp", ".c", ".h"],
}

# Common user-accessible root directories to scan when DB has few results
def _fs_roots() -> list[Path]:
    home = Path.home()
    candidates = [
        home / "Videos",
        home / "Music",
        home / "Pictures",
        home / "Downloads",
        home / "Documents",
        home / "Desktop",
    ]
    # Also add drive roots on Windows
    if os.name == "nt":
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            p = Path(f"{letter}:\\")
            if p.exists():
                candidates.append(p)
    return [p for p in candidates if p.exists()]


_MIN_DB_RESULTS = 10   # supplement with FS scan below this count
_FS_TIMEOUT_S   = 1.5  # max time for filesystem scan
_BATCH_SIZE     = 30   # emit results in batches for smooth UI


@dataclass
class SearchHit:
    path: str
    name: str
    ext: str
    size: int
    source: str   # "db" or "fs"


class _Signals(QObject):
    batch_ready  = pyqtSignal(list, int)   # (hits: list[SearchHit], seq: int)
    finished     = pyqtSignal(int, int)    # (total_count: int, seq: int)


class LiveSearchRunner(QRunnable):
    """
    Instantiate per-query. Pass a fresh cancel token each time; check it in
    tight loops to abort stale searches without killing the thread.
    """

    def __init__(
        self,
        query: str,
        db_path: str,
        cancel: threading.Event,
        seq: int,
    ) -> None:
        super().__init__()
        self.query   = query.strip()
        self.db_path = db_path
        self.cancel  = cancel
        self.seq     = seq
        self.signals = _Signals()
        self.setAutoDelete(True)

    # ── Query parsing ──────────────────────────────────────────────────────

    def _parse(self) -> tuple[str, list[str] | None]:
        """
        Returns (clean_text, ext_filter_or_None).
        ext_filter is a list of lowercase extensions to match, or None = any.
        """
        q = self.query.lower()

        # ".mp4" or "mp4" exact extension
        if q.startswith("."):
            return "", [q]
        if len(q) <= 5 and not q.isspace():
            test = f".{q}"
            all_exts = [e for exts in _TYPE_MAP.values() for e in exts]
            if test in all_exts:
                return "", [test]

        # Natural-language type keyword (may appear anywhere in query)
        for keyword, exts in _TYPE_MAP.items():
            if keyword in q.split():
                rest = q.replace(keyword, "").strip()
                return rest, exts

        return q, None

    # ── DB search ──────────────────────────────────────────────────────────

    def _search_db(self, text: str, ext_filter: list[str] | None) -> list[SearchHit]:
        if not Path(self.db_path).exists():
            return []
        try:
            con = sqlite3.connect(self.db_path, timeout=2)
            con.row_factory = sqlite3.Row
            cur = con.cursor()

            params: list[object] = []
            clauses: list[str] = []

            if ext_filter:
                placeholders = ",".join("?" * len(ext_filter))
                clauses.append(f"extension IN ({placeholders})")
                params.extend(ext_filter)

            if text:
                like = f"%{text}%"
                clauses.append(
                    "(filename LIKE ? OR ai_tags LIKE ? OR ai_summary LIKE ? OR ai_transcript LIKE ?)"
                )
                params.extend([like, like, like, like])

            where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
            sql = f"""
                SELECT path, filename, extension, size_bytes
                FROM   media_files
                {where}
                ORDER BY updated_at DESC
                LIMIT 300
            """
            cur.execute(sql, params)
            rows = cur.fetchall()
            con.close()

            return [
                SearchHit(
                    path=r["path"],
                    name=r["filename"],
                    ext=r["extension"],
                    size=r["size_bytes"] or 0,
                    source="db",
                )
                for r in rows
            ]
        except Exception:
            return []

    # ── Filesystem scan ────────────────────────────────────────────────────

    def _scan_fs(
        self,
        text: str,
        ext_filter: list[str] | None,
        seen: set[str],
    ) -> list[SearchHit]:
        hits: list[SearchHit] = []
        deadline = time.monotonic() + _FS_TIMEOUT_S
        text_lo = text.lower()

        for root in _fs_roots():
            if self.cancel.is_set() or time.monotonic() > deadline:
                break
            try:
                for dirpath, dirnames, filenames in os.walk(root):
                    if self.cancel.is_set() or time.monotonic() > deadline:
                        return hits
                    # Skip hidden and system dirs
                    dirnames[:] = [
                        d for d in dirnames
                        if not d.startswith(".") and d not in ("Windows", "System32", "$Recycle.Bin", "node_modules", "__pycache__")
                    ]
                    for fname in filenames:
                        if self.cancel.is_set():
                            return hits
                        fpath = os.path.join(dirpath, fname)
                        if fpath in seen:
                            continue
                        ext = Path(fname).suffix.lower()
                        if ext_filter and ext not in ext_filter:
                            continue
                        if text_lo and text_lo not in fname.lower():
                            continue
                        try:
                            size = os.path.getsize(fpath)
                        except OSError:
                            size = 0
                        hits.append(SearchHit(
                            path=fpath,
                            name=fname,
                            ext=ext,
                            size=size,
                            source="fs",
                        ))
            except PermissionError:
                continue
        return hits

    # ── Runner entry ───────────────────────────────────────────────────────

    @pyqtSlot()
    def run(self) -> None:
        if self.cancel.is_set() or not self.query:
            self.signals.finished.emit(0, self.seq)
            return

        text, ext_filter = self._parse()

        # 1. DB pass
        db_hits = self._search_db(text, ext_filter)
        if self.cancel.is_set():
            return

        seen = {h.path for h in db_hits}
        total = list(db_hits)

        # Emit DB batch immediately
        if total:
            self.signals.batch_ready.emit(list(total), self.seq)

        # 2. FS supplement if DB is sparse
        if len(db_hits) < _MIN_DB_RESULTS:
            fs_hits = self._scan_fs(text, ext_filter, seen)
            if self.cancel.is_set():
                return
            for i in range(0, len(fs_hits), _BATCH_SIZE):
                if self.cancel.is_set():
                    return
                batch = fs_hits[i : i + _BATCH_SIZE]
                total.extend(batch)
                self.signals.batch_ready.emit(batch, self.seq)

        self.signals.finished.emit(len(total), self.seq)
