"""Media library indexer.

Walk a directory tree, extract metadata, persist records to the DB,
generate thumbnails, and dispatch AI analysis tasks – all without
blocking the UI thread.

Threading model:
  - QThreadPool workers handle I/O-bound filesystem walks.
  - AI analysis is queued separately so heavy inference doesn't stall indexing.
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING

from arqyv.config import AppConfig
from arqyv.core.events import EventBus, Events

if TYPE_CHECKING:
    from arqyv.database.db import Database

log = logging.getLogger(__name__)


class Indexer:
    def __init__(self, db: "Database", config: AppConfig, events: EventBus) -> None:
        self.db = db
        self.config = config
        self.events = events
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

    def start_watcher(self) -> None:
        from arqyv.backend.watcher import FileWatcher
        self._watcher = FileWatcher(indexer=self, events=self.events)
        self._watcher.start()
        log.info("File watcher started.")

    def stop_watcher(self) -> None:
        if self._watcher:
            self._watcher.stop()
            log.info("File watcher stopped.")

    def index_file(self, path: Path) -> None:
        """Index a single file – called by the watcher on FS events."""
        self._executor.submit(self._process_file, path)

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
            import asyncio

            meta = MetadataExtractor.extract(path)
            asyncio.run(self.db.upsert_file(path, meta))

            ThumbnailGenerator.get_or_create(path)

            if self.config.enable_ai:
                from arqyv.ai.analyzer import AIAnalyzer
                # Submit to AI queue asynchronously – don't block indexer
                self._executor.submit(self._run_ai, path)

            self.events.emit(Events.FILE_ADDED, path=str(path))
        except Exception:
            log.exception("Failed to process %s", path)

    def _run_ai(self, path: Path) -> None:
        """Run AI analysis in a separate thread to avoid blocking indexer."""
        try:
            from arqyv.ai.analyzer import AIAnalyzer
            # Re-use a cached instance; this is safe because AIAnalyzer is thread-safe.
            analyzer = AIAnalyzer(config=self.config, events=self.events)
            analyzer.analyze(path)
        except Exception:
            log.exception("AI analysis failed for %s", path)
