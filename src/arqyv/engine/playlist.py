"""Playlist manager with shuffle, repeat, and smart resume.

Smart resume: remembers the playback position for every file across
sessions by persisting a JSON store in the user's data directory.

Zero external dependencies.
"""

from __future__ import annotations

import json
import logging
import random
from enum import Enum, auto
from pathlib import Path
from typing import Iterator

log = logging.getLogger(__name__)

_RESUME_FILE = "resume_positions.json"
_MAX_RESUME_ENTRIES = 5000


class RepeatMode(Enum):
    NONE   = auto()
    ONE    = auto()
    ALL    = auto()


class Playlist:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._tracks: list[Path] = []
        self._order: list[int] = []     # indices into _tracks
        self._cursor: int = 0           # index into _order
        self._shuffle = False
        self._repeat = RepeatMode.NONE
        self._resume: dict[str, int] = {}  # path → last position ms
        self._load_resume()

    # ── Track management ───────────────────────────────────────────────────

    def set_tracks(self, paths: list[Path], start_index: int = 0) -> None:
        self._tracks = list(paths)
        self._rebuild_order(start_index)

    def add(self, path: Path) -> None:
        if path not in self._tracks:
            self._tracks.append(path)
            self._order.append(len(self._tracks) - 1)

    def clear(self) -> None:
        self._tracks.clear()
        self._order.clear()
        self._cursor = 0

    def __len__(self) -> int:
        return len(self._tracks)

    # ── Navigation ─────────────────────────────────────────────────────────

    @property
    def current(self) -> Path | None:
        if not self._order:
            return None
        return self._tracks[self._order[self._cursor]]

    def next(self) -> Path | None:
        if not self._order:
            return None
        if self._repeat == RepeatMode.ONE:
            return self.current
        if self._cursor + 1 < len(self._order):
            self._cursor += 1
        elif self._repeat == RepeatMode.ALL:
            if self._shuffle:
                self._rebuild_order(0)
            self._cursor = 0
        else:
            return None
        return self.current

    def previous(self) -> Path | None:
        if not self._order:
            return None
        self._cursor = max(0, self._cursor - 1)
        return self.current

    def jump_to(self, track_index: int) -> Path | None:
        """Jump to absolute track index (not order index)."""
        try:
            order_idx = self._order.index(track_index)
            self._cursor = order_idx
        except ValueError:
            return None
        return self.current

    @property
    def has_next(self) -> bool:
        if self._repeat in (RepeatMode.ONE, RepeatMode.ALL):
            return True
        return self._cursor + 1 < len(self._order)

    @property
    def has_previous(self) -> bool:
        return self._cursor > 0

    @property
    def cursor(self) -> int:
        return self._cursor

    @property
    def track_count(self) -> int:
        return len(self._tracks)

    def iter_tracks(self) -> Iterator[tuple[int, Path]]:
        for i, idx in enumerate(self._order):
            yield i, self._tracks[idx]

    # ── Modes ──────────────────────────────────────────────────────────────

    def set_shuffle(self, enabled: bool) -> None:
        self._shuffle = enabled
        current = self._order[self._cursor] if self._order else None
        self._rebuild_order()
        if current is not None and current in self._order:
            self._cursor = self._order.index(current)

    def set_repeat(self, mode: RepeatMode) -> None:
        self._repeat = mode

    def toggle_shuffle(self) -> bool:
        self.set_shuffle(not self._shuffle)
        return self._shuffle

    def cycle_repeat(self) -> RepeatMode:
        modes = list(RepeatMode)
        idx = modes.index(self._repeat)
        self._repeat = modes[(idx + 1) % len(modes)]
        return self._repeat

    # ── Smart resume ───────────────────────────────────────────────────────

    def save_position(self, path: Path, position_ms: int) -> None:
        key = str(path)
        if position_ms > 5000:  # don't save if <5 s in
            self._resume[key] = position_ms
            self._save_resume()

    def get_resume_position(self, path: Path) -> int:
        """Return saved position or 0 if none."""
        return self._resume.get(str(path), 0)

    def clear_resume(self, path: Path) -> None:
        self._resume.pop(str(path), None)

    def _load_resume(self) -> None:
        p = self._data_dir / _RESUME_FILE
        try:
            if p.exists():
                self._resume = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._resume = {}

    def _save_resume(self) -> None:
        p = self._data_dir / _RESUME_FILE
        # Evict oldest entries beyond limit
        if len(self._resume) > _MAX_RESUME_ENTRIES:
            keys = list(self._resume.keys())
            for k in keys[:len(self._resume) - _MAX_RESUME_ENTRIES]:
                del self._resume[k]
        try:
            p.write_text(json.dumps(self._resume, indent=2), encoding="utf-8")
        except OSError:
            log.warning("Could not save resume positions.")

    # ── Internal ───────────────────────────────────────────────────────────

    def _rebuild_order(self, start_index: int = 0) -> None:
        order = list(range(len(self._tracks)))
        if self._shuffle:
            # Keep the start track first, shuffle the rest
            rest = [i for i in order if i != start_index]
            random.shuffle(rest)
            order = [start_index] + rest
            self._cursor = 0
        else:
            self._cursor = min(start_index, max(0, len(order) - 1))
        self._order = order
