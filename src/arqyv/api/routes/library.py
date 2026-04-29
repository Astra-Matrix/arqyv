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
    name: str
    size: int
    media_type: str | None
    duration_s: float | None
    width: int | None
    height: int | None
    ai_tags: list[str]
    ai_caption: str | None
    indexed_at: str


class LibraryPage(BaseModel):
    items: list[FileRecord]
    total: int
    page: int
    page_size: int


@router.get("/library", response_model=LibraryPage)
async def list_library(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    media_type: str | None = Query(None, description="Filter: video | audio | image | document"),
    db: Any = Depends(get_db),
) -> LibraryPage:
    from sqlalchemy import select, func
    from arqyv.database.models import MediaFile

    async with db.session() as session:
        q = select(MediaFile)
        if media_type:
            q = q.where(MediaFile.media_type == media_type)

        count_q = select(func.count()).select_from(q.subquery())
        total = (await session.execute(count_q)).scalar_one()

        q = q.offset((page - 1) * page_size).limit(page_size)
        rows = (await session.execute(q)).scalars().all()

    items = [
        FileRecord(
            id=r.id,
            path=r.path,
            name=r.name,
            size=r.size or 0,
            media_type=r.media_type,
            duration_s=r.duration_s,
            width=r.width,
            height=r.height,
            ai_tags=r.ai_tags or [],
            ai_caption=r.ai_caption,
            indexed_at=r.indexed_at.isoformat() if r.indexed_at else "",
        )
        for r in rows
    ]
    return LibraryPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/files/{file_id}", response_model=FileRecord)
async def get_file(file_id: int, db: Any = Depends(get_db)) -> FileRecord:
    from sqlalchemy import select
    from arqyv.database.models import MediaFile

    async with db.session() as session:
        row = (await session.execute(select(MediaFile).where(MediaFile.id == file_id))).scalar_one_or_none()

    if not row:
        raise HTTPException(status_code=404, detail="File not found")

    return FileRecord(
        id=row.id,
        path=row.path,
        name=row.name,
        size=row.size or 0,
        media_type=row.media_type,
        duration_s=row.duration_s,
        width=row.width,
        height=row.height,
        ai_tags=row.ai_tags or [],
        ai_caption=row.ai_caption,
        indexed_at=row.indexed_at.isoformat() if row.indexed_at else "",
    )
