#!/usr/bin/env bash
# Monitor insight card batch output under output/gemini_batch_runs/run_<stamp>/.
#
# Usage (from repo root):
#   ./scripts/insight_cards/monitor_gemini_batch_runs.sh              # one-shot snapshot
#   ./scripts/insight_cards/monitor_gemini_batch_runs.sh -w 10        # refresh every 10s (Ctrl-C to stop)
#   ./scripts/insight_cards/monitor_gemini_batch_runs.sh /path/to/run_20260409_123456
#   ./scripts/insight_cards/monitor_gemini_batch_runs.sh -t 20        # tail last 20 lines of newest category log
#
# Counts only main card JSON files (excludes *_raw.json and *_tokens.json).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PARENT="${GEMINI_BATCH_RUNS_PARENT:-$REPO_ROOT/output/gemini_batch_runs}"

WATCH_SEC=0
TAIL_LOG=0
RUN_DIR=""

usage() {
  sed -n '1,12p' "$0" | tail -n +2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -w|--watch)
      WATCH_SEC="${2:?interval seconds}"
      shift 2
      ;;
    -t|--tail-log)
      TAIL_LOG="${2:?lines}"
      shift 2
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
      RUN_DIR="$1"
      shift
      ;;
  esac
done

count_main_cards() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    echo "0"
    return
  fi
  find "$dir" -maxdepth 1 -type f -name 'insight_card_*.json' ! -name '*_raw.json' ! -name '*_tokens.json' 2>/dev/null | wc -l | tr -d ' '
}

latest_run_dir() {
  local newest=""
  local latest_ts=""
  if [[ ! -d "$PARENT" ]]; then
    echo ""
    return
  fi
  for d in "$PARENT"/run_*; do
    [[ -d "$d" ]] || continue
    base="${d##*/}"
    ts="${base#run_}"
    if [[ -z "$latest_ts" || "$ts" > "$latest_ts" ]]; then
      latest_ts="$ts"
      newest="$d"
    fi
  done
  echo "$newest"
}

newest_category_log() {
  local logdir="$1/insight_batch_logs_batch_seq"
  [[ -d "$logdir" ]] || return
  ls -t "$logdir"/*.log 2>/dev/null | head -1
}

snapshot() {
  local root="$1"
  echo "=============================================="
  echo "gemini_batch_runs monitor"
  echo "  parent     : $PARENT"
  echo "  run dir    : $root"
  echo "  time       : $(date -Iseconds 2>/dev/null || date)"
  if pgrep -fl insight_card_batch_gen_batch_seq >/dev/null 2>&1; then
    echo "  driver     : running (insight_card_batch_gen_batch_seq)"
  elif pgrep -fl insight_card_llamaindex_orchestrator >/dev/null 2>&1; then
    echo "  orchestrator: running (insight_card_llamaindex_orchestrator)"
  else
    echo "  processes  : (no batch driver/orchestrator in this user session)"
  fi
  echo "----------------------------------------------"

  local total=0
  if [[ -d "$root" ]]; then
    for d in "$root"/insight_cards_*; do
      [[ -d "$d" ]] || continue
      slug="${d##*/}"
      slug="${slug#insight_cards_}"
      n="$(count_main_cards "$d")"
      total=$((total + n))
      printf '  %-20s %4s cards\n' "$slug" "$n"
    done
  else
    echo "  (run dir missing)"
  fi
  echo "----------------------------------------------"
  echo "  total main *.json : $total"
  local clog
  clog="$(newest_category_log "$root")"
  if [[ -n "$clog" && -f "$clog" ]]; then
    echo "  latest log        : $clog"
    if [[ "$TAIL_LOG" -gt 0 ]]; then
      echo "  --- tail -$TAIL_LOG ---"
      tail -n "$TAIL_LOG" "$clog" | sed 's/^/  | /'
    fi
  fi
  echo "=============================================="
}

if [[ -z "$RUN_DIR" ]]; then
  RUN_DIR="$(latest_run_dir)"
fi

if [[ -z "$RUN_DIR" || ! -d "$RUN_DIR" ]]; then
  echo "error: no run_* directory under $PARENT" >&2
  exit 1
fi

if [[ "$WATCH_SEC" -gt 0 ]]; then
  while true; do
    clear 2>/dev/null || true
    snapshot "$RUN_DIR"
    sleep "$WATCH_SEC"
  done
else
  snapshot "$RUN_DIR"
fi
