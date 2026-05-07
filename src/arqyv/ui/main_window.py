"""Main application window — next-generation layout.

┌─────────────────────────────────────────────────────────────────────────────┐
│  Header bar:  [⬡ ARQYV]  [─────── Search ───────]  [⬆ Share]  [⚙ …]      │
├────┬──────────────────────┬──────────────────────────┬──────────────────────┤
│ N  │ Sidebar panel        │ Content (preview)         │ Info panel           │
│ a  │  Library / Search /  │  Image / video / doc      │  Metadata + AI tags  │
│ v  │  Collections / Queue │  EmptyState when idle     │                      │
│    │                      │                           │                      │
├────┴──────────────────────┴──────────────────────────┴──────────────────────┤
│  Media Player  ━━━━ seek ━━━━   ⏮ ⏪ ▶ ⏩ ⏭  · time · fmt ·  vol ·  spd   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Status bar:  [● 1 042 files]  [⚡ AI: 3]  [API :8765]  [message …]       │
└─────────────────────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QSize, QThreadPool, pyqtSlot
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from arqyv.config import AppConfig
from arqyv.core.events import EventBus, Events
from arqyv.ui.themes.dark import apply_dark_theme, PALETTE as DARK_P
from arqyv.ui.widgets.empty_state import EmptyStateWidget
from arqyv.ui.widgets.file_browser import FileBrowserWidget
from arqyv.ui.widgets.media_player import MediaPlayerWidget
from arqyv.ui.widgets.metadata_panel import MetadataPanelWidget
from arqyv.ui.widgets.preview_panel import PreviewPanelWidget
from arqyv.ui.widgets.search_bar import SearchBarWidget
from arqyv.ui.widgets.search_results import SearchResultsWidget
from arqyv.ui.widgets.sidebar_nav import SidebarNavWidget
from arqyv.ui.widgets.status_strip import StatusStrip

log = logging.getLogger(__name__)

P = DARK_P


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
        self.setMinimumSize(QSize(1024, 660))
        # No native menubar chrome — we use toolbar + command palette
        self.menuBar().hide()

    # ── UI ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_header()
        self._build_body()
        self._build_status_strip()

    # ── Header bar ─────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        tb = QToolBar("Header", self)
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        tb.setObjectName("headerBar")
        tb.setStyleSheet(f"""
            QToolBar#headerBar {{
                background: {P['bg1']};
                border: none;
                border-bottom: 1px solid {P['border']};
                padding: 4px 12px;
                spacing: 8px;
            }}
            QToolBar#headerBar::separator {{
                background: {P['border2']};
                width: 1px;
                margin: 5px 6px;
            }}
        """)

        # Logo word mark
        from PyQt6.QtWidgets import QLabel
        logo = QLabel("⬡  ARQYV")
        logo.setStyleSheet(f"""
            color: {P['cyan']};
            font-size: 14px;
            font-weight: 800;
            letter-spacing: 0.12em;
            padding: 0 12px 0 4px;
        """)
        tb.addWidget(logo)
        tb.addSeparator()

        # Search bar — stretches to fill available space
        self._search_bar = SearchBarWidget(events=self.events, services=self.services)
        self._search_bar.live_search_changed.connect(self._on_live_search)
        tb.addWidget(self._search_bar)

        tb.addSeparator()

        # Share button
        from PyQt6.QtWidgets import QPushButton
        share_btn = QPushButton("⬆  Share")
        share_btn.setObjectName("ghost")
        share_btn.setFixedHeight(30)
        share_btn.setToolTip("Share the selected file instantly — QR code, no accounts  (Ctrl+Shift+S)")
        share_btn.clicked.connect(self._on_share)
        tb.addWidget(share_btn)

        # Command palette trigger
        palette_btn = QPushButton("⌨  Actions")
        palette_btn.setObjectName("ghost")
        palette_btn.setFixedHeight(30)
        palette_btn.setToolTip("Command palette  (Ctrl+P)")
        palette_btn.clicked.connect(self._open_palette)
        tb.addWidget(palette_btn)

        # Settings
        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("ghost")
        settings_btn.setFixedSize(QSize(30, 30))
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(self._on_settings)
        tb.addWidget(settings_btn)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

    # ── Body (sidebar nav + panel splitter) ────────────────────────────────

    def _build_body(self) -> None:
        container = QWidget()
        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        # Icon navigation strip
        self._nav = SidebarNavWidget()
        self._nav.nav_changed.connect(self._on_nav_changed)
        self._nav.action_triggered.connect(self._on_nav_action)
        h.addWidget(self._nav)

        # Main horizontal splitter: [sidebar panel | content | info panel]
        self._body_split = QSplitter(Qt.Orientation.Horizontal)
        self._body_split.setHandleWidth(1)
        self._body_split.setStyleSheet(f"""
            QSplitter::handle {{
                background: {P['border']};
            }}
        """)

        # ── Left sidebar panel ──────────────────────────────────────────
        self._sidebar_stack = QStackedWidget()
        self._sidebar_stack.setMinimumWidth(220)

        # page 0 — file browser
        self._file_browser = FileBrowserWidget(
            config=self.config, events=self.events, services=self.services
        )
        self._file_browser.file_selected.connect(self._on_file_selected)
        self._sidebar_stack.addWidget(self._file_browser)

        # page 1 — search results
        self._search_results = SearchResultsWidget()
        self._search_results.file_selected.connect(self._on_file_selected)
        self._search_results.file_activated.connect(self._on_file_activated)
        self._search_results.request_clear.connect(self._on_search_clear)
        self._sidebar_stack.addWidget(self._search_results)

        # page 2 — collections placeholder
        from arqyv.ui.widgets.empty_state import EmptyStateWidget
        self._sidebar_stack.addWidget(EmptyStateWidget("collections"))

        # page 3 — queue placeholder
        self._sidebar_stack.addWidget(EmptyStateWidget("queue"))

        self._body_split.addWidget(self._sidebar_stack)

        # ── Center content area ─────────────────────────────────────────
        content_container = QWidget()
        cv = QVBoxLayout(content_container)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(0)

        self._content_stack = QStackedWidget()

        # page 0 — empty state
        self._empty_state = EmptyStateWidget("library")
        self._empty_state.open_folder_requested.connect(self._on_open_folder)
        self._empty_state.open_files_requested.connect(self._on_open_files)
        self._content_stack.addWidget(self._empty_state)

        # page 1 — preview panel
        self._preview = PreviewPanelWidget(config=self.config, events=self.events)
        self._content_stack.addWidget(self._preview)

        cv.addWidget(self._content_stack, 1)

        # Media player docked below content
        self._player = MediaPlayerWidget(config=self.config, events=self.events)
        cv.addWidget(self._player)

        self._body_split.addWidget(content_container)

        # ── Right info panel ────────────────────────────────────────────
        self._metadata = MetadataPanelWidget(events=self.events)
        self._metadata.setMinimumWidth(200)
        self._body_split.addWidget(self._metadata)

        # Initial sizes: sidebar 240 | content 580 | info 260
        self._body_split.setSizes([240, 580, 260])
        self._body_split.setCollapsible(0, True)
        self._body_split.setCollapsible(2, True)

        h.addWidget(self._body_split, 1)

        self.setCentralWidget(container)

    # ── Status strip ───────────────────────────────────────────────────────

    def _build_status_strip(self) -> None:
        self._status_strip = StatusStrip(config=self.config)
        self.setStatusBar(self._status_strip)

    # ── Engine wiring ──────────────────────────────────────────────────────

    def _wire_engine(self) -> None:
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
        self._status_strip.set_index_progress(current, total)
        self._status_strip.show_message(f"Indexing {current}/{total} — {Path(path).name}")

    def _on_file_added(self, path: str = "") -> None:
        self._status_strip.show_message(f"Indexed: {Path(path).name}", 3000)

    # ── Navigation ─────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _on_nav_changed(self, key: str) -> None:
        page_map = {"library": 0, "search": 0, "collections": 2, "queue": 3}
        self._sidebar_stack.setCurrentIndex(page_map.get(key, 0))
        self._empty_state.set_context(key if key in ("library", "search", "collections", "queue") else "default")

    @pyqtSlot(str)
    def _on_nav_action(self, key: str) -> None:
        if key == "share":
            self._on_share()
        elif key == "settings":
            self._on_settings()

    # ── Live search ────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _on_live_search(self, query: str) -> None:
        query = query.strip()
        if not query:
            self._on_search_clear()
            return

        self._search_cancel.set()
        self._search_cancel = threading.Event()
        self._search_seq += 1
        seq = self._search_seq

        # Switch to search mode
        self._nav.set_active("search")
        self._sidebar_stack.setCurrentIndex(1)
        self._search_results.prepare(query, seq)

        db_url = self.config.database_url
        db_path = db_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")

        from arqyv.search.live_search import LiveSearchRunner
        runner = LiveSearchRunner(
            query=query, db_path=db_path, cancel=self._search_cancel, seq=seq,
        )
        runner.signals.batch_ready.connect(self._search_results.append_batch)
        runner.signals.finished.connect(self._search_results.finish)
        QThreadPool.globalInstance().start(runner)

    @pyqtSlot()
    def _on_search_clear(self) -> None:
        self._search_cancel.set()
        self._nav.set_active("library")
        self._sidebar_stack.setCurrentIndex(0)
        self._search_bar.clear_text()

    # ── File selection ─────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _on_file_activated(self, path: str) -> None:
        p = Path(path)
        self._selected_path = p
        self._show_preview(p)
        from arqyv.engine.format import detect, MediaKind
        fmt = detect(p)
        if fmt.kind in (MediaKind.VIDEO, MediaKind.AUDIO):
            self._player.open_file(p)

    @pyqtSlot(str)
    def _on_file_selected(self, path: str) -> None:
        p = Path(path)
        self._selected_path = p
        self._show_preview(p)
        from arqyv.engine.format import detect, MediaKind
        fmt = detect(p)
        if fmt.kind in (MediaKind.VIDEO, MediaKind.AUDIO):
            self._player.open_file(p)

    def _show_preview(self, p: Path) -> None:
        """Switch content area to preview and load the file."""
        self._content_stack.setCurrentIndex(1)
        self._preview.load_file(str(p))
        self._metadata.load_file(str(p))

    # ── Toolbar slots ──────────────────────────────────────────────────────

    @pyqtSlot()
    def _on_open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Open Media Folder")
        if folder:
            if "indexer" in self.services:
                self.services["indexer"].index_directory(folder)
            self._file_browser.navigate_to(folder)

    @pyqtSlot()
    def _on_open_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Open File(s)", "", "Media (*.*)")
        if paths:
            media_paths = [Path(p) for p in paths]
            self._player.open_playlist(media_paths, start=0)

    @pyqtSlot()
    def _on_share(self) -> None:
        path = self._selected_path
        if not path or not path.exists():
            self._status_strip.show_message("Select a file first to share it.", 3000)
            return
        if not self._share_manager:
            return
        from arqyv.ui.dialogs.share_dialog import ShareDialog
        dlg = ShareDialog(manager=self._share_manager, path=path, parent=self)
        dlg.show()

    @pyqtSlot()
    def _on_settings(self) -> None:
        from arqyv.ui.dialogs.settings_dialog import SettingsDialog
        SettingsDialog(config=self.config, parent=self).exec()

    @pyqtSlot()
    def _open_palette(self) -> None:
        """Re-trigger command palette via shortcut simulation."""
        from arqyv.ui.widgets.command_palette import CommandPalette
        if hasattr(self, "_palette"):
            self._palette.show_palette()

    @pyqtSlot(str)
    def _on_track_changed(self, path: str) -> None:
        p = Path(path)
        self.setWindowTitle(f"ARQYV  ·  {p.name}")
        self._status_strip.show_message(f"Now playing: {p.name}")

    @pyqtSlot(str)
    def _on_engine_error(self, msg: str) -> None:
        self._status_strip.show_message(f"⚠ {msg}", 5000)

    @pyqtSlot()
    def _on_batch_rename(self) -> None:
        from arqyv.ui.dialogs.batch_rename_dialog import BatchRenameDialog
        BatchRenameDialog(self).exec()

    @pyqtSlot()
    def _on_cloud_sync(self) -> None:
        from arqyv.ui.dialogs.cloud_sync_dialog import CloudSyncDialog
        CloudSyncDialog(config=self.config, parent=self).exec()

    # ── Theme + command palette ─────────────────────────────────────────────

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
            Command("Open Folder",    "Index a new media folder",              self._on_open_folder,  "Ctrl+O"),
            Command("Open Files",     "Open specific files for playback",       self._on_open_files,   "Ctrl+Shift+O"),
            Command("Share File",     "Share selected file via QR / LAN",       self._on_share,        "Ctrl+Shift+S"),
            Command("Settings",       "Open application settings",              self._on_settings),
            Command("Play / Pause",   "Toggle media playback",                  lambda: self._player.engine and self._player.engine.toggle(), "Space"),
            Command("Next Track",     "Skip to next item in playlist",          lambda: self._player.engine and self._player.engine.play_next(), "]"),
            Command("Previous Track", "Go back to previous item",               lambda: self._player.engine and self._player.engine.play_previous(), "["),
            Command("Stop",           "Stop playback",                          lambda: self._player.engine and self._player.engine.stop(), "S"),
            Command("Batch Rename",   "Rename multiple files at once",          self._on_batch_rename),
            Command("Cloud Sync",     "Manage cloud storage sync",              self._on_cloud_sync),
            Command("Toggle Sidebar", "Show / hide sidebar panel",              self._toggle_sidebar),
            Command("Toggle Info",    "Show / hide info panel",                 self._toggle_info),
            Command("Quit",           "Exit ARQYV",                             self.close, "Ctrl+Q"),
        ]
        self._palette = CommandPalette.install(self, commands)

    # ── Panel toggles ──────────────────────────────────────────────────────

    def _toggle_sidebar(self) -> None:
        sizes = self._body_split.sizes()
        sizes[0] = 0 if sizes[0] > 0 else 240
        self._body_split.setSizes(sizes)

    def _toggle_info(self) -> None:
        sizes = self._body_split.sizes()
        sizes[2] = 0 if sizes[2] > 0 else 260
        self._body_split.setSizes(sizes)

    def closeEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._share_manager:
            self._share_manager.stop_all()
        log.info("Main window closing.")
        super().closeEvent(event)
