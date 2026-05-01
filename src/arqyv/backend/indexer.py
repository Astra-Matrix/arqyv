"""Media library indexer.

Walk a directory tree, extract metadata, persist records to the DB,
generate thumbnails, and dispatch AI analysis tasks — without blocking the UI.

Threading model:
  - ThreadPoolExecutor handles I/O-bound filesystem walks.
  - AI analysis is queued separately so heavy inference never stalls indexing.
  - `run_forever()` is the async microservice entry-point (Version B / Docker).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any

from arqyv.config import AppConfig
from arqyv.core.events import EventBus, Events

if TYPE_CHECKING:
    from arqyv.database.db import Database
    from arqyv.search.engine import SearchEngine

log = logging.getLogger(__name__)

_RESCAN_INTERVAL_S = 3600   # re-scan watched folders every hour in microservice mode


class Indexer:
    def __init__(
        self,
        db: "Database",
        config: AppConfig,
        events: EventBus,
        search_engine: "SearchEngine | None" = None,
    ) -> None:
        self.db = db
        self.config = config
        self.events = events
        self.search_engine = search_engine   # optional; wired by run.py after creation
        self._watcher: "FileWatcher | None" = None
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="indexer")

        all_exts = (
            set(config.media.supported_video)
            | set(config.media.supported_audio)
            | set(config.media.supported_image)
            | set(config.media.supported_document)
        )
        self._supported: frozenset[str] = frozenset(all_exts)

    # ── Public API ─────────────────────────────────────────────────────────

    def index_directory(self, directory: str | Path) -> None:
        """Enqueue a full directory scan (non-blocking)."""
        self._executor.submit(self._scan, Path(directory))

    def index_file(self, path: Path) -> None:
        """Index a single file — called by the watcher on FS events."""
        self._executor.submit(self._process_file, path)

    def start_watcher(self) -> None:
        from arqyv.backend.watcher import FileWatcher
        self._watcher = FileWatcher(indexer=self, events=self.events)
        self._watcher.start()

        # Wire all persisted WatchedFolder paths immediately
        try:
            folders = asyncio.run(self.db.get_watched_folders())
            for folder in folders:
                if os.path.isdir(folder.path):
                    self._watcher.watch(folder.path)
        except Exception:
            log.warning("Could not load watched folders from DB at startup.", exc_info=True)

        log.info("File watcher started.")

    def stop_watcher(self) -> None:
        if self._watcher:
            self._watcher.stop()
            log.info("File watcher stopped.")

    def add_watched_folder(self, path: str | Path) -> None:
        """Register a new path: persist to DB + start watching immediately."""
        path_str = str(path)
        try:
            asyncio.run(self.db.add_watched_folder(path_str))
        except Exception:
            log.warning("Could not persist watched folder %s", path_str, exc_info=True)
        if self._watcher and os.path.isdir(path_str):
            self._watcher.watch(path_str)

    async def run_forever(self) -> None:
        """Microservice mode: load watched folders, index them, then watch forever."""
        folders = await self.db.get_watched_folders()
        for folder in folders:
            self.index_directory(folder.path)

        self.start_watcher()
        log.info("Indexer running (microservice mode). Re-scan every %ds.", _RESCAN_INTERVAL_S)

        while True:
            await asyncio.sleep(_RESCAN_INTERVAL_S)
            # Periodic re-scan picks up any missed changes
            folders = await self.db.get_watched_folders()
            for folder in folders:
                self.index_directory(folder.path)

    # ── Internal scan logic ────────────────────────────────────────────────

    def _scan(self, root: Path) -> None:
        log.info("Scanning directory: %s", root)
        files = [
            Path(dirpath) / f
            for dirpath, _, filenames in os.walk(root)
            for f in filenames
            if Path(f).suffix.lower() in self._supported
        ]
        total = len(files)
        self.events.emit(Events.INDEX_STARTED, path=str(root), total=total)

        for i, file_path in enumerate(files, start=1):
            self._process_file(file_path)
            self.events.emit(Events.INDEX_PROGRESS, current=i, total=total, path=str(file_path))

        self.events.emit(Events.INDEX_COMPLETED, path=str(root), total=total)
        log.info("Indexed %d files in %s", total, root)

    def _process_file(self, path: Path) -> None:
        if not path.exists():
            return
        try:
            from arqyv.media.metadata import MetadataExtractor
            from arqyv.backend.thumbnail import ThumbnailGenerator

            meta = MetadataExtractor.extract(path)
            asyncio.run(self.db.upsert_file(path, meta))
            ThumbnailGenerator.get_or_create(path)

            if self.config.enable_ai:
                self._executor.submit(self._run_ai, path)

            self.events.emit(Events.FILE_ADDED, path=str(path))
        except Exception:
            log.exception("Failed to process %s", path)

    def _run_ai(self, path: Path) -> None:
        """Run AI analysis, persist results to DB, update vector index."""
        try:
            from arqyv.ai.analyzer import AIAnalyzer
            analyzer = AIAnalyzer(config=self.config, events=self.events)
            result = analyzer.analyze(path)

            ai_data: dict[str, Any] = result.get("ai", {})
            if not ai_data:
                return

            # Persist AI fields to MediaFile — tags stored as JSON array
            db_meta: dict[str, Any] = {
                "ai_tags":       ai_data.get("tags", "[]"),
                "ai_summary":    ai_data.get("summary"),
                "ai_analyzed":   True,
            }
            # Transcripts for audio/video
            if "transcript" in ai_data:
                db_meta["ai_transcript"] = ai_data["transcript"]

            asyncio.run(self.db.upsert_file(path, db_meta))
            log.debug("AI metadata persisted for %s", path)

            # Index embedding in vector DB for semantic search
            embedding: list[float] | None = result.get("embedding")
            if embedding and self.search_engine is not None:
                tags_list: list[str] = result.get("tags_list", [])
                self.search_engine.index_embedding(
                    path=str(path),
                    embedding=embedding,
                    metadata={
                        "filename": path.name,
                        "extension": path.suffix.lower(),
                        "tags": ", ".join(tags_list),
                        "summary": ai_data.get("summary", ""),
                    },
                )
                log.debug("Embedding indexed for %s", path)

        except Exception:
            log.exception("AI analysis failed for %s", path)
