"""Safe file operation helpers."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from send2trash import send2trash

log = logging.getLogger(__name__)


def safe_delete(path: Path) -> bool:
    """Move file to OS trash instead of permanently deleting."""
    try:
        send2trash(str(path))
        log.info("Trashed: %s", path)
        return True
    except Exception:
        log.exception("Failed to trash %s", path)
        return False


def copy_file(src: Path, dest: Path, overwrite: bool = False) -> bool:
    if dest.exists() and not overwrite:
        log.warning("Destination exists; skipping: %s", dest)
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    log.debug("Copied: %s → %s", src, dest)
    return True


def move_file(src: Path, dest: Path, overwrite: bool = False) -> bool:
    if dest.exists() and not overwrite:
        log.warning("Destination exists; skipping: %s", dest)
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    log.debug("Moved: %s → %s", src, dest)
    return True


def get_unique_path(path: Path) -> Path:
    """Return a non-conflicting path by appending _(n)."""
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    n = 1
    while True:
        candidate = path.parent / f"{stem}_({n}){suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def human_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
