"""Dark theme stylesheet for ARQYV.

Follows a deep-charcoal palette with teal accent colors.
Applied once on the QApplication or QMainWindow level.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QWidget

_PALETTE = {
    "bg_primary": "#1a1a2e",
    "bg_secondary": "#16213e",
    "bg_tertiary": "#0f3460",
    "accent": "#00b4d8",
    "accent_hover": "#48cae4",
    "text_primary": "#e0e0e0",
    "text_secondary": "#9e9e9e",
    "border": "#2a2a4a",
    "success": "#4caf50",
    "warning": "#ff9800",
    "error": "#f44336",
}

_STYLESHEET = f"""
QMainWindow, QDialog, QWidget {{
    background-color: {_PALETTE['bg_primary']};
    color: {_PALETTE['text_primary']};
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}}

QMenuBar {{
    background-color: {_PALETTE['bg_secondary']};
    border-bottom: 1px solid {_PALETTE['border']};
}}
QMenuBar::item:selected {{
    background-color: {_PALETTE['bg_tertiary']};
}}
QMenu {{
    background-color: {_PALETTE['bg_secondary']};
    border: 1px solid {_PALETTE['border']};
}}
QMenu::item:selected {{
    background-color: {_PALETTE['accent']};
    color: #fff;
}}

QToolBar {{
    background-color: {_PALETTE['bg_secondary']};
    border-bottom: 1px solid {_PALETTE['border']};
    spacing: 4px;
    padding: 4px;
}}

QDockWidget {{
    background-color: {_PALETTE['bg_secondary']};
}}
QDockWidget::title {{
    background-color: {_PALETTE['bg_tertiary']};
    padding: 6px;
    font-weight: bold;
}}

QTreeView, QListView {{
    background-color: {_PALETTE['bg_secondary']};
    border: 1px solid {_PALETTE['border']};
    alternate-background-color: {_PALETTE['bg_primary']};
    selection-background-color: {_PALETTE['accent']};
    selection-color: #fff;
    outline: none;
}}
QTreeView::item:hover, QListView::item:hover {{
    background-color: {_PALETTE['bg_tertiary']};
}}

QLineEdit {{
    background-color: {_PALETTE['bg_tertiary']};
    border: 1px solid {_PALETTE['border']};
    border-radius: 6px;
    padding: 6px 10px;
    color: {_PALETTE['text_primary']};
}}
QLineEdit:focus {{
    border-color: {_PALETTE['accent']};
}}

QPushButton {{
    background-color: {_PALETTE['bg_tertiary']};
    border: 1px solid {_PALETTE['border']};
    border-radius: 5px;
    padding: 5px 12px;
    color: {_PALETTE['text_primary']};
}}
QPushButton:hover {{
    background-color: {_PALETTE['accent']};
    color: #fff;
    border-color: {_PALETTE['accent']};
}}
QPushButton:pressed {{
    background-color: {_PALETTE['accent_hover']};
}}
QPushButton:checked {{
    background-color: {_PALETTE['accent']};
    color: #fff;
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: {_PALETTE['border']};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {_PALETTE['accent']};
    border-radius: 7px;
    width: 14px;
    height: 14px;
    margin: -5px 0;
}}
QSlider::sub-page:horizontal {{
    background: {_PALETTE['accent']};
    border-radius: 2px;
}}

QScrollBar:vertical {{
    background: {_PALETTE['bg_secondary']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {_PALETTE['border']};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QStatusBar {{
    background-color: {_PALETTE['bg_secondary']};
    border-top: 1px solid {_PALETTE['border']};
    color: {_PALETTE['text_secondary']};
    font-size: 11px;
}}

QGroupBox {{
    border: 1px solid {_PALETTE['border']};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    color: {_PALETTE['accent']};
}}

QSplitter::handle {{
    background: {_PALETTE['border']};
}}
"""


def apply_dark_theme(widget: QWidget) -> None:
    widget.setStyleSheet(_STYLESHEET)
