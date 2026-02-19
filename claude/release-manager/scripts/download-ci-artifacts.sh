#!/bin/bash
# Download CI artifacts from a GitHub Actions workflow run.
# Uses GitHub API + curl with retries to handle Azure blob timeouts
# that cause `gh run download` to fail.
#
# Usage:
#   ./download-ci-artifacts.sh <repo> <run-id> <output-dir>
#
# Examples:
#   ./download-ci-artifacts.sh iNavFlight/inav-configurator 22046852707 /tmp/configurator-9.0.2
#   ./download-ci-artifacts.sh iNavFlight/inav 12345678 /tmp/firmware-9.0.2

set -euo pipefail

REPO="${1:?Usage: $0 <repo> <run-id> <output-dir>}"
RUN_ID="${2:?Usage: $0 <repo> <run-id> <output-dir>}"
OUTPUT_DIR="${3:?Usage: $0 <repo> <run-id> <output-dir>}"

MAX_RETRIES=5
CURL_TIMEOUT=300  # 5 minutes per artifact
RETRY_DELAY=10

# Get GitHub token from env, gh CLI, or gh config file
if [ -n "${GH_TOKEN:-}" ]; then
    TOKEN="$GH_TOKEN"
elif TOKEN=$(gh auth token 2>/dev/null); then
    :
elif [ -f "$HOME/.config/gh/hosts.yml" ]; then
    TOKEN=$(grep 'oauth_token:' "$HOME/.config/gh/hosts.yml" | head -1 | awk '{print $2}')
fi

if [ -z "${TOKEN:-}" ]; then
    echo "ERROR: No GitHub token found. Set GH_TOKEN or run 'gh auth login'."
    exit 1
fi

# Use gh if available, otherwise fall back to curl for API calls
api_call() {
    if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
        gh api "$@"
    else
        local endpoint="$1"; shift
        curl -sL \
            -H "Authorization: Bearer $TOKEN" \
            -H "Accept: application/vnd.github+json" \
            "https://api.github.com/$endpoint" "$@"
    fi
}

mkdir -p "$OUTPUT_DIR"

echo "Fetching artifact list for run $RUN_ID in $REPO..."

# Get all artifacts as "id name size" lines
ARTIFACTS=$(curl -sL \
    -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$REPO/actions/runs/$RUN_ID/artifacts?per_page=100" \
    | python3 -c "import json,sys; [print(a['id'], a['name'], a['size_in_bytes']) for a in json.load(sys.stdin).get('artifacts',[])]")

if [ -z "$ARTIFACTS" ]; then
    echo "ERROR: No artifacts found for run $RUN_ID"
    exit 1
fi

TOTAL=$(echo "$ARTIFACTS" | wc -l)
echo "Found $TOTAL artifacts to download."
echo ""

DOWNLOADED=0
FAILED=0
SKIPPED=0

while IFS=' ' read -r id name size; do
    dest="$OUTPUT_DIR/$name"
    human_size=$(numfmt --to=iec-i --suffix=B "$size" 2>/dev/null || echo "${size}B")

    # Skip if already downloaded and non-empty
    if [ -d "$dest" ] && [ "$(find "$dest" -type f 2>/dev/null | head -1)" ]; then
        echo "SKIP  $name (already exists)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    attempt=0
    success=false
    while [ $attempt -lt $MAX_RETRIES ]; do
        attempt=$((attempt + 1))
        echo -n "[$((DOWNLOADED + FAILED + SKIPPED + 1))/$TOTAL] $name ($human_size) attempt $attempt/$MAX_RETRIES... "

        tmpzip=$(mktemp)
        http_code=$(curl -sL --max-time "$CURL_TIMEOUT" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Accept: application/vnd.github+json" \
            -o "$tmpzip" -w "%{http_code}" \
            "https://api.github.com/repos/$REPO/actions/artifacts/$id/zip" 2>/dev/null) || http_code="000"

        if [ "$http_code" = "200" ] && [ -s "$tmpzip" ]; then
            mkdir -p "$dest"
            if unzip -q -o "$tmpzip" -d "$dest" 2>/dev/null; then
                rm -f "$tmpzip"
                file_count=$(find "$dest" -type f | wc -l)
                echo "OK ($file_count file(s))"
                success=true
                break
            else
                echo "unzip failed"
                rm -f "$tmpzip"
                rm -rf "$dest"
            fi
        else
            rm -f "$tmpzip"
            if [ "$http_code" = "000" ]; then
                echo "timeout"
            else
                echo "HTTP $http_code"
            fi
        fi

        if [ $attempt -lt $MAX_RETRIES ]; then
            sleep "$RETRY_DELAY"
        fi
    done

    if $success; then
        DOWNLOADED=$((DOWNLOADED + 1))
    else
        echo "FAILED $name after $MAX_RETRIES attempts"
        FAILED=$((FAILED + 1))
    fi
done <<< "$ARTIFACTS"

echo ""
echo "============================="
echo "Downloaded: $DOWNLOADED"
echo "Skipped:    $SKIPPED"
echo "Failed:     $FAILED"
echo "Total:      $TOTAL"
echo "Output dir: $OUTPUT_DIR"
echo "============================="

if [ $FAILED -gt 0 ]; then
    echo ""
    echo "WARNING: $FAILED artifact(s) failed to download. Re-run this script to retry."
    exit 1
fi
