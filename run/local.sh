#!/usr/bin/env bash
# Start the local Streamlit dashboard with a checked local configuration.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
config_file="${VISION_LAB_ENV_FILE:-"${repo_root}/run/.env"}"

if [[ ! -f "${config_file}" ]]; then
  printf 'Configuration file not found: %s\nCopy run/.env.example to run/.env and set OCI_COMPARTMENT_ID.\n' "${config_file}" >&2
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "${config_file}"
set +a

if [[ -z "${OCI_COMPARTMENT_ID:-}" ]]; then
  printf 'OCI_COMPARTMENT_ID is required. Set it in %s.\n' "${config_file}" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  printf 'uv is required. Install it from https://docs.astral.sh/uv/ and run uv sync --all-groups.\n' >&2
  exit 1
fi

cd "${repo_root}"
exec uv run streamlit run src/vision_lab/app.py \
  --server.address "${VISION_LAB_HOST:-127.0.0.1}" \
  --server.port "${VISION_LAB_PORT:-8501}"
