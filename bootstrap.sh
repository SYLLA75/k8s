#!/usr/bin/env bash
set -e

docker compose up --build -d
sleep 3
xdg-open http://localhost:5000 2>/dev/null || open http://localhost:5000 2>/dev/null || true
