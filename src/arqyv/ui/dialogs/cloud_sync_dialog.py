"""Cloud sync configuration and status dialog."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from arqyv.config import AppConfig


class CloudSyncDialog(QDialog):
    def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Cloud Sync")
        self.setMinimumSize(500, 380)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Connect cloud storage providers:"))

        providers = QListWidget()
        providers.addItem("Google Drive")
        providers.addItem("Microsoft OneDrive")
        providers.addItem("Dropbox")
        layout.addWidget(providers, 1)

        btn_row = QHBoxLayout()
        connect_btn = QPushButton("Connect Selected")
        connect_btn.clicked.connect(self._connect)
        sync_btn = QPushButton("Sync Now")
        sync_btn.clicked.connect(self._sync)
        btn_row.addWidget(connect_btn)
        btn_row.addWidget(sync_btn)
        layout.addLayout(btn_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _connect(self) -> None:
        # TODO: OAuth flow per provider
        pass

    def _sync(self) -> None:
        # TODO: trigger cloud sync worker
        pass
