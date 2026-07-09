#!/bin/bash
# Count fixes vs. features/enhancements merged into a release, for release-note
# and social-media summary blurbs ("N fixes and M new features/enhancements").
#
# Classification is a title-keyword heuristic, not a precise audit:
#   - Excluded: branch-sync/version-bump/CI-only housekeeping (not user-facing)
#   - Fix: title contains "fix" or "bug"
#   - Feature/Enhancement: everything else that's left
#
# Usage: ./count-fixes-and-features.sh <repo-path> <old-tag> <new-ref> [github-owner/repo]
# Run from claude/release-manager/ — repo-path is two levels up from there.
# Example: ./count-fixes-and-features.sh ../../inav 9.0.1 upstream/release/9.1 iNavFlight/inav

set -e

if [ $# -lt 3 ]; then
    echo "Usage: $0 <repo-path> <old-tag> <new-ref> [github-owner/repo]"
    echo ""
    echo "Examples (run from claude/release-manager/):"
    echo "  $0 ../../inav 9.0.1 upstream/release/9.1 iNavFlight/inav"
    echo "  $0 ../../inav-configurator 9.0.1 upstream/maintenance-9.x iNavFlight/inav-configurator"
    exit 1
fi

REPO_PATH="$1"
OLD_TAG="$2"
NEW_REF="$3"
GH_REPO="${4:-}"

if [ -z "$GH_REPO" ]; then
    GH_REPO=$(cd "$REPO_PATH" && git remote get-url upstream 2>/dev/null | sed -E 's#.*[:/]([^/]+/[^/]+)\.git#\1#')
fi

cd "$REPO_PATH"

PR_NUMBERS=$(git log "$OLD_TAG..$NEW_REF" --merges --format='%s' | grep -oE '#[0-9]+' | tr -d '#' | sort -n)
TOTAL=$(echo "$PR_NUMBERS" | grep -c . || true)

echo "Fetching $TOTAL PR titles from $GH_REPO (this makes one gh call per PR, can take a minute)..." >&2

TITLES_TSV=$(mktemp)
for pr in $PR_NUMBERS; do
  gh pr view "$pr" --repo "$GH_REPO" --json number,title --jq '"\(.number)\t\(.title)"' >> "$TITLES_TSV" 2>/dev/null
done

EXCLUDE_PATTERN='\t(release/[0-9.]+ to master|maintenance-[0-9.x]+ to master|master to maintenance|to master$|catch up|agent\.md|version bump|bump.*version|ci: |update release guide|readme)'

EXCLUDED=$(grep -icE "$EXCLUDE_PATTERN" "$TITLES_TSV" || true)
FIXES=$(grep -ivE "$EXCLUDE_PATTERN" "$TITLES_TSV" | grep -icE $'\t.*(fix|bug)' || true)
FEATURES=$((TOTAL - EXCLUDED - FIXES))

echo ""
echo "=== $GH_REPO: $OLD_TAG..$NEW_REF ==="
echo "Total merged PRs: $TOTAL"
echo "Excluded (housekeeping/non-user-facing): $EXCLUDED"
echo "Fixes: $FIXES"
echo "Features/Enhancements: $FEATURES"
echo ""
echo "=== Excluded PRs (verify none of these should count) ==="
grep -iE "$EXCLUDE_PATTERN" "$TITLES_TSV" || echo "(none)"

rm -f "$TITLES_TSV"
