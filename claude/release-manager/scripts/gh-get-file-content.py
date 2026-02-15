#!/usr/bin/env python3
"""Decode and print a file from GitHub Contents API (base64-encoded).

Usage:
    gh api repos/OWNER/REPO/contents/PATH?ref=BRANCH | python3 gh-get-file-content.py [--lines N]

Example:
    gh api repos/iNavFlight/inav/contents/CMakeLists.txt?ref=maintenance-9.x | python3 gh-get-file-content.py --lines 20
"""
import json, sys, base64, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--lines', type=int, default=0, help='Limit output to N lines (0=all)')
parser.add_argument('--grep', type=str, default='', help='Only print lines containing this string')
args = parser.parse_args()

data = json.load(sys.stdin)
content = base64.b64decode(data['content']).decode()

lines = content.split('\n')
if args.grep:
    lines = [l for l in lines if args.grep in l]
if args.lines:
    lines = lines[:args.lines]

for line in lines:
    print(line)
