#!/usr/bin/env bash
# start_server.sh — start Redis, Celery worker (concurrency=1), and uvicorn
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

# Activate venv if present
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "=== AI Architect — Starting Services ==="

# 1. Start Redis (if not already running)
if ! redis-cli ping &>/dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes
    sleep 1
fi
echo "✅ Redis running"

# 2. Start Celery worker — concurrency=1 to prevent OOM from parallel Blender renders
echo "Starting Celery worker (concurrency=1)..."
celery -A app.services.job_service.celery_app worker \
    --concurrency=1 \
    --loglevel=info \
    --logfile=celery.log \
    --detach
echo "✅ Celery worker started (log: celery.log)"

# 3. Start uvicorn
echo "Starting FastAPI server on port 8080..."
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
