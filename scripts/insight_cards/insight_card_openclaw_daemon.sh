#!/usr/bin/env bash
# insight_card_openclaw_daemon.sh
#
# Cartesian batch driver over insight-card axes (category, language, hook_type,
# register, opening_word_class, title_style). Each combo passes full themes[] and
# human_contexts[] JSON arrays into the packaged "large" prompt.
#
# --daemon: re-invokes under nohup so the run survives terminal logout and keeps
# going while the screen is locked (process stays alive; macOS may still sleep
# the machine unless you use caffeinate — see below). Exits immediately after
# printing PID and log paths; the child runs until all combinations finish, then
# exits (no infinite loop).
#
# Excluded languages (default): Telugu, Hindi, English. Override: EXCLUDE_LANGUAGES=''.
#
# Per combo: render prompt → log → openclaw agent --json → oc_gpt_<stamp>_NNNNNN.json
#
# Requirements: bash, jq, uv, openclaw; optional category as first positional arg.
#
# Env:
#   MAX_RUNS, OPENCLAW_AGENT, OC_TIMEOUT, UV_PROJECT_ENVIRONMENT, EXCLUDE_LANGUAGES,
#   OC_GPT_RUNS_PARENT — output root (default: <repo>/output/oc-gpt-runs)
#   CAFFEINATE=1       — on macOS, wrap child in caffeinate -dimsu to reduce sleep
#                        during long runs (installs no extra dep; uses /usr/bin/caffeinate)
#
# Usage:
#   ./scripts/insight_cards/insight_card_openclaw_daemon.sh
#   ./scripts/insight_cards/insight_card_openclaw_daemon.sh Technology
#   ./scripts/insight_cards/insight_card_openclaw_daemon.sh --daemon
#   CAFFEINATE=1 ./scripts/insight_cards/insight_card_openclaw_daemon.sh --daemon Technology

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BATCH_DIR="$REPO_ROOT/python/tennl/batch"
CONFIG_JSON="$BATCH_DIR/src/tennl/batch/resources/insight-cards/insight_card_config.json"
SELF_SCRIPT="${BASH_SOURCE[0]}"
SELF_ABS="$SCRIPT_DIR/$(basename "$SELF_SCRIPT")"

DAEMON_REQUEST=0
SHOW_HELP=0
POS_ARGS=()
for a in "$@"; do
  case "$a" in
    --daemon) DAEMON_REQUEST=1 ;;
    -h|--help) SHOW_HELP=1 ;;
    *) POS_ARGS+=("$a") ;;
  esac
done

usage() {
  cat <<'EOF'
insight_card_openclaw_daemon.sh — OpenClaw batch driver for insight-card combos.

Foreground:
  ./scripts/insight_cards/insight_card_openclaw_daemon.sh [Category]

Background (nohup, survives terminal close; runs until all combos done):
  ./scripts/insight_cards/insight_card_openclaw_daemon.sh --daemon [Category]

Env: MAX_RUNS, OPENCLAW_AGENT, OC_TIMEOUT, OC_GPT_RUNS_PARENT, EXCLUDE_LANGUAGES,
     UV_PROJECT_ENVIRONMENT, CAFFEINATE=1 (macOS, avoid sleep during run)

EOF
}

if [[ "$SHOW_HELP" == 1 ]]; then
  usage
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is required" >&2
  exit 1
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv is required" >&2
  exit 1
fi
if ! command -v openclaw >/dev/null 2>&1; then
  echo "error: openclaw is required (https://docs.openclaw.ai/cli/agent)" >&2
  exit 1
fi
if [[ ! -f "$CONFIG_JSON" ]]; then
  echo "error: config not found: $CONFIG_JSON" >&2
  exit 1
fi

UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$BATCH_DIR/.venv}"
OPENCLAW_AGENT="${OPENCLAW_AGENT:-main}"
OC_TIMEOUT="${OC_TIMEOUT:-600}"

# Default exclusions (pipe-separated for grep -E). Empty EXCLUDE_LANGUAGES clears skip.
EXCLUDE_LANGUAGES_DEFAULT='^(Telugu|Hindi|English)$'
EXCLUDE_LANGUAGES="${EXCLUDE_LANGUAGES:-$EXCLUDE_LANGUAGES_DEFAULT}"

OUT_ROOT="${OC_GPT_RUNS_PARENT:-$REPO_ROOT/output/oc-gpt-runs}"

if [[ "$DAEMON_REQUEST" == 1 && -z "${INSIGHT_OC_DAEMON_CHILD:-}" ]]; then
  mkdir -p "$OUT_ROOT"
  daemon_stamp="$(date +%Y%m%d_%H%M%S)"
  DAEMON_LOG="$OUT_ROOT/daemon_${daemon_stamp}.log"
  DAEMON_PID_FILE="$OUT_ROOT/daemon_${daemon_stamp}.pid"
  # Create log now so tail -f works immediately; bash set -u breaks "${POS_ARGS[@]}" when empty.
  : >"$DAEMON_LOG"

  use_caffeinate=0
  if [[ "${CAFFEINATE:-0}" == 1 ]] && command -v caffeinate >/dev/null 2>&1; then
    use_caffeinate=1
  elif [[ "${CAFFEINATE:-0}" == 1 ]]; then
    echo "warning: CAFFEINATE=1 but caffeinate not found (macOS only); starting without it" >&2
  fi

  if [[ "$use_caffeinate" == 1 ]]; then
    if [[ ${#POS_ARGS[@]} -eq 0 ]]; then
      nohup caffeinate -dimsu env INSIGHT_OC_DAEMON_CHILD=1 bash "$SELF_ABS" \
        >>"$DAEMON_LOG" 2>&1 &
    else
      nohup caffeinate -dimsu env INSIGHT_OC_DAEMON_CHILD=1 bash "$SELF_ABS" "${POS_ARGS[@]}" \
        >>"$DAEMON_LOG" 2>&1 &
    fi
  else
    if [[ ${#POS_ARGS[@]} -eq 0 ]]; then
      nohup env INSIGHT_OC_DAEMON_CHILD=1 bash "$SELF_ABS" \
        >>"$DAEMON_LOG" 2>&1 &
    else
      nohup env INSIGHT_OC_DAEMON_CHILD=1 bash "$SELF_ABS" "${POS_ARGS[@]}" \
        >>"$DAEMON_LOG" 2>&1 &
    fi
  fi
  child_pid=$!
  echo "$child_pid" >"$DAEMON_PID_FILE"
  ln -sf "$DAEMON_LOG" "$OUT_ROOT/daemon_latest.log" 2>/dev/null || true
  ln -sf "$DAEMON_PID_FILE" "$OUT_ROOT/daemon_latest.pid" 2>/dev/null || true
  echo "insight_card_openclaw_daemon: background child started"
  echo "  pid      : $child_pid"
  echo "  log      : $DAEMON_LOG"
  echo "  pid file : $DAEMON_PID_FILE"
  echo "  (symlinks: $OUT_ROOT/daemon_latest.log $OUT_ROOT/daemon_latest.pid)"
  echo "  tail -f $(printf '%q' "$DAEMON_LOG")"
  exit 0
fi

FILTER_CATEGORY=""
if [[ ${#POS_ARGS[@]} -gt 0 ]]; then
  FILTER_CATEGORY="${POS_ARGS[0]}"
fi

should_skip_language() {
  local lang="$1"
  if [[ -z "$EXCLUDE_LANGUAGES" ]]; then
    return 1
  fi
  if printf '%s' "$lang" | grep -Eq "$EXCLUDE_LANGUAGES"; then
    return 0
  fi
  return 1
}

CATEGORIES=()
if [[ -n "$FILTER_CATEGORY" ]]; then
  if ! jq -e --arg c "$FILTER_CATEGORY" '.categories | has($c)' "$CONFIG_JSON" >/dev/null; then
    echo "error: unknown category $(printf '%q' "$FILTER_CATEGORY")" >&2
    exit 1
  fi
  CATEGORIES=( "$FILTER_CATEGORY" )
else
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" ]] && continue
    CATEGORIES+=( "$line" )
  done < <(jq -r '.categories | keys[]' "$CONFIG_JSON")
fi

avoid_titles_line() {
  jq -r '
    (.title_style_hints.avoid // []) as $a |
    if ($a | length) == 0 then "Avoid titles like: "
    else "Avoid titles like: " + ($a | map("\"" + . + "\"") | join(", "))
    end
  ' "$CONFIG_JSON"
}

AVOID_TITLES="$(avoid_titles_line)"
TOPIC_ANCHOR='Compose the card using exactly one theme from the themes pool and exactly one human context from the human contexts pool (both JSON arrays above). Respect every axis below exactly.'

RUN_STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_ROOT="${OC_GPT_RUNS_PARENT:-$REPO_ROOT/output/oc-gpt-runs}"
mkdir -p "$OUT_ROOT"
PROMPT_LOG_DIR="$OUT_ROOT/prompts_$RUN_STAMP"
mkdir -p "$PROMPT_LOG_DIR"

echo "=============================================="
echo "insight_card_openclaw_daemon (bash)"
if [[ -n "${INSIGHT_OC_DAEMON_CHILD:-}" ]]; then
  echo "  mode           : background child (nohup) pid=$$"
fi
echo "  repo root      : $REPO_ROOT"
echo "  batch dir      : $BATCH_DIR"
echo "  config         : $CONFIG_JSON"
echo "  output dir     : $OUT_ROOT"
echo "  prompt logs    : $PROMPT_LOG_DIR"
echo "  openclaw agent : $OPENCLAW_AGENT"
echo "  skip languages : ${EXCLUDE_LANGUAGES:-"(none)"}"
echo "  categories     : (${#CATEGORIES[@]}) ${CATEGORIES[*]}"
if [[ -n "${MAX_RUNS:-}" ]]; then
  echo "  MAX_RUNS       : $MAX_RUNS"
fi
echo "=============================================="

render_payload_to_prompt() {
  local payload_json="$1"
  (
    cd "$BATCH_DIR"
    UV_PROJECT_ENVIRONMENT="$UV_PROJECT_ENVIRONMENT" uv run python -m \
      tennl.batch.generator.insight_cards.insight_card_render_openclaw_prompt <<<"$payload_json"
  )
}

n=0
for cat in "${CATEGORIES[@]}"; do
  themes_json="$(jq -c --arg c "$cat" '.categories[$c].themes // []' "$CONFIG_JSON")"
  hctx_json="$(jq -c --arg c "$cat" '.categories[$c].human_contexts // []' "$CONFIG_JSON")"

  while IFS= read -r lang; do
    [[ -z "$lang" ]] && continue
    if should_skip_language "$lang"; then
      continue
    fi

    while IFS= read -r hook; do
      [[ -z "$hook" ]] && continue
      while IFS= read -r reg; do
        [[ -z "$reg" ]] && continue
        while IFS= read -r owc; do
          [[ -z "$owc" ]] && continue
          while IFS= read -r ts; do
            [[ -z "$ts" ]] && continue

            n=$((n + 1))
            if [[ -n "${MAX_RUNS:-}" && "$n" -gt "$MAX_RUNS" ]]; then
              echo "Stopped at MAX_RUNS=$MAX_RUNS"
              exit 0
            fi

            fname="oc_gpt_${RUN_STAMP}_$(printf '%06d' "$n").json"
            pfile="$PROMPT_LOG_DIR/prompt_$(printf '%06d' "$n").txt"
            outf="$OUT_ROOT/$fname"

            payload="$(jq -n \
              --arg language "$lang" \
              --arg category "$cat" \
              --arg hook_type "$hook" \
              --arg tone "$reg" \
              --arg emotional_register "$reg" \
              --arg opening_word_class "$owc" \
              --arg title_style "$ts" \
              --arg topic "$TOPIC_ANCHOR" \
              --arg themes_json "$themes_json" \
              --arg human_contexts_json "$hctx_json" \
              --arg avoid_titles "$AVOID_TITLES" \
              '{
                prompt_version: "large",
                variables: {
                  language: $language,
                  category: $category,
                  hook_type: $hook_type,
                  tone: $tone,
                  emotional_register: $emotional_register,
                  opening_word_class: $opening_word_class,
                  title_style: $title_style,
                  topic: $topic,
                  themes_json: $themes_json,
                  human_contexts_json: $human_contexts_json,
                  avoid_titles: $avoid_titles
                }
              }')"

            prompt="$(render_payload_to_prompt "$payload")"
            printf '%s' "$prompt" >"$pfile"

            set +e
            openclaw agent \
              --agent "$OPENCLAW_AGENT" \
              --message "$prompt" \
              --json \
              --timeout "$OC_TIMEOUT" \
              >"$outf" 2>"$PROMPT_LOG_DIR/${fname%.json}.stderr.log"
            ec=$?
            set -e

            if [[ "$ec" -ne 0 ]]; then
              jq -n \
                --argjson idx "$n" \
                --arg cat "$cat" \
                --arg lang "$lang" \
                --arg err "openclaw_exit_$ec" \
                '{error: $err, combo_index: $idx, category: $cat, language: $lang}' \
                >"$outf"
            fi

            echo "[$n] wrote $outf (prompt -> $pfile)"
          done < <(jq -r '.title_style_hints.styles[]' "$CONFIG_JSON")
        done < <(jq -r '.opening_word_classes[]' "$CONFIG_JSON")
      done < <(jq -r '.registers[]' "$CONFIG_JSON")
    done < <(jq -r '.hook_types[]' "$CONFIG_JSON")
  done < <(jq -r '.languages[]' "$CONFIG_JSON")
done

echo "Done. $n combination(s). JSON under: $OUT_ROOT (prompts + stderr: $PROMPT_LOG_DIR)"
exit 0
