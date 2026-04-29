"""Transcoder utility using ffmpeg-python.

Provides format conversion, audio extraction, and clip trimming.
All operations run in a subprocess – never blocks the UI.
"""

from __future__ import annotations

import logging
import subprocess
import shutil
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass
class TranscodeOptions:
    output_format: str = "mp4"
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    crf: int = 23
    audio_bitrate: str = "192k"
    start_time: float | None = None
    end_time: float | None = None


class Transcoder:
    """Thin wrapper around ffmpeg CLI for format conversion."""

    @staticmethod
    def is_available() -> bool:
        return shutil.which("ffmpeg") is not None

    @staticmethod
    def transcode(
        source: Path,
        dest: Path,
        opts: TranscodeOptions | None = None,
        on_progress: "callable | None" = None,
    ) -> bool:
        if not Transcoder.is_available():
            log.error("ffmpeg not found in PATH.")
            return False

        opts = opts or TranscodeOptions()
        cmd = ["ffmpeg", "-y", "-i", str(source)]

        if opts.start_time is not None:
            cmd += ["-ss", str(opts.start_time)]
        if opts.end_time is not None:
            cmd += ["-to", str(opts.end_time)]

        cmd += [
            "-c:v", opts.video_codec,
            "-crf", str(opts.crf),
            "-c:a", opts.audio_codec,
            "-b:a", opts.audio_bitrate,
            "-movflags", "+faststart",
            str(dest),
        ]

        log.info("Transcoding: %s → %s", source.name, dest.name)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,
            )
            if result.returncode != 0:
                log.error("ffmpeg error:\n%s", result.stderr)
                return False
            log.info("Transcoded successfully: %s", dest)
            return True
        except subprocess.TimeoutExpired:
            log.error("Transcode timed out for %s", source)
            return False

    @staticmethod
    def extract_audio(source: Path, dest: Path, format: str = "mp3") -> bool:
        """Extract audio track from video file."""
        if not Transcoder.is_available():
            return False
        cmd = [
            "ffmpeg", "-y", "-i", str(source),
            "-vn", "-c:a", "libmp3lame", "-q:a", "2",
            str(dest),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
