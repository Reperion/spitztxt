#!/bin/bash
# spitztxt launcher — prefer venv-0.1.7 (new stack), fall back to .venv
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -x "$SCRIPT_DIR/venv-0.1.7/bin/python" ]; then
  PY="$SCRIPT_DIR/venv-0.1.7/bin/python"
elif [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
  PY="$SCRIPT_DIR/.venv/bin/python"
elif [ -x "$SCRIPT_DIR/venv/bin/python" ]; then
  # last resort: legacy symlink (0.1.2)
  echo "warning: using legacy venv; prefer venv-0.1.7" >&2
  PY="$SCRIPT_DIR/venv/bin/python"
else
  echo "No venv found. Create venv-0.1.7 and pip install -r requirements.txt" >&2
  exit 1
fi

echo "Starting spitztxt (python=$PY)..."
exec "$PY" "$SCRIPT_DIR/spitztxt-CLI.py" "$@"
