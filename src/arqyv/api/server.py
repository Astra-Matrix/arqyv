"""ARQYV API server — FastAPI application factory and lifecycle manager.

Run standalone:  python -m arqyv --api
Embedded mode:   APIServer(services).start() in a background thread.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

import uvicorn

from arqyv.api.app import create_app

log = logging.getLogger(__name__)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


class APIServer:
    """Runs the FastAPI app in a daemon thread alongside the Qt event loop."""

    def __init__(self, services: dict[str, Any], host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        self._services = services
        self._host = host
        self._port = port
        self._thread: threading.Thread | None = None
        self._server: uvicorn.Server | None = None

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

        self._thread = threading.Thread(
            target=self._server.run,
            name="arqyv-api",
            daemon=True,
        )
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
