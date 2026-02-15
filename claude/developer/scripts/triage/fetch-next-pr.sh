#!/bin/bash
# fetch-next-pr.sh - Fetch next open PR for milestone triage
#
# Finds the oldest open PR that:
#   - Has no milestone assigned
#   - Is not a draft
#   - Is not labeled "don't merge"
#   - Was created after the specified date
#
# Usage: fetch-next-pr.sh <owner/repo> <YYYY-MM-DD> [skip-file] [--hierarchical offset] [--output file]
# Example: fetch-next-pr.sh iNavFlight/inav 2025-02-07
# Example: fetch-next-pr.sh iNavFlight/inav 2025-02-07 /tmp/claude/skip-inav.txt --offset 1
# Example: fetch-next-pr.sh iNavFlight/inav 2025-02-07 /tmp/claude/skip-inav.txt --output /tmp/claude/next-pr.txt

set -euo pipefail

REPO="${1:?Usage: fetch-next-pr.sh <owner/repo> <YYYY-MM-DD> [skip-file] [--offset N] [--output file]}"
AFTER_DATE="${2:?Usage: fetch-next-pr.sh <owner/repo> <YYYY-MM-DD> [skip-file] [--offset N] [--output file]}"
SKIP_FILE="${3:-}"
OFFSET=0
OUTPUT_FILE=""

# Parse optional flags (after positional args)
shift 2
[[ -n "${1:-}" && "$1" != "--"* ]] && shift  # skip skip-file if present
while [[ $# -gt 0 ]]; do
    case "$1" in
        --offset) OFFSET="$2"; shift 2 ;;
        --output) OUTPUT_FILE="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Redirect output to file if requested
if [[ -n "$OUTPUT_FILE" ]]; then
    exec > "$OUTPUT_FILE" 2>&1
fi

# Build skip list for jq
SKIP_JSON="[]"
if [[ -n "$SKIP_FILE" && -f "$SKIP_FILE" ]]; then
    SKIP_LINES=$(grep -v '^#' "$SKIP_FILE" | grep -v '^$' || true)
    if [[ -n "$SKIP_LINES" ]]; then
        SKIP_JSON=$(echo "$SKIP_LINES" | jq -R 'tonumber' | jq -s '.' 2>/dev/null || echo "[]")
    fi
fi

# Use cached PR list if available and fresh (< 2 minutes old)
REPO_SLUG=$(echo "$REPO" | tr '/' '-')
CACHE_FILE="/tmp/claude/pr-cache-${REPO_SLUG}.json"
USE_CACHE=false

if [[ -f "$CACHE_FILE" ]]; then
    CACHE_AGE=$(( $(date +%s) - $(stat -c %Y "$CACHE_FILE") ))
    if [[ $CACHE_AGE -lt 120 ]]; then
        USE_CACHE=true
    fi
fi

if [[ "$USE_CACHE" == "true" ]]; then
    PR_JSON=$(cat "$CACHE_FILE")
else
    # Fetch open PRs without milestone, excluding "don't merge" label, after date
    PR_JSON=$(gh api "repos/${REPO}/pulls?state=open&per_page=100&sort=created&direction=asc" \
        --paginate \
        --jq '[.[] | select(.milestone == null) | select(.draft == false) | select((.labels | map(.name) | any(test("don.t merge"; "i"))) | not) | select(.created_at > "'"${AFTER_DATE}"'") | {number: .number, title: .title, createdAt: .created_at, author: .user.login, labels: [.labels[].name], body: .body, url: .html_url, baseBranch: .base.ref}]' \
        2>/dev/null | jq -s 'flatten')
    # Cache the result
    mkdir -p /tmp/claude
    echo "$PR_JSON" > "$CACHE_FILE"
fi

if [[ -z "$PR_JSON" || "$PR_JSON" == "[]" || "$PR_JSON" == "null" ]]; then
    echo "NO_MORE_PRS"
    echo "No more PRs to triage for $REPO (after $AFTER_DATE)"
    exit 0
fi

# Filter out skipped PRs, sort by date, pick item at OFFSET
FILTERED=$(echo "$PR_JSON" | jq --argjson skip "$SKIP_JSON" '
    map(select(.number as $n | $skip | index($n) | not))
    | sort_by(.createdAt)')

REMAINING=$(echo "$FILTERED" | jq 'length')

NEXT_PR=$(echo "$FILTERED" | jq --argjson idx "$OFFSET" '.[$idx] // empty')

if [[ -z "$NEXT_PR" || "$NEXT_PR" == "null" ]]; then
    echo "NO_MORE_PRS"
    echo "No more PRs to triage for $REPO (after $AFTER_DATE)"
    exit 0
fi

# Extract fields
NUMBER=$(echo "$NEXT_PR" | jq -r '.number')
TITLE=$(echo "$NEXT_PR" | jq -r '.title')
URL=$(echo "$NEXT_PR" | jq -r '.url')
AUTHOR=$(echo "$NEXT_PR" | jq -r '.author')
CREATED=$(echo "$NEXT_PR" | jq -r '.createdAt[:10]')
LABELS_RAW=$(echo "$NEXT_PR" | jq -r '[.labels[]] | join(", ")')
LABELS="${LABELS_RAW:-none}"
BODY=$(echo "$NEXT_PR" | jq -r '.body // "No description"')
BASE_BRANCH=$(echo "$NEXT_PR" | jq -r '.baseBranch')

# Check for "needs testing" label
NEEDS_TESTING="No"
if echo "$NEXT_PR" | jq -e '[.labels[]] | any(test("needs testing"; "i"))' >/dev/null 2>&1; then
    NEEDS_TESTING="YES"
fi

# Fetch reviews
REVIEWS=$(gh api "repos/${REPO}/pulls/${NUMBER}/reviews" \
    --jq '[.[] | {author: .user.login, state: .state}] | unique_by(.author)' \
    2>/dev/null || echo "[]")

# Fetch recent issue comments (last 10)
COMMENTS=$(gh api "repos/${REPO}/issues/${NUMBER}/comments?per_page=10&direction=desc" \
    --jq '[.[:10] | reverse | .[] | {
        author: .user.login,
        created: .created_at[:10],
        body: (if (.body | length) > 400 then (.body[:400] + "...") else .body end)
    }]' 2>/dev/null || echo "[]")

# Fetch available milestones for reference
MILESTONES=$(gh api "repos/${REPO}/milestones?state=open" \
    --jq '[.[] | "\(.number):\(.title)"] | join(", ")' \
    2>/dev/null || echo "unknown")

# Output
echo "============================================================"
echo "REPO: $REPO"
echo "PR #$NUMBER: $TITLE"
echo "============================================================"
echo "URL:            $URL"
echo "Author:         $AUTHOR"
echo "Created:        $CREATED"
echo "Base Branch:    $BASE_BRANCH"
echo "Labels:         $LABELS"
echo "Needs Testing:  $NEEDS_TESTING"
echo "Remaining:      $REMAINING PRs to triage (after $AFTER_DATE)"
echo "Milestones:     $MILESTONES"
echo ""
echo "--- Reviews ---"
REVIEW_COUNT=$(echo "$REVIEWS" | jq 'length' 2>/dev/null || echo "0")
if [[ "$REVIEW_COUNT" == "0" ]]; then
    echo "  No reviews"
else
    echo "$REVIEWS" | jq -r '.[] | "  \(.author): \(.state)"' 2>/dev/null
fi
echo ""
echo "--- Description ---"
echo "$BODY"
echo ""
echo "--- Recent Comments (last 10) ---"
COMMENT_COUNT=$(echo "$COMMENTS" | jq 'length' 2>/dev/null || echo "0")
if [[ "$COMMENT_COUNT" == "0" ]]; then
    echo "  No comments"
else
    echo "$COMMENTS" | jq -r '.[] | "[\(.created)] \(.author):\n\(.body)\n"' 2>/dev/null
fi
echo "============================================================"
echo "PR_NUMBER=$NUMBER"
echo "BASE_BRANCH=$BASE_BRANCH"
