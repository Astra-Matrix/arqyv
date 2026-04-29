"""Batch rename dialog with live preview."""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from arqyv.utils.batch_rename import BatchRenamer, RenamePattern

log = logging.getLogger(__name__)


class BatchRenameDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Batch Rename")
        self.setMinimumSize(700, 500)
        self._files: list[Path] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Pattern row
        pattern_row = QHBoxLayout()
        self._pattern_input = QLineEdit()
        self._pattern_input.setPlaceholderText(
            "Pattern: {name} | {date} | {counter:04d} | {ext} | {ai_tag}"
        )
        self._pattern_input.textChanged.connect(self._refresh_preview)
        pattern_row.addWidget(QLabel("Pattern:"))
        pattern_row.addWidget(self._pattern_input, 1)
        layout.addLayout(pattern_row)

        # File list + preview
        cols = QHBoxLayout()

        self._source_list = QListWidget()
        self._source_list.setAlternatingRowColors(True)

        self._preview_list = QListWidget()
        self._preview_list.setAlternatingRowColors(True)

        cols.addWidget(self._mk_group("Original", self._source_list))
        cols.addWidget(self._mk_group("Preview", self._preview_list))
        layout.addLayout(cols, 1)

        # Add files button
        add_btn = QPushButton("Add Files…")
        add_btn.clicked.connect(self._add_files)
        layout.addWidget(add_btn)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Close
        )
        apply_btn = buttons.button(QDialogButtonBox.StandardButton.Apply)
        assert apply_btn is not None
        apply_btn.clicked.connect(self._apply_rename)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _mk_group(self, title: str, widget: QWidget) -> QWidget:
        from PyQt6.QtWidgets import QGroupBox
        box = QGroupBox(title)
        v = QVBoxLayout(box)
        v.addWidget(widget)
        return box

    def _add_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        for p in paths:
            path = Path(p)
            if path not in self._files:
                self._files.append(path)
                self._source_list.addItem(path.name)
        self._refresh_preview()

    def _refresh_preview(self) -> None:
        pattern = self._pattern_input.text()
        self._preview_list.clear()
        renamer = BatchRenamer(pattern=pattern)
        for i, path in enumerate(self._files):
            try:
                new_name = renamer.generate(path, index=i)
            except Exception as e:
                new_name = f"[ERROR: {e}]"
            item = QListWidgetItem(new_name)
            if new_name.startswith("[ERROR"):
                item.setForeground(Qt.GlobalColor.red)
            self._preview_list.addItem(item)

    def _apply_rename(self) -> None:
        pattern = self._pattern_input.text()
        renamer = BatchRenamer(pattern=pattern)
        for i, path in enumerate(self._files):
            try:
                renamer.apply(path, index=i)
                log.info("Renamed: %s", path)
            except Exception:
                log.exception("Failed to rename %s", path)
        self._refresh_preview()
