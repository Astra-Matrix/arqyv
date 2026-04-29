"""Application controller.

Owns the service lifecycle: boots services in order, wires dependencies,
and shuts down cleanly when Qt signals exit.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from PyQt6.QtWidgets import QApplication

from arqyv.config import AppConfig, config as default_config
from arqyv.core.events import EventBus
from arqyv.core.settings import SettingsManager

log = logging.getLogger(__name__)


class Application:
    """Top-level service orchestrator.

    Deliberately not a QObject – all Qt-facing logic lives in MainWindow.
    """

    def __init__(
        self,
        qt_app: QApplication,
        data_dir: Path | None = None,
        debug: bool = False,
    ) -> None:
        self.qt_app = qt_app
        self.debug = debug

        # Allow CLI override of data directory.
        self.config: AppConfig = default_config
        if data_dir is not None:
            self.config = AppConfig(data_dir=data_dir)

        self.events = EventBus()
        self.settings = SettingsManager(config_dir=self.config.config_dir)

        # Lazily-initialized services (set during start())
        self._services: dict[str, Any] = {}

    # ── Lifecycle ──────────────────────────────────────────────────────────

    def start(self) -> None:
        log.info("ARQYV starting (debug=%s)", self.debug)
        self._init_services()
        self._open_main_window()
        self.qt_app.aboutToQuit.connect(self._on_quit)

    def _init_services(self) -> None:
        """Import and start each service lazily to keep cold-start fast."""
        # VLC discovery runs before anything else so the media player widget
        # picks up the right backend on first construction.
        from arqyv.media.vlc_setup import setup_vlc
        setup_vlc()

        from arqyv.database.db import Database
        from arqyv.backend.indexer import Indexer
        from arqyv.search.engine import SearchEngine
        from arqyv.ai.analyzer import AIAnalyzer

        db = Database(url=self.config.db_url, echo=self.config.db.echo)
        asyncio.run(db.init())

        indexer = Indexer(db=db, config=self.config, events=self.events)
        search = SearchEngine(db=db, config=self.config)
        ai = AIAnalyzer(config=self.config, events=self.events)

        self._services = {
            "db": db,
            "indexer": indexer,
            "search": search,
            "ai": ai,
        }

        if self.config.enable_auto_index:
            indexer.start_watcher()

        log.info("All services initialized.")

    def _open_main_window(self) -> None:
        from arqyv.ui.main_window import MainWindow

        window = MainWindow(
            config=self.config,
            events=self.events,
            services=self._services,
        )
        window.show()
        self._services["main_window"] = window

        # Start the local API server after the window is open so services
        # (including main_window itself) are fully registered in self._services.
        if self.config.enable_api_server:
            self._start_api_server()

    def _start_api_server(self) -> None:
        from arqyv.api.server import APIServer
        api = APIServer(services=self._services, port=self.config.api_port)
        api.start()
        self._services["api"] = api

        # Wire EventBus -> WebSocket push
        import asyncio as _asyncio
        import threading
        # The uvicorn event loop runs in the daemon thread; grab it after a brief wait.
        def _attach_bridge() -> None:
            import time
            time.sleep(0.5)  # let uvicorn start its loop
            # Find the loop from the running uvicorn server
            server = api._server
            if server and hasattr(server, "started"):
                try:
                    loop = server.config.loop  # type: ignore[attr-defined]
                except Exception:
                    loop = None
                if loop is None:
                    # Fallback: create a fresh reference loop is inaccessible
                    return
                from arqyv.api.bridge import WebSocketBridge
                self._services["ws_bridge"] = WebSocketBridge(self.events, loop)
                log.info("WebSocket event bridge attached.")

        threading.Thread(target=_attach_bridge, name="ws-bridge-attach", daemon=True).start()
        log.info("ARQYV API server launched at http://127.0.0.1:%d", self.config.api_port)

    def _on_quit(self) -> None:
        log.info("Shutting down…")
        if "api" in self._services:
            self._services["api"].stop()
        if "indexer" in self._services:
            self._services["indexer"].stop_watcher()
        if "db" in self._services:
            asyncio.run(self._services["db"].close())
        log.info("Goodbye.")

    # ── Convenience accessors ──────────────────────────────────────────────

    def get(self, name: str) -> Any:
        """Retrieve a registered service by name."""
        return self._services[name]
