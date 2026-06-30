#!/usr/bin/env bash
set -euo pipefail

docker compose up -d db
docker compose exec -T db sh -c 'until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do sleep 1; done'
docker compose build api
docker compose run --rm api alembic upgrade head

echo "Migraciones aplicadas."
