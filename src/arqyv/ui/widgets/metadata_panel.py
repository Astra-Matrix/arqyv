"""Right-panel: displays technical + AI-generated metadata for selected file."""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from arqyv.core.events import EventBus, Events

log = logging.getLogger(__name__)


class MetadataPanelWidget(QWidget):
    def __init__(self, events: EventBus, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.events = events
        self._build_ui()
        events.subscribe(Events.AI_ANALYSIS_DONE, self._on_analysis_done)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # File info
        self._file_group = self._make_group("File Info")
        layout.addWidget(self._file_group)

        # Technical metadata
        self._tech_group = self._make_group("Technical")
        layout.addWidget(self._tech_group)

        # AI tags
        self._ai_group = self._make_group("AI Analysis")
        layout.addWidget(self._ai_group)

        layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    def _make_group(self, title: str) -> QGroupBox:
        box = QGroupBox(title)
        box.setLayout(QFormLayout())
        return box

    def _set_fields(self, group: QGroupBox, data: dict[str, Any]) -> None:
        form: QFormLayout = group.layout()  # type: ignore[assignment]
        while form.rowCount():
            form.removeRow(0)
        for key, value in data.items():
            lbl = QLabel(str(value))
            lbl.setWordWrap(True)
            form.addRow(f"<b>{key}</b>", lbl)

    def load_file(self, path: str, metadata: dict[str, Any] | None = None) -> None:
        import os
        from pathlib import Path
        from datetime import datetime

        p = Path(path)
        stat = p.stat() if p.exists() else None

        self._set_fields(self._file_group, {
            "Name": p.name,
            "Directory": str(p.parent),
            "Size": f"{stat.st_size / 1024:.1f} KB" if stat else "—",
            "Modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M") if stat else "—",
            "Extension": p.suffix.upper(),
        })

        if metadata:
            self._set_fields(self._tech_group, metadata.get("technical", {}))
            self._set_fields(self._ai_group, metadata.get("ai", {}))

    def _on_analysis_done(self, path: str = "", metadata: dict[str, Any] | None = None) -> None:
        if metadata:
            self._set_fields(self._ai_group, metadata.get("ai", {}))
