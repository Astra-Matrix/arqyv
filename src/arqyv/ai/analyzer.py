"""AI content analyzer – orchestrates embedder, tagger, and summarizer.

Designed to be instantiated once (cached) and called from worker threads.
All heavy model loading happens lazily on first call.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from arqyv.config import AppConfig
from arqyv.core.events import EventBus, Events

log = logging.getLogger(__name__)


class AIAnalyzer:
    _instance: "AIAnalyzer | None" = None

    def __new__(cls, config: AppConfig, events: EventBus) -> "AIAnalyzer":
        # Module-level singleton – avoids reloading models on every worker call.
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instance = instance
        return cls._instance

    def __init__(self, config: AppConfig, events: EventBus) -> None:
        if self._initialized:  # type: ignore[has-type]
            return
        self.config = config
        self.events = events
        self._embedder: "Embedder | None" = None
        self._tagger: "Tagger | None" = None
        self._summarizer: "Summarizer | None" = None
        self._initialized = True

    # ── Lazy loaders ───────────────────────────────────────────────────────

    def _get_embedder(self) -> "Embedder":
        if self._embedder is None:
            from arqyv.ai.embedder import Embedder
            self._embedder = Embedder(model_name=self.config.ai.embedding_model)
        return self._embedder

    def _get_tagger(self) -> "Tagger":
        if self._tagger is None:
            from arqyv.ai.tagger import Tagger
            self._tagger = Tagger()
        return self._tagger

    def _get_summarizer(self) -> "Summarizer":
        if self._summarizer is None:
            from arqyv.ai.summarizer import Summarizer
            self._summarizer = Summarizer()
        return self._summarizer

    # ── Public API ─────────────────────────────────────────────────────────

    def analyze(self, path: Path) -> dict[str, Any]:
        """Run full AI pipeline for a file and emit results."""
        log.debug("AI analyzing: %s", path)
        result: dict[str, Any] = {"path": str(path), "ai": {}}

        try:
            suffix = path.suffix.lower()
            text_content = self._extract_text_content(path, suffix)

            if text_content:
                embedding = self._get_embedder().embed_text(text_content)
                tags = self._get_tagger().tag_text(text_content)
                summary = self._get_summarizer().summarize(text_content)
                result["ai"] = {
                    "tags": ", ".join(tags),
                    "summary": summary,
                    "embedding_dim": len(embedding),
                }
                result["embedding"] = embedding

            self.events.emit(Events.AI_ANALYSIS_DONE, path=str(path), metadata=result)
        except Exception:
            log.exception("AI analysis failed for %s", path)

        return result

    def embed_query(self, query: str) -> list[float]:
        return self._get_embedder().embed_text(query)

    # ── Text extraction per file type ─────────────────────────────────────

    def _extract_text_content(self, path: Path, suffix: str) -> str:
        from arqyv.config import config

        if suffix in config.media.supported_image:
            return self._describe_image(path)
        elif suffix in config.media.supported_audio or suffix in config.media.supported_video:
            return self._transcribe_media(path)
        elif suffix == ".pdf":
            return self._extract_pdf_text(path)
        elif suffix in (".txt", ".md"):
            return path.read_text(encoding="utf-8", errors="ignore")[:8000]
        elif suffix == ".docx":
            return self._extract_docx_text(path)
        return ""

    def _describe_image(self, path: Path) -> str:
        try:
            from transformers import pipeline  # type: ignore[import]
            captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
            result = captioner(str(path))
            return result[0]["generated_text"] if result else ""
        except Exception:
            log.debug("Image captioning unavailable for %s", path)
            return ""

    def _transcribe_media(self, path: Path) -> str:
        try:
            import whisper  # type: ignore[import]
            model = whisper.load_model(self.config.ai.whisper_model)
            result = model.transcribe(str(path), fp16=False)
            return result.get("text", "")
        except Exception:
            log.debug("Transcription failed for %s", path)
            return ""

    def _extract_pdf_text(self, path: Path) -> str:
        try:
            import fitz
            doc = fitz.open(str(path))
            return "\n".join(page.get_text() for page in doc)[:8000]
        except Exception:
            return ""

    def _extract_docx_text(self, path: Path) -> str:
        try:
            from docx import Document
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)[:8000]
        except Exception:
            return ""
