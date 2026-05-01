"""
Async-safe dependency injection container.

Usage:
    container = Container()
    container.register("db", lambda c: Database.create())
    db = await container.resolve("db")   # cached on first call
    await container.teardown()           # closes in reverse order

    async with container.lifespan():     # auto-teardown
        ...
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from contextlib import asynccontextmanager
from typing import Any, Callable, TypeVar, AsyncIterator

log = logging.getLogger(__name__)
T   = TypeVar("T")


class Container:
    """
    Minimal async DI container.

    - Factories are either sync or async callables: ``factory(container) -> T``.
    - First ``resolve()`` call builds and caches; subsequent calls are O(1).
    - ``teardown()`` calls ``.close()`` / ``.aclose()`` on instances in
      reverse registration order, swallowing per-service errors.
    """

    def __init__(self) -> None:
        self._factories:  dict[str, Callable]  = {}
        self._instances:  dict[str, Any]        = {}
        self._order:      list[str]              = []
        self._lock = asyncio.Lock()

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, name: str, factory: Callable) -> None:
        """Register a factory for *name*.  Factory receives this container."""
        if name in self._factories:
            raise ValueError(f"Service '{name}' already registered.")
        self._factories[name] = factory
        self._order.append(name)

    # ── Resolution ────────────────────────────────────────────────────────────

    async def resolve(self, name: str) -> Any:
        """Return the cached instance, building it on first call."""
        if name in self._instances:
            return self._instances[name]
        async with self._lock:
            if name not in self._instances:
                factory = self._factories[name]
                if inspect.iscoroutinefunction(factory):
                    instance = await factory(self)
                else:
                    instance = factory(self)
                self._instances[name] = instance
                log.info("service_resolved name=%s", name)
        return self._instances[name]

    def get(self, name: str) -> Any:
        """Synchronous accessor — raises if not yet resolved."""
        if name not in self._instances:
            raise KeyError(f"Service '{name}' has not been resolved yet.")
        return self._instances[name]

    # ── Teardown ──────────────────────────────────────────────────────────────

    async def teardown(self) -> None:
        """Close all resolved services in reverse registration order."""
        for name in reversed(self._order):
            inst = self._instances.get(name)
            if inst is None:
                continue
            closer = getattr(inst, "aclose", None) or getattr(inst, "close", None)
            if closer:
                try:
                    result = closer()
                    if inspect.isawaitable(result):
                        await result
                    log.info("service_closed name=%s", name)
                except Exception as exc:
                    log.warning("service_close_error name=%s error=%s", name, exc)

    # ── Lifespan context manager ──────────────────────────────────────────────

    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator["Container"]:
        try:
            yield self
        finally:
            await self.teardown()
