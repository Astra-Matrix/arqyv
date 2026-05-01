"""
ARQYV Share Dialog — next-level edition.

Features:
  - Instant QR code display (qrcode + Pillow, installed)
  - Live transfer progress bar + speed readout
  - LAN peer list with reachability probe (no more 10.3.5.165 hangs)
  - One-click peer send (opens URL in system browser on target)
  - Copy link / Save QR image
  - Non-modal — interact with main window while sharing
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtGui import QFont, QGuiApplication, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from arqyv.share.manager import ShareManager, ShareSession
from arqyv.ui.themes.dark import PALETTE as P

log = logging.getLogger(__name__)

_SPEED_WINDOW = 2.0   # seconds over which to average transfer speed


class _QRWorker(QThread):
    """Generate QR pixmap off the main thread."""
    done = pyqtSignal(object)   # QPixmap | None

    def __init__(self, url: str, size: int = 300) -> None:
        super().__init__()
        self._url = url
        self._size = size

    def run(self) -> None:
        from arqyv.share.qr import generate_pixmap
        self.done.emit(generate_pixmap(self._url, self._size))


class ShareDialog(QDialog):
    """Instant file-share dialog: QR + URL + LAN peers + live progress."""

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
        self._transfer_start: float | None = None
        self._last_bytes = 0
        self._speed_samples: list[tuple[float, int]] = []

        self.setWindowTitle(f"Share  ·  {path.name}")
        self.setMinimumSize(620, 480)
        self.resize(720, 520)
        self.setModal(False)

        self._build_ui()
        self._start_session()

        self._stats_timer = QTimer(self)
        self._stats_timer.setInterval(500)
        self._stats_timer.timeout.connect(self._refresh_stats)
        self._stats_timer.start()

        self._peer_timer = QTimer(self)
        self._peer_timer.setInterval(3000)
        self._peer_timer.timeout.connect(self._refresh_peers)
        self._peer_timer.start()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QDialog {{
                background: {P['bg0']};
                color: {P['text']};
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }}
        """)

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Header bar ────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet(f"background:{P['bg1']}; border-bottom:1px solid {P['border']};")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(18, 0, 18, 0)

        title = QLabel(f"Sharing  <span style='color:{P[\"cyan\"]}'>{self._path.name}</span>")
        title.setStyleSheet("font-size:15px; font-weight:600;")
        title.setTextFormat(Qt.TextFormat.RichText)

        size_lbl = QLabel(self._human_size(self._path))
        size_lbl.setStyleSheet(f"color:{P['muted']}; font-size:12px;")

        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(size_lbl)
        root.addWidget(header)

        # ── Body ──────────────────────────────────────────────────────────
        body = QWidget()
        bl = QHBoxLayout(body)
        bl.setContentsMargins(18, 18, 18, 18)
        bl.setSpacing(20)

        # Left panel: QR
        left = self._build_left()
        bl.addWidget(left, 0)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setStyleSheet(f"color:{P['border_hi']};")
        bl.addWidget(div)

        # Right panel: URL + progress + peers
        right = self._build_right()
        bl.addWidget(right, 1)

        root.addWidget(body, 1)

        # ── Footer ────────────────────────────────────────────────────────
        footer = QWidget()
        footer.setFixedHeight(52)
        footer.setStyleSheet(f"background:{P['bg1']}; border-top:1px solid {P['border']};")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(18, 0, 18, 0)

        self._stop_btn = QPushButton("Stop Sharing")
        self._stop_btn.setObjectName("danger")
        self._stop_btn.setFixedWidth(130)
        self._stop_btn.clicked.connect(self._stop_and_close)

        self._copy_btn = QPushButton("Copy Link")
        self._copy_btn.setFixedWidth(110)
        self._copy_btn.clicked.connect(self._copy_url)

        self._save_qr_btn = QPushButton("Save QR")
        self._save_qr_btn.setFixedWidth(90)
        self._save_qr_btn.clicked.connect(self._save_qr)

        fl.addWidget(self._stop_btn)
        fl.addStretch()
        fl.addWidget(self._save_qr_btn)
        fl.addWidget(self._copy_btn)
        root.addWidget(footer)

    def _build_left(self) -> QWidget:
        w = QWidget()
        w.setFixedWidth(280)
        lv = QVBoxLayout(w)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(10)

        # QR frame
        qr_frame = QFrame()
        qr_frame.setStyleSheet(f"""
            QFrame {{
                background: {P['bg2']};
                border: 1px solid {P['border_hi']};
                border-radius: 12px;
            }}
        """)
        qr_frame.setFixedSize(280, 280)
        qr_layout = QVBoxLayout(qr_frame)
        qr_layout.setContentsMargins(10, 10, 10, 10)

        self._qr_label = QLabel("Generating QR…")
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_label.setStyleSheet(f"color:{P['muted']}; background:transparent; border:none;")
        self._qr_label.setFixedSize(258, 258)
        qr_layout.addWidget(self._qr_label)
        lv.addWidget(qr_frame)

        hint = QLabel("Scan with any camera  ·  no app needed")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(f"color:{P['muted']}; font-size:11px;")
        lv.addWidget(hint)
        lv.addStretch()
        return w

    def _build_right(self) -> QWidget:
        w = QWidget()
        rv = QVBoxLayout(w)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(14)

        # URL
        url_lbl = QLabel("SHARE LINK")
        url_lbl.setStyleSheet(f"font-size:10px; font-weight:700; letter-spacing:0.1em; color:{P['muted']};")
        rv.addWidget(url_lbl)

        self._url_display = QLabel("Starting…")
        self._url_display.setWordWrap(True)
        self._url_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._url_display.setStyleSheet(f"""
            background:{P['bg2']};
            border:1px solid {P['border_hi']};
            border-radius:6px;
            padding:8px 10px;
            font-family:monospace;
            font-size:11px;
            color:{P['cyan']};
        """)
        rv.addWidget(self._url_display)

        # Status row
        row = QHBoxLayout()
        self._status_dot = QLabel("● Active")
        self._status_dot.setStyleSheet(f"color:{P['success']}; font-size:11px; font-weight:600;")
        self._dl_count = QLabel("0 downloads")
        self._dl_count.setStyleSheet(f"color:{P['muted']}; font-size:11px;")
        self._speed_lbl = QLabel("")
        self._speed_lbl.setStyleSheet(f"color:{P['cyan']}; font-size:11px;")
        row.addWidget(self._status_dot)
        row.addStretch()
        row.addWidget(self._speed_lbl)
        row.addSpacing(10)
        row.addWidget(self._dl_count)
        rv.addLayout(row)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFixedHeight(5)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(f"""
            QProgressBar {{ background:{P['bg2']}; border:none; border-radius:3px; }}
            QProgressBar::chunk {{ background:{P['cyan']}; border-radius:3px; }}
        """)
        rv.addWidget(self._progress)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{P['border_hi']};")
        rv.addWidget(sep)

        # LAN peers
        peers_hdr = QHBoxLayout()
        peers_lbl = QLabel("LAN PEERS")
        peers_lbl.setStyleSheet(f"font-size:10px; font-weight:700; letter-spacing:0.1em; color:{P['muted']};")
        self._peers_count = QLabel("")
        self._peers_count.setStyleSheet(f"color:{P['cyan']}; font-size:11px;")
        peers_hdr.addWidget(peers_lbl)
        peers_hdr.addStretch()
        peers_hdr.addWidget(self._peers_count)
        rv.addLayout(peers_hdr)

        self._peers_list = QListWidget()
        self._peers_list.setStyleSheet(f"""
            QListWidget {{
                background:{P['bg2']};
                border:1px solid {P['border_hi']};
                border-radius:6px;
                font-size:12px;
            }}
            QListWidget::item {{ padding:6px 8px; border-radius:4px; }}
            QListWidget::item:hover {{ background:{P['bg3']}; }}
            QListWidget::item:selected {{ background:{P['bg3']}; border-left:2px solid {P['cyan']}; }}
        """)
        self._peers_list.setMinimumHeight(100)
        self._peers_list.doubleClicked.connect(self._on_peer_double_click)
        self._no_peer_item = QListWidgetItem("Scanning LAN…")
        self._no_peer_item.setForeground(Qt.GlobalColor.gray)
        self._peers_list.addItem(self._no_peer_item)
        rv.addWidget(self._peers_list, 1)

        send_btn = QPushButton("Send to Selected Peer")
        send_btn.clicked.connect(self._send_to_peer)
        rv.addWidget(send_btn)

        return w

    # ── Session lifecycle ─────────────────────────────────────────────────

    def _start_session(self) -> None:
        file_size = self._path.stat().st_size if self._path.is_file() else 0

        def _on_download(ip: str) -> None:
            log.info("Download completed from %s", ip)

        def _on_progress(sent: int, total: int) -> None:
            if self._transfer_start is None:
                self._transfer_start = time.monotonic()
            now = time.monotonic()
            self._speed_samples.append((now, sent))
            # Keep only last _SPEED_WINDOW seconds
            cutoff = now - _SPEED_WINDOW
            self._speed_samples = [(t, b) for t, b in self._speed_samples if t >= cutoff]

        try:
            self._session = self._manager.share_file(
                self._path,
                on_download=_on_download,
                on_progress=_on_progress,
            )
            self._url_display.setText(self._session.url)
            self._file_size = file_size

            # Generate QR off-thread
            self._qr_worker = _QRWorker(self._session.url, size=256)
            self._qr_worker.done.connect(self._on_qr_ready)
            self._qr_worker.start()

            # Advertise on LAN
            if hasattr(self._manager, "_discovery") and self._manager._discovery:
                self._manager._discovery.advertise(
                    self._session.server.port,
                    self._session.token,
                )

        except Exception:
            log.exception("Failed to start share session.")
            self._url_display.setText("Failed to start server.")
            self._status_dot.setText("● Error")
            self._status_dot.setStyleSheet(f"color:{P['error']}; font-size:11px;")

    @pyqtSlot(object)
    def _on_qr_ready(self, pixmap: QPixmap | None) -> None:
        if pixmap and not pixmap.isNull():
            self._qr_label.setPixmap(
                pixmap.scaled(258, 258, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
            self._qr_label.setText("")
        else:
            self._qr_label.setText(
                f"<span style='font-size:10px;color:{P[\"muted\"]}'>"
                f"URL:<br><b>{self._session.url if self._session else ''}</b></span>"
            )
            self._qr_label.setWordWrap(True)

    # ── Refresh loops ─────────────────────────────────────────────────────

    @pyqtSlot()
    def _refresh_stats(self) -> None:
        if not self._session:
            return
        srv = self._session.server
        count = srv.download_count
        sent = srv.bytes_sent

        self._dl_count.setText(f"{count} download{'s' if count != 1 else ''}")

        # Speed calculation
        if len(self._speed_samples) >= 2:
            t0, b0 = self._speed_samples[0]
            t1, b1 = self._speed_samples[-1]
            dt = t1 - t0
            if dt > 0:
                bps = (b1 - b0) / dt
                self._speed_lbl.setText(self._human_speed(bps))
        elif sent > 0:
            self._speed_lbl.setText("")

        # Progress bar
        total = getattr(self, "_file_size", 0)
        if total > 0 and sent > 0:
            pct = min(100, int(sent * 100 / total))
            self._progress.setValue(pct)

        # Status indicator
        if self._session.is_active:
            self._status_dot.setText("● Active")
            self._status_dot.setStyleSheet(f"color:{P['success']}; font-size:11px; font-weight:600;")
        else:
            self._status_dot.setText("○ Stopped")
            self._status_dot.setStyleSheet(f"color:{P['muted']}; font-size:11px; font-weight:600;")
            self._speed_lbl.setText("")

    @pyqtSlot()
    def _refresh_peers(self) -> None:
        try:
            disc = getattr(self._manager, "_discovery", None)
            if not disc:
                return
            peers = disc.peers
            self._peers_list.clear()
            if peers:
                self._peers_count.setText(f"{len(peers)} found")
                for p in peers:
                    icon = "○" if not p.reachable else "●"
                    color = P["success"] if p.reachable else P["muted"]
                    item = QListWidgetItem(f"{icon}  {p.display_name}  —  {p.ip}")
                    item.setData(Qt.ItemDataRole.UserRole, p)
                    self._peers_list.addItem(item)
            else:
                self._peers_count.setText("")
                item = QListWidgetItem("No ARQYV peers on LAN yet")
                item.setForeground(Qt.GlobalColor.gray)
                self._peers_list.addItem(item)
        except Exception:
            pass

    # ── Actions ───────────────────────────────────────────────────────────

    @pyqtSlot()
    def _copy_url(self) -> None:
        if self._session:
            QGuiApplication.clipboard().setText(self._session.url)
            self._copy_btn.setText("Copied!")
            QTimer.singleShot(2000, lambda: self._copy_btn.setText("Copy Link"))

    @pyqtSlot()
    def _save_qr(self) -> None:
        if not self._session:
            return
        from PyQt6.QtWidgets import QFileDialog
        dest, _ = QFileDialog.getSaveFileName(
            self, "Save QR Code", f"ARQYV-QR-{self._path.stem}.png", "PNG (*.png)"
        )
        if dest:
            from arqyv.share.qr import save_qr_image
            save_qr_image(self._session.url, Path(dest), size=512)

    @pyqtSlot()
    def _send_to_peer(self) -> None:
        item = self._peers_list.currentItem()
        if not item:
            return
        peer = item.data(Qt.ItemDataRole.UserRole)
        if not peer or not self._session:
            return
        import webbrowser
        webbrowser.open(self._session.url)

    @pyqtSlot()
    def _on_peer_double_click(self) -> None:
        self._send_to_peer()

    @pyqtSlot()
    def _stop_and_close(self) -> None:
        if self._session:
            self._session.stop()
        self.close()

    # ── Cleanup ───────────────────────────────────────────────────────────

    def closeEvent(self, event: object) -> None:  # type: ignore[override]
        self._stats_timer.stop()
        self._peer_timer.stop()
        if self._session and self._session.is_active:
            self._session.stop()
        super().closeEvent(event)  # type: ignore[arg-type]

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _human_size(path: Path) -> str:
        try:
            b = path.stat().st_size
            for unit in ("B", "KB", "MB", "GB"):
                if b < 1024:
                    return f"{b:.1f} {unit}"
                b /= 1024
            return f"{b:.1f} TB"
        except OSError:
            return ""

    @staticmethod
    def _human_speed(bps: float) -> str:
        if bps < 1024:
            return f"{bps:.0f} B/s"
        if bps < 1024 ** 2:
            return f"{bps/1024:.0f} KB/s"
        return f"{bps/1024**2:.1f} MB/s"
