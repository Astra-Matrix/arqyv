"""ARQYV Local API Server.

FastAPI application exposing REST + WebSocket endpoints at localhost:8765.
Used by the mobile clients (Flutter / React Native) and future integrations.

Endpoints:
  GET  /api/v1/health          — liveness check
  GET  /api/v1/library         — list indexed files (paginated)
  GET  /api/v1/search          — unified search (semantic + filters)
  GET  /api/v1/files/{id}      — single file metadata
  GET  /api/v1/thumbnails/{id} — thumbnail image (JPEG)
  GET  /api/v1/stream/{id}     — byte-range media stream
  POST /api/v1/playback        — remote playback control
  WS   /ws                     — real-time push (index progress, playback state)
"""
