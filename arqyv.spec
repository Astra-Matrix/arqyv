# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for ARQYV — cross-platform single-folder distribution.

Build:
    Windows:  pyinstaller arqyv.spec
    macOS:    pyinstaller arqyv.spec
    Linux:    pyinstaller arqyv.spec

Output: dist/ARQYV/   (folder mode, easier to update than one-file)
"""

import sys
from pathlib import Path

ROOT = Path(SPEC).parent
SRC  = ROOT / "src" / "arqyv"

block_cipher = None

a = Analysis(
    [str(ROOT / "run.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=[
        # Include all non-Python assets
        (str(SRC / "ui" / "themes"), "arqyv/ui/themes"),
    ],
    hiddenimports=[
        # PyQt6 plugins Qt needs at runtime
        "PyQt6.QtMultimedia",
        "PyQt6.QtMultimediaWidgets",
        "PyQt6.QtSvg",
        # Database
        "aiosqlite",
        "sqlalchemy.dialects.sqlite",
        # Optional AI — imported lazily; include so they bundle if installed
        "sentence_transformers",
        "chromadb",
        "whisper",
        # Watchdog platform observers
        "watchdog.observers",
        "watchdog.observers.polling",
        # Share
        "zeroconf",
        "qrcode",
        "qrcode.image.pil",
        # FastAPI / uvicorn
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "fastapi",
        "anyio",
        "anyio._backends._asyncio",
        # BM25
        "rank_bm25",
        # Image
        "PIL",
        "PIL.Image",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "IPython",
        "jupyter",
        "notebook",
        "test",
        "tests",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ARQYV",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # windowless on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "assets" / "icon.ico") if (ROOT / "assets" / "icon.ico").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ARQYV",
)

# macOS .app bundle (only active on macOS)
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="ARQYV.app",
        icon=str(ROOT / "assets" / "icon.icns") if (ROOT / "assets" / "icon.icns").exists() else None,
        bundle_identifier="com.alaustrup.arqyv",
        info_plist={
            "NSHighResolutionCapable": True,
            "CFBundleShortVersionString": "0.1.0",
            "CFBundleVersion": "1",
            "NSMicrophoneUsageDescription": "ARQYV uses the microphone for voice search.",
        },
    )
