"""
Live search results panel — shown in the left dock when the search bar is active.

Each row:  [TYPE]  filename.ext                           2.4 MB
                   /path/to/directory

Clicking a row selects/previews the file.
Double-click opens/plays it.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from arqyv.search.live_search import SearchHit

from arqyv.ui.themes.dark import PALETTE as P


# ── Type badge colours ────────────────────────────────────────────────────────

_EXT_COLOUR: dict[str, str] = {}
_EXT_LABEL:  dict[str, str] = {}

def _register(label: str, colour: str, exts: list[str]) -> None:
    for e in exts:
        _EXT_COLOUR[e] = colour
        _EXT_LABEL[e]  = label

_register("VID", "#7c3aed",
          [".mp4",".mkv",".avi",".mov",".wmv",".webm",".flv",".m4v",".ts",".mpg",".mpeg"])
_register("AUD", "#0ea5e9",
          [".mp3",".flac",".wav",".aac",".ogg",".opus",".m4a",".wma",".alac",".aiff",".ape"])
_register("IMG", "#059669",
          [".jpg",".jpeg",".png",".gif",".webp",".bmp",".tiff",".heic",".raw",".svg"])
_register("DOC", "#d97706",
          [".pdf",".docx",".doc",".txt",".md",".rtf",".odt",".xlsx",".pptx",".csv"])
_register("ZIP", "#64748b",
          [".zip",".rar",".7z",".tar",".gz",".bz2",".xz"])
_register("COD", "#e11d48",
          [".py",".js",".ts",".jsx",".tsx",".html",".css",".json",".rs",".go",".java"])


def _badge_style(colour: str) -> str:
    return f"""
        background: {colour}22;
        color: {colour};
        border: 1px solid {colour}44;
        border-radius: 3px;
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 0.06em;
        padding: 1px 5px;
        min-width: 28px;
        max-width: 28px;
        qproperty-alignment: AlignCenter;
    """


def _human_size(b: int) -> str:
    if b == 0:
        return ""
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.0f} {unit}" if unit == "B" else f"{b:.1f} {unit}"
        b //= 1024
    return f"{b:.1f} TB"


# ── Row widget ────────────────────────────────────────────────────────────────

class _ResultRow(QWidget):
    def __init__(self, hit: "SearchHit") -> None:
        super().__init__()
        self.path = hit.path
        self.setFixedHeight(48)

        root = QHBoxLayout(self)
        root.setContentsMargins(10, 0, 10, 0)
        root.setSpacing(10)

        # Badge
        colour  = _EXT_COLOUR.get(hit.ext, P["text3"])
        label   = _EXT_LABEL.get(hit.ext, hit.ext.lstrip(".").upper()[:3] or "???")
        badge = QLabel(label)
        badge.setFixedSize(32, 18)
        badge.setStyleSheet(_badge_style(colour))
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(badge)

        # Name + path column
        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        text_col.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(hit.name)
        name_lbl.setStyleSheet(f"color: {P['text']}; font-size: 13px; font-weight: 500;")
        name_lbl.setTextFormat(Qt.TextFormat.PlainText)

        stem  = Path(hit.path).parent
        # Shorten path: keep last 2 components
        parts = stem.parts
        short = os.path.join(*parts[-2:]) if len(parts) >= 2 else str(stem)
        path_lbl = QLabel(short)
        path_lbl.setStyleSheet(f"color: {P['text3']}; font-size: 10px;")
        path_lbl.setTextFormat(Qt.TextFormat.PlainText)

        text_col.addWidget(name_lbl)
        text_col.addWidget(path_lbl)
        root.addLayout(text_col, 1)

        # Size
        if hit.size:
            size_lbl = QLabel(_human_size(hit.size))
            size_lbl.setStyleSheet(f"color: {P['text3']}; font-size: 10px;")
            size_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            size_lbl.setFixedWidth(54)
            root.addWidget(size_lbl)


# ── Results panel ─────────────────────────────────────────────────────────────

class SearchResultsWidget(QWidget):
    file_selected  = pyqtSignal(str)
    file_activated = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._seq  = -1
        self._total = 0
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        hdr = QWidget()
        hdr.setFixedHeight(40)
        hdr.setStyleSheet(f"background: {P['bg1']}; border-bottom: 1px solid {P['border']};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(12, 0, 8, 0)

        self._count_lbl = QLabel("Searching…")
        self._count_lbl.setStyleSheet(f"color: {P['text2']}; font-size: 11px;")
        hl.addWidget(self._count_lbl, 1)

        self._clear_btn = QPushButton("×")
        self._clear_btn.setFixedSize(24, 24)
        self._clear_btn.setObjectName("ghost")
        self._clear_btn.setToolTip("Clear search")
        self._clear_btn.clicked.connect(self.request_clear)
        hl.addWidget(self._clear_btn)
        root.addWidget(hdr)

        # ── Spinner / empty state ──────────────────────────────────────────
        self._empty = QLabel("No results")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.setStyleSheet(f"color: {P['text3']}; font-size: 12px; padding: 32px;")
        self._empty.hide()

        # ── List ───────────────────────────────────────────────────────────
        self._list = QListWidget()
        self._list.setStyleSheet(f"""
            QListWidget {{
                background: {P['bg1']};
                border: none;
                outline: 0;
            }}
            QListWidget::item {{
                padding: 0;
                border-bottom: 1px solid {P['border']};
            }}
            QListWidget::item:hover {{ background: {P['bg3']}; }}
            QListWidget::item:selected {{ background: {P['bg4']}; }}
        """)
        self._list.setSpacing(0)
        self._list.setUniformItemSizes(True)
        self._list.currentItemChanged.connect(self._on_current_changed)
        self._list.itemActivated.connect(self._on_activated)

        root.addWidget(self._empty, 1)
        root.addWidget(self._list, 1)

    # ── Public API ─────────────────────────────────────────────────────────

    request_clear = pyqtSignal()  # tells MainWindow to clear the search bar

    def prepare(self, query: str, seq: int) -> None:
        """Call before starting a new search to reset state."""
        self._seq   = seq
        self._total = 0
        self._list.clear()
        self._empty.hide()
        self._list.show()
        self._count_lbl.setText(f'Searching for  \u201c{query}\u201d\u2026')

    def append_batch(self, hits: "list[SearchHit]", seq: int) -> None:
        if seq != self._seq:
            return
        for hit in hits:
            item = QListWidgetItem(self._list)
            item.setSizeHint(QSize(0, 48))
            item.setData(Qt.ItemDataRole.UserRole, hit.path)
            row = _ResultRow(hit)
            self._list.setItemWidget(item, row)
        self._total += len(hits)
        self._count_lbl.setText(f"{self._total} result{'s' if self._total != 1 else ''}")

    def finish(self, total: int, seq: int) -> None:
        if seq != self._seq:
            return
        if total == 0:
            self._list.hide()
            self._empty.show()
            self._count_lbl.setText("No results")
        else:
            self._count_lbl.setText(f"{total} result{'s' if total != 1 else ''}")

    # ── Slots ──────────────────────────────────────────────────────────────

    def _on_current_changed(self, current: QListWidgetItem | None, _: object) -> None:
        if current:
            path = current.data(Qt.ItemDataRole.UserRole)
            if path:
                self.file_selected.emit(path)

    def _on_activated(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.file_activated.emit(path)
