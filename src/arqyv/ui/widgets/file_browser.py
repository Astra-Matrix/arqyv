"""File browser sidebar with tree + grid/list toggle view."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QModelIndex, QSize, pyqtSignal
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QListView,
    QPushButton,
    QSplitter,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from arqyv.config import AppConfig
from arqyv.core.events import EventBus, Events

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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # View toggle toolbar
        toggle_row = QHBoxLayout()
        self._tree_btn = QPushButton("Tree")
        self._grid_btn = QPushButton("Grid")
        self._list_btn = QPushButton("List")
        for btn in (self._tree_btn, self._grid_btn, self._list_btn):
            btn.setCheckable(True)
            btn.setFixedHeight(24)
            toggle_row.addWidget(btn)
        self._tree_btn.setChecked(True)
        toggle_row.addStretch()

        self._tree_btn.clicked.connect(lambda: self._set_view("tree"))
        self._grid_btn.clicked.connect(lambda: self._set_view("grid"))
        self._list_btn.clicked.connect(lambda: self._set_view("list"))

        layout.addLayout(toggle_row)

        # File system model
        self._fs_model = QFileSystemModel()
        self._fs_model.setRootPath("")

        # Tree view
        self._tree_view = QTreeView()
        self._tree_view.setModel(self._fs_model)
        self._tree_view.setRootIndex(self._fs_model.index(""))
        self._tree_view.hideColumn(1)
        self._tree_view.hideColumn(2)
        self._tree_view.hideColumn(3)
        self._tree_view.clicked.connect(self._on_tree_clicked)
        self._tree_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # List/grid view (icon mode = grid, list mode = list)
        self._list_view = QListView()
        self._list_view.setModel(self._fs_model)
        self._list_view.setViewMode(QListView.ViewMode.IconMode)
        self._list_view.setResizeMode(QListView.ResizeMode.Adjust)
        self._list_view.setGridSize(QSize(100, 100))
        self._list_view.hide()
        self._list_view.clicked.connect(self._on_list_clicked)

        layout.addWidget(self._tree_view, 1)
        layout.addWidget(self._list_view, 1)

    def _set_view(self, mode: str) -> None:
        for btn, name in ((self._tree_btn, "tree"), (self._grid_btn, "grid"), (self._list_btn, "list")):
            btn.setChecked(name == mode)

        if mode == "tree":
            self._tree_view.show()
            self._list_view.hide()
        elif mode == "grid":
            self._tree_view.hide()
            self._list_view.setViewMode(QListView.ViewMode.IconMode)
            self._list_view.show()
        elif mode == "list":
            self._tree_view.hide()
            self._list_view.setViewMode(QListView.ViewMode.ListMode)
            self._list_view.show()

    def _on_tree_clicked(self, index: QModelIndex) -> None:
        path = self._fs_model.filePath(index)
        self._emit_selection(path)

    def _on_list_clicked(self, index: QModelIndex) -> None:
        path = self._fs_model.filePath(index)
        self._emit_selection(path)

    def _emit_selection(self, path: str) -> None:
        self.file_selected.emit(path)
        self.events.emit(Events.FILE_ADDED, path=path)
        log.debug("Selected: %s", path)

    def navigate_to(self, path: str) -> None:
        idx = self._fs_model.index(path)
        self._tree_view.setCurrentIndex(idx)
        self._tree_view.scrollTo(idx)
