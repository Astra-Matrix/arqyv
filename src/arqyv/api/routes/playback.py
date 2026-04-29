"""Remote playback control — mobile clients can control desktop player."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class PlaybackCommand(BaseModel):
    action: Literal["play", "pause", "stop", "next", "previous", "seek", "volume", "open"]
    value: float | str | None = None  # seek fraction / volume 0-100 / file path


class PlaybackState(BaseModel):
    state: str
    position_ms: int
    duration_ms: int
    path: str | None
    volume: int


def get_engine(request: Request) -> Any:
    services = request.app.state.services
    mw = services.get("main_window")
    if mw is None:
        return None
    player = getattr(mw, "_player", None)
    return getattr(player, "_engine", None) if player else None


@router.post("/playback")
async def send_command(cmd: PlaybackCommand, request: Request) -> dict[str, str]:
    engine = get_engine(request)
    if engine is None:
        raise HTTPException(status_code=503, detail="Media engine not available")

    match cmd.action:
        case "play":
            engine.play()
        case "pause":
            engine.pause()
        case "stop":
            engine.stop()
        case "next":
            engine.play_next()
        case "previous":
            engine.play_previous()
        case "seek":
            if cmd.value is not None:
                engine.seek(float(cmd.value))
        case "volume":
            if cmd.value is not None:
                engine.set_volume(int(cmd.value))
        case "open":
            if cmd.value:
                engine.open(str(cmd.value))
        case _:
            raise HTTPException(status_code=400, detail=f"Unknown action: {cmd.action}")

    return {"status": "ok"}


@router.get("/playback", response_model=PlaybackState)
async def get_state(request: Request) -> PlaybackState:
    engine = get_engine(request)
    if engine is None:
        return PlaybackState(state="unavailable", position_ms=0, duration_ms=0, path=None, volume=0)

    current = engine.playlist.current
    backend = getattr(engine, "_backend", None)
    vol = int(getattr(getattr(engine, "dsp", None), "volume", 1.0) * 100)

    return PlaybackState(
        state="playing" if engine.is_playing else "paused",
        position_ms=engine.position_ms,
        duration_ms=engine.duration_ms,
        path=str(current) if current else None,
        volume=vol,
    )
