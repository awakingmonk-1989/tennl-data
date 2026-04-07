#!/usr/bin/env bash
# Verify novelty-pool CLI — batch dry run (N=2) with PG verification.
# Run from repo root: bash python/scripts/verify_novelty_batch.sh
#
# Optional: set AZURE_STORAGE_ACCOUNT_KEY to enable Azure persistence.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

INVOCATIONS="${1:-2}"
TOPICS_JSON="${REPO_ROOT}/contetn_gen_topics_india.json"

if [ ! -f "$TOPICS_JSON" ]; then
  echo "ERROR: Topics JSON not found at ${TOPICS_JSON}" >&2
  exit 1
fi

if [ -n "${AZURE_STORAGE_ACCOUNT_KEY:-}" ]; then
  export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=devworkflow;AccountKey=${AZURE_STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
  echo "Azure persistence: ENABLED"
else
  echo "Azure persistence: DISABLED (AZURE_STORAGE_ACCOUNT_KEY not set)"
fi

export UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv"

echo ""
echo "=== Batch run: ${INVOCATIONS} invocations ==="
echo ""

UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch \
  python -m tennl.batch.workflows.novelty_pool_cli batch \
  --invocations "$INVOCATIONS" \
  --topics-json "$TOPICS_JSON" \
  --content-variant AI_GENERATED \
  --eval-mode sequential \
  --timeout 300

echo ""
echo "=== PostgreSQL verification ==="
echo ""
psql -d content_gen -c "SELECT id, run_id, status, reason FROM content_gen_article ORDER BY run_id"

echo ""
echo "=== Batch directory listing ==="
echo ""
BATCH_DIRS=$(find specs/data -maxdepth 1 -name 'batch_*' -type d | sort)
if [ -z "$BATCH_DIRS" ]; then
  echo "WARNING: No batch directories found in specs/data/"
else
  for d in $BATCH_DIRS; do
    echo "${d}:"
    ls -lh "$d"
    echo ""
  done
fi

ROW_COUNT=$(psql -d content_gen -t -c "SELECT count(*) FROM content_gen_article" | tr -d ' ')
SUCCESS_COUNT=$(psql -d content_gen -t -c "SELECT count(*) FROM content_gen_article WHERE status='success'" | tr -d ' ')
FAILED_COUNT=$(psql -d content_gen -t -c "SELECT count(*) FROM content_gen_article WHERE status='failed'" | tr -d ' ')

echo "=== Summary ==="
echo "  PG total rows:  ${ROW_COUNT}"
echo "  PG success:     ${SUCCESS_COUNT}"
echo "  PG failed:      ${FAILED_COUNT}"
echo "================"
