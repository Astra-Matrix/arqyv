"""
Absolute minimum Qt window test — zero ARQYV code.
Run:  python _qt_test.py
If you see a red-background window titled ARQYV_TEST, Qt is fine.
If nothing appears, Qt itself is broken on this machine.
"""
import sys
import ctypes

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor

app = QApplication(sys.argv)
app.setApplicationName("ARQYV_TEST")

win = QMainWindow()
win.setWindowTitle("ARQYV_TEST  —  close me when you see this")
win.resize(700, 300)
win.move(200, 200)

lbl = QLabel("Qt is working.\nARQYV window IS being created — window manager issue.", win)
lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
lbl.setStyleSheet("font-size: 22px; color: white; background: #7c3aed;")
win.setCentralWidget(lbl)

win.setWindowState(Qt.WindowState.WindowNoState)
win.show()
win.raise_()
win.activateWindow()

# Force foreground via WinAPI
def _force():
    try:
        hwnd = int(win.winId())
        u32 = ctypes.windll.user32
        u32.SetWindowPos(hwnd, -1, 200, 200, 700, 300, 0)  # HWND_TOPMOST, explicit pos+size
        u32.ShowWindow(hwnd, 9)
        u32.SetForegroundWindow(hwnd)
        u32.BringWindowToTop(hwnd)
        print(f"hwnd={hwnd}  forced foreground")
        # Drop topmost after 2s
        QTimer.singleShot(2000, lambda: u32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0001 | 0x0002))
    except Exception as e:
        print(f"WinAPI error: {e}")

QTimer.singleShot(100, _force)

print("Qt event loop running — window should be visible NOW")
sys.exit(app.exec())
