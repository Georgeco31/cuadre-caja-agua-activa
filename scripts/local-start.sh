#!/usr/bin/env bash
set -euo pipefail

docker compose up -d --build db api web

echo "Sistema local iniciado."
echo "API: http://localhost:${API_PORT:-8010}/api/v1/health"
echo "Web: http://localhost:${WEB_PORT:-3000}/login"
