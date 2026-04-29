"""ChromaDB vector store wrapper for semantic search."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_COLLECTION = "arqyv_media"


class SemanticSearch:
    def __init__(self, vector_db_path: Path) -> None:
        self._path = vector_db_path
        self._client: Any = None
        self._collection: Any = None

    def _get_collection(self) -> Any:
        if self._client is None:
            import chromadb  # type: ignore[import]
            self._client = chromadb.PersistentClient(path=str(self._path))
            self._collection = self._client.get_or_create_collection(
                name=_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def add(self, doc_id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        coll = self._get_collection()
        safe_meta = {k: str(v) for k, v in metadata.items() if v is not None}
        coll.upsert(ids=[doc_id], embeddings=[embedding], metadatas=[safe_meta])

    def query(self, query_text: str, n_results: int = 20) -> list[str]:
        """Return file paths ranked by semantic similarity."""
        from arqyv.ai.embedder import Embedder
        from arqyv.config import config

        embedder = Embedder(model_name=config.ai.embedding_model)
        query_vec = embedder.embed_text(query_text)

        coll = self._get_collection()
        results = coll.query(query_embeddings=[query_vec], n_results=min(n_results, coll.count()))
        ids: list[list[str]] = results.get("ids", [[]])
        return ids[0] if ids else []

    def delete(self, doc_id: str) -> None:
        coll = self._get_collection()
        coll.delete(ids=[doc_id])
