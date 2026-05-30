#!/bin/bash
# pre-prompt-inject.sh — UserPromptSubmit hook
# Queries ChromaDB for memories relevant to the current user message and injects
# them as a systemMessage so Claude can see them before responding.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

HOOK_INPUT=$(cat)

TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('transcript_path',''))" 2>/dev/null)
SESSION_ID=$(echo "$HOOK_INPUT" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('session_id',''))" 2>/dev/null)
USER_PROMPT=$(echo "$HOOK_INPUT" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('user_prompt','')[:600])" 2>/dev/null)

if [ -z "$SESSION_ID" ]; then
    exit 0
fi

MEMORY_MSG=$(python3 "$SCRIPT_DIR/passive_inject.py" \
    "$TRANSCRIPT_PATH" "$SESSION_ID" \
    --query-text "$USER_PROMPT" \
    2>/dev/null)

if [ -z "$MEMORY_MSG" ]; then
    exit 0
fi

python3 -c "
import sys, json
print(json.dumps({'systemMessage': sys.argv[1]}))
" "$MEMORY_MSG"
