#!/usr/bin/env python3
"""
PreToolUse hook for Claude Code.

This hook intercepts tool calls before they execute and can:
- Allow, deny, or ask for user confirmation
- Modify tool input parameters
- Add additional context for Claude
"""

import json
import re
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
from claude_evaluator import get_evaluator


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
    # Handle heredocs specially - extract just the first command before heredoc content
    # Pattern matches: << EOF, << 'EOF', << "EOF", <<EOF, <<'EOF', <<"EOF", <<-EOF, etc.
    heredoc_match = re.search(r'<<-?\s*[\'"]?(\w+)[\'"]?\s*\n', command)
    if heredoc_match:
        # Extract just the first line (the actual command) before the heredoc content
        first_line = command.split('\n')[0]
        logger.log_output('info', f'Heredoc detected, checking first line: {first_line}')

        # Check if the first line (the actual command) is allowed
        results = matcher.match_bash(first_line, cwd)

        # If the command part is allowed, allow the whole heredoc
        denied_results = [r for r in results if r['decision'] == 'deny']
        ask_results = [r for r in results if r['decision'] == 'ask']

        if not denied_results and not ask_results:
            logger.log_output('allow', f'Heredoc command allowed: {first_line}')
            return HookOutputGenerator.generate_pretooluse_output(decision='allow')

        # If denied or ask, continue with normal handling but use first_line results
        # Fall through to normal processing with these results
    else:
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
        # Use Claude to evaluate if these are clearly safe
        evaluator = get_evaluator(logger=logger)

        # Evaluate each ask_result with Claude
        claude_decisions = []
        for ask_result in ask_results:
            subcommand = ask_result['subcommand']
            rule_message = ask_result.get('message', 'Operation requires approval')

            # Call Claude to evaluate safety
            decision = evaluator.evaluate_with_claude(
                tool_name='Bash',
                command=subcommand,
                category=ask_result.get('category', 'other'),
                rule_reason=rule_message,
                cwd=cwd
            )

            claude_decisions.append({
                'subcommand': subcommand,
                'decision': decision,
                'rule_message': rule_message
            })

        # If Claude says anything is unsafe/uncertain, ask the user
        user_approval_needed = any(d['decision'] == 'ask_user' for d in claude_decisions)

        if user_approval_needed:
            # Some commands were evaluated as uncertain by Claude - ask user
            commands_to_ask = [d['subcommand'] for d in claude_decisions if d['decision'] == 'ask_user']
            logger.log_output('ask', f"Claude evaluation: User approval needed for: {', '.join(commands_to_ask)}")

            # Build command details for user
            command_details = []
            for decision in claude_decisions:
                status = "✓ Safe" if decision['decision'] == 'allow' else "⚠ Needs approval"
                command_details.append(f"  - {decision['subcommand']} [{status}]")

            additional_context = (
                "Claude evaluated the following operations:\n" + "\n".join(command_details) + "\n\n"
                "Operations marked '⚠ Needs approval' require your explicit approval.\n"
                "Approve or deny the highlighted operations.\n\n"
                "If approved, you can update .claude/hooks/tool_permissions.yaml to automatically "
                "allow similar patterns in the future."
            )

            return HookOutputGenerator.generate_pretooluse_output(
                decision='ask',
                reason=f"Claude evaluation: User approval needed for: {', '.join(commands_to_ask)}",
                additional_context=additional_context
            )
        else:
            # All commands passed Claude evaluation - execute them
            claude_approved = [d['subcommand'] for d in claude_decisions if d['decision'] == 'allow']
            logger.log_output('allow', f"Claude evaluation: All commands approved - {', '.join(claude_approved)}")
            return HookOutputGenerator.generate_pretooluse_output(decision='allow')

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
        # Use Claude to evaluate if this tool use is clearly safe
        evaluator = get_evaluator(logger=logger)

        # Categorize tool if not already known
        if tool_name in ['Read', 'Glob', 'Grep', 'WebSearch', 'WebFetch']:
            category = 'read'
        elif tool_name in ['Write', 'Edit', 'NotebookEdit']:
            category = 'write'
        else:
            category = 'other'

        # Format tool input for Claude context
        input_summary = json.dumps(tool_input, indent=2) if tool_input else "N/A"

        # Call Claude to evaluate safety
        claude_decision = evaluator.evaluate_with_claude(
            tool_name=tool_name,
            command=f"Tool: {tool_name}\nInput: {input_summary}",
            category=category,
            rule_reason=message or f"Tool '{tool_name}' requires approval"
        )

        if claude_decision == 'allow':
            # Claude approved it as safe
            logger.log_output('allow', f"Claude evaluation: {tool_name} approved as safe")
            return HookOutputGenerator.generate_pretooluse_output(decision='allow')
        else:
            # Claude is uncertain - ask the user
            logger.log_output('ask', f"Claude evaluation: User approval needed for {tool_name}")

            additional_context = (
                f"Tool '{tool_name}' requires approval (Claude uncertain).\n"
                f"Tool input:\n{input_summary}\n\n"
                "Please approve or deny this operation.\n"
                "If approved, you can update .claude/hooks/tool_permissions.yaml to automatically "
                "allow similar patterns in the future."
            )

            return HookOutputGenerator.generate_pretooluse_output(
                decision='ask',
                reason=f"Claude evaluation: {message or f'Tool {tool_name} requires approval'}",
                additional_context=additional_context
            )
    else:  # allow
        output = HookOutputGenerator.generate_pretooluse_output(decision='allow')
        if message:
            # For allow with a WARNING message, add it as system_message to show to user
            if message.startswith('WARNING:'):
                output['systemMessage'] = message
            else:
                # For other messages, add as additional context
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
