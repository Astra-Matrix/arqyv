"""Technical metadata extractor.

Uses pymediainfo (wrapper around the MediaInfo library) for video/audio,
mutagen for audio tags, exifread for images, and PyMuPDF for PDFs.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


class MetadataExtractor:
    @staticmethod
    def extract(path: Path) -> dict[str, Any]:
        suffix = path.suffix.lower()

        from arqyv.config import config
        if suffix in config.media.supported_video or suffix in config.media.supported_audio:
            return MetadataExtractor._from_mediainfo(path)
        elif suffix in config.media.supported_image:
            return MetadataExtractor._from_image(path)
        elif suffix == ".pdf":
            return MetadataExtractor._from_pdf(path)
        elif suffix in (".docx", ".doc"):
            return MetadataExtractor._from_docx(path)
        return {}

    @staticmethod
    def _from_mediainfo(path: Path) -> dict[str, Any]:
        try:
            from pymediainfo import MediaInfo  # type: ignore[import]
            info = MediaInfo.parse(str(path))
            result: dict[str, Any] = {}

            for track in info.tracks:
                if track.track_type == "General":
                    result["duration_seconds"] = (track.duration or 0) / 1000
                    result["bit_rate"] = track.overall_bit_rate
                    result["mime_type"] = track.internet_media_type
                elif track.track_type == "Video":
                    result["width"] = track.width
                    result["height"] = track.height
                    result["fps"] = track.frame_rate
                    result["video_codec"] = track.codec_id or track.format
                elif track.track_type == "Audio":
                    result["audio_codec"] = track.codec_id or track.format

            return result
        except Exception:
            log.debug("MediaInfo extraction failed for %s", path)
            return {}

    @staticmethod
    def _from_image(path: Path) -> dict[str, Any]:
        result: dict[str, Any] = {}
        try:
            from PIL import Image
            with Image.open(path) as img:
                result["width"] = img.width
                result["height"] = img.height
                result["mime_type"] = Image.MIME.get(img.format or "", "image/*")
        except Exception:
            log.debug("Pillow failed for %s", path)

        try:
            import exifread  # type: ignore[import]
            with open(path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            if "EXIF DateTimeOriginal" in tags:
                result["fs_created_at"] = str(tags["EXIF DateTimeOriginal"])
            if "GPS GPSLatitude" in tags:
                result["gps_lat"] = str(tags["GPS GPSLatitude"])
            if "GPS GPSLongitude" in tags:
                result["gps_lon"] = str(tags["GPS GPSLongitude"])
        except Exception:
            log.debug("EXIF extraction failed for %s", path)

        return result

    @staticmethod
    def _from_pdf(path: Path) -> dict[str, Any]:
        try:
            import fitz
            doc = fitz.open(str(path))
            meta = doc.metadata or {}
            return {
                "mime_type": "application/pdf",
                "page_count": doc.page_count,
                "pdf_title": meta.get("title"),
                "pdf_author": meta.get("author"),
            }
        except Exception:
            return {"mime_type": "application/pdf"}

    @staticmethod
    def _from_docx(path: Path) -> dict[str, Any]:
        try:
            from docx import Document
            doc = Document(str(path))
            props = doc.core_properties
            return {
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "doc_author": props.author,
                "doc_title": props.title,
                "doc_created": str(props.created) if props.created else None,
            }
        except Exception:
            return {}
