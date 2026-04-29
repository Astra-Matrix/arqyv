"""VLC auto-discovery and DLL injection.

On first import this module scans well-known installation paths for libvlc
and, if found, injects the directory into:
  - os.add_dll_directory()  (Windows Python 3.8+)
  - os.environ['VLC_PLUGIN_PATH']
  - os.environ['PYTHON_VLC_LIB_PATH']

This means a system VLC installation is picked up automatically with
zero user interaction. The user only needs VLC installed at the OS level
(which many users already have) – they never need to touch python-vlc or
any DLL paths manually.

Priority order:
  1. PYTHON_VLC_LIB_PATH env var (user override)
  2. Windows: registry + common Program Files paths
  3. macOS: /Applications, Homebrew
  4. Linux: ldconfig paths, common /usr/lib locations
  5. Same directory as the running executable (bundled / PyInstaller)
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

log = logging.getLogger(__name__)

_VLC_FOUND: bool | None = None   # cached result
_VLC_PATH: Path | None = None


def _find_vlc_windows() -> Path | None:
    """Search Windows registry and common install paths for libvlc.dll."""
    candidates: list[Path] = []

    # Registry lookup (works for standard VLC installer)
    try:
        import winreg  # type: ignore[import]
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for subkey in (
                r"SOFTWARE\VideoLAN\VLC",
                r"SOFTWARE\WOW6432Node\VideoLAN\VLC",
            ):
                try:
                    key = winreg.OpenKey(hive, subkey)
                    install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
                    candidates.append(Path(install_dir))
                    winreg.CloseKey(key)
                except (FileNotFoundError, OSError):
                    pass
    except ImportError:
        pass

    # Common filesystem paths
    for base in (
        Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "VideoLAN" / "VLC",
        Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "VideoLAN" / "VLC",
        Path(r"C:\Program Files\VideoLAN\VLC"),
        Path(r"C:\Program Files (x86)\VideoLAN\VLC"),
        Path.home() / "AppData" / "Local" / "Programs" / "VideoLAN" / "VLC",
    ):
        candidates.append(base)

    for path in candidates:
        if (path / "libvlc.dll").exists():
            return path

    return None


def _find_vlc_macos() -> Path | None:
    """Search macOS app bundle and Homebrew paths."""
    candidates = [
        Path("/Applications/VLC.app/Contents/MacOS/lib"),
        Path("/Applications/VLC.app/Contents/MacOS"),
        Path("/opt/homebrew/lib"),               # Apple Silicon Homebrew
        Path("/usr/local/lib"),                  # Intel Homebrew
        Path("/opt/local/lib"),                  # MacPorts
    ]
    for path in candidates:
        for lib in ("libvlc.dylib", "libvlc.5.dylib"):
            if (path / lib).exists():
                return path
    return None


def _find_vlc_linux() -> Path | None:
    """Search Linux system library paths."""
    import subprocess, shutil

    # Use ldconfig to find the library
    if shutil.which("ldconfig"):
        try:
            out = subprocess.check_output(
                ["ldconfig", "-p"], text=True, stderr=subprocess.DEVNULL
            )
            for line in out.splitlines():
                if "libvlc.so" in line and "=>" in line:
                    lib_path = Path(line.split("=>")[-1].strip())
                    return lib_path.parent
        except Exception:
            pass

    # Fallback static paths
    for path in (
        Path("/usr/lib/x86_64-linux-gnu"),
        Path("/usr/lib/aarch64-linux-gnu"),
        Path("/usr/lib"),
        Path("/usr/local/lib"),
        Path("/snap/vlc/current/usr/lib"),
    ):
        if list(path.glob("libvlc.so*")):
            return path

    return None


def _find_vlc_bundled() -> Path | None:
    """Check if VLC DLLs are bundled alongside the executable (PyInstaller)."""
    exe_dir = Path(sys.executable).parent
    for candidate in (exe_dir, exe_dir / "vlc", exe_dir / "_internal"):
        dll_name = {
            "win32": "libvlc.dll",
            "darwin": "libvlc.dylib",
        }.get(sys.platform, "libvlc.so")
        if (candidate / dll_name).exists():
            return candidate
    return None


def setup_vlc() -> bool:
    """Locate VLC, inject its path, and return True if found.

    Safe to call multiple times – result is cached after first call.
    """
    global _VLC_FOUND, _VLC_PATH

    if _VLC_FOUND is not None:
        return _VLC_FOUND

    # Honour explicit override first
    if os.environ.get("PYTHON_VLC_LIB_PATH"):
        _VLC_FOUND = True
        _VLC_PATH = Path(os.environ["PYTHON_VLC_LIB_PATH"])
        log.info("VLC: using PYTHON_VLC_LIB_PATH=%s", _VLC_PATH)
        return True

    # Try bundled first (PyInstaller), then system install
    path: Path | None = _find_vlc_bundled()
    if path is None:
        if sys.platform == "win32":
            path = _find_vlc_windows()
        elif sys.platform == "darwin":
            path = _find_vlc_macos()
        else:
            path = _find_vlc_linux()

    if path is None:
        log.debug(
            "VLC not found on this system. "
            "Install VLC (https://videolan.org) for extended codec support. "
            "Qt Multimedia is active as the primary playback engine."
        )
        _VLC_FOUND = False
        return False

    _VLC_PATH = path
    log.info("VLC found at: %s", path)

    # Inject path so python-vlc can load the DLLs without user action
    os.environ["PYTHON_VLC_LIB_PATH"] = str(path)
    os.environ["VLC_PLUGIN_PATH"] = str(path / "plugins")

    if sys.platform == "win32":
        try:
            os.add_dll_directory(str(path))
        except (AttributeError, OSError):
            pass  # Python < 3.8 or path invalid – env var fallback still works

    _VLC_FOUND = True
    return True


def vlc_path() -> Path | None:
    return _VLC_PATH


def is_vlc_available() -> bool:
    if _VLC_FOUND is None:
        return setup_vlc()
    return bool(_VLC_FOUND)
