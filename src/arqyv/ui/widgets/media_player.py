"""
ARQYV Media Player Widget — next-generation control surface.

Layout (fixed 88 px tall bar below content area):

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ← seek bar (hover to enlarge)
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  [cover/waveform]  ⏮ ⏪  ⊙ PLAY ⊙  ⏩ ⏭   0:00 / 0:00  FMT   ░░░░vol  │
  │                                                      ┃ ⇀ ↺ CC ┃  −1×+  │
  └──────────────────────────────────────────────────────────────────────────┘
  
Video surface lives in the main content area (PreviewPanelWidget).
This widget is ONLY the control bar + seek bar.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
    QFrame,
)

from arqyv.config import AppConfig
from arqyv.core.events import EventBus, Events
from arqyv.engine.subtitle import SubtitleOverlay
from arqyv.ui.themes.dark import PALETTE as P

log = logging.getLogger(__name__)

_PLAY_SIZE = 40    # primary play/pause button
_BTN_MAIN  = 30    # transport buttons
_BTN_SEC   = 26    # secondary buttons


def _fmt(ms: int) -> str:
    s = max(0, ms) // 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


def _vline() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.VLine)
    f.setStyleSheet(f"color: {P['border2']};")
    f.setFixedHeight(22)
    return f


_SEEK_IDLE = f"""
    QSlider::groove:horizontal {{
        height: 3px;
        background: {P['border2']};
        border-radius: 2px;
        margin: 0 2px;
    }}
    QSlider::sub-page:horizontal {{
        background: {P['cyan']};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {P['cyan']};
        border: 2px solid {P['bg0']};
        border-radius: 6px;
        width: 12px;
        height: 12px;
        margin: -5px 0;
    }}
"""

_SEEK_HOVER = f"""
    QSlider::groove:horizontal {{
        height: 5px;
        background: {P['bg3']};
        border-radius: 3px;
        margin: 0 2px;
    }}
    QSlider::sub-page:horizontal {{
        background: {P['cyan']};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: #fff;
        border: 2px solid {P['cyan']};
        border-radius: 7px;
        width: 14px;
        height: 14px;
        margin: -5px 0;
    }}
"""


class _SeekSlider(QSlider):
    """Seek slider that expands slightly on hover for easier grabbing."""

    def __init__(self) -> None:
        super().__init__(Qt.Orientation.Horizontal)
        self.setRange(0, 1000)
        self.setFixedHeight(20)
        self.setStyleSheet(_SEEK_IDLE)

    def enterEvent(self, event: object) -> None:  # type: ignore[override]
        self.setStyleSheet(_SEEK_HOVER)
        super().enterEvent(event)  # type: ignore[arg-type]

    def leaveEvent(self, event: object) -> None:  # type: ignore[override]
        self.setStyleSheet(_SEEK_IDLE)
        super().leaveEvent(event)  # type: ignore[arg-type]


class MediaPlayerWidget(QWidget):
    """Pure control-surface — all playback logic lives in ARQYVMediaEngine."""

    def __init__(self, config: AppConfig, events: EventBus, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self.events = events
        self._engine = None
        self._rate = 1.0
        self._build_ui()

    # ── Build ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Hidden video widget — preview panel renders visuals; this is for Qt engine wiring
        self._video = QVideoWidget()
        self._video.setFixedSize(1, 1)
        self._video.hide()

        self._subtitle = SubtitleOverlay(self._video)

        # ── Seek bar ───────────────────────────────────────────────────────
        seek_container = QWidget()
        seek_container.setFixedHeight(20)
        seek_container.setStyleSheet(f"background: {P['bg0']};")
        sl = QHBoxLayout(seek_container)
        sl.setContentsMargins(0, 0, 0, 0)

        self._seek = _SeekSlider()
        self._seek.sliderMoved.connect(self._on_seek)
        sl.addWidget(self._seek)
        root.addWidget(seek_container)

        # ── Control bar ────────────────────────────────────────────────────
        bar_widget = QWidget()
        bar_widget.setFixedHeight(68)
        bar_widget.setStyleSheet(f"""
            background: {P['bg1']};
            border-top: 1px solid {P['border']};
        """)
        bar = QHBoxLayout(bar_widget)
        bar.setContentsMargins(16, 0, 16, 0)
        bar.setSpacing(4)

        # ── Transport controls ─────────────────────────────────────────────
        self._prev_btn = self._tbtn("⏮", "Previous",    self._on_prev)
        self._rew_btn  = self._tbtn("⏪", "−10 s",       self._on_rewind)

        self._play_btn = QPushButton("▶")
        self._play_btn.setFixedSize(QSize(_PLAY_SIZE, _PLAY_SIZE))
        self._play_btn.setToolTip("Play / Pause  (Space)")
        self._play_btn.clicked.connect(self._on_play_pause)
        self._play_btn.setStyleSheet(f"""
            QPushButton {{
                background: {P['cyan']};
                border: none;
                border-radius: {_PLAY_SIZE // 2}px;
                color: {P['bg0']};
                font-size: 16px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: #22d8ff;
            }}
            QPushButton:pressed {{
                background: {P['cyan2']};
            }}
        """)

        self._fwd_btn  = self._tbtn("⏩", "+10 s",       self._on_forward)
        self._next_btn = self._tbtn("⏭", "Next",         self._on_next)

        bar.addWidget(self._prev_btn)
        bar.addWidget(self._rew_btn)
        bar.addSpacing(6)
        bar.addWidget(self._play_btn)
        bar.addSpacing(6)
        bar.addWidget(self._fwd_btn)
        bar.addWidget(self._next_btn)
        bar.addSpacing(14)

        # Time display
        self._time_lbl = QLabel("0:00 / 0:00")
        self._time_lbl.setStyleSheet(f"""
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            color: {P['text2']};
            letter-spacing: 0.04em;
            min-width: 110px;
        """)
        bar.addWidget(self._time_lbl)
        bar.addSpacing(8)

        # Format pill
        self._fmt_lbl = QLabel("")
        self._fmt_lbl.setStyleSheet(f"""
            background: {P['bg3']};
            color: {P['text3']};
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.08em;
            padding: 2px 8px;
            border-radius: 10px;
        """)
        bar.addWidget(self._fmt_lbl)

        bar.addStretch()
        bar.addWidget(_vline())
        bar.addSpacing(8)

        # Shuffle / repeat / CC
        self._shuf_btn   = self._sbtn("⇀",  "Shuffle",        self._on_shuffle)
        self._repeat_btn = self._sbtn("↺",  "Repeat",         self._on_repeat)
        self._sub_btn    = self._sbtn("CC", "Load Subtitles",  self._on_load_subs)
        bar.addWidget(self._shuf_btn)
        bar.addWidget(self._repeat_btn)
        bar.addWidget(self._sub_btn)

        bar.addSpacing(8)
        bar.addWidget(_vline())
        bar.addSpacing(8)

        # Volume icon + slider
        self._vol_ico = QLabel("🔊")
        self._vol_ico.setStyleSheet(f"color: {P['text2']}; font-size: 12px;")
        self._vol = QSlider(Qt.Orientation.Horizontal)
        self._vol.setRange(0, 100)
        self._vol.setValue(80)
        self._vol.setFixedWidth(80)
        self._vol.setFixedHeight(18)
        self._vol.setToolTip("Volume")
        self._vol.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 3px; background: {P['border2']}; border-radius: 2px;
            }}
            QSlider::sub-page:horizontal {{
                background: {P['text3']}; border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {P['text2']};
                border-radius: 5px;
                width: 10px; height: 10px; margin: -4px 0;
            }}
            QSlider::handle:horizontal:hover {{
                background: {P['text']};
            }}
        """)
        self._vol.valueChanged.connect(self._on_volume)
        bar.addWidget(self._vol_ico)
        bar.addWidget(self._vol)

        bar.addSpacing(8)
        bar.addWidget(_vline())
        bar.addSpacing(8)

        # Playback speed
        self._spd_dn  = self._sbtn("−", "Slower", self._on_speed_dn)
        self._spd_lbl = QLabel("1×")
        self._spd_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._spd_lbl.setFixedWidth(32)
        self._spd_lbl.setStyleSheet(f"color: {P['text']}; font-size: 12px; font-weight: 600;")
        self._spd_up  = self._sbtn("+", "Faster", self._on_speed_up)

        bar.addWidget(self._spd_dn)
        bar.addWidget(self._spd_lbl)
        bar.addWidget(self._spd_up)

        root.addWidget(bar_widget)

    def _tbtn(self, text: str, tip: str, slot: object) -> QPushButton:
        b = QPushButton(text)
        b.setFixedSize(QSize(_BTN_MAIN, _BTN_MAIN))
        b.setToolTip(tip)
        b.clicked.connect(slot)  # type: ignore[arg-type]
        b.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {P['text2']};
                font-size: 15px;
                border-radius: 6px;
            }}
            QPushButton:hover {{ color: {P['text']}; background: {P['bg3']}; border-radius: 8px; }}
            QPushButton:pressed {{ color: {P['cyan']}; }}
        """)
        return b

    def _sbtn(self, text: str, tip: str, slot: object) -> QPushButton:
        b = QPushButton(text)
        b.setFixedSize(QSize(_BTN_SEC, _BTN_SEC))
        b.setCheckable(True)
        b.setToolTip(tip)
        b.clicked.connect(slot)  # type: ignore[arg-type]
        b.setObjectName("ghost")
        return b

    # ── Engine wiring ──────────────────────────────────────────────────────

    def init_engine(self):
        from arqyv.engine.core import ARQYVMediaEngine
        self._engine = ARQYVMediaEngine(config=self.config, video_widget=self._video, parent=self)
        self._engine.attach_subtitle_overlay(self._subtitle)
        self._engine.state_changed.connect(self._on_state)
        self._engine.position_changed.connect(self._on_position)
        self._engine.format_detected.connect(self._on_format)
        self._engine.error.connect(self._on_error)
        self._engine.set_volume(self._vol.value())
        return self._engine

    @property
    def engine(self):
        return self._engine

    def open_file(self, path: str | Path) -> None:
        if self._engine:
            self._engine.open(path)

    def open_playlist(self, paths: list[Path], start: int = 0) -> None:
        if self._engine:
            self._engine.open_playlist(paths, start)

    # ── Control slots ──────────────────────────────────────────────────────

    @pyqtSlot()
    def _on_play_pause(self) -> None:
        if self._engine: self._engine.toggle()

    @pyqtSlot()
    def _on_prev(self) -> None:
        if self._engine: self._engine.play_previous()

    @pyqtSlot()
    def _on_next(self) -> None:
        if self._engine: self._engine.play_next()

    @pyqtSlot()
    def _on_rewind(self) -> None:
        if self._engine:
            self._engine.seek_ms(max(0, self._engine.position_ms - 10_000))

    @pyqtSlot()
    def _on_forward(self) -> None:
        if self._engine:
            self._engine.seek_ms(self._engine.position_ms + 10_000)

    @pyqtSlot(int)
    def _on_seek(self, value: int) -> None:
        if self._engine: self._engine.seek(value / 1000.0)

    @pyqtSlot(int)
    def _on_volume(self, value: int) -> None:
        if self._engine: self._engine.set_volume(value)
        self._vol_ico.setText("🔇" if value == 0 else ("🔉" if value < 50 else "🔊"))

    @pyqtSlot()
    def _on_speed_up(self) -> None:
        self._rate = round(min(3.0, self._rate + 0.25), 2)
        self._apply_rate()

    @pyqtSlot()
    def _on_speed_dn(self) -> None:
        self._rate = round(max(0.25, self._rate - 0.25), 2)
        self._apply_rate()

    def _apply_rate(self) -> None:
        if self._engine: self._engine.set_rate(self._rate)
        self._spd_lbl.setText(f"{self._rate:g}×")
        color = P["cyan"] if self._rate != 1.0 else P["text"]
        self._spd_lbl.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")

    @pyqtSlot()
    def _on_shuffle(self) -> None:
        if not self._engine: return
        on = self._engine.playlist.toggle_shuffle()
        self._shuf_btn.setChecked(on)

    @pyqtSlot()
    def _on_repeat(self) -> None:
        if not self._engine: return
        from arqyv.engine.playlist import RepeatMode
        mode = self._engine.playlist.cycle_repeat()
        labels = {RepeatMode.NONE: "↺", RepeatMode.ONE: "↻¹", RepeatMode.ALL: "↻"}
        self._repeat_btn.setText(labels[mode])
        self._repeat_btn.setChecked(mode != RepeatMode.NONE)

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
        if state == "playing":
            self._play_btn.setText("⏸")
            self._play_btn.setStyleSheet(self._play_btn.styleSheet().replace(
                P["cyan"], P["cyan2"]
            ))
        else:
            self._play_btn.setText("▶")
            self._play_btn.setStyleSheet(self._play_btn.styleSheet().replace(
                P["cyan2"], P["cyan"]
            ))
        self.events.emit(Events.PLAYER_STATE_CHANGED, state=state)

    @pyqtSlot(int, int)
    def _on_position(self, position_ms: int, duration_ms: int) -> None:
        if duration_ms > 0:
            self._seek.blockSignals(True)
            self._seek.setValue(int(position_ms / duration_ms * 1000))
            self._seek.blockSignals(False)
        self._time_lbl.setText(f"{_fmt(position_ms)}  /  {_fmt(duration_ms)}")
        self.events.emit(Events.PLAYER_POSITION_CHANGED, position=position_ms, length_ms=duration_ms)

    @pyqtSlot(str)
    def _on_format(self, fmt_str: str) -> None:
        short = fmt_str.split("(")[0].strip().upper()
        self._fmt_lbl.setText(short)
        self._fmt_lbl.setToolTip(fmt_str)

    @pyqtSlot(str)
    def _on_error(self, msg: str) -> None:
        log.error("Player error: %s", msg)
        self._fmt_lbl.setText("ERR")
        self._fmt_lbl.setToolTip(msg)
