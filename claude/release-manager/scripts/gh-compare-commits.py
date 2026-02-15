#!/usr/bin/env python3
"""List commits between two git refs via GitHub API.

Usage:
    gh api repos/OWNER/REPO/compare/BASE...HEAD | python3 gh-compare-commits.py

Example:
    gh api repos/iNavFlight/inav/compare/9.0.0...maintenance-9.x 2>&1 | python3 gh-compare-commits.py
"""
import json, sys

data = json.load(sys.stdin)
print(f"ahead_by: {data['ahead_by']}, behind_by: {data['behind_by']}")
print()
for c in data['commits']:
    sha = c['sha'][:10]
    author = c.get('author', {})
    login = author.get('login', '') if author else c['commit']['author']['name']
    msg = c['commit']['message'].split('\n')[0]
    print(f'{sha} {login} | {msg}')
