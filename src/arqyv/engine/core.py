"""ARQYVMediaEngine — the authoritative custom media engine.

This is the single class that owns all media playback state. The UI
widgets talk only to this object; they never import Qt Multimedia or
VLC directly.

Architecture:

  ARQYVMediaEngine
    ├─ FormatDetector     → magic-byte format identification
    ├─ Playlist           → track queue, shuffle, repeat, smart resume
    ├─ SubtitleEngine     → auto-load + parse SRT/VTT/ASS next to file
    ├─ AudioDSP           → EQ settings, peak metering
    └─ PlayerBackend      → Qt Multimedia (Tier 2) or VLC (Tier 1)
                            selected automatically at runtime

No external programs required. Qt Multimedia is bundled with PyQt6
and uses OS-native codecs (WMF / AVFoundation / GStreamer).
VLC is an optional upgrade, auto-detected from any system installation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal

from arqyv.engine.audio_dsp import AudioDSPSettings, EQPreset, PeakMeter
from arqyv.engine.format import MediaFormat, MediaKind, detect
from arqyv.engine.playlist import Playlist, RepeatMode
from arqyv.engine.subtitle import SubtitleOverlay, find_subtitle_for, load_subtitle_file
from arqyv.config import AppConfig

log = logging.getLogger(__name__)


class ARQYVMediaEngine(QObject):
    """Unified media engine — one instance per application window.

    Signals
    -------
    state_changed(str)          → "playing" | "paused" | "stopped" | "ended"
    position_changed(int, int)  → (position_ms, duration_ms)
    track_changed(str)          → absolute path of new track
    error(str)                  → human-readable error message
    subtitle_changed(str)       → current subtitle text ("" = none)
    format_detected(str)        → "MP4 (H.264)" etc.
    """

    state_changed    = pyqtSignal(str)
    position_changed = pyqtSignal(int, int)
    track_changed    = pyqtSignal(str)
    error            = pyqtSignal(str)
    subtitle_changed = pyqtSignal(str)
    format_detected  = pyqtSignal(str)

    def __init__(self, config: AppConfig, video_widget: Any, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._config = config
        self._video_widget = video_widget

        self.playlist = Playlist(config.data_dir)
        self.dsp = AudioDSPSettings()
        self.meter = PeakMeter()

        self._backend: Any = None
        self._subtitle_overlay: SubtitleOverlay | None = None
        self._current_format: MediaFormat | None = None
        self._position_ms = 0
        self._duration_ms = 0

        self._init_backend()

    # ── Backend bootstrap ──────────────────────────────────────────────────

    def _init_backend(self) -> None:
        from arqyv.media.player import create_backend
        try:
            self._backend = create_backend(self._video_widget)
            # Wire Qt Multimedia signals when available
            if hasattr(self._backend, "qt_player"):
                qp = self._backend.qt_player
                qp.playbackStateChanged.connect(self._on_qt_state)
                qp.positionChanged.connect(self._on_qt_position)
                qp.durationChanged.connect(self._on_qt_duration)
                qp.errorOccurred.connect(self._on_qt_error)
                qp.mediaStatusChanged.connect(self._on_qt_media_status)
            log.info("ARQYVMediaEngine ready — backend: %s", type(self._backend).__name__)
        except Exception:
            log.exception("Media backend failed to initialize.")

    # ── Subtitle overlay ───────────────────────────────────────────────────

    def attach_subtitle_overlay(self, overlay: SubtitleOverlay) -> None:
        self._subtitle_overlay = overlay

    def _load_subtitles(self, video_path: Path) -> None:
        if self._subtitle_overlay is None:
            return
        sub_path = find_subtitle_for(video_path)
        if sub_path:
            cues = load_subtitle_file(sub_path)
            self._subtitle_overlay.load_cues(cues)
            log.info("Subtitles loaded: %s (%d cues)", sub_path.name, len(cues))
        else:
            self._subtitle_overlay.load_cues([])

    # ── Playback API ───────────────────────────────────────────────────────

    def open(self, path: str | Path, play_immediately: bool = True) -> None:
        """Open a file. Detects format, resumes position, loads subtitles."""
        p = Path(path)
        if not p.exists():
            self.error.emit(f"File not found: {p.name}")
            return

        fmt = detect(p)
        self._current_format = fmt
        self.format_detected.emit(f"{fmt.name} ({fmt.mime})")

        if fmt.kind not in (MediaKind.VIDEO, MediaKind.AUDIO):
            self.error.emit(f"Not a media file: {p.name}")
            return

        # Smart resume
        resume_pos = self.playlist.get_resume_position(p)
        if resume_pos > 10_000:
            log.info("Resuming %s at %d ms", p.name, resume_pos)

        if self._backend:
            self._backend.open(str(p))
            if resume_pos > 10_000:
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, lambda: self._backend.seek(resume_pos / max(self._duration_ms, 1)))

        if fmt.kind == MediaKind.VIDEO:
            self._load_subtitles(p)

        self.track_changed.emit(str(p))
        if play_immediately:
            self.state_changed.emit("playing")

    def play(self) -> None:
        if self._backend:
            self._backend.play()
            self.state_changed.emit("playing")

    def pause(self) -> None:
        if self._backend:
            self._backend.pause()
            self._save_position()
            self.state_changed.emit("paused")

    def stop(self) -> None:
        if self._backend:
            self._save_position()
            self._backend.stop()
            self._position_ms = 0
            self.state_changed.emit("stopped")
            self.position_changed.emit(0, self._duration_ms)

    def toggle(self) -> None:
        if self._backend and self._backend.is_playing():
            self.pause()
        else:
            self.play()

    def seek(self, fraction: float) -> None:
        if self._backend:
            self._backend.seek(fraction)

    def seek_ms(self, ms: int) -> None:
        if self._duration_ms > 0:
            self.seek(ms / self._duration_ms)

    def set_volume(self, vol: int) -> None:
        self.dsp.volume = vol / 100.0
        if self._backend:
            self._backend.set_volume(vol)

    def set_rate(self, rate: float) -> None:
        if self._backend:
            self._backend.set_rate(rate)

    # ── Playlist controls ──────────────────────────────────────────────────

    def play_next(self) -> None:
        nxt = self.playlist.next()
        if nxt:
            self.open(nxt)
        else:
            self.stop()
            self.state_changed.emit("ended")

    def play_previous(self) -> None:
        # If more than 5 s in → restart current; otherwise go to previous
        if self._position_ms > 5000:
            self.seek(0.0)
        else:
            prev = self.playlist.previous()
            if prev:
                self.open(prev)

    def open_playlist(self, paths: list[Path], start: int = 0) -> None:
        self.playlist.set_tracks(paths, start)
        current = self.playlist.current
        if current:
            self.open(current)

    # ── State queries ──────────────────────────────────────────────────────

    @property
    def is_playing(self) -> bool:
        return bool(self._backend and self._backend.is_playing())

    @property
    def position_ms(self) -> int:
        return self._position_ms

    @property
    def duration_ms(self) -> int:
        return self._duration_ms

    @property
    def current_format(self) -> MediaFormat | None:
        return self._current_format

    # ── Internal ───────────────────────────────────────────────────────────

    def _save_position(self) -> None:
        current = self.playlist.current
        if current and self._position_ms > 0:
            self.playlist.save_position(current, self._position_ms)

    def _on_qt_state(self, state: Any) -> None:
        from PyQt6.QtMultimedia import QMediaPlayer
        mapping = {
            QMediaPlayer.PlaybackState.PlayingState: "playing",
            QMediaPlayer.PlaybackState.PausedState:  "paused",
            QMediaPlayer.PlaybackState.StoppedState: "stopped",
        }
        s = mapping.get(state, "stopped")
        self.state_changed.emit(s)
        if s == "stopped":
            self._save_position()

    def _on_qt_position(self, ms: int) -> None:
        self._position_ms = ms
        self.position_changed.emit(ms, self._duration_ms)
        if self._subtitle_overlay:
            self._subtitle_overlay.set_position_ms(ms)

    def _on_qt_duration(self, ms: int) -> None:
        self._duration_ms = ms
        self.position_changed.emit(self._position_ms, ms)

    def _on_qt_error(self, error: Any, msg: str) -> None:
        log.error("Qt Multimedia error: %s", msg)
        self.error.emit(msg)

    def _on_qt_media_status(self, status: Any) -> None:
        from PyQt6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._save_position()
            self.playlist.clear_resume(self.playlist.current or Path())
            self.play_next()
