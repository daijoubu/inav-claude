#!/usr/bin/env python3
"""
PermissionRequest hook for Claude Code.

This hook intercepts permission requests shown to the user and can:
- Automatically allow or deny them
- Modify tool input parameters for allowed requests
- Interrupt Claude for denied requests
"""

import sys
from typing import Dict, Any

from hook_common import (
    HookConfig,
    HookLogger,
    RuleMatcher,
    HookOutputGenerator,
    read_hook_input,
    write_hook_output
)


def handle_bash_tool(command: str, matcher: RuleMatcher, logger: HookLogger) -> Dict[str, Any]:
    """
    Handle Bash tool permission request with compound command parsing.

    Args:
        command: Bash command string
        matcher: RuleMatcher object
        logger: HookLogger object

    Returns:
        Hook output dict
    """
    results = matcher.match_bash(command)

    # Check if any subcommand is denied
    denied_results = [r for r in results if r['decision'] == 'deny']
    if denied_results:
        # Use the first denied command's info
        denied = denied_results[0]
        logger.log_output('deny', denied['message'], denied['rule_name'])

        return HookOutputGenerator.generate_permissionrequest_output(
            behavior='deny',
            message=denied['message'] or f"Command '{denied['subcommand']}' is not allowed",
            interrupt=True  # Stop Claude when denying
        )

    # Check if any subcommand requires asking - let user see the request
    ask_results = [r for r in results if r['decision'] == 'ask']
    if ask_results:
        # Don't auto-approve, let the user see the permission request
        # This means we don't return anything (hook doesn't override)
        commands_to_ask = [r['subcommand'] for r in ask_results]
        logger.log_output('ask', f"Letting user decide on: {', '.join(commands_to_ask)}")
        # Return empty output - let the permission UI show
        return {}

    # All commands are allowed - auto-approve
    logger.log_output('allow', 'Auto-approving all commands')

    # Special handling for git commit (add reminder)
    git_commit_results = [r for r in results if r['parsed_command'] == 'git' and 'commit' in r['subcommand']]
    if git_commit_results:
        logger.log('Git commit detected in permission request')

    return HookOutputGenerator.generate_permissionrequest_output(
        behavior='allow'
    )


def handle_general_tool(tool_name: str, tool_input: Dict[str, Any], matcher: RuleMatcher, logger: HookLogger) -> Dict[str, Any]:
    """
    Handle general (non-Bash) tool permission requests.

    Args:
        tool_name: Tool name
        tool_input: Tool input dict
        matcher: RuleMatcher object
        logger: HookLogger object

    Returns:
        Hook output dict
    """
    decision, message, rule_name = matcher.match_tool(tool_name, tool_input)

    # If no specific rule matched, use category default
    if decision is None:
        # Simple categorization based on tool name
        if tool_name in ['Read', 'Glob', 'Grep', 'WebSearch', 'WebFetch']:
            category = 'read'
        elif tool_name in ['Write', 'Edit', 'NotebookEdit']:
            category = 'write'
        else:
            category = 'other'

        decision = matcher.config.get_default_decision(category)
        logger.log_output(decision, f'Using category default for {category}', 'default')
    else:
        logger.log_output(decision, message, rule_name)

    if decision == 'deny':
        return HookOutputGenerator.generate_permissionrequest_output(
            behavior='deny',
            message=message or f"Tool '{tool_name}' is not allowed",
            interrupt=True
        )
    elif decision == 'ask':
        # Let the user see the permission request
        logger.log_output('ask', 'Letting user decide')
        return {}  # Empty output = let permission UI show
    else:  # allow
        return HookOutputGenerator.generate_permissionrequest_output(
            behavior='allow'
        )


def main():
    """Main entry point for PermissionRequest hook."""
    # Read input from stdin
    input_data = read_hook_input()

    if 'error' in input_data:
        # Failed to parse input, let the permission request show
        return 0

    # Initialize config and logger
    config = HookConfig()
    logger = HookLogger(config)

    # Log input
    hook_event = input_data.get('hook_event_name', 'PermissionRequest')
    logger.log_input(hook_event, input_data)

    # Extract tool info
    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    # Handle based on tool type
    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        output = handle_bash_tool(command, RuleMatcher(config, logger), logger)
    else:
        output = handle_general_tool(tool_name, tool_input, RuleMatcher(config, logger), logger)

    # Write output (if any)
    if output:
        write_hook_output(output)

    return 0


if __name__ == '__main__':
    sys.exit(main())
