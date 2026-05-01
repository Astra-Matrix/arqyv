"""Command palette — Ctrl+P fuzzy-find over all app actions.

Press Ctrl+P to open. Type to filter. Enter to execute. Escape to dismiss.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QKeyEvent, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from arqyv.ui.themes.dark import PALETTE as P

log = logging.getLogger(__name__)


@dataclass
class Command:
    label: str
    description: str
    action: Callable[[], None]
    shortcut: str = ""


class CommandPalette(QDialog):
    """Floating command palette — summon with Ctrl+P."""

    def __init__(self, commands: list[Command], parent: QWidget | None = None) -> None:
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self._commands = commands
        self._filtered: list[Command] = list(commands)
        self._build_ui()
        self._filter("")

    def _build_ui(self) -> None:
        self.setFixedWidth(560)
        self.setStyleSheet(f"""
            QDialog {{
                background: {P['bg2']};
                border: 1px solid {P['border2']};
                border-radius: 10px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a command…")
        self._input.setFixedHeight(44)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: {P['bg2']};
                border: none;
                border-bottom: 1px solid {P['border2']};
                border-radius: 10px 10px 0 0;
                padding: 0 16px;
                color: {P['text']};
                font-size: 14px;
            }}
        """)
        self._input.textChanged.connect(self._filter)
        self._input.returnPressed.connect(self._execute)
        root.addWidget(self._input)

        self._list = QListWidget()
        self._list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: 0;
                padding: 4px;
            }}
            QListWidget::item {{
                border-radius: 6px;
                padding: 6px 12px;
                color: {P['text2']};
            }}
            QListWidget::item:selected {{
                background: {P['bg4']};
                color: {P['text']};
            }}
            QListWidget::item:hover {{
                background: {P['bg3']};
            }}
        """)
        self._list.setMaximumHeight(320)
        self._list.itemActivated.connect(lambda _: self._execute())
        root.addWidget(self._list)

        self.adjustSize()

    def _filter(self, text: str) -> None:
        q = text.lower().strip()
        self._filtered = [
            c for c in self._commands
            if not q or q in c.label.lower() or q in c.description.lower()
        ]
        self._list.clear()
        for cmd in self._filtered[:20]:
            item = QListWidgetItem()
            widget = _CmdRow(cmd)
            item.setSizeHint(widget.sizeHint())
            self._list.addItem(item)
            self._list.setItemWidget(item, widget)
        if self._list.count():
            self._list.setCurrentRow(0)
        self.adjustSize()

    def _execute(self) -> None:
        row = self._list.currentRow()
        if 0 <= row < len(self._filtered):
            self.close()
            self._filtered[row].action()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # type: ignore[override]
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close()
        elif key == Qt.Key.Key_Down:
            next_row = min(self._list.currentRow() + 1, self._list.count() - 1)
            self._list.setCurrentRow(next_row)
        elif key == Qt.Key.Key_Up:
            prev_row = max(self._list.currentRow() - 1, 0)
            self._list.setCurrentRow(prev_row)
        else:
            super().keyPressEvent(event)

    @staticmethod
    def install(parent: QWidget, commands: list[Command]) -> "CommandPalette | None":
        """Create a global Ctrl+P shortcut that opens the palette."""
        shortcut = QShortcut(QKeySequence("Ctrl+P"), parent)

        def _open() -> None:
            palette = CommandPalette(commands, parent)
            # Center below toolbar
            geo = parent.geometry()
            pw, ph = palette.sizeHint().width(), palette.sizeHint().height()
            palette.move(geo.center().x() - pw // 2, geo.top() + 60)
            palette.show()
            palette._input.setFocus()

        shortcut.activated.connect(_open)
        return None


class _CmdRow(QWidget):
    def __init__(self, cmd: Command) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(1)

        label = QLabel(cmd.label)
        label.setStyleSheet(f"color: {P['text']}; font-size: 13px; font-weight: 500;")
        root.addWidget(label)

        if cmd.description:
            desc = QLabel(cmd.description)
            desc.setStyleSheet(f"color: {P['text2']}; font-size: 11px;")
            root.addWidget(desc)
