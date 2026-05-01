"""Library browser endpoints — paginated file listing."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

router = APIRouter()


def get_db(request: Request) -> Any:
    return request.app.state.services["db"]


class FileRecord(BaseModel):
    id: int
    path: str
    filename: str
    size_bytes: int
    mime_type: str | None
    duration_seconds: float | None
    width: int | None
    height: int | None
    ai_tags: list[str]
    ai_summary: str | None
    indexed_at: str


class LibraryPage(BaseModel):
    items: list[FileRecord]
    total: int
    page: int
    page_size: int


def _to_record(r: Any) -> FileRecord:
    return FileRecord(
        id=r.id,
        path=r.path,
        filename=r.filename,
        size_bytes=r.size_bytes or 0,
        mime_type=r.mime_type,
        duration_seconds=r.duration_seconds,
        width=r.width,
        height=r.height,
        ai_tags=r.get_tags() if hasattr(r, "get_tags") else [],
        ai_summary=r.ai_summary,
        indexed_at=r.indexed_at.isoformat() if r.indexed_at else "",
    )


@router.get("/library", response_model=LibraryPage)
async def list_library(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    mime_type: str | None = Query(None, description="Filter by MIME type prefix e.g. video, audio, image"),
    db: Any = Depends(get_db),
) -> LibraryPage:
    from sqlalchemy import select, func
    from arqyv.database.models import MediaFile

    async with db.session() as session:
        q = select(MediaFile)
        if mime_type:
            q = q.where(MediaFile.mime_type.ilike(f"{mime_type}%"))

        count_q = select(func.count()).select_from(q.subquery())
        total = (await session.execute(count_q)).scalar_one()
        q = q.offset((page - 1) * page_size).limit(page_size)
        rows = (await session.execute(q)).scalars().all()

    return LibraryPage(
        items=[_to_record(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/files/{file_id}", response_model=FileRecord)
async def get_file(file_id: int, db: Any = Depends(get_db)) -> FileRecord:
    from sqlalchemy import select
    from arqyv.database.models import MediaFile

    async with db.session() as session:
        row = (
            await session.execute(select(MediaFile).where(MediaFile.id == file_id))
        ).scalar_one_or_none()

    if not row:
        raise HTTPException(status_code=404, detail="File not found")
    return _to_record(row)
