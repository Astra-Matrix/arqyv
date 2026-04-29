"""Platform detection and OS-specific helpers."""

from __future__ import annotations

import platform
import subprocess
import sys


def is_windows() -> bool:
    return sys.platform == "win32"


def is_macos() -> bool:
    return sys.platform == "darwin"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def open_file_manager(path: str) -> None:
    """Open the system file manager at the given path."""
    import os
    if is_windows():
        subprocess.Popen(["explorer", "/select,", path])
    elif is_macos():
        subprocess.Popen(["open", "-R", path])
    else:
        subprocess.Popen(["xdg-open", os.path.dirname(path)])


def open_with_default_app(path: str) -> None:
    """Open a file with the OS default application."""
    if is_windows():
        import os
        os.startfile(path)  # type: ignore[attr-defined]
    elif is_macos():
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def get_system_info() -> dict[str, str]:
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }
