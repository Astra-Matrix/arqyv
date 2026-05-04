#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  ARQYV — One-line installer for macOS & Linux
#  Usage: curl -fsSL https://arqyv.app/install.sh | bash
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO="https://github.com/Alaustrup/arqyv.git"
INSTALL_DIR="${ARQYV_DIR:-$HOME/.local/share/arqyv}"
BIN_DIR="$HOME/.local/bin"
CYAN='\033[0;36m'; BOLD='\033[1m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

banner() { echo -e "${BOLD}${CYAN}"; cat << 'ART'
    _    ____   _____   ____   __     __
   / \  |  _ \ / _ \ \ / /\ \ / /
  / _ \ | |_) | | | \ V /  \ V /
 / ___ \|  _ <| |_| || |    | |
/_/   \_\_| \_\\__\_\|_|    |_|
ART
echo -e "${NC}  AI-powered personal media library${NC}"; echo; }

info()    { echo -e "  ${CYAN}→${NC} $1"; }
success() { echo -e "  ${GREEN}✓${NC} $1"; }
fatal()   { echo -e "  ${RED}✗${NC} $1"; exit 1; }

require_cmd() { command -v "$1" &>/dev/null || fatal "$1 is required but not installed."; }

# ── Preflight ──────────────────────────────────────────────────────────────
banner
info "Checking prerequisites…"

require_cmd git
require_cmd python3

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [[ "$PY_MAJOR" -lt 3 || ( "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 11 ) ]]; then
  fatal "Python 3.11+ required (found $PY_VER). Install via https://python.org or your package manager."
fi
success "Python $PY_VER found"

# ── Clone / update ─────────────────────────────────────────────────────────
if [[ -d "$INSTALL_DIR/.git" ]]; then
  info "Updating existing install at $INSTALL_DIR…"
  git -C "$INSTALL_DIR" pull --quiet --ff-only
else
  info "Cloning ARQYV into $INSTALL_DIR…"
  git clone --depth 1 "$REPO" "$INSTALL_DIR" --quiet
fi
success "Source ready at $INSTALL_DIR"

# ── Install Python dependencies ────────────────────────────────────────────
info "Installing Python dependencies (this may take a minute)…"
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet -e "$INSTALL_DIR"
success "Dependencies installed"

# ── Optional AI packages ───────────────────────────────────────────────────
if [[ "${ARQYV_AI:-1}" == "1" ]]; then
  info "Installing optional AI packages (Whisper, sentence-transformers)…"
  python3 -m pip install --quiet \
    sentence-transformers \
    openai-whisper \
    chromadb \
    rank-bm25 \
    imagehash 2>/dev/null || info "Some AI packages skipped (no GPU or disk space). ARQYV still runs without them."
fi

# ── Launcher script ────────────────────────────────────────────────────────
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/arqyv" << LAUNCHER
#!/usr/bin/env bash
exec python3 "${INSTALL_DIR}/run.py" "\$@"
LAUNCHER
chmod +x "$BIN_DIR/arqyv"
success "Launcher installed at $BIN_DIR/arqyv"

# ── Desktop entry (Linux) ──────────────────────────────────────────────────
if [[ "$(uname)" == "Linux" ]]; then
  DESKTOP_DIR="$HOME/.local/share/applications"
  mkdir -p "$DESKTOP_DIR"
  cat > "$DESKTOP_DIR/arqyv.desktop" << DESKTOP
[Desktop Entry]
Name=ARQYV
Comment=AI-powered personal media library
Exec=${BIN_DIR}/arqyv
Icon=${INSTALL_DIR}/assets/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Utility;
DESKTOP
  success "Desktop entry created"
fi

# ── PATH hint ──────────────────────────────────────────────────────────────
if ! echo "$PATH" | grep -q "$BIN_DIR"; then
  echo
  echo -e "  ${CYAN}Add this to your shell profile (~/.bashrc or ~/.zshrc):${NC}"
  echo -e "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo
echo -e "${BOLD}${GREEN}  ARQYV installed successfully!${NC}"
echo -e "  Run: ${BOLD}arqyv${NC}   •  Docs: ${CYAN}https://arqyv.app/docs${NC}"
echo
