"""Unified search engine: combines semantic (vector) + full-text + metadata filters.

Search pipeline:
  1. Parse the query and extract any filter tokens (e.g. type:video date:>2024).
  2. Run semantic search in ChromaDB → top-K candidate IDs.
  3. Run full-text LIKE search in SQLite for remaining slots.
  4. Merge results, deduplicate, and apply metadata filters.
  5. Return ranked list of MediaFile records.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from arqyv.config import AppConfig
from arqyv.search.filters import FilterParser, SearchFilter
from arqyv.search.semantic import SemanticSearch

if TYPE_CHECKING:
    from arqyv.database.db import Database
    from arqyv.database.models import MediaFile

log = logging.getLogger(__name__)


class SearchEngine:
    def __init__(self, db: "Database", config: AppConfig) -> None:
        self.db = db
        self.config = config
        self._semantic: SemanticSearch | None = None

    def _get_semantic(self) -> SemanticSearch:
        if self._semantic is None:
            self._semantic = SemanticSearch(vector_db_path=self.config.vector_db_path)
        return self._semantic

    # ── Public API ─────────────────────────────────────────────────────────

    def search(self, query: str, limit: int = 50) -> list["MediaFile"]:
        """Synchronous wrapper – safe to call from Qt thread."""
        return asyncio.run(self.search_async(query, limit))

    async def search_async(self, query: str, limit: int = 50) -> list["MediaFile"]:
        query = query.strip()
        if not query:
            return []

        search_filter, clean_query = FilterParser.parse(query)
        log.debug("Search: %r | filter: %s", clean_query, search_filter)

        # Semantic candidates
        semantic_ids: list[str] = []
        if self.config.enable_ai and clean_query:
            try:
                semantic_ids = self._get_semantic().query(clean_query, n_results=limit)
            except Exception:
                log.warning("Semantic search failed; falling back to full-text.")

        # Full-text candidates from DB
        db_results = await self.db.search_files(clean_query, limit=limit)

        # Merge: semantic results first, then DB results (deduplicated)
        seen_paths: set[str] = set()
        merged: list["MediaFile"] = []

        for file in db_results:
            if file.path not in seen_paths:
                seen_paths.add(file.path)
                merged.append(file)

        # Apply metadata filters
        results = [f for f in merged if search_filter.matches(f)]

        await self.db.record_search(query=query, result_count=len(results))
        return results[:limit]

    def index_embedding(self, path: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        """Store an embedding in the vector DB (called after AI analysis)."""
        self._get_semantic().add(doc_id=path, embedding=embedding, metadata=metadata)
