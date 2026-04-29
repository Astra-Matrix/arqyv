"""Qt Multimedia backend (Tier 2 – zero external dependencies).

Uses QMediaPlayer + QVideoWidget + QAudioOutput from PyQt6.QtMultimedia.
Codec coverage depends on platform:
  Windows → Windows Media Foundation  (H.264, H.265, VP8, MP3, AAC, FLAC …)
  macOS   → AVFoundation              (H.264, H.265, ProRes, AAC, ALAC …)
  Linux   → GStreamer (if installed)  (virtually everything with gst-plugins)
"""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget

log = logging.getLogger(__name__)


class QtBackend:
    def __init__(self, video_widget: QVideoWidget) -> None:
        self._player = QMediaPlayer()
        self._audio = QAudioOutput()
        self._player.setAudioOutput(self._audio)
        self._player.setVideoOutput(video_widget)
        self._audio.setVolume(0.8)  # 80% default

    # ── PlayerBackend protocol ─────────────────────────────────────────────

    def open(self, path: str) -> None:
        self._player.setSource(QUrl.fromLocalFile(path))
        self._player.play()

    def play(self) -> None:
        self._player.play()

    def pause(self) -> None:
        self._player.pause()

    def stop(self) -> None:
        self._player.stop()
        self._player.setPosition(0)

    def toggle(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def seek(self, position_fraction: float) -> None:
        length = self._player.duration()
        if length > 0:
            self._player.setPosition(int(position_fraction * length))

    def set_volume(self, volume: int) -> None:
        self._audio.setVolume(volume / 100.0)

    def set_rate(self, rate: float) -> None:
        self._player.setPlaybackRate(rate)

    def get_position(self) -> float:
        length = self._player.duration()
        if length <= 0:
            return 0.0
        return self._player.position() / length

    def get_length_ms(self) -> int:
        return self._player.duration()

    def is_playing(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def attach_video_surface(self, widget: Any) -> None:
        self._player.setVideoOutput(widget)

    # ── Qt signal access (for the widget to connect UI slots) ─────────────

    @property
    def qt_player(self) -> QMediaPlayer:
        return self._player
