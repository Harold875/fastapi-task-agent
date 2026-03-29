#!/bin/bash

echo "Running migration..."
uv run alembic upgrade head

echo "Starting server..."
uv run fastapi dev --host 0.0.0.0