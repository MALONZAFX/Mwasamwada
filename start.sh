#!/bin/bash
set -e  # Exit on any error

echo "========================================"
echo "🚀 NUCLEAR START SCRIPT"
echo "========================================"

# Check if PORT is set
if [ -z "$PORT" ]; then
    echo "❌ ERROR: PORT environment variable not set!"
    echo "Railway should provide this automatically."
    PORT=8000
    echo "Using default port: $PORT"
fi

echo "📡 Port: $PORT"
echo "📁 Current directory: $(pwd)"
echo "📦 Python version: $(python --version)"

# Run migrations
echo "🔧 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn with maximum logging
echo "🌐 Starting Gunicorn..."
echo "Command: gunicorn mwasa.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --access-logfile - --error-logfile - --log-level debug"

exec gunicorn mwasa.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug