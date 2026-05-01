"""Absolute minimum Qt window — no ARQYV code at all."""
import sys
import ctypes
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import Qt, QTimer

app = QApplication(sys.argv)

label = QLabel()
label.setText("  ARQYV is working!\n\n  If you can see this, Qt is fine.\n  Close this and the main app will launch.")
label.setStyleSheet("background:#050508; color:#00d2ff; font-size:18px; padding:40px;")
label.setWindowTitle("ARQYV")
label.setFixedSize(520, 200)

# Force always-on-top so it can't be hidden behind anything
label.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Window)

label.show()

# Win32 force foreground
try:
    hwnd = int(label.winId())
    ctypes.windll.user32.ShowWindow(hwnd, 9)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    ctypes.windll.user32.BringWindowToTop(hwnd)
    print("Win32 foreground forced")
except Exception as e:
    print(f"Win32 failed: {e}")

print("Window shown with WindowStaysOnTopHint — it MUST be visible now.")
app.exec()
