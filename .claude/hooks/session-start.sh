#!/bin/bash
# SessionStart hook - Role selection prompt scaled to experience level.
# A "cycle" = one full manager-assigns + developer-implements workflow.
# Counter stored in: claude/onboarding/completed-cycles.txt

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ONBOARDING_FILE="$PROJECT_ROOT/claude/onboarding/completed-cycles.txt"

COUNT=0
if [ -f "$ONBOARDING_FILE" ]; then
    RAW=$(cat "$ONBOARDING_FILE" 2>/dev/null | tr -d '[:space:]')
    if [[ "$RAW" =~ ^[0-9]+$ ]]; then
        COUNT="$RAW"
    fi
fi

if [ "$COUNT" -eq 0 ]; then
    exec "$SCRIPT_DIR/onboarding-level-0.sh"
elif [ "$COUNT" -eq 1 ]; then
    exec "$SCRIPT_DIR/onboarding-level-1.sh"
else
    echo '{"systemMessage": "Which role today?  manager / developer / release-manager / security-analyst"}'
fi
