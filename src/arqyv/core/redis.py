"""
Redis-backed event bus — Version B microservice replacement for the
in-process EventBus.

Pub/Sub survives service restarts; any worker can subscribe to any channel.

Requires:  pip install redis[asyncio]>=5.0
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable

log = logging.getLogger(__name__)


class RedisEventBus:
    """
    Thin async wrapper around Redis Pub/Sub.

    Publishing is fire-and-forget (JSON-encoded payload).
    Subscribing returns an async generator that yields decoded payloads.

    Usage (publisher):
        bus = RedisEventBus(url="redis://localhost:6379/0")
        await bus.connect()
        await bus.publish("file.added", {"path": "/media/clip.mp4"})

    Usage (subscriber):
        async for payload in bus.subscribe("file.*"):
            print(payload)
    """

    def __init__(self, url: str = "redis://localhost:6379/0") -> None:
        self._url    = url
        self._redis  = None   # redis.asyncio.Redis
        self._pubsub = None   # redis.asyncio.client.PubSub
        self._handlers: dict[str, list[Callable]] = {}

    async def connect(self) -> None:
        try:
            import redis.asyncio as aioredis
        except ImportError as exc:
            raise RuntimeError(
                "redis[asyncio] is required for Version B. "
                "Run: pip install 'redis[asyncio]>=5.0'"
            ) from exc

        self._redis  = await aioredis.from_url(self._url, decode_responses=True)
        self._pubsub = self._redis.pubsub()
        log.info("redis_connected url=%s", self._url)

    async def close(self) -> None:
        if self._pubsub:
            await self._pubsub.close()
        if self._redis:
            await self._redis.aclose()
        log.info("redis_disconnected")

    # ── Publishing ────────────────────────────────────────────────────────────

    async def publish(self, channel: str, payload: Any = None) -> None:
        if not self._redis:
            raise RuntimeError("Call connect() before publishing.")
        body = json.dumps(payload or {}, default=str)
        await self._redis.publish(channel, body)

    async def set_health(self, service: str, data: dict) -> None:
        """Write health data to a Redis key for the TUI dashboard to read."""
        if not self._redis:
            return
        await self._redis.set(
            f"health:{service}",
            json.dumps(data, default=str),
            ex=30,   # expire after 30 s if no heartbeat
        )

    # ── Subscribing ──────────────────────────────────────────────────────────

    async def subscribe(self, *channels: str) -> None:
        """Subscribe to one or more channel patterns."""
        if not self._pubsub:
            raise RuntimeError("Call connect() first.")
        await self._pubsub.psubscribe(*channels)

    async def listen(self):
        """Async generator that yields (channel, payload) tuples."""
        if not self._pubsub:
            raise RuntimeError("Call connect() and subscribe() first.")
        async for message in self._pubsub.listen():
            if message["type"] in ("message", "pmessage"):
                channel = message.get("channel", "")
                try:
                    payload = json.loads(message["data"])
                except (json.JSONDecodeError, TypeError):
                    payload = message["data"]
                yield channel, payload

    # ── Compatibility shim (matches in-process EventBus interface) ───────────

    def subscribe_sync(self, event: str, handler: Callable) -> None:
        """Register a sync callback — fired via asyncio.create_task on receipt."""
        self._handlers.setdefault(event, []).append(handler)
