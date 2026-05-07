"""
ARQYV Status Strip — custom QStatusBar replacement.

Shows styled chip widgets:
  ● 1 042 files   ·   ⚡ AI: 3   ·   API :8765   ·   message text …
"""

from __future__ import annotations

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QStatusBar,
    QWidget,
)

from arqyv.config import AppConfig
from arqyv.ui.themes.dark import PALETTE as P


def _chip(text: str, colour: str = "", bg: str = "") -> QLabel:
    c  = colour or P["text2"]
    bg = bg     or P["bg2"]
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        QLabel {{
            background: {bg};
            color: {c};
            font-size: 11px;
            font-weight: 500;
            padding: 2px 9px;
            border-radius: 10px;
        }}
    """)
    return lbl


class StatusStrip(QStatusBar):
    """
    Replaces the default QStatusBar with a richer status line.
    Chips are always visible on the right; transient messages appear on the left.
    """

    def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self._msg_timer = QTimer(self)
        self._msg_timer.setSingleShot(True)
        self._msg_timer.timeout.connect(self._clear_message)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QStatusBar {{
                background: {P['bg1']};
                border-top: 1px solid {P['border']};
                color: {P['text2']};
                font-size: 11px;
                padding: 0 8px;
            }}
            QStatusBar::item {{ border: none; }}
        """)
        self.setSizeGripEnabled(False)

        # Transient message label on the left
        self._msg_lbl = QLabel("Ready")
        self._msg_lbl.setStyleSheet(f"color: {P['text2']}; font-size: 11px; padding: 0 4px;")
        self._msg_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(self._msg_lbl, 1)

        # Indexing progress bar (hidden when idle)
        self._prog = QProgressBar()
        self._prog.setRange(0, 100)
        self._prog.setFixedSize(80, 4)
        self._prog.setTextVisible(False)
        self._prog.setStyleSheet(f"""
            QProgressBar {{
                background: {P['bg3']};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: {P['cyan']};
                border-radius: 2px;
            }}
        """)
        self._prog.hide()
        self.addPermanentWidget(self._prog)

        # File count chip
        self._files_chip = _chip("● 0 files")
        self.addPermanentWidget(self._files_chip)

        # AI chip
        self._ai_chip = _chip("⚡ AI idle", P["text3"])
        self.addPermanentWidget(self._ai_chip)

        # API chip
        self._api_chip = _chip(f"API  :{self.config.api_port}", P["text3"])
        self.addPermanentWidget(self._api_chip)

    # ── Public API ─────────────────────────────────────────────────────────

    def show_message(self, text: str, timeout_ms: int = 0) -> None:  # type: ignore[override]
        self._msg_lbl.setText(text)
        if timeout_ms > 0:
            self._msg_timer.start(timeout_ms)

    def _clear_message(self) -> None:
        self._msg_lbl.setText("Ready")

    def set_file_count(self, count: int) -> None:
        self._files_chip.setText(f"● {count:,} files")

    def set_ai_activity(self, active: int) -> None:
        if active > 0:
            self._ai_chip.setText(f"⚡ AI: {active}")
            self._ai_chip.setStyleSheet(self._ai_chip.styleSheet().replace(P["text3"], P["cyan"]))
        else:
            self._ai_chip.setText("⚡ AI idle")

    def set_index_progress(self, current: int, total: int) -> None:
        if total > 0:
            pct = int(current / total * 100)
            self._prog.setValue(pct)
            self._prog.show()
            if current >= total:
                QTimer.singleShot(1500, self._prog.hide)
                self.set_file_count(total)
        else:
            self._prog.hide()

    def set_api_status(self, online: bool) -> None:
        if online:
            self._api_chip.setText(f"API  :{self.config.api_port}")
        else:
            self._api_chip.setText("API  offline")
