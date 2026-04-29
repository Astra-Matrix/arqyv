"""Player backend abstraction.

Selects the best available playback engine at runtime:

  Tier 1 – VLC (python-vlc + libvlc)
    → Maximum codec/format coverage (H.265, AV1, MKV, AC3, DTS, …)
    → Auto-detected from system VLC installation – zero user interaction.

  Tier 2 – Qt Multimedia (QMediaPlayer)
    → Zero external dependency, ships with PyQt6.
    → Uses platform codecs: WMF on Windows, AVFoundation on macOS,
      GStreamer on Linux → excellent coverage for common formats.
    → Works immediately on every supported OS with no installation step.

The widget layer (media_player.py) talks only to the PlayerBackend
protocol – it never imports vlc directly.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

log = logging.getLogger(__name__)


@runtime_checkable
class PlayerBackend(Protocol):
    """Minimal interface any backend must satisfy."""

    def open(self, path: str) -> None: ...
    def play(self) -> None: ...
    def pause(self) -> None: ...
    def stop(self) -> None: ...
    def toggle(self) -> None: ...
    def seek(self, position_fraction: float) -> None: ...
    def set_volume(self, volume: int) -> None: ...   # 0–100
    def set_rate(self, rate: float) -> None: ...
    def get_position(self) -> float: ...             # 0.0–1.0
    def get_length_ms(self) -> int: ...
    def is_playing(self) -> bool: ...
    def attach_video_surface(self, widget: Any) -> None: ...


def create_backend(video_widget: Any) -> "PlayerBackend":
    """Factory: return the best available backend, log which tier is active."""
    from arqyv.media.vlc_setup import setup_vlc

    if setup_vlc():
        try:
            from arqyv.media._vlc_backend import VLCBackend
            backend = VLCBackend(video_widget)
            log.info("Media backend: VLC (extended codec support active)")
            return backend
        except Exception:
            log.warning("VLC found but backend init failed; falling back to Qt Multimedia.", exc_info=True)

    from arqyv.media._qt_backend import QtBackend
    backend = QtBackend(video_widget)
    log.info("Media backend: Qt Multimedia (platform codecs)")
    return backend
