"""Auto-collections — group files by AI tags, date, type, or custom rules.

Collections are computed on demand (never stored) or can be cached to the DB
as virtual playlists. The CollectionManager is stateless and thread-safe.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from arqyv.database.db import Database
    from arqyv.database.models import MediaFile

log = logging.getLogger(__name__)

_MIN_COLLECTION_SIZE = 3      # skip groups smaller than this
_MAX_TAG_COLLECTIONS = 20     # cap the number of tag-based collections shown


@dataclass
class Collection:
    name: str
    description: str
    icon: str                  # single unicode glyph for UI display
    files: list["MediaFile"] = field(default_factory=list)
    kind: str = "tag"          # tag | date | type | custom

    @property
    def count(self) -> int:
        return len(self.files)


class CollectionManager:
    def __init__(self, db: "Database") -> None:
        self.db = db

    # ── Public API ─────────────────────────────────────────────────────────

    async def get_all(self) -> list[Collection]:
        """Return all auto-generated collections, merged and sorted by size."""
        all_files = await self.db.list_files(limit=5000)

        cols: list[Collection] = []
        cols.extend(self._by_type(all_files))
        cols.extend(self._by_date(all_files))
        cols.extend(self._by_tag(all_files))

        # Sort by size descending
        cols.sort(key=lambda c: c.count, reverse=True)
        return cols

    async def get_by_tag(self, tag: str) -> Collection:
        all_files = await self.db.list_files(limit=5000)
        matching = [f for f in all_files if tag.lower() in [t.lower() for t in self._tags(f)]]
        return Collection(name=tag.title(), description=f'Files tagged "{tag}"', icon="", files=matching, kind="tag")

    def get_all_sync(self) -> list[Collection]:
        return asyncio.run(self.get_all())

    # ── Collection generators ──────────────────────────────────────────────

    def _by_type(self, files: list["MediaFile"]) -> list[Collection]:
        groups: dict[str, list["MediaFile"]] = defaultdict(list)
        type_meta = {
            "video":    ("Videos",     "", "video/"),
            "audio":    ("Music",      "", "audio/"),
            "image":    ("Photos",     "", "image/"),
            "document": ("Documents",  "", "application/"),
        }
        for f in files:
            mime = f.mime_type or ""
            for kind, (name, icon, prefix) in type_meta.items():
                if mime.startswith(prefix):
                    groups[kind].append(f)
                    break

        return [
            Collection(name=meta[0], description=f"All {meta[0].lower()}", icon=meta[1], files=grp, kind="type")
            for kind, (meta, grp) in ((k, (type_meta[k], groups[k])) for k in type_meta)
            if len(groups[kind]) >= _MIN_COLLECTION_SIZE
        ]

    def _by_date(self, files: list["MediaFile"]) -> list[Collection]:
        by_year: dict[int, list["MediaFile"]] = defaultdict(list)
        for f in files:
            dt = f.fs_modified_at or f.indexed_at
            if dt:
                by_year[dt.year].append(f)

        return [
            Collection(
                name=str(year),
                description=f"Files from {year}",
                icon="",
                files=grp,
                kind="date",
            )
            for year, grp in sorted(by_year.items(), reverse=True)
            if len(grp) >= _MIN_COLLECTION_SIZE
        ]

    def _by_tag(self, files: list["MediaFile"]) -> list[Collection]:
        tag_files: dict[str, list["MediaFile"]] = defaultdict(list)
        for f in files:
            for tag in self._tags(f):
                if len(tag) >= 3:
                    tag_files[tag.lower()].append(f)

        # Pick the most common tags
        top_tags = sorted(tag_files.items(), key=lambda x: len(x[1]), reverse=True)[:_MAX_TAG_COLLECTIONS]

        return [
            Collection(name=tag.title(), description=f'Tagged "{tag}"', icon="", files=grp, kind="tag")
            for tag, grp in top_tags
            if len(grp) >= _MIN_COLLECTION_SIZE
        ]

    @staticmethod
    def _tags(f: "MediaFile") -> list[str]:
        if not f.ai_tags:
            return []
        try:
            return json.loads(f.ai_tags)
        except (json.JSONDecodeError, TypeError):
            return []
