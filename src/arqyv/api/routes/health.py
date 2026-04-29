"""Health / liveness endpoint."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    api_version: str = "1"


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    from arqyv import __version__
    return HealthResponse(status="ok", version=__version__)
