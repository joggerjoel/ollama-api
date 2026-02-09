#!/usr/bin/env bash
set -e

# Do not run as root or with sudo (would create root-owned venv)
if [[ $EUID -eq 0 ]] || [[ -n "${SUDO_UID:-}" ]]; then
  echo "Do not run setup.sh as root or with sudo. Run it as your normal user."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="${VENV_DIR:-venv}"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment in $VENV_DIR ..."
  python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment ..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Upgrading pip ..."
pip install --upgrade pip

echo "Installing requirements ..."
pip install -r requirements.txt

echo "Setup complete. Activate with: source $VENV_DIR/bin/activate"
