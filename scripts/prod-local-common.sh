#!/usr/bin/env bash
set -euo pipefail

readonly PROD_PROJECT_ROOT="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1
  pwd
)"
readonly PROD_COMPOSE_FILE="${PROD_PROJECT_ROOT}/docker-compose.prod.yml"
readonly PROD_ENV_FILE="${PROD_ENV_FILE:-${PROD_PROJECT_ROOT}/.env.production.local}"

prod_error() {
  echo "ERROR: $*" >&2
}

prod_require_tools() {
  if ! command -v docker >/dev/null 2>&1; then
    prod_error "Docker no esta instalado o no esta disponible en PATH."
    exit 1
  fi

  if ! docker compose version >/dev/null 2>&1; then
    prod_error "Docker Compose v2 no esta disponible."
    exit 1
  fi
}

prod_require_env_file() {
  if [[ ! -f "$PROD_ENV_FILE" ]]; then
    prod_error "Falta ${PROD_ENV_FILE}."
    echo "Crealo con: cp .env.production.example .env.production.local" >&2
    echo "Luego reemplaza todos los valores CHANGE_ME y SERVER_LAN_IP." >&2
    exit 1
  fi
}

prod_read_env_value() {
  local key="$1"
  local value

  value="$(
    awk -v key="$key" '
      index($0, key "=") == 1 {
        value = substr($0, length(key) + 2)
      }
      END {
        print value
      }
    ' "$PROD_ENV_FILE"
  )"
  value="${value%$'\r'}"

  if [[ "$value" == \"*\" && "$value" == *\" ]]; then
    value="${value:1:${#value}-2}"
  elif [[ "$value" == \'*\' && "$value" == *\' ]]; then
    value="${value:1:${#value}-2}"
  fi

  printf '%s' "$value"
}

prod_validate_env_file() {
  local required_keys=(
    ENVIRONMENT
    POSTGRES_DB
    POSTGRES_USER
    POSTGRES_PASSWORD
    DATABASE_URL
    AUTH_SECRET_KEY
    ADMIN_USERNAME
    ADMIN_PASSWORD
    CORS_ORIGINS
    NEXT_PUBLIC_API_URL
  )
  local key
  local value
  local normalized

  for key in "${required_keys[@]}"; do
    value="$(prod_read_env_value "$key")"
    if [[ -z "$value" ]]; then
      prod_error "La variable ${key} falta o esta vacia en ${PROD_ENV_FILE}."
      exit 1
    fi
  done

  for key in POSTGRES_PASSWORD DATABASE_URL AUTH_SECRET_KEY ADMIN_PASSWORD CORS_ORIGINS NEXT_PUBLIC_API_URL; do
    value="$(prod_read_env_value "$key")"
    normalized="$(printf '%s' "$value" | tr '[:lower:]' '[:upper:]')"
    if [[ "$normalized" == *"CHANGE_ME"* || "$normalized" == *"SERVER_LAN_IP"* || "$normalized" == *"REPLACE_ME"* ]]; then
      prod_error "La variable ${key} todavia contiene un marcador de ejemplo."
      exit 1
    fi
  done

  if [[ "$(prod_read_env_value ENVIRONMENT)" != "production" ]]; then
    prod_error "ENVIRONMENT debe ser production."
    exit 1
  fi

  value="$(prod_read_env_value DATABASE_URL)"
  if [[ "$value" != postgresql+psycopg://* ]]; then
    prod_error "DATABASE_URL debe usar postgresql+psycopg://."
    exit 1
  fi

  value="$(prod_read_env_value CORS_ORIGINS)"
  if [[ "$value" == *"*"* ]]; then
    prod_error "CORS_ORIGINS no puede permitir el comodin *."
    exit 1
  fi

  for key in API_PORT WEB_PORT; do
    value="$(prod_read_env_value "$key")"
    if [[ -n "$value" && ! "$value" =~ ^[0-9]+$ ]]; then
      prod_error "La variable ${key} debe ser un puerto numerico."
      exit 1
    fi
  done

  value="$(prod_read_env_value AUTH_SECRET_KEY)"
  if (( ${#value} < 32 )); then
    prod_error "AUTH_SECRET_KEY debe tener al menos 32 caracteres."
    exit 1
  fi

  value="$(prod_read_env_value POSTGRES_PASSWORD)"
  if (( ${#value} < 16 )); then
    prod_error "POSTGRES_PASSWORD debe tener al menos 16 caracteres."
    exit 1
  fi

  value="$(prod_read_env_value ADMIN_PASSWORD)"
  if (( ${#value} < 12 )); then
    prod_error "ADMIN_PASSWORD debe tener al menos 12 caracteres."
    exit 1
  fi
}

prod_compose() {
  docker compose \
    --file "$PROD_COMPOSE_FILE" \
    --env-file "$PROD_ENV_FILE" \
    "$@"
}
