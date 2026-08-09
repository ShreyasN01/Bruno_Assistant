#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Bruno AI Assistant — Setup Script
# Installs all dependencies and prepares the environment for Bruno.
# Safe to run multiple times (idempotent).
# ─────────────────────────────────────────────────────────────────────────────

# ── Color codes ──────────────────────────────────────────────────────────────
GOLD='\033[38;5;178m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Helper functions ─────────────────────────────────────────────────────────
info()    { echo -e "${GREEN}  ✔ ${RESET}$1"; }
warn()    { echo -e "${YELLOW}  ⚠ ${RESET}$1"; }
error()   { echo -e "${RED}  ✖ ${RESET}$1"; }
step()    { echo -e "\n${GOLD}  ▸ ${BOLD}$1${RESET}"; }
divider() { echo -e "${DIM}  ─────────────────────────────────────────────────────${RESET}"; }

# ── ASCII Art Banner ─────────────────────────────────────────────────────────
echo ""
echo -e "${GOLD}"
cat << 'BANNER'
                         ████████████
                      ██████████████████
                   ██████████████████████████
                ████████████████████████████████
             ██████████████████████████████████████
            ████████████████████████████████████████
           ███████████████████████████████████████████
          ████████████████████████████████████████████
          ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
          ═══════════════════════════════════════════

          ██████╗ ██████╗ ██╗   ██╗███╗  ██╗ ██████╗
          ██╔══██╗██╔══██╗██║   ██║████╗ ██║██╔═══██╗
          ██████╔╝██████╔╝██║   ██║██╔██╗██║██║   ██║
          ██╔══██╗██╔══██╗██║   ██║██║╚████║██║   ██║
          ██████╔╝██║  ██║╚██████╔╝██║ ╚███║╚██████╔╝
          ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚══╝ ╚═════╝

           A I    V O I C E    A S S I S T A N T
         ─────────────────────────────────────────
           By order of the Peaky Blinders.
BANNER
echo -e "${RESET}"
divider

# ── Resolve script directory ─────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── 1. Check Python version ─────────────────────────────────────────────────
step "Checking Python version..."

PYTHON_CMD=""
for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [[ "$major" -eq 3 && "$minor" -ge 11 ]]; then
            PYTHON_CMD="$candidate"
            info "Found $candidate (Python $version)"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    error "Python 3.11+ is required but not found."
    echo -e "  ${DIM}Install Python 3.11+ via:${RESET}"
    echo -e "    ${YELLOW}brew install python@3.12${RESET}"
    echo -e "    ${DIM}or visit https://www.python.org/downloads/${RESET}"
    exit 1
fi

# ── 2. Check / Install Homebrew ──────────────────────────────────────────────
step "Checking for Homebrew..."

if command -v brew &>/dev/null; then
    info "Homebrew is installed"
else
    warn "Homebrew not found — installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for Apple Silicon Macs
    if [[ -f /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    info "Homebrew installed"
fi

# ── 3. Install system dependencies ──────────────────────────────────────────
step "Installing system dependencies (portaudio, ffmpeg)..."

install_brew_package() {
    local pkg="$1"
    if brew list "$pkg" &>/dev/null; then
        info "$pkg is already installed"
    else
        warn "Installing $pkg..."
        brew install "$pkg"
        info "$pkg installed"
    fi
}

install_brew_package portaudio
install_brew_package ffmpeg

# ── 4. Create Python virtual environment ────────────────────────────────────
step "Setting up Python virtual environment..."

VENV_DIR="$SCRIPT_DIR/venv"
if [[ -d "$VENV_DIR" ]]; then
    info "Virtual environment already exists at ./venv"
else
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    info "Created virtual environment at ./venv"
fi

# ── 5. Activate venv & install requirements ─────────────────────────────────
step "Installing Python dependencies..."

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
info "Activated virtual environment"

pip install --upgrade pip --quiet
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
info "All Python packages installed"

# ── 6. Copy .env.example → .env ─────────────────────────────────────────────
step "Checking environment file..."

if [[ -f "$SCRIPT_DIR/.env" ]]; then
    info ".env file already exists — not overwriting"
else
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    info "Created .env from .env.example"
fi

# ── Done! ────────────────────────────────────────────────────────────────────
echo ""
divider
echo ""
echo -e "${GOLD}${BOLD}  ✅ Bruno is ready.${RESET}"
echo ""
echo -e "  ${BOLD}Next steps:${RESET}"
echo ""
echo -e "  ${YELLOW}1.${RESET} Open ${BOLD}.env${RESET} and add your API keys:"
echo -e "     ${DIM}• OPENAI_API_KEY      — required (from platform.openai.com)${RESET}"
echo -e "     ${DIM}• ELEVENLABS_API_KEY   — optional, for premium voice${RESET}"
echo -e "     ${DIM}• PICOVOICE_ACCESS_KEY — optional, for wake word detection${RESET}"
echo ""
echo -e "  ${YELLOW}2.${RESET} Activate the virtual environment:"
echo -e "     ${GREEN}source venv/bin/activate${RESET}"
echo ""
echo -e "  ${YELLOW}3.${RESET} Run Bruno:"
echo -e "     ${GREEN}python bruno.py${RESET}             ${DIM}# Full assistant with wake word${RESET}"
echo -e "     ${GREEN}python bruno.py --no-wake${RESET}   ${DIM}# Skip wake word, always listen${RESET}"
echo -e "     ${GREEN}python bruno.py --test${RESET}      ${DIM}# Quick mic & TTS test${RESET}"
echo ""
divider
echo ""
echo -e "  ${GOLD}${DIM}\"Big things have small beginnings.\" — Thomas Shelby${RESET}"
echo ""
