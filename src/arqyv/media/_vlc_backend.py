"""VLC backend (Tier 1 – maximum codec coverage).

Loaded only when libvlc is present on the system (auto-detected by
vlc_setup.setup_vlc() before this module is imported).

Supports everything VLC does: H.265, AV1, VP9, MKV, TS, BDMV, AC3,
DTS, TrueHD, FLAC, APE, MIDI, and hundreds more.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

log = logging.getLogger(__name__)


class VLCBackend:
    def __init__(self, video_widget: Any) -> None:
        import vlc  # type: ignore[import]

        args = ["--no-xlib", "--quiet", "--no-video-title-show"]
        self._instance = vlc.Instance(*args)
        self._player = self._instance.media_player_new()
        self._attach_surface(video_widget)

    def _attach_surface(self, widget: Any) -> None:
        win_id = int(widget.winId())
        if sys.platform == "win32":
            self._player.set_hwnd(win_id)
        elif sys.platform == "darwin":
            self._player.set_nsobject(win_id)
        else:
            self._player.set_xwindow(win_id)

    # ── PlayerBackend protocol ─────────────────────────────────────────────

    def open(self, path: str) -> None:
        media = self._instance.media_new(path)
        self._player.set_media(media)
        self._player.play()

    def play(self) -> None:
        self._player.play()

    def pause(self) -> None:
        self._player.pause()

    def stop(self) -> None:
        self._player.stop()

    def toggle(self) -> None:
        if self._player.is_playing():
            self._player.pause()
        else:
            self._player.play()

    def seek(self, position_fraction: float) -> None:
        self._player.set_position(float(position_fraction))

    def set_volume(self, volume: int) -> None:
        self._player.audio_set_volume(int(volume))

    def set_rate(self, rate: float) -> None:
        self._player.set_rate(float(rate))

    def get_position(self) -> float:
        return float(self._player.get_position())

    def get_length_ms(self) -> int:
        return int(self._player.get_length())

    def is_playing(self) -> bool:
        return bool(self._player.is_playing())

    def attach_video_surface(self, widget: Any) -> None:
        self._attach_surface(widget)
