#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
# shellcheck source=prod-local-common.sh
source "${SCRIPT_DIR}/prod-local-common.sh"

prod_require_tools
prod_require_env_file
prod_validate_env_file

if ! command -v curl >/dev/null 2>&1; then
  prod_error "curl no esta instalado o no esta disponible en PATH."
  exit 1
fi

api_port="$(prod_read_env_value API_PORT)"
web_port="$(prod_read_env_value WEB_PORT)"
api_v1_prefix="$(prod_read_env_value API_V1_PREFIX)"
api_url="http://localhost:${api_port:-8010}${api_v1_prefix:-/api/v1}/health"
web_url="http://localhost:${web_port:-3000}/login"
running_services="$(prod_compose ps --status running --services)"
status=0

echo "Estado de los contenedores de produccion local:"
prod_compose ps

for service in db api web; do
  if grep -Fxq "$service" <<<"$running_services"; then
    echo "OK: contenedor ${service} activo."
  else
    prod_error "El contenedor ${service} no esta activo."
    status=1
  fi
done

if api_response="$(curl --fail --silent --show-error --max-time 5 "$api_url")" \
  && [[ "$api_response" == *'"status":"ok"'* ]]; then
  echo "OK: API responde con status=ok en ${api_url}."
else
  prod_error "La API no responde correctamente en ${api_url}."
  status=1
fi

if curl --fail --silent --show-error --max-time 5 --output /dev/null "$web_url"; then
  echo "OK: Web responde en ${web_url}."
else
  prod_error "La Web no responde en ${web_url}."
  status=1
fi

if alembic_current="$(prod_compose exec --no-TTY api alembic current 2>&1)"; then
  if [[ "$alembic_current" == *"0029_simple_routes"* ]]; then
    echo "OK: Alembic esta en 0029_simple_routes."
  else
    prod_error "Alembic responde, pero no esta en 0029_simple_routes: ${alembic_current}"
    status=1
  fi
else
  prod_error "No se pudo consultar Alembic: ${alembic_current}"
  status=1
fi

if (( status == 0 )); then
  echo "Produccion local responde correctamente."
else
  prod_error "La verificacion encontro fallos. Revisa ./scripts/prod-local-logs.sh."
fi

exit "$status"
