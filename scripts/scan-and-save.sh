#!/usr/bin/env bash
# Run a GitHub scan and save the JSON result to a file.
# Usage: ./scripts/scan-and-save.sh [USERNAME]
#        ./scripts/scan-and-save.sh Mjeedbakr
# Output: output/scan_<USERNAME>.json

set -e

USERNAME="${1:-Mjeedbakr}"
BASE_URL="${BASE_URL:-http://localhost:8000}"
OUTPUT_DIR="output"
OUTPUT_FILE="${OUTPUT_DIR}/scan_${USERNAME}.json"

mkdir -p "$OUTPUT_DIR"

echo "Scanning GitHub user: $USERNAME"
echo "Saving to: $OUTPUT_FILE"

CURL_OPTS=(-s -X POST "${BASE_URL}/scan" -H "Content-Type: application/json" -d "{\"github_username\":\"${USERNAME}\",\"review_mode\":\"portfolio\",\"scan_scope\":\"public\"}")
if [[ "$BASE_URL" == https://* ]]; then
  CURL_OPTS+=(-H "ngrok-skip-browser-warning: true")
fi

curl "${CURL_OPTS[@]}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    json.dump(d, sys.stdout, indent=2, ensure_ascii=False)
except (json.JSONDecodeError, ValueError) as e:
    sys.stderr.write(str(e) + '\n')
    sys.exit(1)
" > "$OUTPUT_FILE"

if [ -s "$OUTPUT_FILE" ] && head -c1 "$OUTPUT_FILE" | grep -q '{'; then
  echo "Done. Result saved to $OUTPUT_FILE (formatted)"
else
  echo "Request may have failed. Check $OUTPUT_FILE for response."
  exit 1
fi
