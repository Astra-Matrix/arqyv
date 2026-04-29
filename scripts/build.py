#!/usr/bin/env python3
"""Build standalone executable using PyInstaller.

Usage:
  python scripts/build.py --platform win   # Windows .exe
  python scripts/build.py --platform mac   # macOS .app
  python scripts/build.py --platform linux # Linux ELF
"""

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"
ASSETS = ROOT / "assets"
ICONS_DIR = ASSETS / "icons"


def build(platform: str) -> None:
    print(f"=== Building ARQYV for {platform} ===")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "ARQYV",
        "--onedir",
        "--windowed",
        "--hidden-import", "arqyv",
        "--hidden-import", "vlc",
        "--hidden-import", "chromadb",
        "--hidden-import", "sentence_transformers",
        "--collect-all", "sentence_transformers",
        "--collect-all", "chromadb",
        "--collect-all", "arqyv",
        str(ROOT / "src" / "arqyv" / "__main__.py"),
    ]

    # Icon is optional — skip silently if not present
    icon_path = ICONS_DIR / ("arqyv.ico" if platform == "win" else "arqyv.icns" if platform == "mac" else "arqyv.png")
    if icon_path.exists():
        cmd += ["--icon", str(icon_path)]
    else:
        print(f"  (icon not found at {icon_path}, building without icon)")

    # Embed assets directory if it exists
    if ASSETS.exists():
        sep = ";" if platform == "win" else ":"
        cmd += ["--add-data", f"{ASSETS}{sep}assets"]

    # Windows version info file (optional)
    if platform == "win":
        vf = ROOT / "scripts" / "version_info.txt"
        if vf.exists():
            cmd += ["--version-file", str(vf)]

    subprocess.run(cmd, check=True, cwd=ROOT)
    print(f"\nBuild complete: {DIST}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["win", "mac", "linux"], default="linux")
    args = parser.parse_args()
    build(args.platform)


if __name__ == "__main__":
    main()
