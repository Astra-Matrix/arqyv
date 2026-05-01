"""Window centering and foreground helpers — Win32 + cross-platform fallback."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QMainWindow, QApplication
    from arqyv.config import AppConfig

log = logging.getLogger(__name__)


_TITLE_BAR_RESERVE = 50   # pixels reserved for the OS title bar + frame top

def center_window(
    win: "QMainWindow",
    cfg: "AppConfig",
    app: "QApplication",
) -> None:
    """
    Resize and center *win* on the primary screen.

    setGeometry() positions the *client* area, but the OS title bar sits
    *above* that origin.  When the work-area is tight (e.g. 1536×816) and
    the window height equals the work-area height, y=0 puts the title bar
    above the screen top — invisible.  We reserve _TITLE_BAR_RESERVE pixels
    at the top so the frame is always reachable.
    """
    screen = app.primaryScreen()
    if not screen:
        return
    geo = screen.availableGeometry()
    # Leave room for the OS frame: width and height must fit inside the usable area
    w = min(cfg.window_width,  geo.width())
    h = min(cfg.window_height, geo.height() - _TITLE_BAR_RESERVE)
    # Center horizontally; ensure enough top margin for the title bar
    x = geo.x() + (geo.width()  - w) // 2
    y = geo.y() + max(_TITLE_BAR_RESERVE, (geo.height() - h) // 2)
    win.setGeometry(x, y, w, h)


def bring_to_foreground(win: "QMainWindow") -> None:
    """
    Pin the window to topmost, force it to the foreground, then release
    topmost after 1 second so it behaves normally from that point on.

    Safe to call on all platforms — falls back silently on non-Windows.
    """
    from PyQt6.QtCore import QTimer
    try:
        import ctypes
        u32  = ctypes.windll.user32
        hwnd = int(win.winId())

        # HWND_TOPMOST (-1), SWP_NOMOVE (0x0002) | SWP_NOSIZE (0x0001)
        u32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
        u32.ShowWindow(hwnd, 9)          # SW_RESTORE
        u32.SetForegroundWindow(hwnd)
        u32.BringWindowToTop(hwnd)

        # Release topmost — HWND_NOTOPMOST (-2)
        QTimer.singleShot(
            1000,
            lambda: u32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0001 | 0x0002),
        )
        log.debug("foreground_pinned hwnd=%s", hwnd)
    except Exception as exc:
        log.debug("foreground_skip reason=%s", exc)
