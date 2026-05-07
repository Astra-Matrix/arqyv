"""
ARQYV Sidebar Navigation — icon strip on the far left.

48 px wide. Navigation items at the top, utility items pinned to the bottom.
Active item gets a left-edge accent bar and bright icon.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from arqyv.ui.themes.dark import PALETTE as P

_W = 48  # strip width px
_BTN = 36  # icon button square


def _nav_qss(active: bool) -> str:
    accent = P["cyan"]
    bg_a   = P["bg3"]
    ic_a   = P["text"]
    ic_n   = P["text3"]
    bg_h   = P["bg2"]
    ic_h   = P["text2"]
    if active:
        return f"""
            QPushButton {{
                background: {bg_a};
                border: none;
                border-radius: 8px;
                color: {ic_a};
                font-size: 17px;
                border-left: 2px solid {accent};
                border-top-left-radius: 0;
                border-bottom-left-radius: 0;
            }}
        """
    return f"""
        QPushButton {{
            background: transparent;
            border: none;
            border-radius: 8px;
            color: {ic_n};
            font-size: 17px;
        }}
        QPushButton:hover {{
            background: {bg_h};
            color: {ic_h};
        }}
    """


class _NavButton(QPushButton):
    """Single icon button in the nav strip."""

    def __init__(self, icon: str, tip: str, key: str) -> None:
        super().__init__(icon)
        self.key = key
        self.setFixedSize(QSize(_W, _BTN))
        self.setToolTip(tip)
        self.setCheckable(False)
        self._active = False
        self._refresh()

    def set_active(self, active: bool) -> None:
        self._active = active
        self._refresh()

    def _refresh(self) -> None:
        self.setStyleSheet(_nav_qss(self._active))


class SidebarNavWidget(QWidget):
    """
    Vertical icon-strip navigation.

    Emits `nav_changed(key)` when a navigation item is clicked.
    Emits `action_triggered(key)` for non-nav actions (share, settings).
    """

    nav_changed      = pyqtSignal(str)
    action_triggered = pyqtSignal(str)

    _NAV_ITEMS: list[tuple[str, str, str]] = [
        ("library",     "󰛶",  "Library"),
        ("search",      "󰍉",  "Search"),
        ("collections", "󱂵",  "Collections"),
        ("queue",       "󰲸",  "Queue"),
    ]

    # Fallback to plain ASCII/unicode if font icons unavailable
    _NAV_FALLBACK: list[tuple[str, str, str]] = [
        ("library",     "⊞",  "Library"),
        ("search",      "⌕",  "Search"),
        ("collections", "⊟",  "Collections"),
        ("queue",       "≣",  "Queue"),
    ]

    _ACTION_ITEMS: list[tuple[str, str, str]] = [
        ("share",    "⬆",  "Share (Ctrl+Shift+S)"),
        ("settings", "⚙",  "Settings"),
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
        self._nav_btns: dict[str, _NavButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        vl = QVBoxLayout(self)
        vl.setContentsMargins(6, 10, 6, 10)
        vl.setSpacing(4)
        vl.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Top logo mark
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
        """)
        logo.setToolTip("ARQYV")
        vl.addWidget(logo)

        # Thin divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color: {P['border2']}; margin: 4px 0;")
        div.setFixedHeight(1)
        vl.addWidget(div)
        vl.addSpacing(4)

        # Navigation items
        for key, icon, tip in self._NAV_FALLBACK:
            btn = _NavButton(icon, tip, key)
            btn.set_active(key == self._active_key)
            btn.clicked.connect(lambda _=False, k=key: self._on_nav(k))
            self._nav_btns[key] = btn
            vl.addWidget(btn)

        vl.addStretch()

        # Bottom divider
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
        if self._active_key != key:
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
