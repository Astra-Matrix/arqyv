"""FastAPI application factory."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arqyv.api.routes import health, library, search, playback, thumbnails, stream
from arqyv.api.ws import router as ws_router


def create_app(services: dict[str, Any]) -> FastAPI:
    app = FastAPI(
        title="ARQYV API",
        version="1.0.0",
        description="Local API for ARQYV desktop — used by mobile clients and remote control.",
        docs_url="/docs",
        redoc_url=None,
    )

    # Allow any local client (Flutter emulator, React Native, browser dev tools)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inject services into app state so route handlers can access them
    app.state.services = services

    # Routers
    prefix = "/api/v1"
    app.include_router(health.router,     prefix=prefix, tags=["health"])
    app.include_router(library.router,    prefix=prefix, tags=["library"])
    app.include_router(search.router,     prefix=prefix, tags=["search"])
    app.include_router(playback.router,   prefix=prefix, tags=["playback"])
    app.include_router(thumbnails.router, prefix=prefix, tags=["thumbnails"])
    app.include_router(stream.router,     prefix=prefix, tags=["stream"])
    app.include_router(ws_router,                        tags=["websocket"])

    return app
