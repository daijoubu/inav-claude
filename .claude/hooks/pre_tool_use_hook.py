#!/usr/bin/env python3
"""
PreToolUse hook for Claude Code.

This hook intercepts tool calls before they execute and can:
- Allow, deny, or ask for user confirmation
- Modify tool input parameters
- Add additional context for Claude
"""

import json
import sys
from typing import Dict, Any, Optional

from hook_common import (
    HookConfig,
    HookLogger,
    RuleMatcher,
    HookOutputGenerator,
    read_hook_input,
    write_hook_output
)


def handle_bash_tool(command: str, matcher: RuleMatcher, logger: HookLogger, cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle Bash tool with special compound command parsing.

    Args:
        command: Bash command string
        matcher: RuleMatcher object
        logger: HookLogger object

    Returns:
        Hook output dict
    """
    results = matcher.match_bash(command, cwd)

    # Check if any subcommand is denied
    denied_results = [r for r in results if r['decision'] == 'deny']
    if denied_results:
        # Use the first denied command's info
        denied = denied_results[0]
        logger.log_output('deny', denied['message'], denied['rule_name'])

        return HookOutputGenerator.generate_pretooluse_output(
            decision='deny',
            reason=denied['message'] or f"Command '{denied['subcommand']}' is not allowed"
        )

    # Check if any subcommand requires asking
    ask_results = [r for r in results if r['decision'] == 'ask']
    if ask_results:
        # Compile a list of commands requiring approval
        commands_to_ask = [r['subcommand'] for r in ask_results]
        logger.log_output('ask', f"Commands require approval: {', '.join(commands_to_ask)}")

        # Suggest editing config to avoid asking next time
        # Format each command with its details for user visibility
        command_details = []
        for r in ask_results:
            command_details.append(f"  - Command: {r['subcommand']}")

        additional_context = (
            f"The following subcommand(s) require approval:\n" + "\n".join(command_details) + "\n\n"
            "IMPORTANT: Tell the user which specific subcommand(s) require approval (listed above), "
            "then ask if they approve. If the user approves, ask them if they'd like you to update "
            ".claude/hooks/tool_permissions.yaml to automatically allow or deny this pattern in the future. "
            "If they want to update the config, prompt the user for the needed field values "
            "(command pattern, argument pattern if needed, category, decision) "
            "and edit .claude/hooks/tool_permissions.yaml to add the new rule."
        )

        return HookOutputGenerator.generate_pretooluse_output(
            decision='ask',
            reason=f"The following commands require approval: {', '.join(commands_to_ask)}",
            additional_context=additional_context
        )

    # Special handling for git commit (add reminder about not mentioning Claude)
    git_commit_results = [r for r in results if r['parsed_command'] == 'git' and 'commit' in r['subcommand']]
    if git_commit_results:
        logger.log_output('allow', 'Git commit - adding reminder about not mentioning Claude')

        return HookOutputGenerator.generate_pretooluse_output(
            decision='allow',
            additional_context=(
                "IMPORTANT: Do not mention Claude, AI, or that this commit was AI-generated "
                "in the commit message. Write the commit message as if a human developer wrote it. "
                "Also, be sure to use your git-workflow and create-pr skills when doing the first "
                "commit on a new task, or when creating a pull request."
            )
        )

    # All commands are allowed
    logger.log_output('allow', 'All commands approved')
    return HookOutputGenerator.generate_pretooluse_output(decision='allow')


def handle_general_tool(tool_name: str, tool_input: Dict[str, Any], matcher: RuleMatcher, logger: HookLogger) -> Dict[str, Any]:
    """
    Handle general (non-Bash) tools.

    Args:
        tool_name: Tool name
        tool_input: Tool input dict
        matcher: RuleMatcher object
        logger: HookLogger object

    Returns:
        Hook output dict
    """
    decision, message, rule_name = matcher.match_tool(tool_name, tool_input)

    # If no specific rule matched, categorize the tool and use category default
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
        return HookOutputGenerator.generate_pretooluse_output(
            decision='deny',
            reason=message or f"Tool '{tool_name}' is not allowed"
        )
    elif decision == 'ask':
        # Suggest editing config to avoid asking next time
        # Include tool input details
        input_summary = json.dumps(tool_input, indent=2) if tool_input else "N/A"

        additional_context = (
            f"Tool '{tool_name}' requires approval.\n"
            f"Tool input:\n{input_summary}\n\n"
            "IMPORTANT: Tell the user which specific tool and inputs require approval (shown above), "
            "then ask if they approve. If the user approves, ask them if they'd like you to update "
            ".claude/hooks/tool_permissions.yaml to automatically allow or deny this pattern in the future. "
            "If they want to update the config, prompt the user for the needed field values "
            "(tool name pattern, input patterns if needed, category, decision) "
            "and edit .claude/hooks/tool_permissions.yaml to add the new rule."
        )

        return HookOutputGenerator.generate_pretooluse_output(
            decision='ask',
            reason=message or f"Tool '{tool_name}' requires approval",
            additional_context=additional_context
        )
    else:  # allow
        output = HookOutputGenerator.generate_pretooluse_output(decision='allow')
        if message:
            # For allow with a message, we can add it as additional context
            output['additionalContext'] = message
        return output


def main():
    """Main entry point for PreToolUse hook."""
    # Read input from stdin
    input_data = read_hook_input()

    if 'error' in input_data:
        # Failed to parse input, allow the tool call to proceed
        write_hook_output(HookOutputGenerator.generate_pretooluse_output(decision='allow'))
        return 0

    # Initialize config and logger
    config = HookConfig()
    logger = HookLogger(config)

    # Log input
    hook_event = input_data.get('hook_event_name', 'PreToolUse')
    logger.log_input(hook_event, input_data)

    # Extract tool info
    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})
    cwd = input_data.get('cwd')

    # Handle based on tool type
    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        output = handle_bash_tool(command, RuleMatcher(config, logger), logger, cwd)
    else:
        output = handle_general_tool(tool_name, tool_input, RuleMatcher(config, logger), logger)

    # Write output
    write_hook_output(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
