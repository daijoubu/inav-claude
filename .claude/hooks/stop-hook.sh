#!/bin/bash
# Stop hook — fires after each Claude response.
# Every TIP_INTERVAL turns, picks a random framework tip and injects it
# as a systemMessage so Claude displays it to the user on the next turn.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIPS_FILE="$SCRIPT_DIR/framework-tips.txt"
COUNTER_FILE="$SCRIPT_DIR/session-turn-count.txt"
TIP_INTERVAL=7   # show a tip every N turns (adjust 5-10 to taste)

# Read and increment the per-session turn counter
COUNT=0
if [ -f "$COUNTER_FILE" ]; then
    RAW=$(cat "$COUNTER_FILE" 2>/dev/null | tr -d '[:space:]')
    [[ "$RAW" =~ ^[0-9]+$ ]] && COUNT="$RAW"
fi
COUNT=$((COUNT + 1))
echo "$COUNT" > "$COUNTER_FILE"

# Only emit a tip on multiples of TIP_INTERVAL
if (( COUNT % TIP_INTERVAL != 0 )); then
    exit 0
fi

# Pick a random tip (skip blank lines and comments)
mapfile -t TIPS < <(grep -v '^\s*#' "$TIPS_FILE" | grep -v '^\s*$')
NUM_TIPS="${#TIPS[@]}"
if (( NUM_TIPS == 0 )); then
    exit 0
fi
CHOSEN="${TIPS[$((RANDOM % NUM_TIPS))]}"

python3 - "$CHOSEN" <<'PYEOF'
import sys, json

tip = sys.argv[1]
# Ask Claude to surface this tip to the user naturally
msg = f"FRAMEWORK TIP (display this to the user now, formatted as a brief tip): {tip}"
print(json.dumps({"systemMessage": msg}))
PYEOF
