"""Media player widget — drives ARQYVMediaEngine.

The widget owns zero playback logic. It is purely a control surface
that translates user interactions into engine calls and engine signals
into UI updates.

Layout:
  ┌─ Video Surface (QVideoWidget) ──────────────────────────┐
  │                                                          │
  │           [Subtitle overlay — transparent]               │
  └──────────────────────────────────────────────────────────┘
  ─── Seek slider ────────────────────────────────────────────
  ▶  ■  0:00 / 0:00  ───────────  🔊 ───  −  1.0×  +  [fmt]
"""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from arqyv.config import AppConfig
from arqyv.core.events import EventBus, Events
from arqyv.engine.subtitle import SubtitleOverlay

log = logging.getLogger(__name__)


class MediaPlayerWidget(QWidget):
    """Pure control-surface widget — all logic lives in ARQYVMediaEngine."""

    def __init__(
        self,
        config: AppConfig,
        events: EventBus,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.events = events
        self._engine: "ARQYVMediaEngine | None" = None  # type: ignore[name-defined]
        self._rate = 1.0
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Video surface + subtitle overlay (stacked)
        self._video = QVideoWidget()
        self._video.setStyleSheet("background:#000;")
        self._video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._video.setMinimumHeight(140)

        self._subtitle = SubtitleOverlay(self._video)
        self._subtitle.resize(self._video.size())
        self._video.resizeEvent = self._on_video_resize  # type: ignore[method-assign]

        root.addWidget(self._video, 1)

        # Seek slider
        self._seek = QSlider(Qt.Orientation.Horizontal)
        self._seek.setRange(0, 1000)
        self._seek.sliderMoved.connect(self._on_seek)
        self._seek.setToolTip("Seek")
        root.addWidget(self._seek)

        # Controls bar
        bar = QHBoxLayout()
        bar.setContentsMargins(8, 4, 8, 6)
        bar.setSpacing(6)

        self._play_btn  = self._mk_btn("▶",  "Play / Pause (Space)", self._on_play_pause, 36)
        self._stop_btn  = self._mk_btn("■",  "Stop",                  self._on_stop,       36)
        self._prev_btn  = self._mk_btn("⏮",  "Previous track",        self._on_prev,       36)
        self._next_btn  = self._mk_btn("⏭",  "Next track",            self._on_next,       36)

        self._time_lbl  = QLabel("0:00 / 0:00")
        self._time_lbl.setFixedWidth(116)
        self._time_lbl.setStyleSheet("font-family:monospace; font-size:12px;")

        vol_icon = QLabel("🔊")
        self._vol = QSlider(Qt.Orientation.Horizontal)
        self._vol.setRange(0, 100)
        self._vol.setValue(80)
        self._vol.setFixedWidth(80)
        self._vol.setToolTip("Volume")
        self._vol.valueChanged.connect(self._on_volume)

        self._spd_dn = self._mk_btn("−", "Slower",  self._on_speed_dn, 26)
        self._spd_lbl = QLabel("1×")
        self._spd_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._spd_lbl.setFixedWidth(36)
        self._spd_up = self._mk_btn("+", "Faster",  self._on_speed_up, 26)

        self._fmt_lbl = QLabel("")
        self._fmt_lbl.setStyleSheet("color:#555; font-size:10px;")

        self._shuf_btn   = self._mk_btn("⇀",  "Toggle shuffle",  self._on_shuffle,   30)
        self._repeat_btn = self._mk_btn("↺",  "Cycle repeat",    self._on_repeat,    30)
        self._sub_btn    = self._mk_btn("CC", "Load subtitles",   self._on_load_subs, 32)

        bar.addWidget(self._prev_btn)
        bar.addWidget(self._play_btn)
        bar.addWidget(self._stop_btn)
        bar.addWidget(self._next_btn)
        bar.addWidget(self._time_lbl)
        bar.addStretch()
        bar.addWidget(self._shuf_btn)
        bar.addWidget(self._repeat_btn)
        bar.addWidget(self._sub_btn)
        bar.addSpacing(8)
        bar.addWidget(vol_icon)
        bar.addWidget(self._vol)
        bar.addSpacing(8)
        bar.addWidget(self._spd_dn)
        bar.addWidget(self._spd_lbl)
        bar.addWidget(self._spd_up)
        bar.addSpacing(8)
        bar.addWidget(self._fmt_lbl)

        root.addLayout(bar)

    @staticmethod
    def _mk_btn(text: str, tip: str, slot: object, w: int) -> QPushButton:
        b = QPushButton(text)
        b.setFixedWidth(w)
        b.setToolTip(tip)
        b.clicked.connect(slot)  # type: ignore[arg-type]
        return b

    # ── Engine wiring ──────────────────────────────────────────────────────

    def init_engine(self) -> "ARQYVMediaEngine":  # type: ignore[name-defined]
        """Create and wire the ARQYVMediaEngine. Call once after __init__."""
        from arqyv.engine.core import ARQYVMediaEngine
        self._engine = ARQYVMediaEngine(
            config=self.config,
            video_widget=self._video,
            parent=self,
        )
        self._engine.attach_subtitle_overlay(self._subtitle)
        self._engine.state_changed.connect(self._on_state)
        self._engine.position_changed.connect(self._on_position)
        self._engine.format_detected.connect(self._on_format)
        self._engine.error.connect(self._on_error)
        # Set initial volume
        self._engine.set_volume(self._vol.value())
        return self._engine

    @property
    def engine(self) -> "ARQYVMediaEngine | None":  # type: ignore[name-defined]
        return self._engine

    # ── Public helpers ─────────────────────────────────────────────────────

    def open_file(self, path: str | Path) -> None:
        if self._engine:
            self._engine.open(path)

    def open_playlist(self, paths: list[Path], start: int = 0) -> None:
        if self._engine:
            self._engine.open_playlist(paths, start)

    # ── Control slots ──────────────────────────────────────────────────────

    @pyqtSlot()
    def _on_play_pause(self) -> None:
        if self._engine:
            self._engine.toggle()

    @pyqtSlot()
    def _on_stop(self) -> None:
        if self._engine:
            self._engine.stop()

    @pyqtSlot()
    def _on_prev(self) -> None:
        if self._engine:
            self._engine.play_previous()

    @pyqtSlot()
    def _on_next(self) -> None:
        if self._engine:
            self._engine.play_next()

    @pyqtSlot(int)
    def _on_seek(self, value: int) -> None:
        if self._engine:
            self._engine.seek(value / 1000.0)

    @pyqtSlot(int)
    def _on_volume(self, value: int) -> None:
        if self._engine:
            self._engine.set_volume(value)

    @pyqtSlot()
    def _on_speed_up(self) -> None:
        self._rate = round(min(3.0, self._rate + 0.25), 2)
        self._apply_rate()

    @pyqtSlot()
    def _on_speed_dn(self) -> None:
        self._rate = round(max(0.25, self._rate - 0.25), 2)
        self._apply_rate()

    def _apply_rate(self) -> None:
        if self._engine:
            self._engine.set_rate(self._rate)
        self._spd_lbl.setText(f"{self._rate:g}×")

    @pyqtSlot()
    def _on_shuffle(self) -> None:
        if self._engine:
            enabled = self._engine.playlist.toggle_shuffle()
            self._shuf_btn.setStyleSheet(
                "color:#00b4d8;" if enabled else ""
            )

    @pyqtSlot()
    def _on_repeat(self) -> None:
        if not self._engine:
            return
        from arqyv.engine.playlist import RepeatMode
        mode = self._engine.playlist.cycle_repeat()
        icons = {RepeatMode.NONE: "↺", RepeatMode.ONE: "↻¹", RepeatMode.ALL: "↻"}
        colors = {RepeatMode.NONE: "", RepeatMode.ONE: "color:#ff9800;", RepeatMode.ALL: "color:#00b4d8;"}
        self._repeat_btn.setText(icons[mode])
        self._repeat_btn.setStyleSheet(colors[mode])

    @pyqtSlot()
    def _on_load_subs(self) -> None:
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Subtitle File", "",
            "Subtitles (*.srt *.vtt *.ass *.ssa);;All files (*)"
        )
        if path and self._engine:
            from arqyv.engine.subtitle import load_subtitle_file
            cues = load_subtitle_file(Path(path))
            self._engine._subtitle_overlay and self._engine._subtitle_overlay.load_cues(cues)

    # ── Engine signal handlers ─────────────────────────────────────────────

    @pyqtSlot(str)
    def _on_state(self, state: str) -> None:
        icons = {"playing": "⏸", "paused": "▶", "stopped": "▶", "ended": "▶"}
        self._play_btn.setText(icons.get(state, "▶"))
        self.events.emit(Events.PLAYER_STATE_CHANGED, state=state)

    @pyqtSlot(int, int)
    def _on_position(self, position_ms: int, duration_ms: int) -> None:
        if duration_ms > 0:
            self._seek.blockSignals(True)
            self._seek.setValue(int(position_ms / duration_ms * 1000))
            self._seek.blockSignals(False)
        self._time_lbl.setText(f"{_fmt(position_ms)} / {_fmt(duration_ms)}")
        self.events.emit(Events.PLAYER_POSITION_CHANGED, position=position_ms, length_ms=duration_ms)

    @pyqtSlot(str)
    def _on_format(self, fmt_str: str) -> None:
        # Show short name only
        short = fmt_str.split("(")[0].strip()
        self._fmt_lbl.setText(short)
        self._fmt_lbl.setToolTip(fmt_str)

    @pyqtSlot(str)
    def _on_error(self, msg: str) -> None:
        log.error("Player error: %s", msg)
        self._fmt_lbl.setText("⚠ error")
        self._fmt_lbl.setToolTip(msg)

    # ── Resize subtitle overlay ────────────────────────────────────────────

    def _on_video_resize(self, event: object) -> None:  # type: ignore[override]
        QVideoWidget.resizeEvent(self._video, event)  # type: ignore[arg-type]
        self._subtitle.resize(self._video.size())


def _fmt(ms: int) -> str:
    s = max(0, ms) // 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"
