#!/bin/bash

# Stop hook — fires after each Claude response.
# Every TIP_INTERVAL turns, emits a random framework tip as a systemMessage.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read stdin once — Claude Code passes session metadata as JSON. The tip logic
# doesn't need any of it, but stdin must be consumed so the hook doesn't block.
cat >/dev/null

TIPS_FILE="$SCRIPT_DIR/framework-tips.txt"
COUNTER_FILE="$SCRIPT_DIR/session-turn-count.txt"
TIP_INTERVAL=10

COUNT=0
if [ -f "$COUNTER_FILE" ]; then
    RAW=$(cat "$COUNTER_FILE" 2>/dev/null | tr -d '[:space:]')
    [[ "$RAW" =~ ^[0-9]+$ ]] && COUNT="$RAW"
fi
COUNT=$((COUNT + 1))
echo "$COUNT" > "$COUNTER_FILE"

TIP_MSG=""
if (( COUNT % TIP_INTERVAL == 0 )); then
    mapfile -t TIPS < <(grep -v '^\s*#' "$TIPS_FILE" | grep -v '^\s*$')
    NUM_TIPS="${#TIPS[@]}"
    if (( NUM_TIPS > 0 )); then
        TIP_MSG="💡 ${TIPS[$((RANDOM % NUM_TIPS))]}"
    fi
fi

if [ -z "$TIP_MSG" ]; then
    exit 0
fi

python3 -c "
import sys, json
print(json.dumps({'systemMessage': sys.argv[1]}))
" "$TIP_MSG"
