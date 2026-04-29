"""File system watcher using watchdog.

Monitors registered directories for file creation, modification, and deletion.
Delegates to Indexer for processing; emits EventBus events for UI updates.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from arqyv.core.events import EventBus, Events

if TYPE_CHECKING:
    from arqyv.backend.indexer import Indexer

log = logging.getLogger(__name__)


class _ARQYVEventHandler(FileSystemEventHandler):
    def __init__(self, indexer: "Indexer", events: EventBus, supported: frozenset[str]) -> None:
        super().__init__()
        self.indexer = indexer
        self.events = events
        self.supported = supported

    def _is_supported(self, path: str) -> bool:
        return Path(path).suffix.lower() in self.supported

    def on_created(self, event: FileCreatedEvent) -> None:  # type: ignore[override]
        if not event.is_directory and self._is_supported(event.src_path):
            log.debug("FS created: %s", event.src_path)
            self.indexer.index_file(Path(event.src_path))

    def on_modified(self, event: FileModifiedEvent) -> None:  # type: ignore[override]
        if not event.is_directory and self._is_supported(event.src_path):
            log.debug("FS modified: %s", event.src_path)
            self.indexer.index_file(Path(event.src_path))
            self.events.emit(Events.FILE_CHANGED, path=event.src_path)

    def on_deleted(self, event: FileDeletedEvent) -> None:  # type: ignore[override]
        if not event.is_directory:
            log.debug("FS deleted: %s", event.src_path)
            self.events.emit(Events.FILE_DELETED, path=event.src_path)

    def on_moved(self, event: FileMovedEvent) -> None:  # type: ignore[override]
        if not event.is_directory and self._is_supported(event.dest_path):
            log.debug("FS moved: %s → %s", event.src_path, event.dest_path)
            self.events.emit(Events.FILE_DELETED, path=event.src_path)
            self.indexer.index_file(Path(event.dest_path))


class FileWatcher:
    def __init__(self, indexer: "Indexer", events: EventBus) -> None:
        self.indexer = indexer
        self.events = events
        self._observer = Observer()
        self._watched_paths: list[str] = []

    def watch(self, path: str | Path) -> None:
        handler = _ARQYVEventHandler(
            indexer=self.indexer,
            events=self.events,
            supported=self.indexer._supported,
        )
        self._observer.schedule(handler, str(path), recursive=True)
        self._watched_paths.append(str(path))
        log.info("Watching: %s", path)

    def start(self) -> None:
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()
