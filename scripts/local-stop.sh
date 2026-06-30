#!/usr/bin/env bash
set -euo pipefail

docker compose down

echo "Sistema local apagado. El volumen postgres_data se conserva."
