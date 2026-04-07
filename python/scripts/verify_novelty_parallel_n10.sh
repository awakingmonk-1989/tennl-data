#!/usr/bin/env bash
# Verify novelty-pool CLI — parallel batch run (N=10).
# Run from repo root:
#   bash python/scripts/verify_novelty_parallel_n10.sh
#
# Azure persistence:
# - Preferred: set AZURE_STORAGE_CONNECTION_STRING
# - Fallback: set AZURE_STORAGE_ACCOUNT_KEY (script will construct the connection string)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

INVOCATIONS="10"
NUM_WORKERS="${NUM_WORKERS:-10}"
TOPICS_JSON="${REPO_ROOT}/contetn_gen_topics_india.json"

if [ ! -f "$TOPICS_JSON" ]; then
  echo "ERROR: Topics JSON not found at ${TOPICS_JSON}" >&2
  exit 1
fi

# Load secrets from repo-local secrets.txt (do not echo values).
# Expected: AZURE_STORAGE_CONNECTION_STRING and/or AZURE_STORAGE_ACCOUNT_KEY.
if [ -f "${REPO_ROOT}/secrets.txt" ]; then
  set -a
  # shellcheck source=/dev/null
  source "${REPO_ROOT}/secrets.txt"
  set +a
fi

if [ -n "${AZURE_STORAGE_CONNECTION_STRING:-}" ] || [ -n "${AZURE_STORAGE_ACCOUNT_KEY:-}" ]; then
  echo "Azure env: LOADED"
else
  echo "ERROR: Azure env missing. Provide AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_KEY in secrets.txt" >&2
  exit 1
fi

export UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv"
STARTED_AT_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo ""
echo "=== Parallel batch run: invocations=${INVOCATIONS} num_workers=${NUM_WORKERS} ==="
echo ""

uv run --project python/tennl/batch \
  python -m tennl.batch.workflows.novelty_pool_cli batch \
  --invocations "$INVOCATIONS" \
  --topics-json "$TOPICS_JSON" \
  --content-variant AI_GENERATED \
  --eval-mode sequential \
  --timeout 300 \
  --num-workers "$NUM_WORKERS"

echo ""
echo "=== Verification (local artifacts + PG + Azure) ==="
echo ""

LATEST_BATCH_DIR="$(ls -1dt specs/data/batch_* 2>/dev/null | head -n 1 || true)"
if [ -z "$LATEST_BATCH_DIR" ]; then
  echo "ERROR: No batch directories found in specs/data/"
  exit 1
fi

uv run --project python/tennl/batch \
  python python/scripts/verify_novelty_batch_run_artifacts.py \
  --batch-dir "$LATEST_BATCH_DIR" \
  --started-at-iso "$STARTED_AT_ISO"

echo ""
echo "=== Batch artifacts verification (latest batch dir) ==="
echo ""

LATEST_BATCH_DIR="$(ls -1dt specs/data/batch_* 2>/dev/null | head -n 1 || true)"
if [ -z "$LATEST_BATCH_DIR" ]; then
  echo "WARNING: No batch directories found in specs/data/"
  exit 0
fi

echo "Latest batch dir: ${LATEST_BATCH_DIR}"
FILE_COUNT="$(ls -1 "$LATEST_BATCH_DIR" | wc -l | tr -d ' ')"
echo "Files: ${FILE_COUNT}"
ls -1 "$LATEST_BATCH_DIR" | head

echo ""
echo "=== PostgreSQL verification (rows for successful artifacts) ==="
echo ""

if ls "$LATEST_BATCH_DIR"/*.json >/dev/null 2>&1; then
  RUN_IDS="$(ls -1 "$LATEST_BATCH_DIR"/*.json | xargs -n 1 basename | sed 's/\.json$//' | tr '\n' ',' | sed 's/,$//')"
  psql -d content_gen -c "SELECT id, run_id, status, reason FROM content_gen_article WHERE run_id = ANY(string_to_array('${RUN_IDS}', ',')) ORDER BY run_id;"
else
  echo "No .json artifacts found; skipping run_id-based PG verification."
fi

