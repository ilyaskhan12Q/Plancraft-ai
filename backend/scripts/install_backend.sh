#!/usr/bin/env bash
# install_backend.sh — set up the AI Architect backend on Ubuntu 22.04
set -e

# Always run from the backend/ directory regardless of where the script is called from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

echo "=== AI Architect — Backend Install ==="
echo "Working directory: $(pwd)"

# Create virtual environment inside backend/
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install Python deps
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install Redis if not present
if ! command -v redis-server &> /dev/null; then
    echo "Installing Redis..."
    sudo apt-get update && sudo apt-get install -y redis-server
fi

# Create required directories
mkdir -p renders uploads

echo ""
echo "✅ Backend install complete."
echo "   Edit backend/.env to set your GEMINI_API_KEY and BLENDER_PATH."
echo "   Then run: bash backend/scripts/start_server.sh"
