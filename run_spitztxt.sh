#!/bin/bash
# spitztxt launcher — activate local venv if present and run the CLI
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d "venv" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
elif [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  echo "No venv found. Create one first, e.g.:"
  echo "  python3 -m venv venv && source venv/bin/activate"
  echo "  pip install torch torchaudio colorama chatterbox-tts"
  exit 1
fi

echo "Starting spitztxt..."
python spitztxt-CLI.py
