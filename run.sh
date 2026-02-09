#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="${VENV_DIR:-venv}"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Virtual environment not found. Run ./setup.sh first."
  exit 1
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

exec uvicorn main:app --host 0.0.0.0 --port 8000 "$@"
