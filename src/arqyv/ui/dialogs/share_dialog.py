"""File share dialog — QR code + URL + LAN peers.

The simplest possible sharing experience:
  1. Open dialog for any file.
  2. A QR code appears instantly.
  3. Scan it on any device (phone, tablet, another PC) — download starts.
  4. If the recipient has ARQYV on LAN, their name appears in the peers list.
  5. Close the dialog → server stops.

No accounts. No subscriptions. No sign-in. No bullshit.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QClipboard, QFont, QGuiApplication
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from arqyv.share.manager import ShareManager, ShareSession

log = logging.getLogger(__name__)


class ShareDialog(QDialog):
    """Shows QR code + URL for instant file sharing."""

    def __init__(
        self,
        manager: ShareManager,
        path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._manager = manager
        self._path = path
        self._session: ShareSession | None = None

        self.setWindowTitle(f"Share — {path.name}")
        self.setMinimumSize(520, 420)
        self.setModal(False)  # allow interaction with main window while sharing

        self._build_ui()
        self._start_session()
        self._peer_timer = QTimer(self)
        self._peer_timer.setInterval(3000)
        self._peer_timer.timeout.connect(self._refresh_peers)
        self._peer_timer.start()

    # ── UI ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QLabel(f"<b>Sharing:</b> {self._path.name}")
        header.setStyleSheet("font-size:14px; color:#e0e0e0;")
        root.addWidget(header)

        # Body splitter: QR left, info right
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: QR code ──────────────────────────────────────────────────
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)

        self._qr_label = QLabel("Generating QR…")
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_label.setFixedSize(280, 280)
        self._qr_label.setStyleSheet("background:#1a1a2e; border-radius:8px;")
        lv.addWidget(self._qr_label)

        scan_hint = QLabel("Scan with any camera app\nor paste URL in browser")
        scan_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scan_hint.setStyleSheet("color:#9e9e9e; font-size:11px;")
        lv.addWidget(scan_hint)
        lv.addStretch()

        # ── Right: URL + stats + peers ─────────────────────────────────────
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setSpacing(8)

        url_title = QLabel("Share Link")
        url_title.setStyleSheet("font-weight:bold; color:#00b4d8;")
        rv.addWidget(url_title)

        self._url_label = QLabel("Starting server…")
        self._url_label.setWordWrap(True)
        self._url_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._url_label.setStyleSheet(
            "background:#0f3460; padding:8px; border-radius:6px; "
            "font-family:monospace; font-size:11px; color:#e0e0e0;"
        )
        rv.addWidget(self._url_label)

        copy_btn = QPushButton("📋  Copy Link")
        copy_btn.clicked.connect(self._copy_url)
        rv.addWidget(copy_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#2a2a4a;")
        rv.addWidget(sep)

        # Stats
        stats_row = QHBoxLayout()
        self._dl_label = QLabel("Downloads: 0")
        self._dl_label.setStyleSheet("color:#9e9e9e; font-size:11px;")
        self._status_label = QLabel("● Active")
        self._status_label.setStyleSheet("color:#4caf50; font-size:11px;")
        stats_row.addWidget(self._dl_label)
        stats_row.addStretch()
        stats_row.addWidget(self._status_label)
        rv.addLayout(stats_row)

        # LAN peers
        peers_title = QLabel("ARQYV peers on your network")
        peers_title.setStyleSheet("font-weight:bold; color:#00b4d8; margin-top:8px;")
        rv.addWidget(peers_title)

        self._peers_list = QListWidget()
        self._peers_list.setMaximumHeight(100)
        self._peers_list.setStyleSheet("background:#16213e;")
        no_peer = QListWidgetItem("No peers found yet…")
        no_peer.setForeground(Qt.GlobalColor.gray)
        self._peers_list.addItem(no_peer)
        rv.addWidget(self._peers_list)

        rv.addStretch()

        # Stop button
        stop_btn = QPushButton("Stop Sharing")
        stop_btn.setStyleSheet("background:#c62828; color:#fff;")
        stop_btn.clicked.connect(self._stop_and_close)
        rv.addWidget(stop_btn)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([290, 210])
        root.addWidget(splitter, 1)

        # Stats refresh timer
        self._stats_timer = QTimer(self)
        self._stats_timer.setInterval(1000)
        self._stats_timer.timeout.connect(self._refresh_stats)
        self._stats_timer.start()

    # ── Session management ─────────────────────────────────────────────────

    def _start_session(self) -> None:
        def on_download(ip: str) -> None:
            log.info("Download from %s", ip)

        try:
            self._session = self._manager.share_file(
                self._path, on_download=on_download
            )
            self._url_label.setText(self._session.url)

            if self._session.qr_pixmap:
                self._qr_label.setPixmap(self._session.qr_pixmap)
            else:
                self._qr_label.setText(
                    f"<b>URL:</b><br>{self._session.url}<br><br>"
                    "(Install qrcode for QR display)"
                )
                self._qr_label.setWordWrap(True)
        except Exception:
            log.exception("Failed to start share session.")
            self._url_label.setText("Failed to start server.")

    @pyqtSlot()
    def _copy_url(self) -> None:
        if self._session:
            QGuiApplication.clipboard().setText(self._session.url)

    @pyqtSlot()
    def _refresh_stats(self) -> None:
        if not self._session:
            return
        count = self._session.server.download_count
        self._dl_label.setText(f"Downloads: {count}")
        if self._session.is_active:
            self._status_label.setText("● Active")
            self._status_label.setStyleSheet("color:#4caf50; font-size:11px;")
        else:
            self._status_label.setText("○ Stopped")
            self._status_label.setStyleSheet("color:#9e9e9e; font-size:11px;")

    @pyqtSlot()
    def _refresh_peers(self) -> None:
        try:
            from arqyv.share.discovery import PeerDiscovery
            # Discovery object is owned by ShareManager; just read peers
            if hasattr(self._manager, "_discovery"):
                peers = self._manager._discovery.peers
                self._peers_list.clear()
                if peers:
                    for p in peers:
                        item = QListWidgetItem(f"💻  {p.display_name}  ({p.ip})")
                        self._peers_list.addItem(item)
                else:
                    item = QListWidgetItem("No peers found yet…")
                    item.setForeground(Qt.GlobalColor.gray)
                    self._peers_list.addItem(item)
        except Exception:
            pass

    @pyqtSlot()
    def _stop_and_close(self) -> None:
        if self._session:
            self._session.stop()
        self.close()

    def closeEvent(self, event: object) -> None:  # type: ignore[override]
        self._stats_timer.stop()
        self._peer_timer.stop()
        if self._session and self._session.is_active:
            self._session.stop()
        super().closeEvent(event)  # type: ignore[arg-type]
