# ARQYV User Manual

Complete reference for every feature in ARQYV. For a quick-start guide see [Getting Started](getting-started.md).

---

## Table of Contents

1. [Overview](#1-overview)
2. [Installation & Requirements](#2-installation--requirements)
3. [Application Layout](#3-application-layout)
4. [Library & Indexing](#4-library--indexing)
5. [Search System](#5-search-system)
6. [Media Playback](#6-media-playback)
7. [AI Analysis](#7-ai-analysis)
8. [Smart Collections](#8-smart-collections)
9. [Content Deduplication](#9-content-deduplication)
10. [File Sharing (P2P)](#10-file-sharing-p2p)
11. [Cloud Sync](#11-cloud-sync)
12. [Audio DSP & EQ](#12-audio-dsp--eq)
13. [Voice Search](#13-voice-search)
14. [Command Palette](#14-command-palette)
15. [Themes](#15-themes)
16. [Settings Reference](#16-settings-reference)
17. [REST API](#17-rest-api)
18. [WebSocket Events](#18-websocket-events)
19. [Plugin System](#19-plugin-system)
20. [Configuration Reference](#20-configuration-reference)
21. [Building from Source](#21-building-from-source)
22. [Distributable Binaries](#22-distributable-binaries)
23. [Troubleshooting](#23-troubleshooting)

---

## 1. Overview

ARQYV is an offline-first desktop application that functions as your personal media intelligence layer. It combines:

- A high-performance indexer that processes tens of thousands of files per hour
- A three-tier search engine: semantic (vector), BM25 keyword, and SQLite full-text
- A custom media player with zero proprietary codec dependencies
- A peer-to-peer file sharing system that works entirely over LAN
- An AI pipeline that auto-generates tags, summaries, captions, and speech transcripts
- A local REST API consumed by mobile companions and automation scripts

Everything runs locally. No telemetry. No accounts. No subscriptions.

---

## 2. Installation & Requirements

### System requirements

| Platform | Minimum | Recommended |
|---|---|---|
| Windows | 10 (64-bit) | 11 |
| macOS | 12 Monterey | 14 Sonoma |
| Linux | Ubuntu 22.04 | Ubuntu 24.04 |
| Python | 3.11 | 3.12 |
| RAM | 4 GB | 16 GB (for AI models) |
| Disk | 500 MB (app) | 2 GB (with AI models cached) |

### Core dependencies (auto-installed)

```
PyQt6 >= 6.6
SQLAlchemy >= 2.0
aiosqlite
alembic
pydantic >= 2.0
pydantic-settings
fastapi
uvicorn
watchdog
mutagen
Pillow
zeroconf
qrcode
platformdirs
```

### Optional AI dependencies

```bash
pip install sentence-transformers transformers torch openai-whisper
pip install chromadb       # vector database for semantic search
pip install rank-bm25      # BM25 keyword precision layer
pip install sounddevice soundfile  # voice search recording
pip install imagehash      # perceptual deduplication for images
```

If any of these are missing, ARQYV gracefully disables the corresponding feature and logs a warning.

---

## 3. Application Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Menu Bar  │  Tool Bar  [search bar — full width]  │  status   │
├────────────┼────────────────────────────────────────────────────┤
│            │                                                    │
│  Left      │            Content / Player Area                  │
│  Sidebar   │                                                    │
│  ─────────   ────────────────────────────────────────────────  │
│  File       │                                                  │
│  Browser    │  Media Player Controls                           │
│    or       ├────────────────────────────────────────────────  │
│  Search     │  Metadata Panel                                  │
│  Results    │                                                  │
└─────────────┴────────────────────────────────────────────────┘
```

### Left sidebar

Shows either the **File Browser** (tree/grid/list view of your indexed folders) or **Search Results** (when a search is active). Toggle between them automatically when you type in the search bar.

### Content area

Displays the video output surface (when playing video) or a thumbnail/info card for the current file.

### Media player

Fixed control bar below the content area. Includes transport controls, seek bar, volume, and EQ access.

### Metadata panel

Right-side panel showing file metadata: dimensions, duration, codec info, AI tags, AI summary, file size, modification date.

### Status bar

Shows: indexed file count, last operation, API server status (green dot when running), indexing progress.

---

## 4. Library & Indexing

### Watched folders

ARQYV monitors one or more folders and indexes every supported file type. To manage watched folders:

1. **Settings → Library** or **File → Add Watched Folder** (`Ctrl+O`)
2. Click **+ Add Folder**, pick a directory
3. Indexing starts immediately; the watcher stays active and picks up new files automatically

### Supported file types

| Category | Extensions |
|---|---|
| Video | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.3gp`, `.ogv`, `.ts`, `.mts`, `.m2ts` |
| Audio | `.mp3`, `.flac`, `.wav`, `.aac`, `.ogg`, `.opus`, `.m4a`, `.wma`, `.aiff`, `.ape`, `.mka` |
| Image | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, `.tiff`, `.svg`, `.heic` |
| Document | `.pdf`, `.docx`, `.doc`, `.txt`, `.md`, `.xlsx`, `.pptx`, `.epub` |

### Indexing pipeline

For each file, ARQYV:

1. Extracts metadata (duration, dimensions, codec, bitrate, EXIF, ID3 tags via `mutagen` / `pymediainfo`)
2. Generates a thumbnail (stored in the local cache directory)
3. Queues AI analysis if enabled

All steps run in a background thread pool and never block the UI.

### File watcher

After the initial scan, `watchdog` monitors the folder tree for:
- New files → immediately indexed
- Modified files → re-indexed
- Deleted files → removed from library and vector index
- Moved files → old path removed, new path indexed

---

## 5. Search System

ARQYV uses a three-tier merge pipeline for every query:

```
Query
  │
  ├─ 1. Semantic (ChromaDB vector similarity)
  │       Understands meaning, not just keywords
  │
  ├─ 2. BM25 keyword (rank-bm25)
  │       Precise term frequency/inverse frequency scoring
  │
  └─ 3. SQLite LIKE fallback
          filename, ai_tags, ai_summary, ai_transcript
          │
          └─ 4. Metadata filter pass
                 Removes results that don't match type:/date:/size: tokens
```

Results from all three tiers are merged and deduplicated. Semantic results rank first (most relevant by meaning), followed by BM25, then SQLite.

### Live search

Type in the search bar. Results appear within 150 ms (debounced). The sidebar switches from the file browser to a search results panel automatically.

Pressing `Esc` or clicking the `×` button clears the search and returns to the file browser.

### Filter tokens

Append filter tokens to any query:

```
beach vacation type:video date:>2023
interviews ext:.mp4 size:>500mb
cats type:image date:2022
```

| Token | Operators | Example |
|---|---|---|
| `type:` | exact | `type:video`, `type:audio`, `type:image`, `type:document` |
| `ext:` | exact | `ext:.mp4`, `ext:.flac` |
| `date:` | `>`, `<`, `=`, `>=`, `<=` | `date:>2024-01-01` |
| `size:` | `>`, `<`, with `kb`/`mb`/`gb` | `size:>100mb` |

### Semantic search accuracy

Semantic results require AI analysis to have run on a file. Files not yet analyzed fall back to BM25 and SQLite. Enable AI in **Settings → AI / Analysis** for best results.

---

## 6. Media Playback

### Supported playback formats

ARQYV uses Qt Multimedia (platform-native codecs) as the primary backend:

- **Windows**: DirectShow / Media Foundation codecs installed with Windows
- **macOS**: AVFoundation (all system-supported formats)
- **Linux**: GStreamer (install plugins for extended format support)

### Playback controls

| Control | Shortcut | Notes |
|---|---|---|
| Play / Pause | `Space` | |
| Seek backward 10s | `←` | |
| Seek forward 10s | `→` | |
| Volume up | `↑` | 5% increments |
| Volume down | `↓` | |
| Mute / Unmute | `M` | |
| Stop | `S` | Resets position to 0 |
| Fullscreen | `F` | Toggle; `Esc` exits |
| Next in playlist | `]` | |
| Previous in playlist | `[` | |

### Playlist

Files in the current search result or collection act as an implicit playlist. Navigate with `[` and `]`.

### Seeking

Drag the seek bar or click anywhere on it to jump. The current position and total duration are displayed in `HH:MM:SS / HH:MM:SS` format.

---

## 7. AI Analysis

### What AI analysis does

When enabled, ARQYV runs each file through a four-stage pipeline:

1. **Text extraction**
   - Images: BLIP image captioning (`Salesforce/blip-image-captioning-base`)
   - Audio/Video: Whisper speech transcription
   - PDFs: PyMuPDF text extraction
   - DOCX / TXT / MD: direct text read

2. **Embedding** (`sentence-transformers/all-MiniLM-L6-v2` by default)
   - Converts the extracted text to a 384-dimension semantic vector
   - Stored in ChromaDB for similarity search

3. **Tagging** — NLP-based keyword extraction from the text content

4. **Summarization** — abstractive summary of the content

All results are persisted to the database and immediately available in search.

### Model download

On first use, models are downloaded from Hugging Face (~80 MB for MiniLM, ~145 MB for Whisper base). Subsequent launches use the cached versions. Set `TRANSFORMERS_CACHE` or `HF_HOME` to control the download location.

### Inference device

- `auto`: uses CUDA if available, then MPS (Apple Silicon), then CPU
- `cuda`: NVIDIA GPU (dramatically faster for large libraries)
- `mps`: Apple Silicon Neural Engine
- `cpu`: always available; slower for large models

Set in **Settings → AI / Analysis → Inference Device**.

### Whisper model sizes

| Model | Size | Speed (CPU) | Quality |
|---|---|---|---|
| `tiny` | 39 MB | ~32× real-time | Basic |
| `base` | 74 MB | ~16× real-time | Good |
| `small` | 244 MB | ~6× real-time | Better |
| `medium` | 769 MB | ~2× real-time | Great |
| `large` | 1.5 GB | ~1× real-time | Best |

`base` is the default. Use `tiny` for background processing on slower machines; `large` for a research-grade transcript library.

---

## 8. Smart Collections

Collections are automatically computed from your library. They appear in the sidebar under a **Collections** section.

### Collection types

| Type | How it's formed |
|---|---|
| **By type** | Videos, Music, Photos, Documents — MIME type prefix matching |
| **By year** | Files grouped by `fs_modified_at` or `indexed_at` year |
| **By AI tag** | Top 20 most-common AI-generated tags with ≥ 3 files |

### Minimum size

Collections with fewer than 3 files are suppressed to avoid noise.

### Refresh

Collections are re-computed whenever you open the sidebar or press Refresh. They reflect the current state of the DB.

---

## 9. Content Deduplication

Access via **Tools → Find Duplicates** or the command palette.

### Exact duplicates

Identified by SHA-256 hash of full file content. Catches identical files regardless of filename, path, or modification date.

### Near-duplicates (images only)

Uses perceptual hash (pHash via `imagehash`) to find visually similar images — resized, rotated, slightly edited versions of the same photo. Requires `pip install imagehash`.

### Results

The deduplication report shows:

- Duplicate groups, each with a canonical "keep" file (first found)
- Wasted disk space per group
- Total reclaimable space

Use the **Send to Trash** button to safely remove duplicates. ARQYV never permanently deletes without confirmation.

---

## 10. File Sharing (P2P)

### Starting a share

1. Select a file in the library or search results
2. Right-click → **Share** or press `Ctrl+Shift+S`
3. The share dialog opens

### How it works

1. ARQYV starts an ephemeral HTTP server on a random port
2. The server streams the file with range-request support (resumable downloads)
3. A QR code encodes the download URL
4. mDNS/Zeroconf broadcasts the share to other ARQYV instances on the LAN

### QR code

Scan with any phone camera to open the download link in a browser. Works with iOS Safari, Android Chrome, and any QR reader.

### LAN peer list

Other machines running ARQYV on the same network appear in the peer list with a reachability indicator (green ● = reachable, yellow ● = resolving, grey ● = unreachable). Click a peer to send the file directly.

### Transfer progress

A live progress bar and speed readout (MB/s) are shown during active transfers.

### Security

Shares are ephemeral — the server shuts down when the dialog is closed or the file finishes transferring. There is no authentication on the share URL by design (LAN-only). Do not share sensitive files over untrusted networks.

---

## 11. Cloud Sync

Cloud sync integrates with Google Drive, OneDrive, and Dropbox via OAuth.

### Setup

Set credentials via environment variables or `.env` file:

```bash
# Google Drive
ARQYV_CLOUD_GOOGLE_CLIENT_ID=your_client_id
ARQYV_CLOUD_GOOGLE_CLIENT_SECRET=your_client_secret

# OneDrive
ARQYV_CLOUD_ONEDRIVE_CLIENT_ID=your_client_id

# Dropbox
ARQYV_CLOUD_DROPBOX_APP_KEY=your_app_key
ARQYV_CLOUD_DROPBOX_APP_SECRET=your_app_secret
```

Enable in **Settings → Cloud → Enable cloud sync**.

### Behavior

Cloud sync is one-way upload by default — your local library is mirrored to the cloud provider. Two-way sync (pull changes from cloud) is planned for Phase 3.

---

## 12. Audio DSP & EQ

### EQ bands

ARQYV includes a parametric EQ with configurable bands. Each band has:
- **Frequency** (Hz): center frequency
- **Gain** (dB): boost or cut, ±12 dB range
- **Q** (quality factor): controls the bandwidth of the filter

### Built-in presets

| Preset | Description |
|---|---|
| Flat | No processing (default) |
| Bass Boost | Enhanced low frequencies for speakers without subwoofers |
| Vocal Boost | Mid-frequency emphasis for speech and podcasts |
| Cinema | Balanced for dialogue + surround fx |
| Night Mode | Reduced volume + compressed dynamics for late-night listening |

### Accessing EQ

Open the **EQ** panel from the media player toolbar (equalizer icon). Changes take effect immediately.

---

## 13. Voice Search

Press the microphone button in the search bar to start recording. Speak your query naturally. When you stop speaking, Whisper transcribes the audio in a background thread and populates the search bar.

### Requirements

```bash
pip install sounddevice soundfile openai-whisper
```

Enable in **Settings → AI / Analysis → Enable voice search**.

### Privacy

Voice search is 100% local. No audio is sent to any server. Transcription happens on your machine using the locally cached Whisper model.

---

## 14. Command Palette

Press `Ctrl+P` anywhere in ARQYV to open the command palette — a floating searchable list of all actions.

Type to filter. Use `↑` / `↓` to navigate. `Enter` executes. `Esc` dismisses.

Every keyboard shortcut is listed beside its command in the palette.

---

## 15. Themes

### Dark theme (default)

Near-black (#080810) background, electric cyan accents, subtle violet secondary. Optimized for extended use in low-light environments.

### Light theme

Clean white (#f8f9fa) background, blue accents. Optimized for daylit environments and reduced eye strain.

### Switching

**Settings → General → Theme** — takes effect immediately without restart.

Or open the command palette (`Ctrl+P`), type "light" or "dark", and select the theme command.

---

## 16. Settings Reference

Open with `Ctrl+,` or **Edit → Settings**.

### General tab

| Setting | Description |
|---|---|
| Theme | Dark or Light |
| Language | UI language (en, fr, de, es, ja, zh) |
| Auto-index on startup | Index all watched folders when ARQYV launches |
| Enable API server | Start REST API on port 8765 |

### Library tab

Manage watched folders. Add new directories or remove existing ones. Changes take effect immediately — removed folders stop being watched; added folders start indexing now.

### AI / Analysis tab

| Setting | Description |
|---|---|
| Enable AI analysis | Toggle the full AI pipeline |
| Whisper model | tiny / base / small / medium / large |
| Embedding model | sentence-transformers model for semantic search |
| Inference device | auto / cpu / cuda / mps |
| Max worker threads | Parallelism for AI inference |
| Enable voice search | Microphone + Whisper for spoken queries |

### Media tab

Thumbnail dimensions and JPEG quality for the cached thumbnail previews.

### Cloud tab

Enable cloud sync and configure OAuth credentials.

---

## 17. REST API

The local API server runs at `http://127.0.0.1:8765` when enabled.

### Authentication

None — the server binds to localhost only. External access requires a reverse proxy.

### Endpoints

#### `GET /api/v1/library`

Paginated file listing.

Query params:
- `page` (int, default 1)
- `page_size` (int, default 50, max 200)
- `mime_type` (string, optional) — filter prefix e.g. `video`, `audio`, `image`

Response:
```json
{
  "items": [
    {
      "id": 1,
      "path": "/home/user/Movies/film.mp4",
      "filename": "film.mp4",
      "size_bytes": 1234567890,
      "mime_type": "video/mp4",
      "duration_seconds": 5400.0,
      "width": 1920,
      "height": 1080,
      "ai_tags": ["action", "outdoor", "crowd"],
      "ai_summary": "A fast-paced action scene set outdoors.",
      "indexed_at": "2025-01-15T14:32:00"
    }
  ],
  "total": 1042,
  "page": 1,
  "page_size": 50
}
```

#### `GET /api/v1/files/{id}`

Single file detail. Same schema as `items[]` above.

#### `GET /api/v1/search?q={query}&limit={n}`

Unified search (semantic + BM25 + full-text + filters).

Response:
```json
{
  "query": "beach sunset",
  "results": [
    {
      "id": 42,
      "path": "/home/user/Photos/beach.jpg",
      "filename": "beach.jpg",
      "mime_type": "image/jpeg",
      "score": 0.93,
      "ai_summary": "A sunset over the ocean with golden light.",
      "ai_tags": ["sunset", "beach", "nature"],
      "thumbnail_url": "/api/v1/thumbnails/42"
    }
  ],
  "total": 17
}
```

#### `GET /api/v1/thumbnails/{id}`

Returns a JPEG thumbnail (up to 320×240). Generates on-the-fly if not cached.

#### `GET /api/v1/stream/{id}`

HTTP byte-range streaming for media playback in browsers or mobile apps.

### Interactive docs

Visit `http://localhost:8765/docs` for full Swagger UI with live request testing.

---

## 18. WebSocket Events

Connect to `ws://localhost:8765/ws` to receive real-time events.

### Event format

```json
{ "event": "event.name", "payload": { ... } }
```

### Available events

| Event | Payload | Description |
|---|---|---|
| `file.added` | `{ "path": "..." }` | New file indexed |
| `file.changed` | `{ "path": "..." }` | File re-indexed |
| `file.deleted` | `{ "path": "..." }` | File removed from library |
| `index.progress` | `{ "current": 42, "total": 1000, "path": "..." }` | Indexing progress |
| `index.completed` | `{ "path": "...", "total": 1000 }` | Scan finished |
| `playback.state` | `{ "state": "playing", "position_ms": 12000, "duration_ms": 360000, "path": "..." }` | Playback state update |
| `ai.done` | `{ "path": "...", "tags": [...], "summary": "..." }` | AI analysis complete |

---

## 19. Plugin System

Plugins are discovered automatically via Python entry-points.

### Plugin types

#### `MetadataPlugin`

Extract additional metadata not handled by ARQYV's built-in pipeline.

```python
from arqyv.plugins import MetadataPlugin
from pathlib import Path
from typing import Any

class GeoTagPlugin(MetadataPlugin):
    name = "geotag_extractor"
    supported_extensions = [".jpg", ".jpeg", ".heic"]

    def extract(self, path: Path) -> dict[str, Any]:
        # Extract GPS coordinates from EXIF
        return {"latitude": 48.8584, "longitude": 2.2945}
```

#### `TaggerPlugin`

Add custom AI-generated tags.

```python
from arqyv.plugins import TaggerPlugin
from pathlib import Path

class NudityDetector(TaggerPlugin):
    name = "safety_tagger"
    supported_extensions = []  # empty = all types

    def tag(self, path: Path) -> list[str]:
        return ["safe"]  # or ["nsfw"] based on your model
```

#### `PostProcessPlugin`

Run arbitrary logic after a file is indexed.

```python
from arqyv.plugins import PostProcessPlugin
from pathlib import Path
from typing import Any

class SlackNotifier(PostProcessPlugin):
    name = "slack_notifier"
    supported_extensions = [".mp4"]

    def process(self, path: Path, db_record: dict[str, Any]) -> None:
        # Send a Slack message when a new video is indexed
        ...
```

### Registering a plugin

In your plugin package's `pyproject.toml`:

```toml
[project.entry-points."arqyv.plugins"]
my_plugin = "my_package.plugin:MyPlugin"
```

Install your package alongside ARQYV:

```bash
pip install ./my-arqyv-plugin
```

ARQYV discovers and loads it automatically at next launch.

---

## 20. Configuration Reference

All settings can be set via environment variables. ARQYV also reads a `.env` file in the working directory.

| Environment Variable | Default | Type | Description |
|---|---|---|---|
| `ARQYV_THEME` | `dark` | string | `dark` or `light` |
| `ARQYV_LANGUAGE` | `en` | string | UI language code |
| `ARQYV_ENABLE_AI` | `true` | bool | AI analysis pipeline |
| `ARQYV_ENABLE_VOICE_SEARCH` | `true` | bool | Voice search recording |
| `ARQYV_ENABLE_CLOUD_SYNC` | `false` | bool | Cloud provider sync |
| `ARQYV_ENABLE_AUTO_INDEX` | `true` | bool | Index on startup |
| `ARQYV_ENABLE_API_SERVER` | `true` | bool | REST API at 8765 |
| `ARQYV_API_PORT` | `8765` | int | REST API port |
| `ARQYV_WINDOW_WIDTH` | `1440` | int | Initial window width |
| `ARQYV_WINDOW_HEIGHT` | `900` | int | Initial window height |
| `ARQYV_AI_EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | string | Embedding model |
| `ARQYV_AI_WHISPER_MODEL` | `base` | string | Whisper size |
| `ARQYV_AI_DEVICE` | `auto` | string | Torch device |
| `ARQYV_AI_MAX_WORKERS` | `4` | int | AI thread pool size |
| `DATABASE_URL` | SQLite (auto-path) | string | SQLAlchemy DB URL |
| `REDIS_URL` | `redis://localhost:6379/0` | string | Redis for Version B |
| `ARQYV_CLOUD_GOOGLE_CLIENT_ID` | — | string | Google Drive OAuth |
| `ARQYV_CLOUD_GOOGLE_CLIENT_SECRET` | — | string | Google Drive OAuth |
| `ARQYV_CLOUD_ONEDRIVE_CLIENT_ID` | — | string | OneDrive OAuth |
| `ARQYV_CLOUD_DROPBOX_APP_KEY` | — | string | Dropbox OAuth |
| `ARQYV_CLOUD_DROPBOX_APP_SECRET` | — | string | Dropbox OAuth |

Data directories are determined by the OS via `platformdirs`:

| Directory | Windows | macOS | Linux |
|---|---|---|---|
| Data | `%APPDATA%\ARQYV` | `~/Library/Application Support/ARQYV` | `~/.local/share/ARQYV` |
| Config | `%APPDATA%\ARQYV` | `~/Library/Preferences/ARQYV` | `~/.config/ARQYV` |
| Cache | `%LOCALAPPDATA%\ARQYV\Cache` | `~/Library/Caches/ARQYV` | `~/.cache/ARQYV` |

---

## 21. Building from Source

```bash
git clone https://github.com/Alaustrup/arqyv.git
cd arqyv

# Install all dependencies including development extras
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
mypy src/
```

---

## 22. Distributable Binaries

```bash
pip install pyinstaller
pyinstaller arqyv.spec --clean --noconfirm
# Output: dist/ARQYV/
```

CI builds are triggered by pushing a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
# GitHub Actions builds Win/Mac/Linux, creates a GitHub Release
```

---

## 23. Troubleshooting

### ARQYV window doesn't appear

- Check that `QT_QPA_PLATFORM` is not set to `offscreen` in your environment
- Try running `python run.py --debug` and check the log output
- On Windows, the window may appear behind other windows — check the taskbar

### AI analysis is very slow

- Switch inference device to `cuda` (NVIDIA) or `mps` (Apple Silicon) in Settings
- Use a smaller Whisper model (`tiny` instead of `base`)
- Reduce `ARQYV_AI_MAX_WORKERS` to prevent thermal throttling on laptops

### Search returns no results

- Wait for indexing to complete (status bar shows progress)
- Semantic search requires AI analysis — check that AI is enabled
- Try a simpler query first (single keyword) to verify the pipeline works

### File sharing QR code not working

- Ensure both devices are on the same Wi-Fi network
- Check that your firewall allows the random port ARQYV selects
- Try copying the URL manually instead of scanning the QR code

### `ModuleNotFoundError` for AI packages

```bash
pip install sentence-transformers transformers torch openai-whisper
```

ARQYV continues to run without these; only AI features are disabled.

### Database migration errors

```bash
cd src/arqyv/database
alembic upgrade head
```

### Logs

Logs are written to:
- **Windows**: `%APPDATA%\ARQYV\arqyv.log`
- **macOS**: `~/Library/Application Support/ARQYV/arqyv.log`
- **Linux**: `~/.local/share/ARQYV/arqyv.log`

Run with `--debug` for verbose output including SQL queries and AI pipeline timing.
