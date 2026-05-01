"""ARQYV light theme — clean, minimal, professional."""

from __future__ import annotations
from PyQt6.QtWidgets import QWidget

P = {
    "bg0":    "#f8f9fa",
    "bg1":    "#ffffff",
    "bg2":    "#f1f3f5",
    "bg3":    "#e9ecef",
    "bg4":    "#dee2e6",
    "cyan":   "#0077cc",
    "cyan2":  "#005fa3",
    "violet": "#6d28d9",
    "text":   "#1a1a2e",
    "text2":  "#4a4a6a",
    "text3":  "#9090aa",
    "success":"#16a34a",
    "warning":"#d97706",
    "error":  "#dc2626",
    "border": "#dee2e6",
    "border2":"#e9ecef",
}

_QSS = f"""
* {{ box-sizing: border-box; }}

QMainWindow, QDialog, QWidget {{
    background: {P['bg0']};
    color: {P['text']};
    font-family: 'Segoe UI', 'Inter', 'SF Pro Text', sans-serif;
    font-size: 13px;
}}
QMenuBar {{
    background: {P['bg1']};
    border-bottom: 1px solid {P['border']};
    padding: 1px 4px;
}}
QMenuBar::item {{ padding: 5px 10px; border-radius: 4px; color: {P['text2']}; }}
QMenuBar::item:selected {{ background: {P['bg3']}; color: {P['text']}; }}
QMenu {{
    background: {P['bg1']};
    border: 1px solid {P['border']};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{ padding: 7px 18px 7px 12px; border-radius: 4px; color: {P['text2']}; }}
QMenu::item:selected {{ background: {P['bg3']}; color: {P['text']}; }}
QMenu::separator {{ height: 1px; background: {P['border']}; margin: 3px 8px; }}
QToolBar {{
    background: {P['bg1']};
    border: none;
    border-bottom: 1px solid {P['border']};
    padding: 4px 10px;
}}
QDockWidget {{
    background: {P['bg1']};
    color: {P['text2']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
}}
QDockWidget::title {{
    background: {P['bg1']};
    padding: 8px 12px;
    border-bottom: 1px solid {P['border']};
}}
QTreeView, QListView, QListWidget {{
    background: {P['bg1']};
    border: none;
    selection-background-color: transparent;
    outline: 0;
}}
QTreeView::item, QListView::item, QListWidget::item {{
    padding: 5px 6px;
    border-radius: 4px;
    color: {P['text2']};
}}
QTreeView::item:hover, QListView::item:hover {{ background: {P['bg2']}; color: {P['text']}; }}
QTreeView::item:selected, QListView::item:selected {{
    background: {P['bg3']};
    color: {P['cyan']};
    border-left: 2px solid {P['cyan']};
    padding-left: 4px;
}}
QHeaderView::section {{
    background: {P['bg1']};
    color: {P['text3']};
    border: none;
    border-bottom: 1px solid {P['border']};
    padding: 6px 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
}}
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {P['bg1']};
    border: 1px solid {P['border']};
    border-radius: 7px;
    padding: 7px 11px;
    color: {P['text']};
}}
QLineEdit:focus, QTextEdit:focus {{ border-color: {P['cyan']}; }}
QPushButton {{
    background: {P['bg2']};
    border: 1px solid {P['border']};
    border-radius: 6px;
    padding: 6px 14px;
    color: {P['text2']};
    font-size: 12px;
    font-weight: 500;
    min-height: 26px;
}}
QPushButton:hover {{ background: {P['bg3']}; color: {P['text']}; }}
QPushButton:pressed {{ background: {P['bg4']}; color: {P['cyan']}; }}
QPushButton:checked {{ background: {P['bg4']}; border-color: {P['cyan']}; color: {P['cyan']}; }}
QPushButton#ghost {{ background: transparent; border: none; color: {P['text2']}; }}
QPushButton#ghost:hover {{ background: {P['bg2']}; color: {P['text']}; }}
QPushButton#ghost:checked {{ color: {P['cyan']}; }}
QSlider::groove:horizontal {{ height: 2px; background: {P['border']}; border-radius: 1px; }}
QSlider::handle:horizontal {{ background: {P['cyan']}; border-radius: 5px; width: 10px; height: 10px; margin: -4px 0; }}
QSlider::sub-page:horizontal {{ background: {P['cyan']}; border-radius: 1px; }}
QScrollBar:vertical {{ background: transparent; width: 4px; margin: 2px 0; }}
QScrollBar::handle:vertical {{ background: {P['border']}; border-radius: 2px; min-height: 20px; }}
QScrollBar:horizontal {{ background: transparent; height: 4px; }}
QScrollBar::handle:horizontal {{ background: {P['border']}; border-radius: 2px; min-width: 20px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; height: 0; }}
QStatusBar {{ background: {P['bg1']}; border-top: 1px solid {P['border']}; color: {P['text2']}; font-size: 11px; }}
QTabBar::tab {{ background: transparent; border: none; border-bottom: 2px solid transparent; padding: 8px 16px; color: {P['text2']}; }}
QTabBar::tab:selected {{ color: {P['cyan']}; border-bottom: 2px solid {P['cyan']}; }}
QGroupBox {{
    border: 1px solid {P['border']};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 12px;
    background: {P['bg1']};
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 14px; top: -8px; padding: 0 6px; color: {P['text3']}; font-size: 10px; font-weight: 700; background: {P['bg0']}; }}
QSplitter::handle:horizontal {{ background: {P['border']}; width: 1px; }}
QToolTip {{ background: {P['bg1']}; color: {P['text']}; border: 1px solid {P['border']}; border-radius: 5px; padding: 5px 9px; }}
QProgressBar {{ background: {P['bg2']}; border: none; border-radius: 2px; height: 4px; font-size: 0; }}
QProgressBar::chunk {{ background: {P['cyan']}; border-radius: 2px; }}
"""


def apply_light_theme(widget: QWidget) -> None:
    widget.setStyleSheet(_QSS)


PALETTE = P
