#!/usr/bin/env bash
# Verify novelty-pool CLI — single run with Azure Storage persistence.
# Run from repo root: bash python/scripts/verify_novelty_cli.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

if [ -z "${AZURE_STORAGE_ACCOUNT_KEY:-}" ]; then
  echo "ERROR: AZURE_STORAGE_ACCOUNT_KEY env var is not set." >&2
  exit 1
fi

export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=devworkflow;AccountKey=${AZURE_STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
export UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv"

uv run --project python/tennl/batch \
  python -m tennl.batch.workflows.novelty_pool_cli single \
  --topic "Home & Living" \
  --sub-topic "Daily Living Hacks" \
  --content-variant AI_GENERATED \
  --content-mode guide \
  --angle practical_breakdown \
  --tone calm \
  --hook-style practical_problem \
  --eval-mode sequential \
  --timeout 300
