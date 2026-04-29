"""Search endpoint — unified semantic + full-text + filter query."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel

router = APIRouter()


def get_search(request: Request) -> Any:
    return request.app.state.services["search"]


class SearchResult(BaseModel):
    id: int
    path: str
    name: str
    media_type: str | None
    score: float
    ai_caption: str | None
    ai_tags: list[str]
    thumbnail_url: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Natural language query with optional filter tokens"),
    limit: int = Query(30, ge=1, le=100),
    search_engine: Any = Depends(get_search),
) -> SearchResponse:
    raw = await search_engine.query(q, limit=limit)

    results = [
        SearchResult(
            id=r.id,
            path=r.path,
            name=r.name,
            media_type=r.media_type,
            score=getattr(r, "score", 1.0),
            ai_caption=r.ai_caption,
            ai_tags=r.ai_tags or [],
            thumbnail_url=f"/api/v1/thumbnails/{r.id}",
        )
        for r in raw
    ]
    return SearchResponse(query=q, results=results, total=len(results))
