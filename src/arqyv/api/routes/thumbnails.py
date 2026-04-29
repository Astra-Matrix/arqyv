"""Thumbnail endpoint — returns a JPEG thumbnail for any indexed file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, Response

router = APIRouter()


def get_services(request: Request) -> dict[str, Any]:
    return request.app.state.services


@router.get("/thumbnails/{file_id}")
async def get_thumbnail(file_id: int, services: dict[str, Any] = Depends(get_services)) -> Response:
    from sqlalchemy import select
    from arqyv.database.models import MediaFile

    db = services["db"]
    async with db.session() as session:
        row = (await session.execute(select(MediaFile).where(MediaFile.id == file_id))).scalar_one_or_none()

    if not row:
        raise HTTPException(status_code=404, detail="File not found")

    # Return cached thumbnail if it exists
    cache_path = Path(row.thumbnail_path) if getattr(row, "thumbnail_path", None) else None
    if cache_path and cache_path.exists():
        return FileResponse(str(cache_path), media_type="image/jpeg")

    # Generate on the fly for images
    file_path = Path(row.path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Source file not found on disk")

    if row.media_type == "image":
        try:
            from PIL import Image
            import io
            img = Image.open(file_path)
            img.thumbnail((320, 320))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=80)
            return Response(content=buf.getvalue(), media_type="image/jpeg")
        except Exception:
            raise HTTPException(status_code=500, detail="Thumbnail generation failed")

    raise HTTPException(status_code=404, detail="No thumbnail available")
