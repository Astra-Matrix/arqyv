"""
ARQYV — Monolith launcher.

Usage:
    python run.py [--debug] [--data-dir PATH]
"""

from __future__ import annotations

import atexit
import asyncio
import logging
import os
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ── Path bootstrap ────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent
_SRC  = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
# Force the native Windows platform plugin — prevents QT_QPA_PLATFORM=offscreen
# from silently rendering every window into an invisible buffer.
if sys.platform == "win32":
    os.environ["QT_QPA_PLATFORM"] = "windows"

# ── CLI args ──────────────────────────────────────────────────────────────────
_debug = "--debug" in sys.argv
_data_dir: Path | None = None
for _i, _a in enumerate(sys.argv[1:], 1):
    if _a == "--data-dir" and _i < len(sys.argv) - 1:
        _data_dir = Path(sys.argv[_i + 1])

# ── Logging (structured JSON in prod, pretty in debug) ────────────────────────
from arqyv.utils.logger import configure_logging
configure_logging(debug=_debug, json_output=not _debug)
log = logging.getLogger("arqyv.run")

# ── Qt bootstrap ──────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore    import Qt, QTimer

qt_app = QApplication(sys.argv)
qt_app.setApplicationName("ARQYV")
qt_app.setOrganizationName("Alaustrup")

# ── Core imports ──────────────────────────────────────────────────────────────
from arqyv                import __version__
from arqyv.config         import AppConfig, config as _default_config
from arqyv.core.events    import EventBus
from arqyv.core.settings  import SettingsManager

qt_app.setApplicationVersion(__version__)
log.info("boot", extra={"version": __version__, "debug": _debug})


@dataclass
class AppContext:
    """Typed container for all runtime services."""
    config:      AppConfig
    events:      EventBus
    settings:    SettingsManager
    db:          Any = field(default=None)
    indexer:     Any = field(default=None)
    search:      Any = field(default=None)
    ai:          Any = field(default=None)
    api:         Any = field(default=None)
    ws_bridge:   Any = field(default=None)
    main_window: Any = field(default=None)

    def as_services(self) -> dict[str, Any]:
        """Return a name→instance mapping for components that expect a plain dict."""
        return {
            k: v for k, v in vars(self).items()
            if v is not None and k not in ("config", "events", "settings")
        }


# ── Config ────────────────────────────────────────────────────────────────────
cfg      = AppConfig(data_dir=_data_dir) if _data_dir else _default_config
events   = EventBus()
settings = SettingsManager(config_dir=cfg.config_dir)
ctx      = AppContext(config=cfg, events=events, settings=settings)

# ── VLC auto-detection (non-blocking) ────────────────────────────────────────
from arqyv.media.vlc_setup import setup_vlc
setup_vlc()

# ── Database ──────────────────────────────────────────────────────────────────
from arqyv.database.db import Database
ctx.db = Database(url=cfg.db_url, echo=cfg.db.echo)
asyncio.run(ctx.db.init())

# ── Backend services ──────────────────────────────────────────────────────────
from arqyv.backend.indexer import Indexer
from arqyv.search.engine   import SearchEngine
from arqyv.ai.analyzer     import AIAnalyzer

ctx.search  = SearchEngine(db=ctx.db, config=cfg)
ctx.indexer = Indexer(db=ctx.db, config=cfg, events=events, search_engine=ctx.search)
ctx.ai      = AIAnalyzer(config=cfg, events=events)

if cfg.enable_auto_index:
    ctx.indexer.start_watcher()

log.info("services_ready")

# ── Main window ───────────────────────────────────────────────────────────────
from arqyv.ui.main_window  import MainWindow
from arqyv.ui.window_utils import center_window, bring_to_foreground

ctx.main_window = MainWindow(config=cfg, events=events, ctx=ctx)
center_window(ctx.main_window, cfg, qt_app)
ctx.main_window.setWindowState(Qt.WindowState.WindowNoState)
ctx.main_window.show()

QTimer.singleShot(200, lambda: bring_to_foreground(ctx.main_window))

# ── Optional API server ───────────────────────────────────────────────────────
if cfg.enable_api_server:
    from arqyv.api.server import APIServer
    ctx.api = APIServer(services=ctx.as_services(), port=cfg.api_port)
    ctx.api.start()
    log.info("api_ready", extra={"port": cfg.api_port})

    def _attach_ws_bridge() -> None:
        import time; time.sleep(0.5)
        try:
            from arqyv.api.bridge import WebSocketBridge
            # Use the uvicorn event loop so coroutines are actually executed
            loop = ctx.api.loop
            if loop is None:
                log.warning("ws_bridge_failed: uvicorn loop not ready")
                return
            ctx.ws_bridge = WebSocketBridge(events, loop)
            log.info("ws_bridge_ready")
        except Exception as exc:
            log.warning("ws_bridge_failed", extra={"error": str(exc)})

    threading.Thread(target=_attach_ws_bridge, name="ws-bridge", daemon=True).start()

# ── Graceful shutdown ─────────────────────────────────────────────────────────
_shutdown_called = False

def _shutdown() -> None:
    global _shutdown_called
    if _shutdown_called:
        return
    _shutdown_called = True
    log.info("shutdown_start")
    try:
        if ctx.api:      ctx.api.stop()
        if ctx.indexer:  ctx.indexer.stop_watcher()
        if ctx.db:       asyncio.run(ctx.db.close())
    except Exception as exc:
        log.warning("shutdown_error", extra={"error": str(exc)})
    log.info("shutdown_complete")

atexit.register(_shutdown)
qt_app.aboutToQuit.connect(_shutdown)

# ── Enter event loop ──────────────────────────────────────────────────────────
log.info("event_loop_enter")
sys.exit(qt_app.exec())
