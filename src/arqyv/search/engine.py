"""Unified search engine: semantic (Chroma) + BM25 keyword + SQLite full-text + filters.

Search pipeline:
  1. Parse the query — extract filter tokens (type:video, date:>2024, etc.).
  2. Semantic search via ChromaDB → ranked file-path IDs.
  3. BM25 keyword search over in-memory corpus (populated as files are indexed).
  4. SQLite LIKE fallback for any remaining slots.
  5. Merge, deduplicate, apply metadata filters, return ranked MediaFile list.
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

# Maximum candidate pool before applying filters
_SEMANTIC_K = 40
_BM25_K     = 40


class SearchEngine:
    def __init__(self, db: "Database", config: AppConfig) -> None:
        self.db = db
        self.config = config
        self._semantic: SemanticSearch | None = None

        # BM25 in-memory corpus: path → tokenized document string
        self._bm25_corpus: dict[str, str] = {}
        self._bm25_paths: list[str] = []
        self._bm25_index: Any = None   # rank_bm25.BM25Okapi, created lazily
        self._bm25_dirty = False

    # ── Semantic backend ───────────────────────────────────────────────────

    def _get_semantic(self) -> SemanticSearch:
        if self._semantic is None:
            self._semantic = SemanticSearch(vector_db_path=self.config.vector_db_path)
        return self._semantic

    # ── BM25 backend ───────────────────────────────────────────────────────

    def _get_bm25(self) -> Any | None:
        if not self._bm25_corpus:
            return None
        if self._bm25_dirty or self._bm25_index is None:
            try:
                from rank_bm25 import BM25Okapi  # type: ignore[import]
                self._bm25_paths = list(self._bm25_corpus.keys())
                tokenized = [doc.lower().split() for doc in self._bm25_corpus.values()]
                self._bm25_index = BM25Okapi(tokenized)
                self._bm25_dirty = False
            except ImportError:
                log.debug("rank_bm25 not installed; BM25 search disabled.")
                return None
        return self._bm25_index

    def _bm25_search(self, query: str, k: int) -> list[str]:
        bm25 = self._get_bm25()
        if bm25 is None:
            return []
        tokens = query.lower().split()
        scores = bm25.get_scores(tokens)
        top_k = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [self._bm25_paths[i] for i in top_k if scores[i] > 0]

    # ── Public API ─────────────────────────────────────────────────────────

    def search(self, query: str, limit: int = 50) -> list["MediaFile"]:
        """Synchronous wrapper — safe to call from a Qt thread."""
        return asyncio.run(self.search_async(query, limit))

    async def search_async(self, query: str, limit: int = 50) -> list["MediaFile"]:
        query = query.strip()
        if not query:
            return []

        search_filter, clean_query = FilterParser.parse(query)
        log.debug("Search: %r | filter=%s", clean_query, search_filter)

        seen_paths: set[str] = set()
        merged: list["MediaFile"] = []

        # 1. Semantic results — fetch DB records for each returned path
        if self.config.enable_ai and clean_query:
            try:
                semantic_paths = self._get_semantic().query(clean_query, n_results=_SEMANTIC_K)
                if semantic_paths:
                    sem_records = await self.db.get_files_by_paths(semantic_paths)
                    # Preserve semantic ranking order
                    path_to_record = {r.path: r for r in sem_records}
                    for path in semantic_paths:
                        if path in path_to_record and path not in seen_paths:
                            seen_paths.add(path)
                            merged.append(path_to_record[path])
            except Exception:
                log.warning("Semantic search failed; continuing with keyword search.")

        # 2. BM25 results
        if clean_query:
            bm25_paths = self._bm25_search(clean_query, _BM25_K)
            if bm25_paths:
                bm25_records = await self.db.get_files_by_paths(bm25_paths)
                for r in bm25_records:
                    if r.path not in seen_paths:
                        seen_paths.add(r.path)
                        merged.append(r)

        # 3. SQLite LIKE fallback
        remaining = max(0, limit - len(merged))
        if remaining > 0 or not merged:
            db_results = await self.db.search_files(clean_query, limit=limit)
            for r in db_results:
                if r.path not in seen_paths:
                    seen_paths.add(r.path)
                    merged.append(r)

        # 4. Apply metadata filters
        results = [f for f in merged if search_filter.matches(f)]

        await self.db.record_search(query=query, result_count=len(results))
        return results[:limit]

    def index_embedding(self, path: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        """Store an embedding in ChromaDB and update the BM25 corpus."""
        self._get_semantic().add(doc_id=path, embedding=embedding, metadata=metadata)

        # Build BM25 document from filename + tags + summary
        doc_tokens = " ".join([
            metadata.get("filename", ""),
            metadata.get("tags", ""),
            metadata.get("summary", ""),
        ]).strip()
        if doc_tokens:
            self._bm25_corpus[path] = doc_tokens
            self._bm25_dirty = True

    def add_to_bm25(self, path: str, text: str) -> None:
        """Add / update a file in the BM25 index without a vector embedding."""
        self._bm25_corpus[path] = text
        self._bm25_dirty = True

    def remove_from_index(self, path: str) -> None:
        """Remove a file from both the vector index and BM25 corpus."""
        try:
            self._get_semantic().delete(path)
        except Exception:
            pass
        self._bm25_corpus.pop(path, None)
        self._bm25_dirty = True
