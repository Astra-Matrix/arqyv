"""
ARQYV dark theme — professional edition.

Pure black base. Single cyan accent. Clean geometry.
"""

from __future__ import annotations
from PyQt6.QtWidgets import QWidget

P = {
    "bg0":       "#080810",   # window base
    "bg1":       "#0d0d18",   # panels / toolbar
    "bg2":       "#13131f",   # input / card bg
    "bg3":       "#1a1a2a",   # hover / row alt
    "bg4":       "#222235",   # selected / active
    "cyan":      "#00d2ff",   # primary accent
    "cyan2":     "#00a8cc",   # pressed / muted accent
    "violet":    "#7c3aed",
    "text":      "#e8e8f0",
    "text2":     "#8888a0",
    "text3":     "#44445a",
    "success":   "#22c55e",
    "warning":   "#f59e0b",
    "error":     "#ef4444",
    "border":    "#16162a",
    "border2":   "#1e1e32",
}

_QSS = f"""
* {{ box-sizing: border-box; }}

QMainWindow, QDialog, QWidget {{
    background: {P['bg0']};
    color: {P['text']};
    font-family: 'Segoe UI', 'Inter', 'SF Pro Text', sans-serif;
    font-size: 13px;
}}

/* ── Menu ─────────────────────────────────────────────── */
QMenuBar {{
    background: {P['bg1']};
    border-bottom: 1px solid {P['border']};
    padding: 1px 4px;
    spacing: 2px;
}}
QMenuBar::item {{
    padding: 5px 10px;
    border-radius: 4px;
    color: {P['text2']};
}}
QMenuBar::item:selected, QMenuBar::item:pressed {{
    background: {P['bg3']};
    color: {P['text']};
}}
QMenu {{
    background: {P['bg1']};
    border: 1px solid {P['border2']};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 7px 18px 7px 12px;
    border-radius: 4px;
    color: {P['text2']};
}}
QMenu::item:selected {{
    background: {P['bg3']};
    color: {P['text']};
}}
QMenu::separator {{
    height: 1px;
    background: {P['border2']};
    margin: 3px 8px;
}}

/* ── Toolbar ──────────────────────────────────────────── */
QToolBar {{
    background: {P['bg1']};
    border: none;
    border-bottom: 1px solid {P['border']};
    padding: 4px 10px;
    spacing: 4px;
}}
QToolBar::separator {{
    background: {P['border2']};
    width: 1px;
    margin: 5px 8px;
}}

/* ── Dock ─────────────────────────────────────────────── */
QDockWidget {{
    background: {P['bg1']};
    color: {P['text2']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}}
QDockWidget::title {{
    background: {P['bg1']};
    padding: 8px 12px 6px 12px;
    border-bottom: 1px solid {P['border']};
}}
QDockWidget::close-button, QDockWidget::float-button {{
    background: transparent;
    border: none;
    padding: 2px;
}}

/* ── Tree / List / Table ──────────────────────────────── */
QTreeView, QListView, QListWidget, QTableView {{
    background: {P['bg1']};
    border: none;
    alternate-background-color: {P['bg0']};
    selection-background-color: transparent;
    selection-color: {P['text']};
    outline: 0;
    show-decoration-selected: 1;
}}
QTreeView::item, QListView::item, QListWidget::item {{
    padding: 5px 6px;
    border-radius: 4px;
    color: {P['text2']};
}}
QTreeView::item:hover, QListView::item:hover, QListWidget::item:hover {{
    background: {P['bg3']};
    color: {P['text']};
}}
QTreeView::item:selected, QListView::item:selected, QListWidget::item:selected {{
    background: {P['bg4']};
    color: {P['text']};
    border-left: 2px solid {P['cyan']};
    padding-left: 4px;
}}
QTreeView::branch {{ background: transparent; }}
QTreeView::branch:selected {{ background: {P['bg4']}; }}
QHeaderView {{ background: transparent; border: none; }}
QHeaderView::section {{
    background: {P['bg1']};
    color: {P['text3']};
    border: none;
    border-bottom: 1px solid {P['border2']};
    padding: 6px 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}
QHeaderView::section:first {{ padding-left: 12px; }}

/* ── Inputs ───────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {P['bg2']};
    border: 1px solid {P['border2']};
    border-radius: 7px;
    padding: 7px 11px;
    color: {P['text']};
    selection-background-color: {P['cyan']};
    selection-color: {P['bg0']};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {P['cyan']};
}}
QLineEdit:placeholder {{ color: {P['text3']}; }}

/* ── Buttons ──────────────────────────────────────────── */
QPushButton {{
    background: {P['bg2']};
    border: 1px solid {P['border2']};
    border-radius: 6px;
    padding: 6px 14px;
    color: {P['text2']};
    font-size: 12px;
    font-weight: 500;
    min-height: 26px;
}}
QPushButton:hover {{
    background: {P['bg3']};
    border-color: {P['border2']};
    color: {P['text']};
}}
QPushButton:pressed {{
    background: {P['bg4']};
    color: {P['cyan']};
}}
QPushButton:checked {{
    background: {P['bg4']};
    border-color: {P['cyan']};
    color: {P['cyan']};
    font-weight: 600;
}}
QPushButton:disabled {{
    color: {P['text3']};
    border-color: {P['border']};
    background: {P['bg1']};
}}
QPushButton#primary {{
    background: {P['cyan']};
    color: {P['bg0']};
    border: none;
    font-weight: 700;
}}
QPushButton#primary:hover {{ background: #22d8ff; }}
QPushButton#primary:pressed {{ background: {P['cyan2']}; }}
QPushButton#ghost {{
    background: transparent;
    border: none;
    color: {P['text2']};
    padding: 4px 8px;
}}
QPushButton#ghost:hover {{ color: {P['text']}; background: {P['bg3']}; }}
QPushButton#ghost:checked {{ color: {P['cyan']}; }}
QPushButton#danger {{
    background: transparent;
    border: 1px solid {P['error']};
    color: {P['error']};
}}
QPushButton#danger:hover {{ background: {P['error']}; color: #fff; }}

/* ── Sliders ──────────────────────────────────────────── */
QSlider::groove:horizontal {{
    height: 2px;
    background: {P['border2']};
    border-radius: 1px;
}}
QSlider::handle:horizontal {{
    background: {P['cyan']};
    border-radius: 5px;
    width: 10px;
    height: 10px;
    margin: -4px 0;
}}
QSlider::handle:horizontal:hover {{
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {P['cyan']};
    border-radius: 1px;
}}

/* ── Scrollbars ───────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent; width: 4px; margin: 2px 0;
}}
QScrollBar::handle:vertical {{
    background: {P['border2']};
    border-radius: 2px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {P['text3']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent; height: 4px; margin: 0 2px;
}}
QScrollBar::handle:horizontal {{
    background: {P['border2']};
    border-radius: 2px;
    min-width: 20px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Status bar ───────────────────────────────────────── */
QStatusBar {{
    background: {P['bg1']};
    border-top: 1px solid {P['border']};
    color: {P['text2']};
    font-size: 11px;
}}
QStatusBar::item {{ border: none; }}

/* ── Tab bar ──────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {P['border2']};
    border-top: none;
    border-radius: 0 0 6px 6px;
    background: {P['bg1']};
}}
QTabBar {{
    background: transparent;
}}
QTabBar::tab {{
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 16px;
    color: {P['text2']};
    font-size: 12px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    color: {P['cyan']};
    border-bottom: 2px solid {P['cyan']};
}}
QTabBar::tab:hover:!selected {{
    color: {P['text']};
    background: {P['bg3']};
}}

/* ── GroupBox ─────────────────────────────────────────── */
QGroupBox {{
    border: 1px solid {P['border2']};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 12px;
    background: {P['bg1']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    top: -8px;
    padding: 0 6px;
    color: {P['text3']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    background: {P['bg0']};
}}

/* ── Splitter ─────────────────────────────────────────── */
QSplitter::handle:horizontal {{
    background: {P['border']};
    width: 1px;
}}
QSplitter::handle:vertical {{
    background: {P['border']};
    height: 1px;
}}

/* ── ComboBox ─────────────────────────────────────────── */
QComboBox {{
    background: {P['bg2']};
    border: 1px solid {P['border2']};
    border-radius: 6px;
    padding: 6px 10px;
    color: {P['text']};
    min-height: 26px;
}}
QComboBox:hover {{ border-color: {P['cyan']}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {P['bg1']};
    border: 1px solid {P['border2']};
    selection-background-color: {P['bg3']};
    outline: 0;
}}

/* ── Progress bar ─────────────────────────────────────── */
QProgressBar {{
    background: {P['bg2']};
    border: none;
    border-radius: 2px;
    height: 4px;
    text-align: center;
    font-size: 0;
}}
QProgressBar::chunk {{
    background: {P['cyan']};
    border-radius: 2px;
}}

/* ── Tooltip ──────────────────────────────────────────── */
QToolTip {{
    background: {P['bg2']};
    color: {P['text']};
    border: 1px solid {P['border2']};
    border-radius: 5px;
    padding: 5px 9px;
    font-size: 12px;
}}

/* ── CheckBox / RadioButton ───────────────────────────── */
QCheckBox, QRadioButton {{ spacing: 7px; color: {P['text2']}; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 15px; height: 15px;
    border: 1px solid {P['border2']};
    border-radius: 4px;
    background: {P['bg2']};
}}
QCheckBox::indicator:checked {{
    background: {P['cyan']};
    border-color: {P['cyan']};
}}
QRadioButton::indicator {{ border-radius: 8px; }}
QRadioButton::indicator:checked {{
    background: {P['cyan']};
    border-color: {P['cyan']};
}}

/* ── Frame ────────────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {P['border2']};
}}
"""


def apply_dark_theme(widget: QWidget) -> None:
    widget.setStyleSheet(_QSS)


PALETTE = P
