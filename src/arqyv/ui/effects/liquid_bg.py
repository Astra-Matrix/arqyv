"""
ARQYV Liquid Background — slowly drifting radial gradient orbs.

Renders a set of soft, large luminous blobs whose centres oscillate on
independent sine/cosine paths, creating an organic "lava lamp" feel.
The widget paints only its own layer; set it as the background of a
panel by making it the first child and stacking content on top.

Usage
-----
    bg = LiquidBackground(parent=panel_widget)
    bg.resize(panel_widget.size())
    bg.lower()                     # keep it behind content

Alternatively, use it as a base class:

    class SidebarPanel(LiquidBackground):
        …
"""

from __future__ import annotations

import math

from PyQt6.QtCore import QEvent, QPointF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter, QRadialGradient
from PyQt6.QtWidgets import QWidget

from arqyv.ui.themes.dark import PALETTE as P


# ── Orb definitions ────────────────────────────────────────────────────────────
# Each entry: (cx_norm, cy_norm, r_norm, freq_x, freq_y, phase_x, phase_y, color, max_alpha)
# *_norm values are 0–1 relative to widget size.
# freq_* controls oscillation frequency (radians per tick).
# The orbs are deliberately slow so they feel like liquid, not animation.

_ORB_DEFS: list[tuple] = [
    # cx    cy    r     fx       fy       px   py   colour              a
    (0.15,  0.20, 0.55, 0.00025, 0.00018, 0.0, 1.2, P["cyan"],         18),
    (0.85,  0.75, 0.48, 0.00019, 0.00027, 2.4, 0.5, P["violet"],       15),
    (0.50,  0.05, 0.38, 0.00033, 0.00021, 1.1, 3.0, "#00a8cc",         12),
    (0.08,  0.85, 0.32, 0.00022, 0.00035, 3.5, 0.8, P["violet2"],      14),
    (0.75,  0.15, 0.28, 0.00041, 0.00016, 0.7, 2.1, P["cyan"],         10),
    (0.40,  0.90, 0.25, 0.00030, 0.00042, 1.9, 1.5, "#1a0040",         20),
]

_TICK_MS    = 33       # ~30 fps for background (lighter than particle overlay)
_AMPLITUDE  = 0.14     # how far each orb drifts from its base position (0–1)


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


class LiquidBackground(QWidget):
    """
    Animated soft-glow orb background widget.

    Set `lower()` or use as the first child so content renders above it.
    Call `set_intensity(0.0–1.0)` to fade the effect in/out (e.g. on focus).
    """

    def __init__(
        self,
        parent:    QWidget | None = None,
        intensity: float = 1.0,
    ) -> None:
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._t         = 0
        self._intensity = max(0.0, min(1.0, intensity))

        # Pre-parse hex colours once
        self._orbs: list[tuple] = []
        for cx, cy, r, fx, fy, px, py, colour, a in _ORB_DEFS:
            rgb = _hex_to_rgb(colour) if colour.startswith("#") else _hex_to_rgb(colour)
            self._orbs.append((cx, cy, r, fx, fy, px, py, rgb, a))

        self._timer = QTimer(self)
        self._timer.setInterval(_TICK_MS)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        if parent:
            parent.installEventFilter(self)

    # ── Public API ─────────────────────────────────────────────────────────────

    def set_intensity(self, value: float) -> None:
        self._intensity = max(0.0, min(1.0, value))
        self.update()

    # ── Internals ──────────────────────────────────────────────────────────────

    def _tick(self) -> None:
        self._t += 1
        self.update()

    def paintEvent(self, event: object) -> None:  # type: ignore[override]
        if self._intensity < 0.005:
            return

        w, h = self.width(), self.height()
        if w < 2 or h < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        t = self._t
        for cx_n, cy_n, r_n, fx, fy, px, py, (cr, cg, cb), max_a in self._orbs:
            # Oscillate centre
            x = (cx_n + math.sin(t * fx * math.tau + px) * _AMPLITUDE) * w
            y = (cy_n + math.cos(t * fy * math.tau + py) * _AMPLITUDE) * h
            r = r_n * min(w, h)

            a = int(max_a * self._intensity)

            grad = QRadialGradient(QPointF(x, y), r)
            grad.setColorAt(0.0,  QColor(cr, cg, cb, a))
            grad.setColorAt(0.45, QColor(cr, cg, cb, int(a * 0.35)))
            grad.setColorAt(1.0,  QColor(cr, cg, cb, 0))

            painter.setBrush(QBrush(grad))
            painter.drawEllipse(QPointF(x, y), r, r)

        painter.end()

    # ── Resize tracking ────────────────────────────────────────────────────────

    def eventFilter(self, obj: object, event: object) -> bool:  # type: ignore[override]
        if isinstance(event, QEvent) and event.type() == QEvent.Type.Resize:
            from PyQt6.QtWidgets import QWidget as _W
            if isinstance(obj, _W):
                self.resize(obj.size())
                self.lower()   # keep behind content children
        return False
