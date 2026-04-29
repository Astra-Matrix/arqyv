"""WebSocket hub — real-time push to connected mobile clients.

Clients connect to ws://localhost:8765/ws and receive JSON events:

  {"event": "index.progress", "current": 12, "total": 200, "path": "..."}
  {"event": "file.added",     "path": "..."}
  {"event": "playback.state", "state": "playing", "position_ms": 3400, ...}
  {"event": "ping"}

The desktop EventBus forwards events here via WebSocketBridge,
which is wired in app.py after the main window is opened.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

log = logging.getLogger(__name__)
router = APIRouter()

# Shared connection registry (module-level singleton)
_connections: set[WebSocket] = set()


async def broadcast(event: str, payload: dict[str, Any] | None = None) -> None:
    """Send a JSON event to all connected WebSocket clients."""
    if not _connections:
        return
    message = json.dumps({"event": event, **(payload or {})})
    dead: set[WebSocket] = set()
    for ws in list(_connections):
        try:
            await ws.send_text(message)
        except Exception:
            dead.add(ws)
    _connections.difference_update(dead)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    _connections.add(ws)
    log.info("WebSocket client connected (total: %d)", len(_connections))
    try:
        while True:
            # Keep alive — clients may send "ping", we echo "pong"
            data = await ws.receive_text()
            if data.strip() == "ping":
                await ws.send_text('{"event":"pong"}')
    except WebSocketDisconnect:
        pass
    finally:
        _connections.discard(ws)
        log.info("WebSocket client disconnected (total: %d)", len(_connections))
