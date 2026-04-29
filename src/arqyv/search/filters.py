"""Query filter parser.

Supports tokens like:
  type:video         – file extension group
  ext:.mp4           – exact extension
  size:>100mb        – file size comparison
  date:>2024-01-01   – modification date
  tag:holiday        – AI tag contains

Example:
  "beach sunset type:video date:>2024-06" → query="beach sunset", filters applied.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arqyv.database.models import MediaFile

_TOKEN_RE = re.compile(r"(\w+):(\S+)")
_SIZE_RE = re.compile(r"([<>]=?|=)(\d+(?:\.\d+)?)(b|kb|mb|gb)?", re.IGNORECASE)
_DATE_RE = re.compile(r"([<>]=?|=)(\d{4}(?:-\d{2}(?:-\d{2})?)?)")

_TYPE_MAP = {
    "video": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv", ".m4v"},
    "audio": {".mp3", ".flac", ".wav", ".aac", ".ogg", ".opus", ".m4a"},
    "image": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"},
    "document": {".pdf", ".docx", ".doc", ".txt", ".md", ".xlsx", ".pptx"},
}

_SIZE_UNITS = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3}


@dataclass
class SearchFilter:
    type_group: str | None = None
    extension: str | None = None
    size_op: str | None = None
    size_bytes: int | None = None
    date_op: str | None = None
    date_value: datetime | None = None
    tag: str | None = None

    def matches(self, file: "MediaFile") -> bool:
        if self.type_group:
            exts = _TYPE_MAP.get(self.type_group, set())
            if file.extension not in exts:
                return False

        if self.extension and file.extension != self.extension.lower():
            return False

        if self.size_bytes is not None and self.size_op:
            if not _compare(file.size_bytes or 0, self.size_op, self.size_bytes):
                return False

        if self.date_value is not None and self.date_op and file.fs_modified_at:
            if not _compare(file.fs_modified_at.timestamp(), self.date_op, self.date_value.timestamp()):
                return False

        if self.tag:
            tags = file.get_tags() if hasattr(file, "get_tags") else []
            if not any(self.tag.lower() in t.lower() for t in tags):
                return False

        return True


def _compare(a: float, op: str, b: float) -> bool:
    return {
        ">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b, "=": a == b,
    }.get(op, True)


class FilterParser:
    @staticmethod
    def parse(query: str) -> tuple[SearchFilter, str]:
        f = SearchFilter()
        remaining = query

        for match in _TOKEN_RE.finditer(query):
            key, value = match.group(1).lower(), match.group(2)
            remaining = remaining.replace(match.group(0), "").strip()

            if key == "type":
                f.type_group = value.lower()
            elif key == "ext":
                f.extension = value if value.startswith(".") else f".{value}"
            elif key == "size":
                m = _SIZE_RE.match(value)
                if m:
                    op, num, unit = m.group(1), float(m.group(2)), (m.group(3) or "b").lower()
                    f.size_op = op
                    f.size_bytes = int(num * _SIZE_UNITS.get(unit, 1))
            elif key == "date":
                m = _DATE_RE.match(value)
                if m:
                    op, date_str = m.group(1), m.group(2)
                    try:
                        f.date_op = op
                        f.date_value = datetime.fromisoformat(date_str)
                    except ValueError:
                        pass
            elif key == "tag":
                f.tag = value

        return f, remaining.strip()
