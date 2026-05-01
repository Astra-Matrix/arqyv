"""
Right-panel: technical + AI metadata for the selected file.
Clean key/value rows, no heavy group boxes.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from arqyv.core.events import EventBus, Events
from arqyv.ui.themes.dark import PALETTE as P

log = logging.getLogger(__name__)


def _section(title: str) -> QLabel:
    lbl = QLabel(title.upper())
    lbl.setStyleSheet(f"""
        color: {P['text3']};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.14em;
        padding: 10px 0 5px 0;
    """)
    return lbl


def _divider() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color: {P['border2']}; margin: 0;")
    f.setFixedHeight(1)
    return f


class _Row(QWidget):
    def __init__(self, key: str, value: str, mono: bool = False) -> None:
        super().__init__()
        hl = QHBoxLayout(self)
        hl.setContentsMargins(0, 3, 0, 3)
        hl.setSpacing(8)

        k = QLabel(key)
        k.setFixedWidth(90)
        k.setStyleSheet(f"color: {P['text2']}; font-size: 11px;")
        k.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        v = QLabel(value or "—")
        v.setWordWrap(True)
        v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        font_family = "'Courier New', monospace" if mono else "inherit"
        v.setStyleSheet(
            f"color: {P['text']}; font-size: 12px; font-family: {font_family};"
        )

        hl.addWidget(k)
        hl.addWidget(v, 1)

    def update_value(self, value: str) -> None:
        self.findChildren(QLabel)[1].setText(value or "—")  # type: ignore[index]


class MetadataPanelWidget(QWidget):
    def __init__(self, events: EventBus, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.events = events
        self._rows: dict[str, _Row] = {}
        self._build_ui()
        events.subscribe(Events.AI_ANALYSIS_DONE, self._on_analysis_done)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        hdr = QWidget()
        hdr.setFixedHeight(44)
        hdr.setStyleSheet(f"background: {P['bg1']}; border-bottom: 1px solid {P['border']};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(12, 0, 12, 0)
        title = QLabel("INFO")
        title.setStyleSheet(f"color: {P['text3']}; font-size: 10px; font-weight: 700; letter-spacing: 0.14em;")
        hl.addWidget(title)
        hl.addStretch()
        outer.addWidget(hdr)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._content = QWidget()
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(14, 6, 14, 14)
        self._layout.setSpacing(0)

        # Placeholder
        self._placeholder = QLabel("Select a file\nto see details")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet(f"color: {P['text3']}; font-size: 12px; padding: 40px 0;")
        self._layout.addWidget(self._placeholder)
        self._layout.addStretch()

        scroll.setWidget(self._content)
        outer.addWidget(scroll, 1)

    def load_file(self, path: str, metadata: dict[str, Any] | None = None) -> None:
        p = Path(path)
        self._placeholder.hide()
        self._clear_rows()

        stat = p.stat() if p.exists() else None
        size_str = self._human_size(stat.st_size) if stat else "—"
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d  %H:%M") if stat else "—"

        self._add_section("File")
        self._add_row("Name",    p.stem,       mono=False)
        self._add_row("Type",    p.suffix.upper().lstrip(".") or "—")
        self._add_row("Size",    size_str,     mono=True)
        self._add_row("Modified", mtime,       mono=True)
        self._add_row("Path",    str(p.parent), mono=True)

        if metadata:
            tech = metadata.get("technical", {})
            if tech:
                self._layout.addWidget(_divider())
                self._add_section("Technical")
                for k, v in tech.items():
                    self._add_row(k, str(v), mono=True)

            ai = metadata.get("ai", {})
            if ai:
                self._layout.addWidget(_divider())
                self._add_section("AI Analysis")
                for k, v in ai.items():
                    self._add_row(k, str(v))

        self._layout.addStretch()

    def _on_analysis_done(self, path: str = "", metadata: dict[str, Any] | None = None) -> None:
        if not metadata:
            return
        ai = metadata.get("ai", {})
        for k, v in ai.items():
            key = f"ai_{k}"
            if key in self._rows:
                self._rows[key].update_value(str(v))

    # ── Helpers ────────────────────────────────────────────────────────────

    def _clear_rows(self) -> None:
        self._rows.clear()
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget() and item.widget() is not self._placeholder:
                item.widget().deleteLater()

    def _add_section(self, title: str) -> None:
        self._layout.addWidget(_section(title))

    def _add_row(self, key: str, value: str, mono: bool = False) -> None:
        row = _Row(key, value, mono=mono)
        self._rows[key] = row
        self._layout.addWidget(row)

    @staticmethod
    def _human_size(b: int) -> str:
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024  # type: ignore[assignment]
        return f"{b:.1f} PB"
