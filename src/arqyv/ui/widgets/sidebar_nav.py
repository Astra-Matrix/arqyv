"""
ARQYV Sidebar Navigation — icon strip on the far left.

48 px wide. Navigation items at top, utility items pinned to the bottom.
Active item renders a left-edge cyan accent bar with an animated breathing
glow ring behind the icon. Hover items get a shimmer sweep.
"""

from __future__ import annotations

import math

from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPainter, QRadialGradient
from PyQt6.QtWidgets import (
    QFrame,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from arqyv.ui.effects.shimmer import ShimmerEffect
from arqyv.ui.themes.dark import PALETTE as P

_W   = 48   # strip width px
_BTN = 36   # icon button square


# ── Glow-ring active button ────────────────────────────────────────────────────

class _NavButton(QPushButton):
    """
    Single icon button in the nav strip.

    When active, a slow-breathing radial glow ring is painted behind the icon.
    """

    def __init__(self, icon: str, tip: str, key: str) -> None:
        super().__init__(icon)
        self.key      = key
        self._active  = False
        self._t       = 0
        self._shimmer = ShimmerEffect.install(self, duration_ms=500, cooldown_ms=600)

        self.setFixedSize(QSize(_W, _BTN))
        self.setToolTip(tip)
        self.setCheckable(False)

        self._glow_timer = QTimer(self)
        self._glow_timer.setInterval(30)
        self._glow_timer.timeout.connect(self._pulse)
        self._refresh()

    # ── Active state ───────────────────────────────────────────────────────

    def set_active(self, active: bool) -> None:
        if self._active == active:
            return
        self._active = active
        if active:
            self._glow_timer.start()
        else:
            self._glow_timer.stop()
            self._t = 0
        self.update()
        self._refresh()

    def _pulse(self) -> None:
        self._t += 1
        self.update()

    # ── Style ──────────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {P['bg3']};
                    border: none;
                    border-radius: 8px;
                    color: {P['text']};
                    font-size: 17px;
                    border-left: 2px solid {P['cyan']};
                    border-top-left-radius: 0;
                    border-bottom-left-radius: 0;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    color: {P['text3']};
                    font-size: 17px;
                }}
                QPushButton:hover {{
                    background: {P['bg2']};
                    color: {P['text2']};
                }}
            """)

    # ── Painting — glow ring ───────────────────────────────────────────────

    def paintEvent(self, event: object) -> None:  # type: ignore[override]
        if self._active:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)

            cx  = self.width() / 2
            cy  = self.height() / 2
            # Breathing radius: 14–22 px
            r   = 14 + math.sin(self._t * 0.05) * 4
            a   = int((0.15 + math.sin(self._t * 0.05) * 0.06) * 255)

            grad = QRadialGradient(cx, cy, r * 1.8)
            grad.setColorAt(0.0, QColor(0, 212, 255, a))
            grad.setColorAt(0.6, QColor(0, 212, 255, a // 3))
            grad.setColorAt(1.0, QColor(0, 212, 255, 0))
            painter.setBrush(QBrush(grad))
            painter.drawEllipse(
                int(cx - r * 1.8), int(cy - r * 1.8),
                int(r * 3.6),      int(r * 3.6),
            )
            painter.end()

        # Let Qt draw the text/label on top
        super().paintEvent(event)  # type: ignore[arg-type]


# ── Strip widget ───────────────────────────────────────────────────────────────

class SidebarNavWidget(QWidget):
    """
    Vertical icon-strip navigation.

    Emits `nav_changed(key)` when a nav item is clicked.
    Emits `action_triggered(key)` for bottom utility items.
    """

    nav_changed      = pyqtSignal(str)
    action_triggered = pyqtSignal(str)

    _NAV_ITEMS: list[tuple[str, str, str]] = [
        ("library",     "⊞", "Library"),
        ("search",      "⌕", "Search"),
        ("collections", "⊟", "Collections"),
        ("queue",       "≣", "Queue"),
    ]

    _ACTION_ITEMS: list[tuple[str, str, str]] = [
        ("share",    "⬆", "Share  (Ctrl+Shift+S)"),
        ("settings", "⚙", "Settings"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(_W)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f"""
            SidebarNavWidget {{
                background: {P['bg1']};
                border-right: 1px solid {P['border']};
            }}
        """)
        self._active_key: str = "library"
        self._nav_btns:   dict[str, _NavButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        vl = QVBoxLayout(self)
        vl.setContentsMargins(6, 10, 6, 10)
        vl.setSpacing(4)
        vl.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo mark
        logo = QPushButton("⬡")
        logo.setFixedSize(QSize(_W - 12, _BTN))
        logo.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {P['cyan']};
                font-size: 20px;
                font-weight: 700;
            }}
            QPushButton:hover {{ color: #33daff; }}
        """)
        logo.setToolTip("ARQYV")
        vl.addWidget(logo)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color: {P['border2']}; margin: 4px 0;")
        div.setFixedHeight(1)
        vl.addWidget(div)
        vl.addSpacing(4)

        # Nav items
        for key, icon, tip in self._NAV_ITEMS:
            btn = _NavButton(icon, tip, key)
            btn.set_active(key == self._active_key)
            btn.clicked.connect(lambda _=False, k=key: self._on_nav(k))
            self._nav_btns[key] = btn
            vl.addWidget(btn)

        vl.addStretch()

        div2 = QFrame()
        div2.setFrameShape(QFrame.Shape.HLine)
        div2.setStyleSheet(f"color: {P['border2']}; margin: 4px 0;")
        div2.setFixedHeight(1)
        vl.addWidget(div2)

        # Action items
        for key, icon, tip in self._ACTION_ITEMS:
            btn = _NavButton(icon, tip, key)
            btn.clicked.connect(lambda _=False, k=key: self.action_triggered.emit(k))
            vl.addWidget(btn)

    def _on_nav(self, key: str) -> None:
        if self._active_key in self._nav_btns:
            self._nav_btns[self._active_key].set_active(False)
        self._active_key = key
        self._nav_btns[key].set_active(True)
        self.nav_changed.emit(key)

    def set_active(self, key: str) -> None:
        self._on_nav(key)

    @property
    def active_key(self) -> str:
        return self._active_key
