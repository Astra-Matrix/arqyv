"""Search bar — full-width, prominent, debounced, voice-search off-thread."""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

from arqyv.core.events import EventBus, Events
from arqyv.ui.themes.dark import PALETTE as P

log = logging.getLogger(__name__)
_DEBOUNCE_MS      = 280
_LIVE_DEBOUNCE_MS = 150   # faster debounce for live results


class _TranscribeSignals(QObject):
    done = pyqtSignal(str)
    error = pyqtSignal()


class _TranscribeTask(QRunnable):
    """Runs Whisper inference on a thread-pool thread — never blocks the GUI."""

    def __init__(self, recorder: object) -> None:
        super().__init__()
        self.recorder = recorder
        self.signals = _TranscribeSignals()

    @pyqtSlot()
    def run(self) -> None:
        try:
            text: str = self.recorder.stop_and_transcribe()  # type: ignore[attr-defined]
            self.signals.done.emit(text)
        except Exception:
            log.exception("Transcription error.")
            self.signals.error.emit()


class SearchBarWidget(QWidget):
    search_requested     = pyqtSignal(str)
    live_search_changed  = pyqtSignal(str)   # emitted on every keystroke (debounced)

    def __init__(self, events: EventBus, services: dict[str, Any], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.events = events
        self.services = services

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._execute)

        self._live_debounce = QTimer(self)
        self._live_debounce.setSingleShot(True)
        self._live_debounce.timeout.connect(self._emit_live)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search input — full width, pill shaped
        self._input = QLineEdit()
        self._input.setPlaceholderText("Search  —  semantic · full-text · filter: type:video after:2024")
        self._input.setMinimumWidth(480)
        self._input.setFixedHeight(32)
        self._input.setClearButtonEnabled(True)
        self._input.textChanged.connect(self._on_text_changed)
        self._input.returnPressed.connect(self._execute)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: {P['bg2']};
                border: 1px solid {P['border2']};
                border-radius: 16px;
                padding: 0 14px 0 36px;
                color: {P['text']};
                font-size: 13px;
                selection-background-color: {P['cyan']};
                selection-color: {P['bg0']};
            }}
            QLineEdit:focus {{
                border-color: {P['cyan']};
                background: {P['bg3']};
            }}
        """)
        layout.addWidget(self._input, 1)

        # Voice search button
        self._mic = QPushButton("⏺")
        self._mic.setFixedSize(32, 32)
        self._mic.setToolTip("Voice Search — hold to record")
        self._mic.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {P['text2']};
                font-size: 12px;
                margin-left: 4px;
                border-radius: 16px;
            }}
            QPushButton:hover {{ background: {P['bg3']}; color: {P['text']}; }}
            QPushButton:pressed {{ background: {P['cyan']}; color: {P['bg0']}; }}
        """)
        self._mic.pressed.connect(self._on_voice_start)
        self._mic.released.connect(self._on_voice_stop)
        layout.addWidget(self._mic)

    def _on_text_changed(self, text: str) -> None:
        self._live_debounce.start(_LIVE_DEBOUNCE_MS)
        self._debounce.start(_DEBOUNCE_MS)

    def _emit_live(self) -> None:
        self.live_search_changed.emit(self._input.text())

    def clear_text(self) -> None:
        """Called from the results panel's × button."""
        self._input.clear()

    def _execute(self) -> None:
        q = self._input.text().strip()
        if not q:
            return
        log.debug("Search: %r", q)
        self.search_requested.emit(q)
        self.events.emit(Events.SEARCH_RESULTS, query=q)

    def _on_voice_start(self) -> None:
        try:
            from arqyv.ai.voice_search import VoiceSearchRecorder
            self._recorder = VoiceSearchRecorder()
            self._recorder.start()
            self._mic.setText("⏹")
        except Exception:
            log.debug("Voice search unavailable.")

    def _on_voice_stop(self) -> None:
        self._mic.setText("⏺")
        if not hasattr(self, "_recorder"):
            return
        # Dispatch Whisper inference to a thread-pool worker — never blocks the UI
        task = _TranscribeTask(self._recorder)
        task.signals.done.connect(self._on_transcribe_done)
        task.signals.error.connect(lambda: self._mic.setText("⏺"))
        QThreadPool.globalInstance().start(task)
        del self._recorder

    @pyqtSlot(str)
    def _on_transcribe_done(self, text: str) -> None:
        if text:
            self._input.setText(text)
            self._execute()
