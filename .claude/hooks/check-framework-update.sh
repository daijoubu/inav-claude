#!/bin/bash
# SessionStart hook - asks (roughly monthly) whether to update the harness
# repo itself. Never runs git pull itself - only ever asks.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FETCH_HEAD="$PROJECT_ROOT/.git/FETCH_HEAD"
ASK_MARKER="$SCRIPT_DIR/last-framework-update-ask.txt"

UPDATE_INTERVAL_DAYS=30
REASK_INTERVAL_DAYS=7

cat >/dev/null  # drain stdin so the hook doesn't block

# No FETCH_HEAD (e.g. a same-day fresh clone) - not yet due.
if [ ! -f "$FETCH_HEAD" ]; then
    exit 0
fi

NOW=$(date +%s)
FETCH_MTIME=$(stat -c %Y "$FETCH_HEAD" 2>/dev/null)
[[ "$FETCH_MTIME" =~ ^[0-9]+$ ]] || exit 0

AGE_DAYS=$(( (NOW - FETCH_MTIME) / 86400 ))
if (( AGE_DAYS < UPDATE_INTERVAL_DAYS )); then
    exit 0
fi

# upstream, if configured, is where real framework updates land (origin is
# this checkout's own fork). Otherwise origin is the canonical remote.
if git -C "$PROJECT_ROOT" remote get-url upstream >/dev/null 2>&1; then
    UPDATE_REMOTE="upstream"
else
    UPDATE_REMOTE="origin"
fi
UPDATE_BRANCH="master"

# Local-only comparison (no fetch) - catches "already pushed, nothing to
# pull" even though FETCH_HEAD is stale. Can't see updates that landed on
# $UPDATE_REMOTE since our last fetch/push of it; worst case we ask a
# cadence period later than ideal, which is fine for a reminder.
BEHIND_COUNT=$(git -C "$PROJECT_ROOT" rev-list "HEAD..$UPDATE_REMOTE/$UPDATE_BRANCH" --count 2>/dev/null)
if [[ "$BEHIND_COUNT" =~ ^[0-9]+$ ]] && (( BEHIND_COUNT == 0 )); then
    exit 0
fi

# Don't re-ask every session while still overdue.
if [ -f "$ASK_MARKER" ]; then
    LAST_ASKED=$(cat "$ASK_MARKER" 2>/dev/null | tr -d '[:space:]')
    if [[ "$LAST_ASKED" =~ ^[0-9]+$ ]]; then
        ASKED_DAYS_AGO=$(( (NOW - LAST_ASKED) / 86400 ))
        if (( ASKED_DAYS_AGO < REASK_INTERVAL_DAYS )); then
            exit 0
        fi
    fi
fi

echo "$NOW" > "$ASK_MARKER"

python3 -c "
import sys, json
print(json.dumps({'systemMessage': sys.argv[1]}))
" "It's been about $AGE_DAYS days since this harness repo (claude/ and .claude/) was last updated from $UPDATE_REMOTE. Want me to run 'git pull --ff-only $UPDATE_REMOTE $UPDATE_BRANCH' in the repo root? It's non-destructive and reversible - just say no to skip."
