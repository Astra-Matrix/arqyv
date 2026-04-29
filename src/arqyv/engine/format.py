"""Pure-Python format detector based on magic bytes.

Never relies on file extensions — reads the first 32 bytes of the file
and maps them to a canonical MediaFormat descriptor.

Zero external dependencies.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path


class MediaKind(Enum):
    VIDEO    = auto()
    AUDIO    = auto()
    IMAGE    = auto()
    DOCUMENT = auto()
    ARCHIVE  = auto()
    UNKNOWN  = auto()


@dataclass(frozen=True)
class MediaFormat:
    name: str            # human-readable, e.g. "Matroska Video"
    mime: str            # e.g. "video/x-matroska"
    kind: MediaKind
    extensions: tuple[str, ...]   # canonical extensions for this format


# ── Magic signature table ──────────────────────────────────────────────────
# (offset, bytes_to_match, format)

_SIGNATURES: list[tuple[int, bytes, MediaFormat]] = [
    # ── Video ──────────────────────────────────────────────────────────────
    (4,  b"ftyp",         MediaFormat("MPEG-4 / MP4",        "video/mp4",              MediaKind.VIDEO,    (".mp4", ".m4v", ".m4a", ".m4b"))),
    (0,  b"\x1a\x45\xdf\xa3", MediaFormat("Matroska",        "video/x-matroska",       MediaKind.VIDEO,    (".mkv", ".mka", ".mks", ".webm"))),
    (0,  b"RIFF",         MediaFormat("AVI",                 "video/x-msvideo",         MediaKind.VIDEO,    (".avi",))),
    (0,  b"\x00\x00\x00\x00" + b"ftyp", MediaFormat("QuickTime MOV", "video/quicktime", MediaKind.VIDEO,   (".mov",))),
    (0,  b"\x30\x26\xb2\x75", MediaFormat("Windows Media",   "video/x-ms-wmv",         MediaKind.VIDEO,    (".wmv", ".wma", ".asf"))),
    (0,  b"FLV\x01",     MediaFormat("Flash Video",          "video/x-flv",            MediaKind.VIDEO,    (".flv",))),
    (0,  b"\x47",        MediaFormat("MPEG-TS",              "video/mp2t",             MediaKind.VIDEO,    (".ts", ".mts", ".m2ts"))),
    (0,  b"\x00\x00\x01\xba", MediaFormat("MPEG-PS",         "video/mpeg",             MediaKind.VIDEO,    (".mpg", ".mpeg", ".vob"))),
    (0,  b"\x00\x00\x01\xb3", MediaFormat("MPEG Video",      "video/mpeg",             MediaKind.VIDEO,    (".mpg", ".mpeg"))),
    (0,  b"OggS",        MediaFormat("Ogg",                  "video/ogg",              MediaKind.VIDEO,    (".ogv", ".ogm", ".ogg"))),
    (0,  b"\x1f\x45\xdf\xa3", MediaFormat("WebM",            "video/webm",             MediaKind.VIDEO,    (".webm",))),
    # ── Audio ──────────────────────────────────────────────────────────────
    (0,  b"ID3",         MediaFormat("MP3 (ID3)",            "audio/mpeg",             MediaKind.AUDIO,    (".mp3",))),
    (0,  b"\xff\xfb",   MediaFormat("MP3",                  "audio/mpeg",             MediaKind.AUDIO,    (".mp3",))),
    (0,  b"\xff\xf3",   MediaFormat("MP3",                  "audio/mpeg",             MediaKind.AUDIO,    (".mp3",))),
    (0,  b"fLaC",       MediaFormat("FLAC",                 "audio/flac",             MediaKind.AUDIO,    (".flac",))),
    (0,  b"RIFF",       MediaFormat("WAV",                  "audio/wav",              MediaKind.AUDIO,    (".wav",))),
    (0,  b"OggS",       MediaFormat("Ogg Audio",            "audio/ogg",              MediaKind.AUDIO,    (".ogg", ".opus", ".oga"))),
    (0,  b"MAC ",       MediaFormat("Monkey's Audio",        "audio/ape",              MediaKind.AUDIO,    (".ape",))),
    (0,  b"\x00\x00\x00 ftyp", MediaFormat("AAC / M4A",     "audio/aac",              MediaKind.AUDIO,    (".aac", ".m4a"))),
    (0,  b"FORM",       MediaFormat("AIFF",                 "audio/aiff",             MediaKind.AUDIO,    (".aif", ".aiff"))),
    (0,  b"\x30\x26\xb2\x75", MediaFormat("WMA",            "audio/x-ms-wma",         MediaKind.AUDIO,    (".wma",))),
    # ── Image ──────────────────────────────────────────────────────────────
    (0,  b"\xff\xd8\xff", MediaFormat("JPEG",               "image/jpeg",             MediaKind.IMAGE,    (".jpg", ".jpeg"))),
    (0,  b"\x89PNG\r\n", MediaFormat("PNG",                 "image/png",              MediaKind.IMAGE,    (".png",))),
    (0,  b"GIF87a",     MediaFormat("GIF",                  "image/gif",              MediaKind.IMAGE,    (".gif",))),
    (0,  b"GIF89a",     MediaFormat("GIF",                  "image/gif",              MediaKind.IMAGE,    (".gif",))),
    (0,  b"RIFF",       MediaFormat("WebP",                 "image/webp",             MediaKind.IMAGE,    (".webp",))),
    (0,  b"BM",         MediaFormat("BMP",                  "image/bmp",              MediaKind.IMAGE,    (".bmp",))),
    (0,  b"II*\x00",    MediaFormat("TIFF (LE)",            "image/tiff",             MediaKind.IMAGE,    (".tif", ".tiff"))),
    (0,  b"MM\x00*",    MediaFormat("TIFF (BE)",            "image/tiff",             MediaKind.IMAGE,    (".tif", ".tiff"))),
    # ── Documents ──────────────────────────────────────────────────────────
    (0,  b"%PDF",       MediaFormat("PDF",                  "application/pdf",         MediaKind.DOCUMENT, (".pdf",))),
    (0,  b"PK\x03\x04", MediaFormat("ZIP / Office XML",    "application/zip",         MediaKind.DOCUMENT, (".docx", ".xlsx", ".pptx", ".zip", ".epub"))),
    (0,  b"\xd0\xcf\x11\xe0", MediaFormat("MS Office (OLE)", "application/msword",   MediaKind.DOCUMENT, (".doc", ".xls", ".ppt"))),
]

_UNKNOWN = MediaFormat("Unknown", "application/octet-stream", MediaKind.UNKNOWN, ())


def detect(path: Path | str) -> MediaFormat:
    """Identify a file's true format from its magic bytes.

    Reads at most 32 bytes — fast and safe on any file size.
    Falls back to extension heuristic only when magic bytes are ambiguous.
    """
    path = Path(path)
    try:
        header = path.read_bytes()[:32]
    except (OSError, PermissionError):
        return _UNKNOWN

    for offset, magic, fmt in _SIGNATURES:
        end = offset + len(magic)
        if header[offset:end] == magic:
            # Disambiguate RIFF container (WAV vs AVI vs WebP)
            if magic == b"RIFF" and len(header) >= 12:
                tag = header[8:12]
                if tag == b"WAVE":
                    return MediaFormat("WAV", "audio/wav", MediaKind.AUDIO, (".wav",))
                if tag == b"AVI ":
                    return MediaFormat("AVI", "video/x-msvideo", MediaKind.VIDEO, (".avi",))
                if tag == b"WEBP":
                    return MediaFormat("WebP", "image/webp", MediaKind.IMAGE, (".webp",))
            return fmt

    # Last-resort extension fallback
    ext = path.suffix.lower()
    for _, _, fmt in _SIGNATURES:
        if ext in fmt.extensions:
            return fmt

    return _UNKNOWN


def is_playable(path: Path | str) -> bool:
    fmt = detect(path)
    return fmt.kind in (MediaKind.VIDEO, MediaKind.AUDIO)


def is_streamable(path: Path | str) -> bool:
    """True for formats that support HTTP byte-range streaming."""
    fmt = detect(path)
    return fmt.mime in {
        "video/mp4", "audio/mpeg", "audio/flac", "audio/wav",
        "video/webm", "audio/ogg",
    }
