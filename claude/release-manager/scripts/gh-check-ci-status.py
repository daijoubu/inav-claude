#!/usr/bin/env python3
"""Summarize CI check-run conclusions from GitHub API.

Usage:
    gh api repos/OWNER/REPO/commits/REF/check-runs | python3 gh-check-ci-status.py

Example:
    gh api repos/iNavFlight/inav/commits/maintenance-9.x/check-runs 2>&1 | python3 gh-check-ci-status.py
"""
import json, sys
from collections import Counter

data = json.load(sys.stdin)
c = Counter(r['conclusion'] for r in data['check_runs'] if r['conclusion'])
for k, v in c.items():
    print(f'{k}: {v}')
