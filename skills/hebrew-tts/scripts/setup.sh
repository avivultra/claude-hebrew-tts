#!/usr/bin/env bash
# setup.sh — One-time setup for claude-hebrew-tts (macOS / Linux)
# Creates a local Python venv inside the skill folder and installs edge-tts.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_ROOT/venv"
VENV_PY="$VENV_DIR/bin/python"

echo "[claude-hebrew-tts setup]"
echo "Skill root : $SKILL_ROOT"
echo "Venv dir   : $VENV_DIR"

# 1) Locate Python 3.
PYTHON=""
for candidate in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
            PYTHON="$candidate"
            break
        fi
    fi
done
if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.10+ not found. Install from https://www.python.org/ or your package manager." >&2
    exit 1
fi
echo "Using Python: $PYTHON ($($PYTHON --version))"

# 2) Create venv.
if [ ! -x "$VENV_PY" ]; then
    echo "Creating venv..."
    "$PYTHON" -m venv "$VENV_DIR"
else
    echo "Venv already exists."
fi

# 3) Install edge-tts.
echo "Installing edge-tts..."
"$VENV_PY" -m pip install --quiet --upgrade pip
"$VENV_PY" -m pip install --quiet edge-tts

# 4) Smoke-test.
"$VENV_PY" -c "import edge_tts; print('edge-tts OK')"

# 5) Check for an audio player (Linux only — macOS has afplay built-in).
if [ "$(uname -s)" = "Linux" ]; then
    HAS_PLAYER=0
    for player in mpg123 ffplay cvlc; do
        if command -v "$player" >/dev/null 2>&1; then HAS_PLAYER=1; break; fi
    done
    if [ "$HAS_PLAYER" -eq 0 ]; then
        echo "WARNING: No audio player found (mpg123 / ffplay / cvlc)." >&2
        echo "         Install one with your package manager, e.g. 'sudo apt install mpg123'." >&2
        echo "         Or use '--save OUT.mp3' to write files without playing." >&2
    fi
fi

echo ""
echo "Setup complete. You can now ask Claude to read Hebrew aloud."
