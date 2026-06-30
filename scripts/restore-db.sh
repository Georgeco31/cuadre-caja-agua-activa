#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Uso: ./scripts/restore-db.sh backups/nombre_backup.sql"
  exit 1
fi

backup_file="$1"

if [[ ! -f "$backup_file" ]]; then
  echo "No existe el archivo de backup: $backup_file"
  exit 1
fi

docker compose up -d db
docker compose exec -T db sh -c 'until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do sleep 1; done'
docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" "$POSTGRES_DB"' < "$backup_file"

echo "Backup restaurado desde: $backup_file"
