#!/bin/bash
# Simple Gunicorn runner for Chabokan.net
# This script runs Gunicorn directly without complex configuration

set -e

echo "🚀 Starting Gunicorn server..."

# Get port from environment or use default
PORT=${PORT:-8000}

# Start Gunicorn directly
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    construction_project.wsgi:application
