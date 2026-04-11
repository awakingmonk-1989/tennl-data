#!/usr/bin/env bash
# insight_card_openclaw_smoke.sh
#
# One real OpenClaw invocation + validation (prompt variables, output path, JSON).
#
# Invokes the daemon script in the foreground (no --daemon flag). For a
# detached run until all combos finish, use insight_card_openclaw_daemon.sh --daemon.
#
# OPENCLAW_AGENT is forced to "main" for this smoke run.
#
# Usage (from repo root):
#   ./scripts/insight_cards/insight_card_openclaw_smoke.sh
# Env:
#   OC_TIMEOUT — openclaw timeout seconds (default: 120)
#   SMOKE_CATEGORY — category key (default: Technology)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SMOKE_CATEGORY="${SMOKE_CATEGORY:-Technology}"
OC_TIMEOUT="${OC_TIMEOUT:-120}"

# Isolated output tree so we can glob the single artifact.
SMOKE_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/tennl_oc_gpt_smoke.XXXXXX")"
cleanup() { rm -rf "$SMOKE_ROOT"; }
trap cleanup EXIT

export OC_GPT_RUNS_PARENT="$SMOKE_ROOT"
export MAX_RUNS=1
export OPENCLAW_AGENT=main

echo "=== OpenClaw insight-card smoke ==="
echo "  Foreground driver (not a detached daemon)."
echo "  OPENCLAW_AGENT : main (forced)"
echo "  category       : $SMOKE_CATEGORY"
echo "  output parent  : $SMOKE_ROOT"
echo "  OC_TIMEOUT     : $OC_TIMEOUT"
echo "===================================="

"$SCRIPT_DIR/insight_card_openclaw_daemon.sh" "$SMOKE_CATEGORY"

OUT_JSON=""
while IFS= read -r f; do
  OUT_JSON="$f"
  break
done < <(find "$SMOKE_ROOT" -maxdepth 1 -type f -name 'oc_gpt_*.json' | sort)
if [[ -z "$OUT_JSON" ]]; then
  echo "error: no oc_gpt_*.json under $SMOKE_ROOT" >&2
  exit 1
fi

PROMPT_FILE=""
while IFS= read -r f; do
  PROMPT_FILE="$f"
  break
done < <(find "$SMOKE_ROOT" -type f -path '*/prompts_*/prompt_000001.txt' | sort)
if [[ -z "$PROMPT_FILE" ]]; then
  echo "error: no prompt_000001.txt under $SMOKE_ROOT" >&2
  exit 1
fi

echo "--- prompt file: $PROMPT_FILE"
# First combo after language skips: Tamil × first hook × first register × first owc × first title style
grep -q 'Language: STRICTLY In Tamil' "$PROMPT_FILE" || { echo "error: expected Tamil in prompt" >&2; exit 1; }
grep -q "Category: $SMOKE_CATEGORY" "$PROMPT_FILE" || { echo "error: expected category in prompt" >&2; exit 1; }
grep -q 'Hook style: contrarian-claim' "$PROMPT_FILE" || { echo "error: expected hook_type in prompt" >&2; exit 1; }
grep -q 'Themes pool (JSON array' "$PROMPT_FILE" || { echo "error: expected themes_json section" >&2; exit 1; }
grep -q '"behaviour and habit"' "$PROMPT_FILE" || { echo "error: expected Technology theme in prompt" >&2; exit 1; }

echo "--- output json: $OUT_JSON"
jq empty "$OUT_JSON" || { echo "error: outer file is not valid JSON" >&2; exit 1; }

status="$(jq -r '.status // empty' "$OUT_JSON")"
if [[ "$status" != "ok" ]]; then
  echo "error: expected .status ok, got $(jq -c . "$OUT_JSON" | head -c 400)" >&2
  exit 1
fi

jq -e '(.result.payloads | type == "array") and (.result.payloads | length > 0)' "$OUT_JSON" >/dev/null \
  || { echo "error: missing .result.payloads" >&2; exit 1; }

inner="$(jq -r '.result.payloads[0].text // empty' "$OUT_JSON")"
if [[ -z "$inner" ]]; then
  echo "error: empty .result.payloads[0].text" >&2
  exit 1
fi

echo "$inner" | jq empty || { echo "error: inner payloads[0].text is not valid JSON" >&2; exit 1; }

echo "$inner" | jq -e '
  (.title | type == "string") and (.title | length > 0)
  and (.category | type == "string")
  and (.content | type == "string") and (.content | length > 0)
  and (.layout | type == "string")
  and (.content_blocks | type == "object")
  and (.tone | type == "string")
  and (.emotional_register | type == "string")
  and (.title_style | type == "string")
  and (.hook_type | type == "string")
  and (.opening_word_class | type == "string")
' >/dev/null || { echo "error: inner JSON missing insight-card-shaped fields" >&2; exit 1; }

echo "=== smoke OK (OpenClaw agent=main, 1 invocation, valid envelope + card JSON) ==="
exit 0
