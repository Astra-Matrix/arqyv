"""Async database layer using SQLAlchemy 2.x + aiosqlite.

All public methods are async. Callers in synchronous threads must use
asyncio.run() or an event loop bridge (e.g. asyncio.get_event_loop()).
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import select, delete

from arqyv.database.models import Base, MediaFile, SearchHistory, WatchedFolder

log = logging.getLogger(__name__)


class Database:
    def __init__(self, url: str, echo: bool = False) -> None:
        self._url = url
        self._engine: AsyncEngine = create_async_engine(url, echo=echo, future=True)
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def init(self) -> None:
        """Create all tables if they don't exist."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info("Database initialized: %s", self._url)

    async def close(self) -> None:
        await self._engine.dispose()
        log.info("Database connection closed.")

    # ── Session context manager ────────────────────────────────────────────

    def session(self) -> AsyncSession:
        return self._session_factory()

    # ── MediaFile CRUD ─────────────────────────────────────────────────────

    async def upsert_file(self, path: Path, meta: dict[str, Any]) -> MediaFile:
        async with self.session() as sess:
            async with sess.begin():
                result = await sess.execute(
                    select(MediaFile).where(MediaFile.path == str(path))
                )
                record = result.scalar_one_or_none()

                if record is None:
                    record = MediaFile(path=str(path), filename=path.name, extension=path.suffix.lower())
                    sess.add(record)

                stat = path.stat() if path.exists() else None
                record.size_bytes = stat.st_size if stat else 0
                record.fs_modified_at = datetime.fromtimestamp(stat.st_mtime) if stat else None

                for key, value in meta.items():
                    if hasattr(record, key):
                        setattr(record, key, value)

                record.updated_at = datetime.utcnow()

        return record

    async def get_file(self, path: str) -> MediaFile | None:
        async with self.session() as sess:
            result = await sess.execute(select(MediaFile).where(MediaFile.path == path))
            return result.scalar_one_or_none()

    async def delete_file(self, path: str) -> None:
        async with self.session() as sess:
            async with sess.begin():
                await sess.execute(delete(MediaFile).where(MediaFile.path == path))

    async def list_files(
        self,
        extension: str | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> list[MediaFile]:
        async with self.session() as sess:
            q = select(MediaFile)
            if extension:
                q = q.where(MediaFile.extension == extension.lower())
            q = q.order_by(MediaFile.updated_at.desc()).limit(limit).offset(offset)
            result = await sess.execute(q)
            return list(result.scalars().all())

    async def get_files_by_paths(self, paths: list[str]) -> list[MediaFile]:
        """Fetch MediaFile records for a given list of paths (preserves order)."""
        if not paths:
            return []
        async with self.session() as sess:
            q = select(MediaFile).where(MediaFile.path.in_(paths))
            result = await sess.execute(q)
            records = {r.path: r for r in result.scalars().all()}
        return [records[p] for p in paths if p in records]

    async def search_files(self, query: str, limit: int = 50) -> list[MediaFile]:
        """Simple LIKE-based full-text search (pre-semantic fallback)."""
        async with self.session() as sess:
            like = f"%{query}%"
            q = (
                select(MediaFile)
                .where(
                    MediaFile.filename.ilike(like)
                    | MediaFile.ai_tags.ilike(like)
                    | MediaFile.ai_summary.ilike(like)
                    | MediaFile.ai_transcript.ilike(like)
                )
                .limit(limit)
            )
            result = await sess.execute(q)
            return list(result.scalars().all())

    # ── Watched folders ────────────────────────────────────────────────────

    async def add_watched_folder(self, path: str) -> WatchedFolder:
        async with self.session() as sess:
            async with sess.begin():
                result = await sess.execute(
                    select(WatchedFolder).where(WatchedFolder.path == path)
                )
                existing = result.scalar_one_or_none()
                if existing:
                    return existing
                folder = WatchedFolder(path=path)
                sess.add(folder)
        return folder

    async def get_watched_folders(self) -> list[WatchedFolder]:
        async with self.session() as sess:
            result = await sess.execute(
                select(WatchedFolder).where(WatchedFolder.enabled == True)
            )
            return list(result.scalars().all())

    # ── Search history ─────────────────────────────────────────────────────

    async def record_search(self, query: str, result_count: int) -> None:
        async with self.session() as sess:
            async with sess.begin():
                sess.add(SearchHistory(query=query, result_count=result_count))
