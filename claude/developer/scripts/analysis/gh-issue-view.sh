#!/bin/bash
# Fetch GitHub issue or PR details with comments
# Usage: gh-issue-view.sh <number> [repo]
# Default repo: iNavFlight/inav

NUMBER="${1:?Usage: gh-issue-view.sh <number> [repo]}"
REPO="${2:-iNavFlight/inav}"

gh issue view "$NUMBER" --repo "$REPO" --json title,body,comments \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Title:', data['title'])
print()
print('Body:')
print(data['body'][:3000] if data['body'] else '(empty)')
print()
print(f'Comments: {len(data[\"comments\"])}')
for c in data['comments'][:10]:
    print(f'---')
    print(f'{c[\"author\"][\"login\"]}:')
    print(c['body'][:500])
"
