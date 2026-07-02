#!/usr/bin/env bash
set -euo pipefail

api_url="${API_HEALTH_URL:-http://localhost:${API_PORT:-8010}${API_V1_PREFIX:-/api/v1}/health}"
web_url="${WEB_LOGIN_URL:-http://localhost:${WEB_PORT:-3000}/login}"
status=0

if ! command -v curl >/dev/null 2>&1; then
  echo "ERROR: curl no esta instalado o no esta disponible en PATH."
  exit 1
fi

check_url() {
  local label="$1"
  local url="$2"

  if curl --fail --silent --show-error --max-time 5 --output /dev/null "$url"; then
    echo "OK: $label responde en $url"
  else
    echo "ERROR: $label no responde en $url"
    status=1
  fi
}

echo "Health check local de Cuadre de Caja Agua Activa"
echo "No se modifican datos."

check_url "Backend" "$api_url"
check_url "Frontend" "$web_url"

if [[ "$status" -eq 0 ]]; then
  echo "Sistema local responde correctamente."
else
  echo "Revisa que el sistema este levantado con ./scripts/local-start.sh"
fi

exit "$status"
