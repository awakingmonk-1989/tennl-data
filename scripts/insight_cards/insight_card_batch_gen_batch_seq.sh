#!/usr/bin/env bash
# insight_card_batch_gen_batch_seq.sh
#
# Sequential batch driver for insight card generation (one orchestrator process
# per category, never overlapping). Each run uses parallel mode INSIDE the
# orchestrator (--mode parallel --workers N) for LLM calls, but categories are
# executed strictly one-after-another to reduce concurrent disk writes and
# avoid IO pressure from many processes writing triples at once.
#
# Categories source (packaged seed JSON):
#   Path: python/tennl/batch/src/tennl/batch/resources/insight-cards/insight_card_config.json
#   Category names are the OBJECT KEYS under the top-level "categories" object:
#     $.categories | keys[]
#   Example: "Finance", "Technology", "Urban Life" (key is the display name).
#
# Requirements: bash, jq, uv; run from repo root recommended.
#
# LLM: insight batches MUST use Gemini via LiteLLM (see tasks/2026-04-08-litellm-gemini-*.md).
# Without TENNL_LLM_PROVIDER, AppSettings defaults to azure-foundry-openai (see
# settings/util/providers.py). This script exports litellm explicitly.
#
# Usage:
#   ./scripts/insight_cards/insight_card_batch_gen_batch_seq.sh
#   ./scripts/insight_cards/insight_card_batch_gen_batch_seq.sh Finance
#   ./scripts/insight_cards/insight_card_batch_gen_batch_seq.sh -n 50 -w 4 Technology
#   ./scripts/insight_cards/insight_card_batch_gen_batch_seq.sh -n 2 --dry-run
#
# Defaults: COUNT=100, WORKERS=5. Each invocation writes under repo-root output/:
#   <repo>/output/gemini_batch_runs/run_<YYYYMMDD_HHMMSS>/
# with insight_batch_logs_batch_seq/ and insight_cards_<slug>/ inside that run folder.
# Override parent only: GEMINI_BATCH_RUNS_PARENT=/path/to/parent (default: REPO_ROOT/output/gemini_batch_runs)
#
# When no positional category is given, skip these exact keys from insight_card_config.json (edit here):
#   EXCLUDE_CATEGORIES — does not apply if you pass a single category on the CLI.

set -euo pipefail

EXCLUDE_CATEGORIES=(
  #   Culture
  #   Finance
  #   History
  #   Life
  #   Mindfulness
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BATCH_DIR="$REPO_ROOT/python/tennl/batch"
CONFIG_JSON="$BATCH_DIR/src/tennl/batch/resources/insight-cards/insight_card_config.json"
UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$BATCH_DIR/.venv}"

export UV_PROJECT_ENVIRONMENT
export TENNL_LLM_PROVIDER="${TENNL_LLM_PROVIDER:-litellm}"

COUNT=100
WORKERS=5
DRY_RUN=0
SINGLE_CATEGORY=""

usage() {
  sed -n '1,35p' "$0" | tail -n +2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--count)
      COUNT="${2:?}"
      shift 2
      ;;
    -w|--workers)
      WORKERS="${2:?}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      SINGLE_CATEGORY="$1"
      shift
      ;;
  esac
done

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is required (brew install jq / apt install jq)" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv is required" >&2
  exit 1
fi

if [[ ! -f "$CONFIG_JSON" ]]; then
  echo "error: config not found: $CONFIG_JSON" >&2
  exit 1
fi

# Slug for output directory names (spaces -> underscores)
slugify() {
  echo "$1" | tr ' ' '_'
}

read_all_categories() {
  jq -r '.categories | keys[]' "$CONFIG_JSON"
}

CATEGORIES=()
if [[ -n "$SINGLE_CATEGORY" ]]; then
  CATEGORIES+=("$SINGLE_CATEGORY")
else
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" ]] && continue
    CATEGORIES+=("$line")
  done < <(read_all_categories)
fi

if [[ ${#CATEGORIES[@]} -eq 0 ]]; then
  echo "error: no categories to process" >&2
  exit 1
fi

# Apply exclusions only for "all categories" mode (not when a single category was passed).
if [[ -z "$SINGLE_CATEGORY" && ${#EXCLUDE_CATEGORIES[@]} -gt 0 ]]; then
  FILTERED=()
  for cat in "${CATEGORIES[@]}"; do
    skip=false
    for ex in "${EXCLUDE_CATEGORIES[@]}"; do
      if [[ "$cat" == "$ex" ]]; then
        skip=true
        break
      fi
    done
    if [[ "$skip" == false ]]; then
      FILTERED+=("$cat")
    fi
  done
  CATEGORIES=("${FILTERED[@]}")
fi

if [[ ${#CATEGORIES[@]} -eq 0 ]]; then
  echo "error: no categories left after exclusions (check EXCLUDE_CATEGORIES)" >&2
  exit 1
fi

# One timestamped directory per script invocation (resolution: seconds).
RUN_STAMP="$(date +%Y%m%d_%H%M%S)"
GEMINI_BATCH_RUNS_PARENT="${GEMINI_BATCH_RUNS_PARENT:-$REPO_ROOT/output/gemini_batch_runs}"
RUN_ROOT="$GEMINI_BATCH_RUNS_PARENT/run_$RUN_STAMP"
LOG_DIR="$RUN_ROOT/insight_batch_logs_batch_seq"
OUTPUT_BASE="$RUN_ROOT"
mkdir -p "$LOG_DIR"

echo "=============================================="
echo "insight_card_batch_gen_batch_seq"
echo "  repo root     : $REPO_ROOT"
echo "  batch dir     : $BATCH_DIR"
echo "  TENNL_LLM_PROVIDER : $TENNL_LLM_PROVIDER"
echo "  runs parent   : $GEMINI_BATCH_RUNS_PARENT"
echo "  this run dir  : $RUN_ROOT"
echo "  config json   : $CONFIG_JSON"
echo "  count         : $COUNT"
echo "  workers/run   : $WORKERS (orchestrator --mode parallel)"
echo "  dry-run       : $DRY_RUN"
if [[ -z "$SINGLE_CATEGORY" && ${#EXCLUDE_CATEGORIES[@]} -gt 0 ]]; then
  echo "  excluded      : ${EXCLUDE_CATEGORIES[*]}"
fi
echo "  categories    : (${#CATEGORIES[@]}) ${CATEGORIES[*]}"
echo "  log dir       : $LOG_DIR"
echo "  output base   : $OUTPUT_BASE/insight_cards_<slug>/"
echo "=============================================="

run_one_category() {
  local cat="$1"
  local slug
  slug="$(slugify "$cat")"
  local out_dir="$OUTPUT_BASE/insight_cards_${slug}"
  local logfile="$LOG_DIR/${slug}_$(date +%Y%m%d_%H%M%S).log"
  mkdir -p "$out_dir"

  echo ""
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  echo "START category=$(printf '%q' "$cat") count=$COUNT workers=$WORKERS"
  echo "  output-dir -> $out_dir"
  echo "  log        -> $logfile"
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

  : >"$logfile"

  local -a cmd=(
    uv run python -m tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator
    --category "$cat"
    --count "$COUNT"
    --mode parallel
    --workers "$WORKERS"
    --output-dir "$out_dir"
    --future-result-timeout-s 120
  )
  if [[ "$DRY_RUN" -eq 1 ]]; then
    cmd+=(--dry-run)
  fi

  (
    cd "$BATCH_DIR"
    "${cmd[@]}"
  ) >>"$logfile" 2>&1 &
  local pid=$!

  # Monitor: every 5s print status + last lines of log while orchestrator runs.
  (
    while kill -0 "$pid" 2>/dev/null; do
      echo ""
      echo "---------- [monitor $(date -Iseconds)] category=$(printf '%q' "$cat") pid=$pid ----------"
      if [[ -s "$logfile" ]]; then
        tail -n 15 "$logfile" | sed 's/^/  | /'
      else
        echo "  | (log empty yet)"
      fi
      sleep 5
    done
  ) &
  local mon_pid=$!

  set +e
  wait "$pid"
  local ec=$?
  set -e

  sleep 0.5
  kill "$mon_pid" 2>/dev/null || true
  wait "$mon_pid" 2>/dev/null || true

  echo ""
  echo "---------- DONE category=$(printf '%q' "$cat") exit_code=$ec ----------"
  echo "---------- Last 40 log lines ----------"
  tail -n 40 "$logfile" | sed 's/^/  | /'
  echo "=========================================="

  return "$ec"
}

failed=0
for cat in "${CATEGORIES[@]}"; do
  if ! run_one_category "$cat"; then
    echo "error: category failed: $cat" >&2
    failed=1
  fi
done

if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
echo ""
echo "All categories completed successfully."
exit 0
