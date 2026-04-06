#!/usr/bin/env bash
# Download Rocket.new project: project-structure -> file-content for each file.
# Bash 3.2-safe (no mapfile).
set -euo pipefail

ROOT="/Users/devansh/tennl-data/all-new-rt"
BASE="https://xplatform9952back.builtwithrocket.new/api"

# Same headers as provided curl (no Cookie in original)
HDRS=(
  -H 'Accept: application/json, text/plain, */*'
  -H 'Accept-Language: en-GB,en;q=0.9'
  -H 'Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlblR5cGUiOiJhY2Nlc3MiLCJ1c2VyIjp7Il9pZCI6IjY5ZDBkNTgzOTlhMzA5MDAxNGE5Mjk5NyIsImlkIjoiNjlkMGQ1ODM5OWEzMDkwMDE0YTkyOTk3IiwidHlwZSI6Mywic2Vzc2lvbklkIjoiYmU0MDJmZjAtZjE3NC00MjAyLTk4MTktNDAzY2M2OGI1ZGQ0In0sImlhdCI6MTc3NTI5MzgyOCwiZXhwIjoxNzc1MzgwMjI4fQ.3uwQQwweSdLCwQ5JaaZnMTduNh_aVWT3SUEJjGP0Kvw'
  -H 'Cache-Control: no-cache'
  -H 'Connection: keep-alive'
  -H 'Content-Type: application/json'
  -H 'Expires: 0'
  -H 'Origin: https://www.rocket.new'
  -H 'Pragma: no-cache'
  -H 'Referer: https://www.rocket.new/'
  -H 'Sec-Fetch-Dest: empty'
  -H 'Sec-Fetch-Mode: cors'
  -H 'Sec-Fetch-Site: cross-site'
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
  -H 'X-Thread-Id: 69d0d5a153f834001409f799'
  -H 'companyId: 69d0d58399a3090014a9299d'
  -H 'pageURL: https://www.rocket.new/69d0d5a153f834001409f799#code'
  -H 'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"'
  -H 'sec-ch-ua-mobile: ?0'
  -H 'sec-ch-ua-platform: "macOS"'
)

mkdir -p "$ROOT"

STRUCT_JSON=$(mktemp)
PATHLIST=$(mktemp)
trap 'rm -f "$STRUCT_JSON" "$PATHLIST"' EXIT

curl -sS "${HDRS[@]}" \
  --data-raw '{}' \
  "$BASE/project-structure" \
  -o "$STRUCT_JSON"

if ! jq -e . >/dev/null 2>&1 <"$STRUCT_JSON"; then
  echo "project-structure: not valid JSON" >&2
  cat "$STRUCT_JSON" >&2
  exit 1
fi

# Collect every file path from nested tree
jq -r '.. | objects | select(.type == "file") | .path' <"$STRUCT_JSON" >"$PATHLIST"
nfiles=$(wc -l <"$PATHLIST" | tr -d ' ')
echo "Found $nfiles files"

while IFS= read -r apath; do
  [[ -z "$apath" ]] && continue
  rel="${apath#/}"
  dest="$ROOT/$rel"
  mkdir -p "$(dirname "$dest")"

  fc_json=$(mktemp)
  curl -sS "${HDRS[@]}" \
    --data-raw "$(jq -nc --arg p "$apath" '{path: $p}')" \
    "$BASE/file-content" \
    -o "$fc_json"

  if ! jq -e .content >/dev/null 2>&1 <"$fc_json"; then
    echo "SKIP or ERROR: $apath" >&2
    cat "$fc_json" >&2
    rm -f "$fc_json"
    continue
  fi

  # API returns base64 for binary assets; plain text for source files.
  ext="${rel##*.}"
  ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
  case "$ext_lower" in
    png|jpg|jpeg|gif|webp|ico|bmp|pdf|zip|gz|woff|woff2|ttf|eot)
      jq -r '.content' <"$fc_json" | base64 -d >"$dest"
      ;;
    *)
      jq -r '.content' <"$fc_json" >"$dest"
      ;;
  esac
  rm -f "$fc_json"
  echo "wrote $dest"
done <"$PATHLIST"

echo "Done -> $ROOT"
