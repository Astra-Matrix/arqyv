"""Media streaming endpoint — byte-range aware file streaming.

Supports HTTP range requests so mobile media players can seek without
downloading the entire file. Works with any file type on disk.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

router = APIRouter()

CHUNK = 1024 * 256  # 256 KB chunks


def get_db(request: Request) -> Any:
    return request.app.state.services["db"]


def _guess_mime(path: Path) -> str:
    import mimetypes
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


@router.get("/stream/{file_id}")
async def stream_file(file_id: int, request: Request, db: Any = Depends(get_db)) -> StreamingResponse:
    from sqlalchemy import select
    from arqyv.database.models import MediaFile

    async with db.session() as session:
        row = (await session.execute(select(MediaFile).where(MediaFile.id == file_id))).scalar_one_or_none()

    if not row:
        raise HTTPException(status_code=404, detail="File not found")

    path = Path(row.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    file_size = path.stat().st_size
    mime = _guess_mime(path)

    # Parse Range header (bytes=start-end)
    range_header = request.headers.get("Range")
    start = 0
    end = file_size - 1

    if range_header:
        try:
            unit, rng = range_header.split("=")
            s, e = rng.split("-")
            start = int(s) if s else 0
            end = int(e) if e else file_size - 1
        except (ValueError, IndexError):
            raise HTTPException(status_code=416, detail="Invalid Range header")

    content_length = end - start + 1
    status_code = 206 if range_header else 200

    def iter_file() -> Any:
        with open(path, "rb") as f:
            f.seek(start)
            remaining = content_length
            while remaining > 0:
                data = f.read(min(CHUNK, remaining))
                if not data:
                    break
                remaining -= len(data)
                yield data

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Type": mime,
    }
    return StreamingResponse(iter_file(), status_code=status_code, headers=headers, media_type=mime)
