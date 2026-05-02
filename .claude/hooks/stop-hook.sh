#!/bin/bash
# Stop hook — fires after each Claude response.
# 1. Ingests new session content into ChromaDB memory (background, delta-only).
# 2. Passively injects highly relevant memories as a systemMessage.
# 3. Every TIP_INTERVAL turns, appends a random framework tip.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read stdin once — Claude Code passes session metadata as JSON
HOOK_INPUT=$(cat)
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('transcript_path',''))" 2>/dev/null)
SESSION_ID=$(echo "$HOOK_INPUT" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('session_id',''))" 2>/dev/null)

# ── 1. Background-ingest the session (delta only — fast if nothing new) ──────
INGEST_SCRIPT="$SCRIPT_DIR/../../claude/developer/scripts/analysis/ingest_session.py"
if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$INGEST_SCRIPT" ]; then
    python3 "$INGEST_SCRIPT" "$TRANSCRIPT_PATH" \
        >>"$SCRIPT_DIR/ingest.log" 2>&1 &
    disown
fi

# ── 2. Passive memory injection ───────────────────────────────────────────────
MEMORY_MSG=""
if [ -n "$TRANSCRIPT_PATH" ] && [ -n "$SESSION_ID" ]; then
    MEMORY_MSG=$(python3 "$SCRIPT_DIR/passive_inject.py" \
        "$TRANSCRIPT_PATH" "$SESSION_ID" 2>/dev/null)
fi

# ── 3. Framework tip (every TIP_INTERVAL turns) ───────────────────────────────
TIPS_FILE="$SCRIPT_DIR/framework-tips.txt"
COUNTER_FILE="$SCRIPT_DIR/session-turn-count.txt"
TIP_INTERVAL=7

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

# ── 4. Emit combined systemMessage if anything to say ─────────────────────────
if [ -z "$MEMORY_MSG" ] && [ -z "$TIP_MSG" ]; then
    exit 0
fi

python3 - "$MEMORY_MSG" "$TIP_MSG" <<'PYEOF'
import sys, json

memory_msg = sys.argv[1]
tip_msg    = sys.argv[2]

parts = [p for p in [memory_msg, tip_msg] if p]
combined = "\n\n".join(parts)
print(json.dumps({"systemMessage": combined}))
PYEOF
