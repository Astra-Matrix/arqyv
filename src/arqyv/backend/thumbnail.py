"""Thumbnail generator with disk cache.

Strategy per file type:
  - Image  → Pillow resize
  - Video  → VLC first-frame extraction
  - Audio  → embedded cover art via mutagen, fallback waveform icon
  - PDF    → PyMuPDF page 0 render
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

log = logging.getLogger(__name__)

_THUMB_SIZE = (320, 240)
_CACHE_DIR: Path | None = None


def _cache_dir() -> Path:
    global _CACHE_DIR
    if _CACHE_DIR is None:
        from arqyv.config import config
        _CACHE_DIR = config.thumbnail_cache_path
    return _CACHE_DIR


def _cache_path(source: Path) -> Path:
    digest = hashlib.blake2b(str(source).encode(), digest_size=16).hexdigest()
    return _cache_dir() / f"{digest}.jpg"


class ThumbnailGenerator:
    @staticmethod
    def get_or_create(source: Path) -> Path | None:
        cached = _cache_path(source)
        if cached.exists():
            return cached

        suffix = source.suffix.lower()
        try:
            from arqyv.config import config
            if suffix in config.media.supported_image:
                return ThumbnailGenerator._from_image(source, cached)
            elif suffix in config.media.supported_video:
                return ThumbnailGenerator._from_video(source, cached)
            elif suffix in config.media.supported_audio:
                return ThumbnailGenerator._from_audio(source, cached)
            elif suffix == ".pdf":
                return ThumbnailGenerator._from_pdf(source, cached)
        except Exception:
            log.exception("Thumbnail failed for %s", source)
        return None

    @staticmethod
    def _from_image(source: Path, dest: Path) -> Path:
        from PIL import Image
        with Image.open(source) as img:
            img.thumbnail(_THUMB_SIZE, Image.Resampling.LANCZOS)
            img.convert("RGB").save(dest, "JPEG", quality=85, optimize=True)
        return dest

    @staticmethod
    def _from_video(source: Path, dest: Path) -> Path | None:
        try:
            import vlc  # type: ignore[import]
            import time

            inst = vlc.Instance("--no-xlib", "--quiet")
            player = inst.media_player_new()
            media = inst.media_new(str(source))
            player.set_media(media)
            player.play()
            time.sleep(1.5)
            player.set_position(0.1)
            time.sleep(0.5)
            ok = player.video_take_snapshot(0, str(dest), *_THUMB_SIZE)
            player.stop()
            return dest if ok == 0 and dest.exists() else None
        except ImportError:
            return None

    @staticmethod
    def _from_audio(source: Path, dest: Path) -> Path | None:
        try:
            from mutagen import File as MutagenFile
            from PIL import Image
            import io

            audio = MutagenFile(str(source))
            if audio is None:
                return None
            cover_data: bytes | None = None

            # ID3 (MP3)
            if hasattr(audio, "tags") and audio.tags:
                for tag in audio.tags.values():
                    if hasattr(tag, "data") and hasattr(tag, "mime"):
                        cover_data = tag.data
                        break
            # FLAC
            if cover_data is None and hasattr(audio, "pictures"):
                pics = audio.pictures  # type: ignore[attr-defined]
                if pics:
                    cover_data = pics[0].data

            if cover_data:
                with Image.open(io.BytesIO(cover_data)) as img:
                    img.thumbnail(_THUMB_SIZE, Image.Resampling.LANCZOS)
                    img.convert("RGB").save(dest, "JPEG", quality=85)
                return dest
        except Exception:
            log.debug("No cover art for %s", source)
        return None

    @staticmethod
    def _from_pdf(source: Path, dest: Path) -> Path | None:
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            import io

            doc = fitz.open(str(source))
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            img.thumbnail(_THUMB_SIZE, Image.Resampling.LANCZOS)
            img.convert("RGB").save(dest, "JPEG", quality=85)
            return dest
        except Exception:
            log.debug("PDF thumbnail failed for %s", source)
        return None
