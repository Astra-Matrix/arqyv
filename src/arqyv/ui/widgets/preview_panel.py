"""Central preview panel.

Renders the appropriate preview depending on file type:
  - Image  → scaled QPixmap
  - Video  → first-frame thumbnail + "Play" overlay
  - Audio  → waveform stub + cover art
  - PDF    → first-page render via PyMuPDF
  - Other  → generic icon + file info
"""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from arqyv.config import AppConfig
from arqyv.core.events import EventBus

log = logging.getLogger(__name__)


class PreviewPanelWidget(QWidget):
    def __init__(self, config: AppConfig, events: EventBus, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self.events = events
        self._current_path: Path | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self._label = QLabel("Select a file to preview")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setMinimumSize(200, 200)
        layout.addWidget(self._label, 1)

    def load_file(self, path: str) -> None:
        p = Path(path)
        self._current_path = p
        suffix = p.suffix.lower()

        if suffix in self.config.media.supported_image:
            self._show_image(p)
        elif suffix in self.config.media.supported_video:
            self._show_video_thumb(p)
        elif suffix in self.config.media.supported_document and suffix == ".pdf":
            self._show_pdf_thumb(p)
        else:
            self._label.setText(f"📄 {p.name}\n\n{suffix.upper()} file")

    def _show_image(self, path: Path) -> None:
        pix = QPixmap(str(path))
        if pix.isNull():
            self._label.setText("Could not load image.")
            return
        scaled = pix.scaled(
            self._label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)

    def _show_video_thumb(self, path: Path) -> None:
        from arqyv.backend.thumbnail import ThumbnailGenerator
        thumb_path = ThumbnailGenerator.get_or_create(path)
        if thumb_path:
            self._show_image(thumb_path)
        else:
            self._label.setText(f"🎬 {path.name}")

    def _show_pdf_thumb(self, path: Path) -> None:
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            page = doc[0]
            mat = fitz.Matrix(1.5, 1.5)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")

            qt_pix = QPixmap()
            qt_pix.loadFromData(img_bytes, "PNG")
            self._label.setPixmap(
                qt_pix.scaled(
                    self._label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        except Exception:
            log.exception("PDF preview failed for %s", path)
            self._label.setText(f"📄 {path.name}")
