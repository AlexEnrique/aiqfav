#!/bin/bash

set -e

echo "Running migrations..."
uv run alembic upgrade head

echo "Starting application..."
exec "$@"