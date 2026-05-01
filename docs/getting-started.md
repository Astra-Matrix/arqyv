# Getting Started with ARQYV

This guide takes you from zero to a fully running personal media library in under 10 minutes.

---

## 1. Installation

### From source (recommended for now)

```bash
git clone https://github.com/Alaustrup/arqyv.git
cd arqyv
python -m pip install -e .
```

### Minimum Python version

Python **3.11** or later is required. Verify:

```bash
python --version
# Python 3.11.x or higher
```

### Optional AI dependencies

For full AI features (auto-tags, image captions, voice search):

```bash
pip install sentence-transformers transformers torch openai-whisper
```

If these are not installed, ARQYV runs in metadata-only mode and disables AI analysis automatically.

---

## 2. Launch

**Windows** (double-click or run from command prompt):
```
launch.bat
```

**Any platform** (from the repo root):
```bash
python run.py
```

**Command-line options:**
```
python run.py --help
python run.py --debug         # verbose log output
python run.py --no-ai         # disable AI analysis
python run.py --no-api        # disable REST API server
```

---

## 3. Add your first media folder

1. When ARQYV opens, click **File → Add Watched Folder** (or press `Ctrl+O`).
2. Select any folder containing videos, music, images, or documents.
3. Indexing starts immediately in the background — a progress bar appears in the status bar.
4. Once indexing finishes, your files appear in the left sidebar.

ARQYV watches the folder for changes after indexing. New files are picked up automatically.

---

## 4. Search your library

### Live search
Click the search bar (or press `/`) and start typing. Results appear instantly:

- Type `video` → all video files
- Type `.mp4` → files with that extension
- Type `beach` → files with "beach" in filename, AI tags, or transcripts
- Type `2023` → files from that year

### Filter tokens
Narrow results with inline filters:

| Token | Example | Effect |
|---|---|---|
| `type:` | `type:video` | Filter by media type |
| `ext:` | `ext:.flac` | Filter by file extension |
| `date:` | `date:>2024` | Files modified after 2024 |
| `size:` | `size:>100mb` | Files larger than 100 MB |

Example: `beach type:video date:>2023`

### Semantic search
When AI analysis is enabled, ARQYV understands meaning — not just filenames:
- `interview footage` finds videos with speech about interviews
- `sunset over water` finds images and videos matching that scene description
- `contract document` finds PDFs containing contract language

---

## 5. Play media

Double-click any file in the library or search results to play it immediately.

### Playback controls

| Action | Shortcut |
|---|---|
| Play / Pause | `Space` |
| Skip forward 10s | `→` |
| Skip back 10s | `←` |
| Volume up | `↑` |
| Volume down | `↓` |
| Mute | `M` |
| Fullscreen (video) | `F` |
| Next track | `]` |
| Previous track | `[` |
| Stop | `S` |

---

## 6. Share a file (P2P LAN)

1. Right-click any file → **Share File** (or select it and press `Ctrl+Shift+S`).
2. The share dialog opens, showing:
   - A **QR code** — scan with any phone on the same Wi-Fi to download
   - A **direct URL** — paste into any browser on the LAN
   - A **peer list** — one-click send to discovered ARQYV instances
3. Transfer progress and speed are shown in real time.

No internet required. No accounts. No cloud storage consumed.

---

## 7. Keyboard shortcuts

Press `Ctrl+P` to open the **Command Palette** — a searchable list of all actions.

| Shortcut | Action |
|---|---|
| `Ctrl+P` | Command Palette |
| `Ctrl+O` | Open / Add Folder |
| `Ctrl+Shift+O` | Open Files |
| `Ctrl+Shift+S` | Share Selected File |
| `Ctrl+,` | Settings |
| `Ctrl+Q` | Quit |
| `/` | Focus Search Bar |
| `Esc` | Clear Search / Close Panel |
| `Space` | Play / Pause |
| `F` | Toggle Fullscreen |
| `M` | Mute |

---

## 8. Auto-collections

ARQYV automatically groups your files into smart collections visible in the sidebar:

- **By type**: Videos, Music, Photos, Documents
- **By year**: 2024, 2023, 2022, …
- **By AI tag**: Collections named after the most common tags in your library (requires AI analysis)

Click any collection to browse its contents. Collections update automatically as new files are indexed.

---

## 9. Settings

Open **Settings** with `Ctrl+,` or **Edit → Settings**.

Key settings:
- **General**: Theme (dark/light), language, auto-index on startup
- **Library**: Add / remove watched folders
- **AI / Analysis**: Whisper model size, embedding model, inference device (CPU/GPU)
- **Cloud**: Enable Google Drive / OneDrive / Dropbox sync

---

## 10. Next steps

- Read the [User Manual](user-manual.md) for full documentation of every feature.
- Install ARQYV on your phone using the Flutter companion app (coming in Phase 3).
- Extend ARQYV with your own metadata extractors or taggers via the [Plugin System](user-manual.md#plugins).
