"""Application settings dialog with tabbed layout."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from arqyv.config import AppConfig


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        tabs.addTab(self._make_general_tab(), "General")
        tabs.addTab(self._make_ai_tab(), "AI / Analysis")
        tabs.addTab(self._make_media_tab(), "Media")
        tabs.addTab(self._make_cloud_tab(), "Cloud")

        layout.addWidget(tabs)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _make_general_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        theme_cb = QComboBox()
        theme_cb.addItems(["dark", "light"])
        theme_cb.setCurrentText(self.config.theme)
        form.addRow("Theme:", theme_cb)

        lang_cb = QComboBox()
        lang_cb.addItems(["en", "fr", "de", "es"])
        lang_cb.setCurrentText(self.config.language)
        form.addRow("Language:", lang_cb)

        auto_index = QCheckBox("Auto-index watched folders on startup")
        auto_index.setChecked(self.config.enable_auto_index)
        form.addRow(auto_index)

        return w

    def _make_ai_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        enable_ai = QCheckBox("Enable AI content analysis")
        enable_ai.setChecked(self.config.enable_ai)
        form.addRow(enable_ai)

        whisper_cb = QComboBox()
        whisper_cb.addItems(["tiny", "base", "small", "medium", "large"])
        whisper_cb.setCurrentText(self.config.ai.whisper_model)
        form.addRow("Whisper Model:", whisper_cb)

        device_cb = QComboBox()
        device_cb.addItems(["auto", "cpu", "cuda", "mps"])
        device_cb.setCurrentText(self.config.ai.device)
        form.addRow("Inference Device:", device_cb)

        workers = QSpinBox()
        workers.setRange(1, 16)
        workers.setValue(self.config.ai.max_workers)
        form.addRow("Max Workers:", workers)

        return w

    def _make_media_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.addRow(QLabel("Supported extensions are auto-detected from MediaInfo."))
        return w

    def _make_cloud_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        enable_cloud = QCheckBox("Enable cloud sync")
        enable_cloud.setChecked(self.config.enable_cloud_sync)
        form.addRow(enable_cloud)

        form.addRow(QLabel("Configure OAuth credentials in Settings → Cloud."))
        return w
