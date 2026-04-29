# ARQYV

**The last great desktop application — personal data unification, done right.**

> Cross-platform · PyQt6 · Custom Media Engine · Semantic AI Search · P2P Sharing · Local-first · No accounts

ARQYV unifies every file you own — video, audio, documents, photos — across local storage and cloud providers into a single, intelligent, searchable library. It plays anything, understands everything, and lets you share instantly.

---

## Feature Overview

| Feature | Status |
|---|---|
| Cross-platform desktop (Windows / macOS / Linux) | ✅ |
| **ARQYVMediaEngine** — custom media layer, zero external installs | ✅ |
| Magic-byte format detector (40+ formats, pure Python) | ✅ |
| Subtitle engine: SRT / VTT / ASS — pure Python parser + Qt overlay | ✅ |
| Playlist: shuffle, repeat, **smart resume** (remembers position) | ✅ |
| Audio DSP: EQ presets, peak metering | ✅ |
| Qt Multimedia (primary) + VLC (auto-detected upgrade, zero config) | ✅ |
| **ARQYVShare** — instant P2P file sharing, no accounts, no subscriptions | ✅ |
| One-click QR code share → scan on any device, download starts | ✅ |
| LAN peer discovery via mDNS / zeroconf | ✅ |
| Semantic search (sentence-transformers + ChromaDB vector DB) | ✅ |
| Filter tokens: `type:video size:>100mb date:>2024 tag:holiday` | ✅ |
| AI content analysis: image captioning, audio/video transcription, NLP | ✅ |
| Voice search (local Whisper — no cloud, no API key) | ✅ |
| Smart metadata extraction (magic bytes, mutagen, EXIF, PDF, MediaInfo) | ✅ |
| Batch rename engine with template tokens | ✅ |
| Cloud sync: Google Drive, OneDrive, Dropbox (OAuth2) | ✅ |
| File system watcher — auto-indexes on file change | ✅ |
| Thumbnail cache (video frames, audio cover art, PDF pages, images) | ✅ |
| Mobile scaffold: Flutter + React Native | ✅ |
| CI matrix: Windows / macOS / Linux × Python 3.11 / 3.12 | ✅ |
| PyInstaller + Nuitka build pipeline | ✅ |

---

## Project Structure

```
ARQYV/
├── src/arqyv/
│   ├── main.py              # CLI entry point
│   ├── config.py            # Pydantic settings (env-driven)
│   ├── core/
│   │   ├── app.py           # Service orchestrator / lifecycle
│   │   ├── events.py        # Pub/sub EventBus
│   │   └── settings.py      # Persistent user preferences (JSON)
│   ├── ui/
│   │   ├── main_window.py   # QMainWindow with dock layout
│   │   ├── widgets/         # search bar, file browser, media player, preview, metadata
│   │   ├── dialogs/         # settings, batch rename, cloud sync
│   │   └── themes/          # dark.py (charcoal + teal), light.py
│   ├── backend/
│   │   ├── indexer.py       # ThreadPoolExecutor-based directory scanner
│   │   ├── watcher.py       # watchdog FS event handler
│   │   ├── thumbnail.py     # VLC/Pillow/PyMuPDF thumbnail generator + disk cache
│   │   └── transcoder.py    # ffmpeg wrapper for format conversion
│   ├── ai/
│   │   ├── analyzer.py      # Orchestrator (singleton) with lazy model loading
│   │   ├── embedder.py      # sentence-transformers semantic embeddings
│   │   ├── tagger.py        # spaCy NLP → entity + keyword tags
│   │   ├── voice_search.py  # sounddevice recorder + Whisper transcription
│   │   └── summarizer.py    # Extractive summarizer (no GPU required)
│   ├── search/
│   │   ├── engine.py        # Unified search (semantic + full-text + filters)
│   │   ├── semantic.py      # ChromaDB vector store wrapper
│   │   └── filters.py       # Query token parser (type:, ext:, size:, date:, tag:)
│   ├── database/
│   │   ├── db.py            # Async SQLAlchemy 2.x + aiosqlite
│   │   ├── models.py        # MediaFile, Tag, WatchedFolder, SearchHistory
│   │   └── migrations/      # Alembic environment
│   ├── cloud/
│   │   ├── base.py          # CloudProvider ABC
│   │   ├── gdrive.py        # Google Drive (OAuth2 + Drive API v3)
│   │   ├── onedrive.py      # OneDrive (MSAL + Graph API)
│   │   └── dropbox_provider.py
│   ├── engine/              # ARQYVMediaEngine — custom media layer
│   │   ├── core.py          # Central engine: orchestrates backend + playlist + DSP
│   │   ├── format.py        # Magic-byte format detector (40+ formats, pure Python)
│   │   ├── subtitle.py      # SRT/VTT/ASS parser + SubtitleOverlay Qt widget
│   │   ├── playlist.py      # Shuffle, repeat, smart resume (persists position)
│   │   └── audio_dsp.py     # EQ presets, peak metering
│   ├── media/
│   │   ├── player.py        # PlayerBackend protocol + factory (Qt / VLC)
│   │   ├── _qt_backend.py   # Qt Multimedia backend (zero dependencies)
│   │   ├── _vlc_backend.py  # VLC backend (auto-detected, optional)
│   │   ├── vlc_setup.py     # VLC auto-discovery (registry, paths, DLL injection)
│   │   ├── metadata.py      # MediaInfo + mutagen + EXIF + PyMuPDF extractor
│   │   └── codec_manager.py # Runtime codec availability check
│   ├── share/               # ARQYVShare — P2P file sharing
│   │   ├── server.py        # Ephemeral stdlib HTTP server with token auth
│   │   ├── discovery.py     # mDNS/zeroconf LAN peer discovery
│   │   ├── qr.py            # QR code → QPixmap generator
│   │   └── manager.py       # ShareManager public API
│   └── utils/
│       ├── logger.py        # Rich console + rotating file log
│       ├── batch_rename.py  # Template engine ({name}, {date}, {counter}, …)
│       ├── file_ops.py      # Safe delete (trash), copy, move, unique path
│       └── platform_utils.py
├── mobile/
│   ├── flutter/             # Flutter scaffold (iOS + Android)
│   └── react_native/        # RN scaffold (alternative)
├── tests/
│   ├── test_core/           # EventBus, settings
│   ├── test_search/         # Filter parser, semantic
│   ├── test_ai/             # Summarizer, tagger
│   └── test_database/       # DB CRUD integration tests
├── scripts/
│   ├── setup_dev.py         # One-shot dev environment bootstrap
│   └── build.py             # PyInstaller cross-platform build
├── .github/workflows/
│   ├── ci.yml               # Test matrix: Win + macOS + Linux × Python 3.11/3.12
│   └── release.yml          # Tag-triggered binary release
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── alembic.ini
└── .env.example
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Nothing else required — media playback works out of the box via Qt Multimedia (bundled with PyQt6), using OS-native codecs (Windows Media Foundation / AVFoundation / GStreamer).
- **Optional:** Install [VLC](https://www.videolan.org/vlc/) for extended codec support (H.265, AV1, MKV, AC3, DTS…). Auto-detected at startup — no config needed.
- **Optional:** [MediaInfo](https://mediaarea.net/en/MediaInfo) CLI for deeper technical metadata extraction.
- **Optional:** ffmpeg for format transcoding.

### 1. Clone and set up dev environment

```bash
git clone https://github.com/Alaustrup/arqyv.git
cd arqyv

# Automated setup (installs deps, spaCy model, pre-commit hooks)
python scripts/setup_dev.py
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env – cloud credentials, AI model sizes, etc.
```

### 3. Run

```bash
arqyv
# or with debug logging:
arqyv --debug
```

---

## Configuration

All settings are driven by environment variables (or `.env`) with the `ARQYV_` prefix.
See `.env.example` for the full list.

Key options:

| Variable | Default | Description |
|---|---|---|
| `ARQYV_THEME` | `dark` | `dark` or `light` |
| `ARQYV_ENABLE_AI` | `true` | Toggle AI analysis pipeline |
| `ARQYV_AI_WHISPER_MODEL` | `base` | Whisper model size (`tiny`→`large`) |
| `ARQYV_AI_DEVICE` | `auto` | `cpu`, `cuda`, `mps`, or `auto` |
| `ARQYV_ENABLE_CLOUD_SYNC` | `false` | Enable cloud provider integrations |
| `ARQYV_DB_URL` | _(auto)_ | Override SQLite path or use PostgreSQL |

---

## Search Syntax

ARQYV supports natural-language queries enriched with filter tokens:

```
beach sunset type:video date:>2024-01 size:<500mb
holiday portrait type:image tag:family
interview ext:.mp4 date:>2023-06-01
```

| Token | Example | Description |
|---|---|---|
| `type:` | `type:video` | Filter by media type group |
| `ext:` | `ext:.flac` | Exact file extension |
| `size:` | `size:>50mb` | File size comparison |
| `date:` | `date:>2024-01` | Modification date comparison |
| `tag:` | `tag:vacation` | AI-generated tag contains |

---

## AI Pipeline

1. **Indexer** scans files and submits to AI queue (non-blocking).
2. **MetadataExtractor** pulls technical data (resolution, duration, codec).
3. **AIAnalyzer** routes by file type:
   - **Image** → BLIP image captioning (HuggingFace)
   - **Video/Audio** → Whisper transcription
   - **PDF/DOCX** → direct text extraction
4. **Embedder** produces 384-dim sentence-transformer vectors.
5. **Tagger** uses spaCy NER + noun chunks for keyword extraction.
6. **Summarizer** generates an extractive summary (no GPU needed).
7. Vectors are stored in **ChromaDB** for sub-100ms semantic search.

---

## Building Standalone Executables

```bash
# Windows
python scripts/build.py --platform win

# macOS
python scripts/build.py --platform mac

# Linux
python scripts/build.py --platform linux
```

Output: `dist/ARQYV/` – a self-contained directory ready for distribution.

---

## Running Tests

```bash
pytest tests/ -v --cov=src/arqyv
```

CI runs the full matrix across Windows, macOS, and Linux on Python 3.11 and 3.12.

---

## Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Generate a new migration after model changes
alembic revision --autogenerate -m "add new column"
```

---

## Mobile Client

See [`mobile/README.md`](mobile/README.md) for the Flutter and React Native scaffold.
The mobile clients connect to an ARQYV API server (FastAPI, to be implemented)
at `localhost:8765`.

---

## Roadmap

- [ ] FastAPI local API server (enable mobile + remote control)
- [ ] GPU-accelerated AI inference (CUDA / MPS auto-detection)
- [ ] Duplicate detection (perceptual hashing)
- [ ] Face recognition clustering
- [ ] IPTC/XMP metadata write-back
- [ ] Advanced timeline view
- [ ] Plugin system

---

## License

MIT © Alaustrup
