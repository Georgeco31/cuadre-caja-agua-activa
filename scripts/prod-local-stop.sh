#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
# shellcheck source=prod-local-common.sh
source "${SCRIPT_DIR}/prod-local-common.sh"

prod_require_tools
prod_require_env_file

prod_compose down

echo "Produccion local apagada. El volumen postgres_prod_data se conserva."
