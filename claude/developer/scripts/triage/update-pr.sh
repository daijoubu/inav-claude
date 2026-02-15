#!/bin/bash
# update-pr.sh - Set milestone, base branch, and labels on a GitHub PR
#
# Usage: update-pr.sh <owner/repo> <pr_number> [options]
#   --milestone <number>      Set milestone by API number
#   --base <branch>           Set base branch
#   --add-label <label>       Add a label (repeatable)
#   --remove-label <label>    Remove a label (repeatable)
#
# Examples:
#   update-pr.sh iNavFlight/inav 11126 --milestone 50 --base maintenance-9.x --add-label "New target"
#   update-pr.sh iNavFlight/inav 11126 --milestone 51
#   update-pr.sh iNavFlight/inav 11126 --add-label "New target" --add-label "Enhancement"

set -euo pipefail

REPO="${1:?Usage: update-pr.sh <owner/repo> <pr_number> [--milestone N] [--base branch] [--add-label label] [--remove-label label]}"
PR="${2:?Usage: update-pr.sh <owner/repo> <pr_number> [--milestone N] [--base branch] [--add-label label] [--remove-label label]}"
shift 2

MILESTONE=""
BASE=""
ADD_LABELS=()
REMOVE_LABELS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --milestone) MILESTONE="$2"; shift 2 ;;
        --base) BASE="$2"; shift 2 ;;
        --add-label) ADD_LABELS+=("$2"); shift 2 ;;
        --remove-label) REMOVE_LABELS+=("$2"); shift 2 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

ERRORS=0

# Set milestone via issues API
if [[ -n "$MILESTONE" ]]; then
    if gh api --method PATCH "repos/${REPO}/issues/${PR}" -f "milestone=${MILESTONE}" --silent 2>/dev/null; then
        echo "OK: milestone set to ${MILESTONE}"
    else
        echo "FAIL: could not set milestone ${MILESTONE}" >&2
        ERRORS=$((ERRORS + 1))
    fi
fi

# Set base branch via pulls API
if [[ -n "$BASE" ]]; then
    if gh api --method PATCH "repos/${REPO}/pulls/${PR}" -f "base=${BASE}" --silent 2>/dev/null; then
        echo "OK: base branch set to ${BASE}"
    else
        echo "FAIL: could not set base branch ${BASE}" >&2
        ERRORS=$((ERRORS + 1))
    fi
fi

# Add labels via gh issue edit (most reliable method)
for LABEL in "${ADD_LABELS[@]+${ADD_LABELS[@]}}"; do
    if gh issue edit "${PR}" --repo "${REPO}" --add-label "${LABEL}" >/dev/null 2>&1; then
        echo "OK: added label \"${LABEL}\""
    else
        echo "FAIL: could not add label \"${LABEL}\"" >&2
        ERRORS=$((ERRORS + 1))
    fi
done

# Remove labels via gh issue edit
for LABEL in "${REMOVE_LABELS[@]+${REMOVE_LABELS[@]}}"; do
    if gh issue edit "${PR}" --repo "${REPO}" --remove-label "${LABEL}" >/dev/null 2>&1; then
        echo "OK: removed label \"${LABEL}\""
    else
        echo "FAIL: could not remove label \"${LABEL}\"" >&2
        ERRORS=$((ERRORS + 1))
    fi
done

if [[ $ERRORS -gt 0 ]]; then
    echo "${ERRORS} operation(s) failed" >&2
    exit 1
fi
