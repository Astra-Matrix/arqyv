"""
Find every visible window owned by any python process and teleport it
to the center of the primary monitor. Run while ARQYV is running.
"""
import ctypes
import ctypes.wintypes as wt

user32 = ctypes.windll.user32
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)

SW_RESTORE = 9
HWND_TOPMOST   = -1
HWND_NOTOPMOST = -2
SWP_NOMOVE  = 0x0002
SWP_NOSIZE  = 0x0001

# Get primary monitor work area
class RECT(ctypes.Structure):
    _fields_ = [("left",ctypes.c_long),("top",ctypes.c_long),
                ("right",ctypes.c_long),("bottom",ctypes.c_long)]

wa = RECT()
user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(wa), 0)  # SPI_GETWORKAREA
sw = wa.right - wa.left
sh = wa.bottom - wa.top
print(f"Work area: {sw}x{sh}")

found = []

def _cb(hwnd, _):
    buf = ctypes.create_unicode_buffer(512)
    user32.GetWindowTextW(hwnd, buf, 512)
    title = buf.value
    if title and user32.IsWindowVisible(hwnd):
        wr = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(wr))
        w = wr.right - wr.left
        h = wr.bottom - wr.top
        found.append((hwnd, title, wr.left, wr.top, w, h))
    return True

user32.EnumWindows(EnumWindowsProc(_cb), 0)

# Find ARQYV window
arqyv = [(h,t,x,y,w,hh) for h,t,x,y,w,hh in found if "ARQYV" in t or "arqyv" in t.lower()]
print(f"\nAll visible windows: {len(found)}")
print(f"ARQYV windows found: {len(arqyv)}")

for hwnd, title, x, y, w, h in arqyv:
    print(f"  HWND={hwnd}  title='{title}'  pos=({x},{y})  size={w}x{h}")
    # Move to center of primary monitor
    nx = wa.left + (sw - w) // 2
    ny = wa.top  + (sh - h) // 2
    print(f"  Moving to center: ({nx},{ny})")
    user32.SetWindowPos(hwnd, HWND_TOPMOST, nx, ny, w, h, 0)
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
    import time; time.sleep(1)
    user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
    print(f"  Done — window should be center screen now.")

if not arqyv:
    print("\nNo ARQYV window found. All visible window titles:")
    for _, t, x, y, w, h in found[:40]:
        print(f"  '{t}'  ({x},{y})  {w}x{h}")
