"""Application settings dialog — watched folders, AI, media, cloud, appearance."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from arqyv.config import AppConfig

log = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, services: dict[str, Any] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self.services = services or {}
        self.setWindowTitle("Settings")
        self.setMinimumSize(580, 480)
        self._changed: dict[str, Any] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        tabs = QTabWidget()
        tabs.addTab(self._tab_general(),    "General")
        tabs.addTab(self._tab_library(),    "Library")
        tabs.addTab(self._tab_ai(),         "AI / Analysis")
        tabs.addTab(self._tab_media(),      "Media")
        tabs.addTab(self._tab_cloud(),      "Cloud")
        root.addWidget(tabs, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._apply_and_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    # ── Tabs ───────────────────────────────────────────────────────────────

    def _tab_general(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(16, 16, 16, 16)

        self._theme_cb = QComboBox()
        self._theme_cb.addItems(["dark", "light"])
        self._theme_cb.setCurrentText(self.config.theme)
        form.addRow("Theme:", self._theme_cb)

        self._lang_cb = QComboBox()
        self._lang_cb.addItems(["en", "fr", "de", "es", "ja", "zh"])
        self._lang_cb.setCurrentText(self.config.language)
        form.addRow("Language:", self._lang_cb)

        self._auto_index_cb = QCheckBox("Auto-index watched folders on startup")
        self._auto_index_cb.setChecked(self.config.enable_auto_index)
        form.addRow(self._auto_index_cb)

        self._api_cb = QCheckBox("Enable local REST API server (port 8765)")
        self._api_cb.setChecked(self.config.enable_api_server)
        form.addRow(self._api_cb)

        return w

    def _tab_library(self) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(16, 16, 16, 16)

        lbl = QLabel("Watched folders are indexed on startup and monitored for changes.")
        lbl.setWordWrap(True)
        vl.addWidget(lbl)

        self._folder_list = QListWidget()
        self._folder_list.setAlternatingRowColors(True)
        self._folder_list.setMinimumHeight(120)
        vl.addWidget(self._folder_list)
        self._load_watched_folders()

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ Add Folder")
        add_btn.clicked.connect(self._add_folder)
        rm_btn = QPushButton("Remove Selected")
        rm_btn.clicked.connect(self._remove_folder)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(rm_btn)
        btn_row.addStretch()
        vl.addLayout(btn_row)

        return w

    def _tab_ai(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(16, 16, 16, 16)

        self._enable_ai_cb = QCheckBox("Enable AI content analysis (tags, summaries, embeddings)")
        self._enable_ai_cb.setChecked(self.config.enable_ai)
        form.addRow(self._enable_ai_cb)

        self._whisper_cb = QComboBox()
        self._whisper_cb.addItems(["tiny", "base", "small", "medium", "large"])
        self._whisper_cb.setCurrentText(self.config.ai.whisper_model)
        form.addRow("Whisper Model:", self._whisper_cb)

        self._embed_cb = QComboBox()
        self._embed_cb.addItems([
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        ])
        self._embed_cb.setCurrentText(self.config.ai.embedding_model)
        form.addRow("Embedding Model:", self._embed_cb)

        self._device_cb = QComboBox()
        self._device_cb.addItems(["auto", "cpu", "cuda", "mps"])
        self._device_cb.setCurrentText(self.config.ai.device)
        form.addRow("Inference Device:", self._device_cb)

        self._workers_sb = QSpinBox()
        self._workers_sb.setRange(1, 16)
        self._workers_sb.setValue(self.config.ai.max_workers)
        form.addRow("Max Worker Threads:", self._workers_sb)

        self._voice_cb = QCheckBox("Enable voice search (requires sounddevice + whisper)")
        self._voice_cb.setChecked(self.config.enable_voice_search)
        form.addRow(self._voice_cb)

        return w

    def _tab_media(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(16, 16, 16, 16)

        thumb_lbl = QLabel(
            "Thumbnail dimensions (width × height in pixels).\n"
            "Larger thumbnails improve grid view quality but use more disk."
        )
        thumb_lbl.setWordWrap(True)
        form.addRow(thumb_lbl)

        self._thumb_w = QSpinBox()
        self._thumb_w.setRange(64, 1920)
        self._thumb_w.setValue(self.config.media.thumbnail_size[0])
        self._thumb_h = QSpinBox()
        self._thumb_h.setRange(64, 1080)
        self._thumb_h.setValue(self.config.media.thumbnail_size[1])

        size_row = QHBoxLayout()
        size_row.addWidget(self._thumb_w)
        size_row.addWidget(QLabel("×"))
        size_row.addWidget(self._thumb_h)
        size_row.addStretch()
        form.addRow("Thumbnail Size:", size_row)

        self._thumb_q = QSpinBox()
        self._thumb_q.setRange(1, 100)
        self._thumb_q.setValue(self.config.media.thumbnail_quality)
        form.addRow("JPEG Quality:", self._thumb_q)

        return w

    def _tab_cloud(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(16, 16, 16, 16)

        self._cloud_cb = QCheckBox("Enable cloud sync")
        self._cloud_cb.setChecked(self.config.enable_cloud_sync)
        form.addRow(self._cloud_cb)

        note = QLabel(
            "OAuth credentials are stored in environment variables or a .env file.\n"
            "Set ARQYV_CLOUD_GOOGLE_CLIENT_ID, ARQYV_CLOUD_ONEDRIVE_CLIENT_ID,\n"
            "or ARQYV_CLOUD_DROPBOX_APP_KEY to enable each provider."
        )
        note.setWordWrap(True)
        form.addRow(note)

        return w

    # ── Watched folder helpers ─────────────────────────────────────────────

    def _load_watched_folders(self) -> None:
        self._folder_list.clear()
        db = self.services.get("db")
        if not db:
            return
        try:
            import asyncio
            folders = asyncio.run(db.get_watched_folders())
            for f in folders:
                self._folder_list.addItem(f.path)
        except Exception:
            log.warning("Could not load watched folders.", exc_info=True)

    def _add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Add Watched Folder")
        if not folder:
            return
        # Persist to DB immediately
        db = self.services.get("db")
        if db:
            try:
                import asyncio
                asyncio.run(db.add_watched_folder(folder))
            except Exception:
                log.warning("Failed to persist folder %s", folder, exc_info=True)
        # Also wire watcher if indexer is available
        indexer = self.services.get("indexer")
        if indexer:
            indexer.add_watched_folder(folder)
        self._folder_list.addItem(folder)

    def _remove_folder(self) -> None:
        item = self._folder_list.currentItem()
        if item:
            self._folder_list.takeItem(self._folder_list.row(item))

    # ── Apply changes ──────────────────────────────────────────────────────

    def _apply_and_accept(self) -> None:
        new_theme = self._theme_cb.currentText()
        if new_theme != self.config.theme:
            self._apply_theme(new_theme)

        self.accept()

    def _apply_theme(self, theme: str) -> None:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            return
        top = app.topLevelWidgets()
        if not top:
            return
        root = top[0]
        if theme == "dark":
            from arqyv.ui.themes.dark import apply_dark_theme
            apply_dark_theme(root)
        else:
            from arqyv.ui.themes.light import apply_light_theme
            apply_light_theme(root)
