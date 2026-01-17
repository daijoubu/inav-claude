#!/usr/bin/env python3
"""
SubagentStart and SubagentStop hooks for Claude Code.

Logs the full input data to understand what fields are available
for identifying which sub-agent is running.
"""

import json
import os
import sys
from datetime import datetime

LOG_FILE = os.path.expanduser("~/inavflight/.claude/hooks/subagent_events.log")

def log_event(event_name: str, input_data: dict):
    """Log the full input data for a subagent event."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"[{timestamp}] {event_name}\n")
        f.write(f"{'='*60}\n")
        f.write(json.dumps(input_data, indent=2, default=str))
        f.write("\n")

def main():
    """Main entry point."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        input_data = {"error": f"Failed to parse JSON: {e}"}

    event_name = input_data.get("hook_event_name", "Unknown")
    log_event(event_name, input_data)

    # Output empty JSON to allow the event to proceed
    print("{}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
