"""
ARQYV dark theme — next-generation edition.

Depth hierarchy:
  bg0  #05050d   — absolute base (window chrome, outer edge)
  bg1  #0a0a14   — panel surfaces, toolbars, status bar
  bg2  #0f0f1c   — card backgrounds, inputs
  bg3  #161624   — hover state, alternating rows
  bg4  #1e1e30   — active/selected surface

Single accent: electric cyan #00d4ff
Violet secondary: #7c3aed  (used sparingly — badges, highlights)
"""

from __future__ import annotations
from PyQt6.QtWidgets import QWidget

P = {
    "bg0":       "#05050d",
    "bg1":       "#090912",
    "bg2":       "#0e0e1a",
    "bg3":       "#141422",
    "bg4":       "#1c1c2e",
    "cyan":      "#00d4ff",
    "cyan2":     "#00a8cc",
    "violet":    "#7c3aed",
    "violet2":   "#5b21b6",
    "text":      "#f0f0fb",   # brighter, crisper white
    "text2":     "#9898be",   # more visible secondary
    "text3":     "#48486a",   # tertiary — still subtle
    "success":   "#22c55e",
    "warning":   "#f59e0b",
    "error":     "#ef4444",
    "border":    "#0e0e1e",
    "border2":   "#161628",
}

_QSS = f"""
/* ── Global reset ─────────────────────────────────────────── */
* {{ box-sizing: border-box; outline: none; }}

QMainWindow, QDialog, QWidget {{
    background: {P['bg0']};
    color: {P['text']};
    font-family: 'Segoe UI Variable', 'Segoe UI', 'Inter', 'SF Pro Display', system-ui, sans-serif;
    font-size: 14px;
    line-height: 1.55;
}}

/* ── Menu ─────────────────────────────────────────────────── */
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
    border-radius: 10px;
    padding: 5px;
}}
QMenu::item {{
    padding: 7px 20px 7px 12px;
    border-radius: 5px;
    color: {P['text2']};
    font-size: 13.5px;
}}
QMenu::item:selected {{
    background: {P['bg3']};
    color: {P['text']};
}}
QMenu::separator {{
    height: 1px;
    background: {P['border2']};
    margin: 4px 10px;
}}

/* ── Toolbar ──────────────────────────────────────────────── */
QToolBar {{
    background: {P['bg1']};
    border: none;
    border-bottom: 1px solid {P['border']};
    padding: 4px 10px;
    spacing: 6px;
}}
QToolBar::separator {{
    background: {P['border2']};
    width: 1px;
    margin: 5px 6px;
}}

/* ── Dock ─────────────────────────────────────────────────── */
QDockWidget {{
    background: {P['bg1']};
    color: {P['text3']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.14em;
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

/* ── Tree / List / Table ──────────────────────────────────── */
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
    padding: 6px 8px;
    border-radius: 5px;
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
    padding-left: 6px;
}}
QTreeView::branch {{ background: transparent; }}
QTreeView::branch:selected {{ background: {P['bg4']}; }}
QHeaderView {{ background: transparent; border: none; }}
QHeaderView::section {{
    background: {P['bg1']};
    color: {P['text3']};
    border: none;
    border-bottom: 1px solid {P['border2']};
    padding: 6px 10px;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
}}
QHeaderView::section:first {{ padding-left: 14px; }}

/* ── Inputs ───────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {P['bg2']};
    border: 1px solid {P['border2']};
    border-radius: 8px;
    padding: 7px 12px;
    color: {P['text']};
    selection-background-color: {P['cyan']};
    selection-color: {P['bg0']};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {P['cyan']};
    background: {P['bg3']};
}}

/* ── Buttons ──────────────────────────────────────────────── */
QPushButton {{
    background: {P['bg2']};
    border: 1px solid {P['border2']};
    border-radius: 7px;
    padding: 6px 14px;
    color: {P['text2']};
    font-size: 13.5px;
    font-weight: 400;
    min-height: 28px;
}}
QPushButton:hover {{
    background: {P['bg3']};
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
    border-radius: 8px;
}}
QPushButton#primary:hover  {{ background: #22dbff; }}
QPushButton#primary:pressed {{ background: {P['cyan2']}; }}
QPushButton#ghost {{
    background: transparent;
    border: none;
    color: {P['text2']};
    padding: 4px 8px;
    border-radius: 6px;
}}
QPushButton#ghost:hover    {{ color: {P['text']}; background: {P['bg3']}; }}
QPushButton#ghost:checked  {{ color: {P['cyan']}; background: {P['bg3']}; }}
QPushButton#danger {{
    background: transparent;
    border: 1px solid {P['error']};
    color: {P['error']};
    border-radius: 7px;
}}
QPushButton#danger:hover {{ background: {P['error']}; color: #fff; }}

/* ── Sliders ──────────────────────────────────────────────── */
QSlider::groove:horizontal {{
    height: 3px;
    background: {P['border2']};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {P['cyan']};
    border-radius: 5px;
    width: 10px;
    height: 10px;
    margin: -4px 0;
}}
QSlider::handle:horizontal:hover {{
    width: 14px; height: 14px;
    margin: -6px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {P['cyan']};
    border-radius: 2px;
}}

/* ── Scrollbars — appear only on hover ───────────────────── */
QScrollBar:vertical {{
    background: transparent; width: 5px; margin: 2px 0;
}}
QScrollBar::handle:vertical {{
    background: {P['border2']};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {P['text3']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent; height: 5px; margin: 0 2px;
}}
QScrollBar::handle:horizontal {{
    background: {P['border2']};
    border-radius: 3px;
    min-width: 24px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Status bar ───────────────────────────────────────────── */
QStatusBar {{
    background: {P['bg1']};
    border-top: 1px solid {P['border']};
    color: {P['text2']};
    font-size: 11px;
    min-height: 28px;
    padding: 0 8px;
}}
QStatusBar::item {{ border: none; }}

/* ── Splitter ─────────────────────────────────────────────── */
QSplitter::handle:horizontal {{
    background: {P['border']};
    width: 1px;
}}
QSplitter::handle:vertical {{
    background: {P['border']};
    height: 1px;
}}

/* ── Tab bar ──────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {P['border2']};
    border-top: none;
    border-radius: 0 0 7px 7px;
    background: {P['bg1']};
}}
QTabBar {{ background: transparent; }}
QTabBar::tab {{
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 9px 18px;
    color: {P['text2']};
    font-size: 13px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    color: {P['cyan']};
    border-bottom: 2px solid {P['cyan']};
    font-weight: 500;
}}
QTabBar::tab:hover:!selected {{
    color: {P['text']};
    background: {P['bg3']};
    border-radius: 6px 6px 0 0;
}}

/* ── GroupBox ─────────────────────────────────────────────── */
QGroupBox {{
    border: 1px solid {P['border2']};
    border-radius: 9px;
    margin-top: 18px;
    padding-top: 14px;
    background: {P['bg1']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px; top: -9px;
    padding: 0 6px;
    color: {P['text3']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    background: {P['bg0']};
}}

/* ── ComboBox ─────────────────────────────────────────────── */
QComboBox {{
    background: {P['bg2']};
    border: 1px solid {P['border2']};
    border-radius: 7px;
    padding: 6px 10px;
    color: {P['text']};
    min-height: 28px;
}}
QComboBox:hover {{ border-color: {P['cyan']}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {P['bg1']};
    border: 1px solid {P['border2']};
    border-radius: 7px;
    selection-background-color: {P['bg3']};
    outline: 0;
}}

/* ── Progress bar ─────────────────────────────────────────── */
QProgressBar {{
    background: {P['bg2']};
    border: none;
    border-radius: 3px;
    height: 5px;
    text-align: center;
    font-size: 0;
}}
QProgressBar::chunk {{
    background: {P['cyan']};
    border-radius: 3px;
}}

/* ── Tooltip ──────────────────────────────────────────────── */
QToolTip {{
    background: {P['bg2']};
    color: {P['text']};
    border: 1px solid {P['border2']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ── CheckBox / RadioButton ───────────────────────────────── */
QCheckBox, QRadioButton {{ spacing: 8px; color: {P['text2']}; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px; height: 16px;
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

/* ── Frame lines ──────────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {P['border2']};
}}

/* ── SpinBox ──────────────────────────────────────────────── */
QSpinBox, QDoubleSpinBox {{
    background: {P['bg2']};
    border: 1px solid {P['border2']};
    border-radius: 7px;
    padding: 5px 8px;
    color: {P['text']};
    min-height: 28px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {P['cyan']}; }}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: transparent;
    border: none;
    width: 16px;
}}
"""


def apply_dark_theme(widget: QWidget) -> None:
    widget.setStyleSheet(_QSS)


PALETTE = P
