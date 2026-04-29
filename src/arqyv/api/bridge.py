"""WebSocketBridge — connects ARQYV's Qt EventBus to the WebSocket hub.

Subscribes to internal events and forwards them as async broadcasts
so connected mobile clients receive live updates without polling.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from arqyv.core.events import EventBus, Events

log = logging.getLogger(__name__)


class WebSocketBridge:
    """Translates EventBus callbacks into asyncio-safe WebSocket broadcasts."""

    def __init__(self, events: EventBus, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._events = events
        self._attach()

    def _attach(self) -> None:
        self._events.subscribe(Events.INDEX_PROGRESS, self._on_index_progress)
        self._events.subscribe(Events.FILE_ADDED,     self._on_file_added)

    def _push(self, event: str, payload: dict[str, Any]) -> None:
        from arqyv.api.ws import broadcast
        asyncio.run_coroutine_threadsafe(broadcast(event, payload), self._loop)

    def _on_index_progress(self, current: int = 0, total: int = 0, path: str = "") -> None:
        self._push(Events.INDEX_PROGRESS, {"current": current, "total": total, "path": path})

    def _on_file_added(self, path: str = "") -> None:
        self._push(Events.FILE_ADDED, {"path": path})

    def push_playback(self, state: str, position_ms: int, duration_ms: int, path: str | None) -> None:
        """Call this from the media engine's state_changed signal."""
        self._push("playback.state", {
            "state": state,
            "position_ms": position_ms,
            "duration_ms": duration_ms,
            "path": path,
        })
