#!/bin/bash
# Simple startup script for Railway
# Railway provides PORT environment variable

PORT=${PORT:-8080}
echo "Starting server on port $PORT"
exec uvicorn main:app --host 0.0.0.0 --port $PORT
