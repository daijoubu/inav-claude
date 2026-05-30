#!/bin/bash
# Stop hook — fires after each Claude response.
# 1. Ingests new session content into ChromaDB memory (background, delta-only).
# 2. Every TIP_INTERVAL turns, emits a random framework tip.
# Memory injection is handled by pre-prompt-inject.sh (UserPromptSubmit hook).

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

# ── 2. Framework tip (every TIP_INTERVAL turns) ───────────────────────────────
# (Memory injection moved to UserPromptSubmit hook: pre-prompt-inject.sh)
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

# ── 3. Emit tip as systemMessage if due ──────────────────────────────────────
if [ -z "$TIP_MSG" ]; then
    exit 0
fi

python3 -c "
import sys, json
print(json.dumps({'systemMessage': sys.argv[1]}))
" "$TIP_MSG"
