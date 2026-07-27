#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
# shellcheck source=prod-local-common.sh
source "${SCRIPT_DIR}/prod-local-common.sh"

prod_require_tools
prod_require_env_file
prod_validate_env_file

prod_compose config --quiet
prod_compose up --detach --build db api web
prod_compose ps

api_port="$(prod_read_env_value API_PORT)"
web_port="$(prod_read_env_value WEB_PORT)"
api_v1_prefix="$(prod_read_env_value API_V1_PREFIX)"

echo "Produccion local iniciada sin ejecutar migraciones ni seeds automaticamente."
echo "API: http://localhost:${api_port:-8010}${api_v1_prefix:-/api/v1}/health"
echo "Web: http://localhost:${web_port:-3000}/login"
echo "Antes del primer uso de una base vacia, ejecuta conscientemente las migraciones documentadas."
