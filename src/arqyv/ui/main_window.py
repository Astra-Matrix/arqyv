"""Main application window.

Layout:
  ┌─ Toolbar: [Search ──────────────────────] [Share] [Settings] ──────────┐
  │ ┌─ Library ──┐ ┌─ Preview / Content ────────────────┐ ┌─ Info ───────┐ │
  │ │ File tree  │ │                                     │ │ Metadata     │ │
  │ │            │ │                                     │ │ AI tags      │ │
  │ └────────────┘ └─────────────────────────────────────┘ └─────────────┘ │
  │ ┌─ Media Player ─────────────────────────────────────────────────────┐  │
  │ │ ⏮ ▶ ■ ⏭   0:00 / 0:00        🔊 ── −1.0×+  CC  ↺  ⇀  [format]  │  │
  │ └────────────────────────────────────────────────────────────────────┘  │
  │ ┌─ Status bar ─────────────────────────────────────────────────────────┐ │
  └──────────────────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import threading

from PyQt6.QtCore import Qt, QSize, QThreadPool, pyqtSlot
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QWidget,
)

from arqyv.config import AppConfig
from arqyv.core.events import EventBus, Events
from arqyv.ui.themes.dark import apply_dark_theme, PALETTE as DARK_P
from arqyv.ui.widgets.file_browser import FileBrowserWidget
from arqyv.ui.widgets.media_player import MediaPlayerWidget
from arqyv.ui.widgets.metadata_panel import MetadataPanelWidget
from arqyv.ui.widgets.preview_panel import PreviewPanelWidget
from arqyv.ui.widgets.search_bar import SearchBarWidget
from arqyv.ui.widgets.search_results import SearchResultsWidget

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: AppConfig,
        events: EventBus,
        services: dict[str, Any] | None = None,
        ctx: Any = None,
    ) -> None:
        super().__init__()
        self.config = config
        self.events = events
        # Accept either a typed AppContext (Version A) or a plain dict (legacy).
        if ctx is not None:
            self.ctx = ctx
            self.services: dict[str, Any] = ctx.as_services()
        else:
            self.ctx = None
            self.services = services or {}

        self._selected_path: Path | None = None
        self._share_manager: Any | None = None
        self._search_seq: int = 0
        self._search_cancel: threading.Event = threading.Event()

        self._setup_window()
        self._build_ui()
        self._wire_engine()
        self._connect_events()
        self._apply_theme()
        self._init_share_manager()
        self._install_command_palette()

    # ── Window ─────────────────────────────────────────────────────────────

    def _setup_window(self) -> None:
        self.setWindowTitle("ARQYV")
        self.resize(self.config.window_width, self.config.window_height)
        self.setMinimumSize(QSize(960, 620))

    # ── UI ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_toolbar()
        self._build_docks()
        self._build_central()
        self._build_status_bar()
        self._build_menu()

    def _build_toolbar(self) -> None:
        tb = QToolBar("Main", self)
        tb.setIconSize(QSize(18, 18))
        tb.setMovable(False)
        tb.setObjectName("mainToolbar")

        self._search_bar = SearchBarWidget(events=self.events, services=self.services)
        self._search_bar.live_search_changed.connect(self._on_live_search)
        tb.addWidget(self._search_bar)
        tb.addSeparator()

        share_act = QAction("⬆  Share", self)
        share_act.setToolTip("Share the selected file instantly — QR code, no accounts")
        share_act.triggered.connect(self._on_share)
        tb.addAction(share_act)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

    def _build_docks(self) -> None:
        # Left dock: stacked — page 0 = file browser, page 1 = live search results
        self._file_browser = FileBrowserWidget(
            config=self.config, events=self.events, services=self.services
        )
        self._file_browser.file_selected.connect(self._on_file_selected)

        self._search_results = SearchResultsWidget()
        self._search_results.file_selected.connect(self._on_file_selected)
        self._search_results.file_activated.connect(self._on_file_activated)
        self._search_results.request_clear.connect(self._on_search_clear)

        self._left_stack = QStackedWidget()
        self._left_stack.addWidget(self._file_browser)    # page 0
        self._left_stack.addWidget(self._search_results)  # page 1

        left = QDockWidget("Library", self)
        left.setWidget(self._left_stack)
        left.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        left.setMinimumWidth(240)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left)

        # Right: metadata / AI info panel
        self._metadata = MetadataPanelWidget(events=self.events)
        right = QDockWidget("Info", self)
        right.setWidget(self._metadata)
        right.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        right.setMinimumWidth(200)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right)

    def _build_central(self) -> None:
        # Vertical splitter: preview (top) + player (bottom)
        outer = QSplitter(Qt.Orientation.Vertical)

        self._preview = PreviewPanelWidget(config=self.config, events=self.events)
        self._player = MediaPlayerWidget(config=self.config, events=self.events)

        outer.addWidget(self._preview)
        outer.addWidget(self._player)
        outer.setSizes([520, 280])

        self.setCentralWidget(outer)

    def _build_status_bar(self) -> None:
        from arqyv.ui.themes.dark import PALETTE as P
        self._status = QStatusBar(self)
        self.setStatusBar(self._status)

        # Permanent right-side widgets
        from PyQt6.QtWidgets import QLabel
        self._api_indicator = QLabel(f"API  ·  127.0.0.1:{self.config.api_port}")
        self._api_indicator.setStyleSheet(f"color: {P['text3']}; font-size: 11px; padding: 0 10px;")
        self._status.addPermanentWidget(self._api_indicator)

        self._status.showMessage("Ready")

    def _build_menu(self) -> None:
        mb = self.menuBar()
        assert mb

        # File
        fm = mb.addMenu("&File")
        open_act = QAction("&Open Folder…", self)
        open_act.setShortcut(QKeySequence.StandardKey.Open)
        open_act.triggered.connect(self._on_open_folder)
        fm.addAction(open_act)

        open_files_act = QAction("Open File(s)…", self)
        open_files_act.setShortcut("Ctrl+Shift+O")
        open_files_act.triggered.connect(self._on_open_files)
        fm.addAction(open_files_act)

        fm.addSeparator()

        share_act = QAction("⬆  &Share Selected…", self)
        share_act.setShortcut("Ctrl+Shift+S")
        share_act.triggered.connect(self._on_share)
        fm.addAction(share_act)

        fm.addSeparator()

        quit_act = QAction("&Quit", self)
        quit_act.setShortcut(QKeySequence.StandardKey.Quit)
        quit_act.triggered.connect(self.close)
        fm.addAction(quit_act)

        # Playback
        pm = mb.addMenu("&Playback")
        for label, shortcut, slot in (
            ("Play / Pause", "Space", lambda: self._player.engine and self._player.engine.toggle()),
            ("Stop",         "S",    lambda: self._player.engine and self._player.engine.stop()),
            ("Next",         "]",    lambda: self._player.engine and self._player.engine.play_next()),
            ("Previous",     "[",    lambda: self._player.engine and self._player.engine.play_previous()),
        ):
            act = QAction(label, self)
            act.setShortcut(shortcut)
            act.triggered.connect(slot)
            pm.addAction(act)

        # Tools
        tm = mb.addMenu("&Tools")
        batch = QAction("Batch Rename…", self)
        batch.triggered.connect(self._on_batch_rename)
        tm.addAction(batch)

        cloud = QAction("Cloud Sync…", self)
        cloud.triggered.connect(self._on_cloud_sync)
        tm.addAction(cloud)

        tm.addSeparator()

        settings = QAction("&Settings…", self)
        settings.triggered.connect(self._on_settings)
        tm.addAction(settings)

        # Help
        hm = mb.addMenu("&Help")
        hm.addAction(QAction("About ARQYV", self))

    # ── Engine wiring ──────────────────────────────────────────────────────

    def _wire_engine(self) -> None:
        """Initialize ARQYVMediaEngine inside the player widget."""
        engine = self._player.init_engine()
        engine.track_changed.connect(self._on_track_changed)
        engine.error.connect(self._on_engine_error)
        log.info("ARQYVMediaEngine wired to MainWindow.")

    # ── Share manager ──────────────────────────────────────────────────────

    def _init_share_manager(self) -> None:
        from arqyv.share.manager import ShareManager
        self._share_manager = ShareManager(self.config)
        self._share_manager.start_discovery()

    # ── Event wiring ───────────────────────────────────────────────────────

    def _connect_events(self) -> None:
        self.events.subscribe(Events.INDEX_PROGRESS, self._on_index_progress)
        self.events.subscribe(Events.FILE_ADDED,     self._on_file_added)

    def _on_index_progress(self, current: int = 0, total: int = 0, path: str = "") -> None:
        self._status.showMessage(f"Indexing {current}/{total} — {Path(path).name}")

    def _on_file_added(self, path: str = "") -> None:
        self._status.showMessage(f"Indexed: {Path(path).name}", 3000)

    # ── Slots ──────────────────────────────────────────────────────────────

    @pyqtSlot()
    def _on_open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Open Media Folder")
        if folder:
            self.services["indexer"].index_directory(folder)
            self._file_browser.navigate_to(folder)

    @pyqtSlot()
    def _on_open_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open File(s)", "",
            "Media (*.*)"
        )
        if paths:
            media_paths = [Path(p) for p in paths]
            self._player.open_playlist(media_paths, start=0)

    # ── Live search ────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _on_live_search(self, query: str) -> None:
        query = query.strip()
        if not query:
            self._on_search_clear()
            return

        # Cancel any in-flight search
        self._search_cancel.set()
        self._search_cancel = threading.Event()
        self._search_seq += 1
        seq = self._search_seq

        # Switch left panel to results view
        self._left_stack.setCurrentIndex(1)
        self._search_results.prepare(query, seq)

        # Resolve DB path from config URL
        db_url = self.config.database_url
        db_path = db_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")

        from arqyv.search.live_search import LiveSearchRunner
        runner = LiveSearchRunner(
            query=query,
            db_path=db_path,
            cancel=self._search_cancel,
            seq=seq,
        )
        runner.signals.batch_ready.connect(self._search_results.append_batch)
        runner.signals.finished.connect(self._search_results.finish)
        QThreadPool.globalInstance().start(runner)

    @pyqtSlot()
    def _on_search_clear(self) -> None:
        self._search_cancel.set()
        self._left_stack.setCurrentIndex(0)
        self._search_bar.clear_text()

    @pyqtSlot(str)
    def _on_file_activated(self, path: str) -> None:
        """Double-click in results → play immediately."""
        p = Path(path)
        self._selected_path = p
        self._preview.load_file(path)
        self._metadata.load_file(path)
        from arqyv.engine.format import detect, MediaKind
        fmt = detect(p)
        if fmt.kind in (MediaKind.VIDEO, MediaKind.AUDIO):
            self._player.open_file(p)

    @pyqtSlot(str)
    def _on_file_selected(self, path: str) -> None:
        p = Path(path)
        self._selected_path = p
        self._preview.load_file(path)
        self._metadata.load_file(path)

        # Auto-open in player if it's media
        from arqyv.engine.format import detect, MediaKind
        fmt = detect(p)
        if fmt.kind in (MediaKind.VIDEO, MediaKind.AUDIO):
            self._player.open_file(p)

    @pyqtSlot()
    def _on_share(self) -> None:
        path = self._selected_path
        if not path or not path.exists():
            self._status.showMessage("Select a file first to share it.", 3000)
            return
        if not self._share_manager:
            return
        from arqyv.ui.dialogs.share_dialog import ShareDialog
        dlg = ShareDialog(manager=self._share_manager, path=path, parent=self)
        dlg.show()

    @pyqtSlot(str)
    def _on_track_changed(self, path: str) -> None:
        p = Path(path)
        self.setWindowTitle(f"ARQYV  ·  {p.name}")
        self._status.showMessage(f"Now playing: {p.name}")

    @pyqtSlot(str)
    def _on_engine_error(self, msg: str) -> None:
        self._status.showMessage(f"⚠ {msg}", 5000)

    @pyqtSlot()
    def _on_batch_rename(self) -> None:
        from arqyv.ui.dialogs.batch_rename_dialog import BatchRenameDialog
        BatchRenameDialog(self).exec()

    @pyqtSlot()
    def _on_cloud_sync(self) -> None:
        from arqyv.ui.dialogs.cloud_sync_dialog import CloudSyncDialog
        CloudSyncDialog(config=self.config, parent=self).exec()

    @pyqtSlot()
    def _on_settings(self) -> None:
        from arqyv.ui.dialogs.settings_dialog import SettingsDialog
        SettingsDialog(config=self.config, parent=self).exec()

    def _apply_theme(self) -> None:
        theme = getattr(self.config, "theme", "dark")
        if theme == "light":
            from arqyv.ui.themes.light import apply_light_theme
            apply_light_theme(self)
        else:
            apply_dark_theme(self)

    def _install_command_palette(self) -> None:
        from arqyv.ui.widgets.command_palette import Command, CommandPalette
        commands = [
            Command("Open Folder",       "Index a new media folder",                   self._on_open_folder,   "Ctrl+O"),
            Command("Open Files",        "Open specific files for playback",            self._on_open_files,    "Ctrl+Shift+O"),
            Command("Share File",        "Share selected file via QR / LAN",            self._on_share,         "Ctrl+Shift+S"),
            Command("Settings",          "Open application settings",                   self._on_settings),
            Command("Play / Pause",      "Toggle media playback",                       lambda: self._player.engine and self._player.engine.toggle(), "Space"),
            Command("Next Track",        "Skip to next item in playlist",               lambda: self._player.engine and self._player.engine.play_next(), "]"),
            Command("Previous Track",    "Go back to previous item",                    lambda: self._player.engine and self._player.engine.play_previous(), "["),
            Command("Stop",              "Stop playback",                               lambda: self._player.engine and self._player.engine.stop(), "S"),
            Command("Batch Rename",      "Rename multiple files at once",               self._on_batch_rename),
            Command("Cloud Sync",        "Manage cloud storage sync",                   self._on_cloud_sync),
            Command("Quit",              "Exit ARQYV",                                  self.close,             "Ctrl+Q"),
        ]
        CommandPalette.install(self, commands)

    def closeEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._share_manager:
            self._share_manager.stop_all()
        log.info("Main window closing.")
        super().closeEvent(event)
