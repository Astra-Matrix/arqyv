"""Semantic text embedder using sentence-transformers.

Produces normalized float32 vectors suitable for cosine similarity search.
Model is loaded once and kept in memory for the process lifetime.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model: Any = None
        log.info("Embedder will load model: %s (on first use)", model_name)

    def _load(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # type: ignore[import]
            log.info("Loading embedding model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> list[float]:
        model = self._load()
        vec = model.encode(text, normalize_embeddings=True, show_progress_bar=False)
        return vec.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        model = self._load()
        vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vecs.tolist()
