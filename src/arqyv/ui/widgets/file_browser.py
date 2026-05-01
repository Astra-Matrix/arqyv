"""
File browser sidebar — clean tree with icon-only view toggle.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QModelIndex, QSize, pyqtSignal
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from arqyv.config import AppConfig
from arqyv.core.events import EventBus, Events
from arqyv.ui.themes.dark import PALETTE as P

log = logging.getLogger(__name__)


class FileBrowserWidget(QWidget):
    file_selected = pyqtSignal(str)

    def __init__(
        self,
        config: AppConfig,
        events: EventBus,
        services: dict[str, Any],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.events = events
        self.services = services
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ─────────────────────────────────────────────────────
        hdr = QWidget()
        hdr.setFixedHeight(38)
        hdr.setStyleSheet(f"background: {P['bg1']}; border-bottom: 1px solid {P['border']};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(12, 0, 8, 0)
        hl.setSpacing(4)

        title = QLabel("LIBRARY")
        title.setStyleSheet(f"color: {P['text3']}; font-size: 10px; font-weight: 700; letter-spacing: 0.14em;")
        hl.addWidget(title)
        hl.addStretch()

        # View toggle — icon-only buttons
        self._v_tree = self._toggle_btn("≡", "tree",  "Tree view")
        self._v_list = self._toggle_btn("☰", "list",  "List view")
        self._v_grid = self._toggle_btn("⊞", "grid",  "Grid view")
        self._v_tree.setChecked(True)
        hl.addWidget(self._v_tree)
        hl.addWidget(self._v_list)
        hl.addWidget(self._v_grid)
        root.addWidget(hdr)

        # ── File system model ──────────────────────────────────────────────
        self._fs = QFileSystemModel()
        self._fs.setRootPath("")

        # Tree view
        self._tree = QTreeView()
        self._tree.setModel(self._fs)
        self._tree.setRootIndex(self._fs.index(""))
        self._tree.hideColumn(1)
        self._tree.hideColumn(2)
        self._tree.hideColumn(3)
        self._tree.header().hide()
        self._tree.setIndentation(14)
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._tree.setAnimated(True)
        self._tree.clicked.connect(lambda i: self._emit(self._fs.filePath(i)))
        self._tree.setStyleSheet(f"""
            QTreeView {{
                background: {P['bg1']};
                border: none;
                font-size: 13px;
            }}
            QTreeView::item {{
                padding: 4px 4px 4px 2px;
                border-radius: 4px;
                color: {P['text2']};
            }}
            QTreeView::item:hover {{ background: {P['bg3']}; color: {P['text']}; }}
            QTreeView::item:selected {{
                background: {P['bg4']};
                color: {P['text']};
                border-left: 2px solid {P['cyan']};
            }}
        """)

        # List / grid view
        self._grid_view = QListView()
        self._grid_view.setModel(self._fs)
        self._grid_view.setViewMode(QListView.ViewMode.IconMode)
        self._grid_view.setResizeMode(QListView.ResizeMode.Adjust)
        self._grid_view.setGridSize(QSize(90, 90))
        self._grid_view.setSpacing(4)
        self._grid_view.hide()
        self._grid_view.clicked.connect(lambda i: self._emit(self._fs.filePath(i)))
        self._grid_view.setStyleSheet(f"""
            QListView {{
                background: {P['bg1']};
                border: none;
                font-size: 11px;
            }}
            QListView::item {{
                padding: 4px;
                border-radius: 6px;
                color: {P['text2']};
            }}
            QListView::item:hover {{ background: {P['bg3']}; color: {P['text']}; }}
            QListView::item:selected {{ background: {P['bg4']}; color: {P['text']}; }}
        """)

        root.addWidget(self._tree, 1)
        root.addWidget(self._grid_view, 1)

    def _toggle_btn(self, text: str, mode: str, tip: str) -> QPushButton:
        b = QPushButton(text)
        b.setFixedSize(26, 26)
        b.setCheckable(True)
        b.setToolTip(tip)
        b.setObjectName("ghost")
        b.clicked.connect(lambda: self._set_view(mode))
        return b

    def _set_view(self, mode: str) -> None:
        self._v_tree.setChecked(mode == "tree")
        self._v_list.setChecked(mode == "list")
        self._v_grid.setChecked(mode == "grid")

        if mode == "tree":
            self._tree.show()
            self._grid_view.hide()
        elif mode == "list":
            self._tree.hide()
            self._grid_view.setViewMode(QListView.ViewMode.ListMode)
            self._grid_view.setGridSize(QSize(0, 0))
            self._grid_view.show()
        elif mode == "grid":
            self._tree.hide()
            self._grid_view.setViewMode(QListView.ViewMode.IconMode)
            self._grid_view.setGridSize(QSize(90, 90))
            self._grid_view.show()

    def _emit(self, path: str) -> None:
        if path:
            self.file_selected.emit(path)
            self.events.emit(Events.FILE_ADDED, path=path)
            log.debug("Selected: %s", path)

    def navigate_to(self, path: str) -> None:
        idx = self._fs.index(path)
        self._tree.setCurrentIndex(idx)
        self._tree.scrollTo(idx)
        self._tree.expand(idx)
