"""Search bar widget with real-time suggestions and voice search toggle."""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCompleter,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)

from arqyv.core.events import EventBus, Events

log = logging.getLogger(__name__)

_DEBOUNCE_MS = 300


class SearchBarWidget(QWidget):
    search_requested = pyqtSignal(str)

    def __init__(self, events: EventBus, services: dict[str, Any], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.events = events
        self.services = services

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._execute_search)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Search your library… (Semantic + Full-text)")
        self._input.setMinimumWidth(400)
        self._input.setClearButtonEnabled(True)
        self._input.textChanged.connect(self._on_text_changed)
        self._input.returnPressed.connect(self._execute_search)

        self._voice_btn = QPushButton("🎙")
        self._voice_btn.setFixedWidth(36)
        self._voice_btn.setToolTip("Voice Search (hold to record)")
        self._voice_btn.pressed.connect(self._on_voice_start)
        self._voice_btn.released.connect(self._on_voice_stop)

        layout.addWidget(self._input, 1)
        layout.addWidget(self._voice_btn)

    def _on_text_changed(self, text: str) -> None:
        self._debounce_timer.start(_DEBOUNCE_MS)

    def _execute_search(self) -> None:
        query = self._input.text().strip()
        if not query:
            return
        log.debug("Search: %r", query)
        self.search_requested.emit(query)
        self.events.emit(Events.SEARCH_RESULTS, query=query)

    def _on_voice_start(self) -> None:
        from arqyv.ai.voice_search import VoiceSearchRecorder
        self._recorder = VoiceSearchRecorder()
        self._recorder.start()
        self._voice_btn.setText("⏹")

    def _on_voice_stop(self) -> None:
        if hasattr(self, "_recorder"):
            text = self._recorder.stop_and_transcribe()
            self._input.setText(text)
            self._execute_search()
        self._voice_btn.setText("🎙")
