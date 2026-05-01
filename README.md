# ARQYV

**AI-Powered Personal Media Library** — search, play, organize, and share every file you own, on every device, forever.

[![Build](https://github.com/Alaustrup/arqyv/actions/workflows/build.yml/badge.svg)](https://github.com/Alaustrup/arqyv/actions/workflows/build.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6-green)](https://pypi.org/project/PyQt6)
[![License: MIT](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

---

## What is ARQYV?

ARQYV is a cross-platform desktop application that turns your local file collection into a fully-searchable, AI-understood personal media vault. It indexes every video, audio track, image, and document; enriches them with AI-generated tags, summaries, and embeddings; and surfaces exactly what you need in milliseconds — with or without an internet connection.

### Core capabilities

| Capability | Details |
|---|---|
| **Smart search** | Semantic (Chroma vector DB) + BM25 keyword + SQLite full-text, merged and ranked |
| **Live search** | Results appear as you type — no Enter required |
| **AI analysis** | Auto-tagging via NLP, image captioning via BLIP, speech transcription via Whisper |
| **Custom media engine** | Qt Multimedia primary; optional VLC upgrade; zero proprietary dependencies |
| **Peer-to-peer sharing** | Instant LAN share with QR code, mDNS discovery, HTTP streaming |
| **Smart collections** | Auto-generated groups by type, year, and AI tag clusters |
| **Content deduplication** | SHA-256 exact + perceptual hash (pHash) near-duplicate detection |
| **Plugin system** | Drop in any entry-point plugin to extend metadata, tagging, or post-processing |
| **Local REST API** | FastAPI server on port 8765 — drive ARQYV from scripts or a Flutter mobile app |
| **WebSocket bridge** | Real-time push events for mobile clients and dashboards |
| **Cloud sync** | Google Drive, OneDrive, Dropbox (OAuth keys via environment variables) |
| **Voice search** | Speak a query; Whisper transcribes and searches |
| **Command palette** | Press Ctrl+P for keyboard-first access to every action |
| **Light & dark themes** | Full theme system; toggle in Settings |

---

## Quick start

### Requirements
- Python 3.11 or later
- Windows 10+, macOS 12+, or Ubuntu 22.04+

### Install from source

```bash
git clone https://github.com/Alaustrup/arqyv.git
cd arqyv
python -m pip install -e ".[dev]"
```

### Launch

```bash
# Windows (recommended — suppresses console)
launch.bat

# Any platform
python run.py

# With optional arguments
python run.py --debug          # verbose logging
python run.py --no-ai          # skip AI analysis
python run.py --no-api         # skip REST API server
```

### First run

1. ARQYV opens and prompts you to add a watched folder.
2. Go to **Settings → Library → Add Folder** and pick your media directory.
3. Indexing runs in the background — watch the status bar for progress.
4. Start typing in the search bar to find anything instantly.

---

## Project structure

```
arqyv/
├── run.py                  # Monolith launcher
├── launch.bat              # Windows launcher (windowless)
├── arqyv.spec              # PyInstaller build spec
├── pyproject.toml
├── src/arqyv/
│   ├── ai/                 # Embedder, tagger, summarizer, voice search
│   ├── api/                # FastAPI app, routes, WebSocket bridge
│   ├── backend/            # Indexer, FileWatcher, thumbnails, collections, dedup
│   ├── config.py           # Pydantic settings (env var overrides)
│   ├── core/               # EventBus, Redis pub/sub (Version B)
│   ├── database/           # SQLAlchemy models, async DB, Alembic migrations
│   ├── engine/             # Custom media engine, audio DSP, EQ presets
│   ├── media/              # Metadata extractor, thumbnail generator
│   ├── plugins/            # Plugin base classes and registry
│   ├── search/             # SearchEngine, SemanticSearch, BM25, filters
│   ├── share/              # P2P share server, mDNS discovery, QR code
│   ├── ui/
│   │   ├── dialogs/        # Settings, share, batch rename
│   │   ├── themes/         # dark.py, light.py
│   │   └── widgets/        # Search bar, media player, file browser, …
│   └── workers/            # Microservice entry-points (Version B / Docker)
├── docs/
│   ├── user-manual.md
│   └── getting-started.md
└── .github/workflows/
    └── build.yml           # Win/Mac/Linux PyInstaller matrix
```

---

## Configuration

All settings can be overridden by environment variables. Prefix: `ARQYV_`.

| Variable | Default | Description |
|---|---|---|
| `ARQYV_THEME` | `dark` | `dark` or `light` |
| `ARQYV_ENABLE_AI` | `true` | Enable AI analysis |
| `ARQYV_ENABLE_API_SERVER` | `true` | Start REST API on port 8765 |
| `ARQYV_API_PORT` | `8765` | REST/WebSocket port |
| `ARQYV_AI_WHISPER_MODEL` | `base` | Whisper model size |
| `ARQYV_AI_DEVICE` | `auto` | `cpu`, `cuda`, `mps`, or `auto` |
| `DATABASE_URL` | SQLite | Override with Postgres for Version B |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis for microservice mode |
| `ARQYV_CLOUD_GOOGLE_CLIENT_ID` | — | Google Drive OAuth |
| `ARQYV_CLOUD_ONEDRIVE_CLIENT_ID` | — | OneDrive OAuth |
| `ARQYV_CLOUD_DROPBOX_APP_KEY` | — | Dropbox OAuth |

See `src/arqyv/config.py` for all available settings.

---

## Building distributable binaries

```bash
pip install pyinstaller
pyinstaller arqyv.spec --clean --noconfirm
# Output: dist/ARQYV/
```

CI builds for Win/Mac/Linux are triggered on any `v*.*.*` tag push.

---

## Extending with plugins

Create a package, subclass `MetadataPlugin`, `TaggerPlugin`, or `PostProcessPlugin`, and register it:

```toml
[project.entry-points."arqyv.plugins"]
my_plugin = "my_package.plugin:MyPlugin"
```

Then `pip install` your package and ARQYV discovers it automatically at launch.

---

## REST API

The local API runs at `http://localhost:8765` when `ARQYV_ENABLE_API_SERVER=true`.

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/library` | GET | Paginated file listing |
| `/api/v1/files/{id}` | GET | Single file details |
| `/api/v1/search?q=…` | GET | Unified search |
| `/api/v1/thumbnails/{id}` | GET | JPEG thumbnail |
| `/api/v1/stream/{id}` | GET | HTTP range-request media stream |
| `/ws` | WebSocket | Real-time events (index progress, playback state) |

Full OpenAPI docs: `http://localhost:8765/docs`

---

## License

MIT © 2025 Alaustrup
