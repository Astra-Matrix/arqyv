"""
ARQYV Particle Overlay — mouse-reactive sparkles and shimmers.

A fully transparent child widget that sits on top of the entire window.
Mouse movement (fed from MainWindow.mouseMoveEvent) spawns glowing
particle sparks that drift upward, fade, and disappear.

Physics:
  • Each particle has position, velocity, radius, alpha, and an RGB colour.
  • Every tick (~60 fps): position += velocity, vy += gravity, alpha -= decay.
  • Dead particles (alpha < 0.01) are culled.

Rendering:
  • Each particle → QRadialGradient circle (centre bright, edge transparent).
  • Star-shaped cross drawn for ~30 % of particles at full radius.
  • No background is painted — the widget is purely additive on top.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List

from PyQt6.QtCore import QEvent, QPointF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget


# ── Colour palette ─────────────────────────────────────────────────────────────

_PALETTE: list[tuple[int, int, int]] = [
    (0,   212, 255),  # electric cyan
    (180, 230, 255),  # ice blue
    (124,  58, 237),  # violet
    (0,   160, 200),  # deep teal
    (255, 255, 255),  # pure white (rare)
]

_WHITE_CHANCE = 0.08   # probability of a white spark
_STAR_CHANCE  = 0.28   # probability of a star-shaped spark vs soft dot


# ── Data ───────────────────────────────────────────────────────────────────────

@dataclass(slots=True)
class _Spark:
    x:     float
    y:     float
    vx:    float
    vy:    float
    r:     float          # glow radius (pixels)
    a:     float          # alpha  0 → 1
    decay: float          # alpha lost per frame
    cr:    int
    cg:    int
    cb:    int
    star:  bool


# ── Overlay widget ─────────────────────────────────────────────────────────────

class ParticleOverlay(QWidget):
    """
    Transparent, non-interactive overlay that renders sparkle particles.

    Usage
    -----
    overlay = ParticleOverlay(main_window)
    # Then in main_window.mouseMoveEvent:
    overlay.feed(event.position().x(), event.position().y())
    """

    _MAX_SPARKS = 200     # hard cap — keeps GPU/CPU lean
    _TICK_MS    = 16      # ~60 fps

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        # Pass all mouse/keyboard events through to whatever is underneath
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        # Don't let Qt fill our background — we paint only the particles
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.resize(parent.size())
        self.raise_()

        self._sparks: List[_Spark] = []

        self._timer = QTimer(self)
        self._timer.setInterval(self._TICK_MS)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        # Resize to match parent whenever parent resizes
        parent.installEventFilter(self)

    # ── Public API ─────────────────────────────────────────────────────────────

    def feed(self, x: float, y: float, burst: int = 0) -> None:
        """
        Spawn particles at (x, y).

        Parameters
        ----------
        x, y  : window-relative coordinates
        burst : extra particles (0 = normal move, >0 = click/burst event)
        """
        n = random.randint(2, 4) + burst
        for _ in range(n):
            angle  = random.uniform(0, math.tau)
            speed  = random.uniform(0.4, 2.4)
            use_white = random.random() < _WHITE_CHANCE
            if use_white:
                cr, cg, cb = 255, 255, 255
            else:
                cr, cg, cb = random.choice(_PALETTE)

            self._sparks.append(_Spark(
                x     = x + random.gauss(0, 7),
                y     = y + random.gauss(0, 7),
                vx    = math.cos(angle) * speed,
                vy    = math.sin(angle) * speed - 1.0,   # bias upward
                r     = random.uniform(2.5, 6.5),
                a     = random.uniform(0.55, 0.95),
                decay = random.uniform(0.016, 0.034),
                cr    = cr, cg = cg, cb = cb,
                star  = random.random() < _STAR_CHANCE,
            ))

        # Trim to cap
        if len(self._sparks) > self._MAX_SPARKS:
            self._sparks = self._sparks[-self._MAX_SPARKS:]

    # ── Physics tick ───────────────────────────────────────────────────────────

    def _tick(self) -> None:
        alive: List[_Spark] = []
        for s in self._sparks:
            s.x  += s.vx
            s.y  += s.vy
            s.vy += 0.055       # gentle gravity
            s.vx *= 0.98        # horizontal drag
            s.r  *= 0.974       # slow shrink
            s.a  -= s.decay
            if s.a > 0.01:
                alive.append(s)

        changed = len(alive) != len(self._sparks)
        self._sparks = alive
        if self._sparks or changed:
            self.update()

    # ── Painting ───────────────────────────────────────────────────────────────

    def paintEvent(self, event: object) -> None:  # type: ignore[override]
        if not self._sparks:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        for s in self._sparks:
            a8      = int(s.a * 255)
            glow_r  = s.r * 3.2

            # Outer soft glow
            grad = QRadialGradient(QPointF(s.x, s.y), glow_r)
            grad.setColorAt(0.0,  QColor(s.cr, s.cg, s.cb, a8))
            grad.setColorAt(0.35, QColor(s.cr, s.cg, s.cb, int(a8 * 0.45)))
            grad.setColorAt(1.0,  QColor(s.cr, s.cg, s.cb, 0))
            painter.setBrush(QBrush(grad))
            painter.drawEllipse(QPointF(s.x, s.y), glow_r, glow_r)

            # Inner hot core
            core_r = s.r * 0.9
            core_grad = QRadialGradient(QPointF(s.x, s.y), core_r)
            core_grad.setColorAt(0.0, QColor(255, 255, 255, min(255, int(a8 * 1.4))))
            core_grad.setColorAt(1.0, QColor(s.cr, s.cg, s.cb, 0))
            painter.setBrush(QBrush(core_grad))
            painter.drawEllipse(QPointF(s.x, s.y), core_r, core_r)

            # Star cross for designated sparks
            if s.star and s.r > 1.5:
                arm = s.r * 2.2
                pen = QPen(QColor(s.cr, s.cg, s.cb, int(a8 * 0.8)))
                pen.setWidthF(max(0.8, s.r * 0.28))
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                cx, cy = s.x, s.y
                painter.drawLine(QPointF(cx - arm, cy), QPointF(cx + arm, cy))
                painter.drawLine(QPointF(cx, cy - arm), QPointF(cx, cy + arm))
                d = arm * 0.55
                painter.drawLine(QPointF(cx - d, cy - d), QPointF(cx + d, cy + d))
                painter.drawLine(QPointF(cx + d, cy - d), QPointF(cx - d, cy + d))
                painter.setPen(Qt.PenStyle.NoPen)

        painter.end()

    # ── Resize tracking ────────────────────────────────────────────────────────

    def eventFilter(self, obj: object, event: object) -> bool:  # type: ignore[override]
        if isinstance(event, QEvent) and event.type() == QEvent.Type.Resize:
            from PyQt6.QtWidgets import QWidget as _W
            if isinstance(obj, _W):
                self.resize(obj.size())
                self.raise_()
        return False
