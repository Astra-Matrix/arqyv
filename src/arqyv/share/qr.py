"""QR code generator for share links.

Renders a QR code as a QPixmap usable directly in PyQt6 widgets.
Uses the `qrcode` library (pure Python, depends only on Pillow which
we already require).

Falls back to a text-only label if qrcode is unavailable.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtGui import QPixmap

log = logging.getLogger(__name__)


def generate_pixmap(url: str, size: int = 300) -> QPixmap | None:
    """Return a QPixmap of the QR code for `url`, or None on failure."""
    try:
        import qrcode  # type: ignore[import]
        from qrcode.image.pil import PilImage  # type: ignore[import]
        import io

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="white", back_color="#1a1a2e")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buf.read(), "PNG")
        return pixmap.scaled(size, size)

    except ImportError:
        log.debug("qrcode not installed; QR display unavailable.")
        return None
    except Exception:
        log.exception("QR generation failed.")
        return None


def save_qr_image(url: str, dest: Path, size: int = 512) -> bool:
    """Save QR code as a PNG file. Returns True on success."""
    try:
        import qrcode  # type: ignore[import]

        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(str(dest))
        return True
    except Exception:
        log.exception("QR save failed.")
        return False
