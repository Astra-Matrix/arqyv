"""Lightweight pub/sub event bus.

Decouples services from UI without forcing Qt signals everywhere.
All handlers run synchronously on the calling thread; for heavy work
schedule via a QThreadPool or asyncio task instead.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable

log = logging.getLogger(__name__)

Handler = Callable[..., None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event: str, handler: Handler) -> None:
        self._subscribers[event].append(handler)
        log.debug("Subscribed %s -> %s", handler.__qualname__, event)

    def unsubscribe(self, event: str, handler: Handler) -> None:
        self._subscribers[event] = [
            h for h in self._subscribers[event] if h is not handler
        ]

    def emit(self, event: str, **payload: Any) -> None:
        log.debug("Event: %s | payload: %s", event, payload)
        for handler in list(self._subscribers.get(event, [])):
            try:
                handler(**payload)
            except Exception:
                log.exception("Handler %s raised on event %s", handler.__qualname__, event)


# ── Standard event name constants ─────────────────────────────────────────

class Events:
    # Indexing
    INDEX_STARTED = "index.started"
    INDEX_PROGRESS = "index.progress"
    INDEX_COMPLETED = "index.completed"
    INDEX_ERROR = "index.error"

    # Files
    FILE_ADDED = "file.added"
    FILE_CHANGED = "file.changed"
    FILE_DELETED = "file.deleted"

    # AI
    AI_ANALYSIS_DONE = "ai.analysis_done"
    AI_TAGS_UPDATED = "ai.tags_updated"

    # Search
    SEARCH_RESULTS = "search.results"

    # Cloud
    CLOUD_SYNC_STARTED = "cloud.sync_started"
    CLOUD_SYNC_DONE = "cloud.sync_done"
    CLOUD_SYNC_ERROR = "cloud.sync_error"

    # Media player
    PLAYER_STATE_CHANGED = "player.state_changed"
    PLAYER_POSITION_CHANGED = "player.position_changed"
