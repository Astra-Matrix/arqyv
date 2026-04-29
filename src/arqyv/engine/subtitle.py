"""Pure-Python subtitle engine.

Parses SRT, WebVTT, and ASS/SSA subtitle files with zero external
dependencies.  The SubtitleOverlay widget renders cues as a QPainter
overlay directly on the video surface.

Supported formats detected automatically by content, not extension:
  SRT  — SubRip Text        (.srt)
  VTT  — Web Video Text     (.vtt)
  ASS  — Advanced SubStation (.ass, .ssa)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget

log = logging.getLogger(__name__)


# ── Data model ─────────────────────────────────────────────────────────────

@dataclass
class Cue:
    start_ms: int
    end_ms: int
    text: str       # plain text, HTML stripped

    def active_at(self, position_ms: int) -> bool:
        return self.start_ms <= position_ms < self.end_ms


# ── Parsers ────────────────────────────────────────────────────────────────

_TIMECODE_RE = re.compile(
    r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})"
)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_ASS_EVENT_RE = re.compile(
    r"Dialogue:\s*\d+,(\d+:\d+:\d+\.\d+),(\d+:\d+:\d+\.\d+),[^,]*,[^,]*,\d+,\d+,\d+,[^,]*,(.*)"
)


def _tc_to_ms(h: str, m: str, s: str, ms: str) -> int:
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)


def _strip_html(text: str) -> str:
    return _HTML_TAG_RE.sub("", text).strip()


def parse_srt(text: str) -> list[Cue]:
    cues: list[Cue] = []
    blocks = re.split(r"\n\s*\n", text.strip())
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        # Find timecode line
        tc_line = next((l for l in lines if "-->" in l), None)
        if not tc_line:
            continue
        parts = tc_line.split("-->")
        if len(parts) != 2:
            continue
        s_m = _TIMECODE_RE.search(parts[0])
        e_m = _TIMECODE_RE.search(parts[1])
        if not s_m or not e_m:
            continue
        start = _tc_to_ms(*s_m.groups())
        end   = _tc_to_ms(*e_m.groups())
        tc_idx = lines.index(tc_line)
        body = "\n".join(lines[tc_idx + 1:])
        cues.append(Cue(start, end, _strip_html(body)))
    return cues


def parse_vtt(text: str) -> list[Cue]:
    # VTT is nearly identical to SRT but uses "." as ms separator
    cleaned = re.sub(r"^WEBVTT.*\n", "", text, flags=re.MULTILINE)
    # Convert "." ms separator to "," for shared SRT parser
    cleaned = re.sub(r"(\d{2}:\d{2}:\d{2})\.(\d{3})", r"\1,\2", cleaned)
    return parse_srt(cleaned)


def _ass_tc_to_ms(tc: str) -> int:
    # ASS format: H:MM:SS.cc  (centiseconds)
    m = re.match(r"(\d+):(\d{2}):(\d{2})\.(\d{2})", tc)
    if not m:
        return 0
    h, mi, s, cs = m.groups()
    return (int(h) * 3600 + int(mi) * 60 + int(s)) * 1000 + int(cs) * 10


def parse_ass(text: str) -> list[Cue]:
    cues: list[Cue] = []
    for line in text.splitlines():
        m = _ASS_EVENT_RE.match(line)
        if not m:
            continue
        start_tc, end_tc, body = m.groups()
        # Strip ASS override tags like {\an8}, {\i1}
        body = re.sub(r"\{[^}]*\}", "", body).replace(r"\N", "\n").strip()
        cues.append(Cue(_ass_tc_to_ms(start_tc), _ass_tc_to_ms(end_tc), body))
    return cues


def load_subtitle_file(path: Path) -> list[Cue]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    text_stripped = text.lstrip("\ufeff")  # BOM

    if text_stripped.startswith("WEBVTT"):
        cues = parse_vtt(text_stripped)
        log.debug("Loaded VTT: %d cues from %s", len(cues), path.name)
    elif re.search(r"^\[Script Info\]", text_stripped, re.MULTILINE):
        cues = parse_ass(text_stripped)
        log.debug("Loaded ASS: %d cues from %s", len(cues), path.name)
    else:
        cues = parse_srt(text_stripped)
        log.debug("Loaded SRT: %d cues from %s", len(cues), path.name)

    return sorted(cues, key=lambda c: c.start_ms)


def find_subtitle_for(video_path: Path) -> Path | None:
    """Auto-detect a subtitle file next to the video (same stem)."""
    for ext in (".srt", ".vtt", ".ass", ".ssa"):
        candidate = video_path.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None


# ── Qt overlay widget ──────────────────────────────────────────────────────

class SubtitleOverlay(QWidget):
    """Transparent widget rendered on top of the video surface.

    Call set_position_ms() every ~100 ms from the player timer.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self._cues: list[Cue] = []
        self._current_text = ""

        self._font = QFont("Arial", 18, QFont.Weight.Bold)
        self._text_color = QColor(255, 255, 255)
        self._outline_color = QColor(0, 0, 0)

    def load_cues(self, cues: list[Cue]) -> None:
        self._cues = cues
        self._current_text = ""
        self.update()

    def set_position_ms(self, position_ms: int) -> None:
        text = ""
        for cue in self._cues:
            if cue.active_at(position_ms):
                text = cue.text
                break
        if text != self._current_text:
            self._current_text = text
            self.update()

    def paintEvent(self, event: object) -> None:  # type: ignore[override]
        if not self._current_text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self._font)

        fm = painter.fontMetrics()
        lines = self._current_text.split("\n")
        line_h = fm.height() + 4
        total_h = line_h * len(lines)
        y_base = self.height() - total_h - 24  # 24px from bottom

        for i, line in enumerate(lines):
            text_w = fm.horizontalAdvance(line)
            x = (self.width() - text_w) // 2
            y = y_base + i * line_h + fm.ascent()

            # Outline pass (4 directions)
            painter.setPen(QPen(self._outline_color, 3))
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                painter.drawText(x + dx, y + dy, line)

            # Text pass
            painter.setPen(self._text_color)
            painter.drawText(x, y, line)

        painter.end()
