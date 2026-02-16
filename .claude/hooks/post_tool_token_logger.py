#!/usr/bin/env python3
"""
PostToolUse hook to log token usage from Task tool invocations.

Extracts usage data from the structured tool_response and logs to CSV for analysis.
"""

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# Metrics file location
METRICS_DIR = Path(__file__).parent.parent.parent / "claude" / "metrics"
CSV_FILE = METRICS_DIR / "token-usage.csv"
LOG_FILE = METRICS_DIR / "token-logger.log"


def log_debug(message: str):
    """Log debug message to file."""
    try:
        with open(LOG_FILE, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass  # Silent fail for logging


def read_hook_input() -> dict:
    """Read JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def write_hook_output(output: dict):
    """Write JSON output to stdout."""
    print(json.dumps(output))


def extract_usage_from_response(tool_response: dict) -> dict:
    """
    Extract usage information from Task tool response.

    The tool_response dict contains:
    - totalTokens: total token count
    - totalDurationMs: execution time in ms
    - totalToolUseCount: number of tool invocations
    """
    usage = {}

    if isinstance(tool_response, dict):
        if 'totalTokens' in tool_response:
            usage['total_tokens'] = tool_response['totalTokens']
        if 'totalDurationMs' in tool_response:
            usage['duration_ms'] = tool_response['totalDurationMs']
        if 'totalToolUseCount' in tool_response:
            usage['tool_uses'] = tool_response['totalToolUseCount']

    return usage


def extract_task_info(tool_input: dict) -> dict:
    """Extract agent type and description from Task tool input."""
    info = {
        'agent_type': tool_input.get('subagent_type', 'unknown'),
        'description': tool_input.get('description', 'unknown')
    }
    return info


def log_to_csv(agent_type: str, description: str, usage: dict):
    """Append usage record to CSV file."""
    if not usage:
        log_debug(f"No usage data to log for {agent_type}")
        return

    # Ensure metrics directory exists
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    # Check if file exists to determine if we need header
    file_exists = CSV_FILE.exists()

    timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    row = {
        'timestamp': timestamp,
        'agent_or_skill': agent_type,
        'total_tokens': usage.get('total_tokens', 0),
        'tool_uses': usage.get('tool_uses', 0),
        'duration_ms': usage.get('duration_ms', 0),
        'task_description': description
    }

    try:
        with open(CSV_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        log_debug(f"Logged: {agent_type} - {usage.get('total_tokens', 0)} tokens")
    except Exception as e:
        log_debug(f"Error writing CSV: {e}")


def main():
    """Main hook entry point."""
    hook_input = read_hook_input()

    # Get tool information
    tool_name = hook_input.get('tool_name', '')
    tool_input = hook_input.get('tool_input', {})
    tool_response = hook_input.get('tool_response', {})

    # Only process Task tool
    if tool_name != 'Task':
        write_hook_output({'continue': True})
        return

    # Extract task info
    task_info = extract_task_info(tool_input)

    # Extract usage from structured response
    usage = extract_usage_from_response(tool_response)

    # Log if we have usage data
    if usage:
        log_to_csv(task_info['agent_type'], task_info['description'], usage)
        log_debug(f"SUCCESS: Logged {task_info['agent_type']} - {usage}")
    else:
        log_debug(f"No usage data found for {task_info['agent_type']}")

    # Always continue (PostToolUse doesn't block)
    write_hook_output({'continue': True})


if __name__ == '__main__':
    main()
