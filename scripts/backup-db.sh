#!/usr/bin/env bash
set -euo pipefail

backup_dir="${BACKUP_DIR:-backups}"
timestamp="$(date +%Y%m%d_%H%M%S)"
backup_file="${backup_dir}/cuadre_caja_${timestamp}.sql"

mkdir -p "$backup_dir"
docker compose up -d db
docker compose exec -T db sh -c 'until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do sleep 1; done'
docker compose exec -T db sh -c 'pg_dump --clean --if-exists -U "$POSTGRES_USER" "$POSTGRES_DB"' > "$backup_file"

echo "Backup creado: $backup_file"
