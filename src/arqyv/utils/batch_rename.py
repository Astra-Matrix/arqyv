"""Batch rename engine with template-based pattern support.

Pattern tokens:
  {name}          – original stem (no extension)
  {ext}           – extension including dot
  {counter}       – sequential number (format: {counter:04d})
  {date}          – file modification date (YYYY-MM-DD)
  {year}          – 4-digit year
  {month}         – 2-digit month
  {day}           – 2-digit day
  {size_kb}       – file size in KB (integer)
  {ai_tag}        – first AI tag (requires prior indexing)
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"\{(\w+)(?::([^}]+))?\}")


class RenamePattern:
    """Parsed rename pattern for fast repeated application."""

    def __init__(self, raw: str) -> None:
        self.raw = raw

    def render(self, path: Path, index: int = 0, ai_tags: list[str] | None = None) -> str:
        stat = path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime)

        context = {
            "name": path.stem,
            "ext": path.suffix,
            "counter": index + 1,
            "date": mtime.strftime("%Y-%m-%d"),
            "year": mtime.strftime("%Y"),
            "month": mtime.strftime("%m"),
            "day": mtime.strftime("%d"),
            "size_kb": int(stat.st_size / 1024),
            "ai_tag": (ai_tags[0] if ai_tags else "untagged"),
        }

        result = self.raw
        for match in _TOKEN_RE.finditer(self.raw):
            token, fmt = match.group(1), match.group(2)
            value = context.get(token, match.group(0))
            if fmt:
                try:
                    formatted = f"{value:{fmt}}"
                except (ValueError, TypeError):
                    formatted = str(value)
            else:
                formatted = str(value)
            result = result.replace(match.group(0), formatted, 1)

        # Sanitize: replace illegal filename chars
        result = re.sub(r'[<>:"/\\|?*]', "_", result)
        return result.strip()


class BatchRenamer:
    def __init__(self, pattern: str) -> None:
        self._pattern = RenamePattern(pattern)

    def generate(self, path: Path, index: int = 0) -> str:
        return self._pattern.render(path, index)

    def apply(self, path: Path, index: int = 0) -> Path:
        new_name = self.generate(path, index)
        dest = path.parent / new_name
        if dest.exists() and dest != path:
            raise FileExistsError(f"Target already exists: {dest}")
        path.rename(dest)
        log.info("Renamed: %s → %s", path.name, new_name)
        return dest
