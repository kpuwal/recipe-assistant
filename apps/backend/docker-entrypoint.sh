#!/bin/sh
set -e

echo "🚀 Starting Recipe Assistant API..."

PORT=${PORT:-8000}

exec uvicorn main:app \
    --host 0.0.0.0 \
    --port "$PORT"