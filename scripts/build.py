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
SPEC_FILE = ROOT / "arqyv.spec"


def build(platform: str) -> None:
    print(f"=== Building ARQYV for {platform} ===")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "ARQYV",
        "--onedir",
        "--windowed",
        "--icon", str(ROOT / "assets" / "icons" / "arqyv.ico"),
        "--add-data", f"{ROOT / 'assets'}:assets",
        "--hidden-import", "vlc",
        "--hidden-import", "chromadb",
        "--hidden-import", "sentence_transformers",
        "--collect-all", "sentence_transformers",
        "--collect-all", "chromadb",
        str(ROOT / "src" / "arqyv" / "main.py"),
    ]

    if platform == "win":
        cmd += ["--version-file", str(ROOT / "scripts" / "version_info.txt")]

    subprocess.run(cmd, check=True, cwd=ROOT)
    print(f"\n✓ Build complete: {DIST}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["win", "mac", "linux"], default="linux")
    args = parser.parse_args()
    build(args.platform)


if __name__ == "__main__":
    main()
