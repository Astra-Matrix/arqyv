"""
ARQYV Empty State — shown in the content area when no file is selected.

Wraps a LiquidBackground so the content area is never just a flat void.
The icon pulses slowly. CTA buttons have a shimmer on hover.
"""

from __future__ import annotations

import math

from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QRadialGradient, QBrush
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from arqyv.ui.effects.liquid_bg import LiquidBackground
from arqyv.ui.effects.shimmer import ShimmerEffect
from arqyv.ui.themes.dark import PALETTE as P


# ── Pulsing icon label ─────────────────────────────────────────────────────────

class _PulseIcon(QWidget):
    """Draws a large glyph surrounded by a slow-breathing glow ring."""

    def __init__(self, glyph: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(QSize(100, 100))
        self._glyph = glyph
        self._t     = 0
        t = QTimer(self)
        t.setInterval(30)
        t.timeout.connect(self._tick)
        t.start()

    def _tick(self) -> None:
        self._t += 1
        self.update()

    def set_glyph(self, g: str) -> None:
        self._glyph = g
        self.update()

    def paintEvent(self, event: object) -> None:  # type: ignore[override]
        cx, cy = self.width() / 2, self.height() / 2
        # Very subtle breath: ±3 px radius, very low alpha — just enough to
        # hint that the icon is alive without calling attention to itself.
        pulse = 30 + math.sin(self._t * 0.025) * 3
        alpha = int((0.055 + math.sin(self._t * 0.025) * 0.02) * 255)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        grad = QRadialGradient(cx, cy, pulse * 2.0)
        grad.setColorAt(0.0, QColor(0, 212, 255, alpha))
        grad.setColorAt(1.0, QColor(0, 212, 255, 0))
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(int(cx - pulse * 2), int(cy - pulse * 2),
                            int(pulse * 4), int(pulse * 4))

        from PyQt6.QtGui import QFont
        f = QFont("Segoe UI", 28)
        painter.setFont(f)
        painter.setPen(QColor(P["text3"]))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._glyph)
        painter.end()


# ── Main widget ────────────────────────────────────────────────────────────────

class EmptyStateWidget(QWidget):
    """
    Full-area placeholder with liquid orb background and pulsing icon.

    Signals
    -------
    open_folder_requested
    open_files_requested
    """

    open_folder_requested = pyqtSignal()
    open_files_requested  = pyqtSignal()

    _CONTEXTS: dict[str, tuple[str, str, str]] = {
        "library": (
            "⊞",
            "Your library is empty",
            "Add a folder to start indexing your media.",
        ),
        "search": (
            "⌕",
            "Start typing to search",
            "Search by filename, extension, or AI content tags.",
        ),
        "collections": (
            "⊟",
            "No collections yet",
            "Collections are built automatically after indexing.",
        ),
        "queue": (
            "≣",
            "Queue is empty",
            "Double-click any file to add it to the playback queue.",
        ),
        "default": (
            "⬡",
            "Nothing selected",
            "Pick a file from the sidebar to preview it here.",
        ),
    }

    def __init__(self, context: str = "library", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._context = context
        self._build_ui()

    def _build_ui(self) -> None:
        # Liquid orb background layer
        self._bg = LiquidBackground(self, intensity=0.45)
        self._bg.resize(self.size())
        self._bg.lower()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(2)

        center = QWidget()
        center.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(center)
        cl.setContentsMargins(40, 0, 40, 0)
        cl.setSpacing(0)
        cl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        icon, title, body = self._CONTEXTS.get(self._context, self._CONTEXTS["default"])

        # Pulsing icon
        self._icon = _PulseIcon(icon)
        icon_row = QWidget()
        icon_row.setStyleSheet("background: transparent;")
        ir = QHBoxLayout(icon_row)
        ir.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        ir.addWidget(self._icon)
        cl.addWidget(icon_row)
        cl.addSpacing(20)

        # Title
        self._title_lbl = QLabel(title)
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._title_lbl.setStyleSheet(f"""
            background: transparent;
            color: {P['text']};
            font-size: 18px;
            font-weight: 600;
            letter-spacing: -0.02em;
        """)
        cl.addWidget(self._title_lbl)
        cl.addSpacing(10)

        # Body text
        self._body_lbl = QLabel(body)
        self._body_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._body_lbl.setWordWrap(True)
        self._body_lbl.setStyleSheet(f"""
            background: transparent;
            color: {P['text2']};
            font-size: 13px;
        """)
        cl.addWidget(self._body_lbl)

        # CTA buttons for library context
        if self._context == "library":
            cl.addSpacing(28)
            btn_row = QWidget()
            btn_row.setStyleSheet("background: transparent;")
            bl = QHBoxLayout(btn_row)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setSpacing(10)
            bl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            open_folder_btn = QPushButton("Open Folder…")
            open_folder_btn.setObjectName("primary")
            open_folder_btn.setFixedHeight(36)
            open_folder_btn.setMinimumWidth(140)
            open_folder_btn.clicked.connect(self.open_folder_requested)
            ShimmerEffect.install(open_folder_btn, duration_ms=700)

            open_files_btn = QPushButton("Open Files…")
            open_files_btn.setFixedHeight(36)
            open_files_btn.setMinimumWidth(120)
            open_files_btn.clicked.connect(self.open_files_requested)
            ShimmerEffect.install(open_files_btn)

            bl.addWidget(open_folder_btn)
            bl.addWidget(open_files_btn)
            cl.addWidget(btn_row)

            cl.addSpacing(20)
            hint = QLabel("Or press  Ctrl+P  to open the command palette")
            hint.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            hint.setStyleSheet(f"background: transparent; color: {P['text3']}; font-size: 11px;")
            cl.addWidget(hint)

        outer.addWidget(center)
        outer.addStretch(3)

    def resizeEvent(self, event: object) -> None:  # type: ignore[override]
        self._bg.resize(self.size())
        super().resizeEvent(event)  # type: ignore[arg-type]

    def set_context(self, context: str) -> None:
        self._context = context
        icon, title, body = self._CONTEXTS.get(context, self._CONTEXTS["default"])
        self._icon.set_glyph(icon)
        self._title_lbl.setText(title)
        self._body_lbl.setText(body)
