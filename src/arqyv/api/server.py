"""ARQYV API server — FastAPI application factory and lifecycle manager."""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any

import uvicorn

from arqyv.api.app import create_app

log = logging.getLogger(__name__)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


class APIServer:
    """Runs the FastAPI app in a daemon thread alongside the Qt event loop.

    The uvicorn thread creates its own asyncio event loop. We capture that
    loop and expose it via `self.loop` so the WebSocketBridge can schedule
    coroutines onto it from the Qt main thread.
    """

    def __init__(self, services: dict[str, Any], host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        self._services = services
        self._host = host
        self._port = port
        self._thread: threading.Thread | None = None
        self._server: uvicorn.Server | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._loop_ready = threading.Event()

    @property
    def loop(self) -> asyncio.AbstractEventLoop | None:
        """The uvicorn event loop. Available after start() returns."""
        self._loop_ready.wait(timeout=5)
        return self._loop

    def start(self) -> None:
        app = create_app(self._services)
        config = uvicorn.Config(
            app,
            host=self._host,
            port=self._port,
            log_level="warning",
            access_log=False,
        )
        self._server = uvicorn.Server(config)

        def _run() -> None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._loop = loop
            self._loop_ready.set()
            loop.run_until_complete(self._server.serve())

        self._thread = threading.Thread(target=_run, name="arqyv-api", daemon=True)
        self._thread.start()
        log.info("ARQYV API server started at http://%s:%d", self._host, self._port)

    def stop(self) -> None:
        if self._server:
            self._server.should_exit = True
        if self._thread:
            self._thread.join(timeout=3)
        log.info("ARQYV API server stopped.")

    @property
    def url(self) -> str:
        return f"http://{self._host}:{self._port}"
