"""Persistent user preferences (window geometry, recent paths, etc.).

Uses QSettings-style JSON storage so it is portable between platforms.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_FILENAME = "user_settings.json"


class SettingsManager:
    def __init__(self, config_dir: Path) -> None:
        self._path = config_dir / _FILENAME
        self._data: dict[str, Any] = {}
        self._load()

    # ── I/O ────────────────────────────────────────────────────────────────

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                log.warning("Could not read settings file; starting fresh.")
                self._data = {}

    def save(self) -> None:
        try:
            self._path.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError:
            log.exception("Failed to save settings.")

    # ── API ─────────────────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    def get_recent_paths(self) -> list[str]:
        return self._data.get("recent_paths", [])

    def add_recent_path(self, path: str, max_entries: int = 20) -> None:
        recents: list[str] = self._data.get("recent_paths", [])
        if path in recents:
            recents.remove(path)
        recents.insert(0, path)
        self._data["recent_paths"] = recents[:max_entries]
        self.save()
