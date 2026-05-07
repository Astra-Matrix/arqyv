"""
ARQYV Shimmer Effect — diagonal highlight sweep on hover.

`ShimmerEffect` is a QObject-based event filter you attach to any QWidget.
On mouse-enter it spawns a transparent child overlay that plays a single
left-to-right diagonal white gradient sweep (like an iOS/macOS metal sheen).

Usage
-----
    btn = QPushButton("Open Folder")
    ShimmerEffect.install(btn)

Or apply to an entire panel:
    ShimmerEffect.install(toolbar_widget, duration_ms=1200)
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,
    pyqtSlot,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
)
from PyQt6.QtWidgets import QWidget


# ── Inner overlay widget ───────────────────────────────────────────────────────

class _ShimmerOverlay(QWidget):
    """
    Transparent overlay that renders a single diagonal shimmer stripe.
    `_progress` drives the stripe from left-off-screen to right-off-screen.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self._progress: float = -0.3
        self.resize(parent.size())
        self.hide()

    # ── Animated property ──────────────────────────────────────────────────

    def _get_progress(self) -> float:
        return self._progress

    @pyqtSlot(float)
    def _set_progress(self, v: float) -> None:
        self._progress = v
        self.update()

    progress = pyqtProperty(float, _get_progress, _set_progress)

    # ── Paint ──────────────────────────────────────────────────────────────

    def paintEvent(self, event: object) -> None:  # type: ignore[override]
        w, h = self.width(), self.height()
        if w < 2 or h < 2:
            return

        # The stripe sweeps diagonally: centre X tracks _progress
        cx = self._progress * (w + 200) - 100
        half_w = w * 0.22   # stripe half-width

        # Diagonal sheen: gradient along X with a slight tilt
        x0 = cx - half_w
        x1 = cx + half_w
        grad = QLinearGradient(QPointF(x0, 0), QPointF(x1, h * 0.6))
        grad.setColorAt(0.0,  QColor(255, 255, 255, 0))
        grad.setColorAt(0.35, QColor(255, 255, 255, 14))
        grad.setColorAt(0.50, QColor(255, 255, 255, 26))
        grad.setColorAt(0.65, QColor(255, 255, 255, 14))
        grad.setColorAt(1.0,  QColor(255, 255, 255, 0))

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(QRectF(0, 0, w, h))
        painter.end()


# ── Effect controller ──────────────────────────────────────────────────────────

class ShimmerEffect(QObject):
    """
    Install on any QWidget to add a hover shimmer sweep.

    Parameters
    ----------
    target      : the widget to shimmer
    duration_ms : duration of the sweep animation in milliseconds
    cooldown_ms : minimum gap between shimmers (prevents retriggering on jitter)
    """

    def __init__(
        self,
        target:      QWidget,
        duration_ms: int = 650,
        cooldown_ms: int = 800,
    ) -> None:
        super().__init__(target)
        self._target      = target
        self._duration    = duration_ms
        self._cooldown    = cooldown_ms
        self._running     = False
        self._anim: QPropertyAnimation | None = None

        self._overlay = _ShimmerOverlay(target)
        target.installEventFilter(self)

    # ── Install helper ─────────────────────────────────────────────────────

    @staticmethod
    def install(
        widget:      QWidget,
        duration_ms: int = 650,
        cooldown_ms: int = 800,
    ) -> "ShimmerEffect":
        return ShimmerEffect(widget, duration_ms, cooldown_ms)

    # ── Event filter ───────────────────────────────────────────────────────

    def eventFilter(self, obj: object, event: object) -> bool:  # type: ignore[override]
        if not isinstance(event, QEvent):
            return False
        t = event.type()
        if t == QEvent.Type.Enter and not self._running:
            self._play()
        elif t == QEvent.Type.Resize:
            from PyQt6.QtWidgets import QWidget as _W
            if isinstance(obj, _W):
                self._overlay.resize(obj.size())
        return False

    # ── Animation ──────────────────────────────────────────────────────────

    def _play(self) -> None:
        self._running = True
        self._overlay._progress = -0.3
        self._overlay.show()
        self._overlay.raise_()

        anim = QPropertyAnimation(self._overlay, b"progress", self)
        anim.setStartValue(-0.3)
        anim.setEndValue(1.3)
        anim.setDuration(self._duration)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.finished.connect(self._on_done)
        anim.start()
        self._anim = anim

    @pyqtSlot()
    def _on_done(self) -> None:
        self._overlay.hide()
        # Cooldown prevents retriggering immediately
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(self._cooldown, self._reset)

    def _reset(self) -> None:
        self._running = False
