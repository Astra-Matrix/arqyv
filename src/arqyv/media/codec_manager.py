"""Codec and format support manager.

Provides a runtime check of what formats are actually playable
on the current system via VLC, and exposes the full supported list.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class CodecInfo:
    name: str
    extension: str
    requires_vlc: bool = False


# Formats that play natively in browsers/Qt without VLC:
NATIVE_FORMATS = {
    ".mp4", ".webm", ".ogg", ".mp3", ".wav",
}

# Formats that need libVLC:
VLC_FORMATS = {
    ".mkv", ".avi", ".mov", ".wmv", ".flv", ".m4v", ".3gp", ".ts", ".mts",
    ".m2ts", ".ogv", ".aac", ".flac", ".opus", ".m4a", ".wma", ".aiff",
    ".ape", ".mka", ".ac3", ".dts",
}


class CodecManager:
    def __init__(self) -> None:
        self._vlc_available: bool | None = None
        self._ffmpeg_available: bool | None = None

    def vlc_available(self) -> bool:
        if self._vlc_available is None:
            try:
                import vlc  # type: ignore[import]
                self._vlc_available = True
            except ImportError:
                self._vlc_available = False
        return self._vlc_available

    def ffmpeg_available(self) -> bool:
        if self._ffmpeg_available is None:
            self._ffmpeg_available = shutil.which("ffmpeg") is not None
        return self._ffmpeg_available

    def can_play(self, extension: str) -> bool:
        ext = extension.lower()
        if ext in NATIVE_FORMATS:
            return True
        if ext in VLC_FORMATS:
            return self.vlc_available()
        return self.vlc_available()  # VLC handles virtually everything

    def get_all_supported(self) -> set[str]:
        supported = set(NATIVE_FORMATS)
        if self.vlc_available():
            supported |= VLC_FORMATS
        return supported

    def report(self) -> dict[str, bool]:
        return {
            "vlc": self.vlc_available(),
            "ffmpeg": self.ffmpeg_available(),
            "formats": len(self.get_all_supported()),
        }
