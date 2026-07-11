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
    InjectionConfig,
    InjectionMatcher,
    InjectionThrottle,
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

        denial_message = denied['message'] or f"Command '{denied['subcommand']}' is not allowed"
        return HookOutputGenerator.generate_pretooluse_output(
            decision='deny',
            reason=denial_message,
            system_message=f"DENIAL: {denial_message}"
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
        denial_message = message or f"Tool '{tool_name}' is not allowed"
        return HookOutputGenerator.generate_pretooluse_output(
            decision='deny',
            reason=denial_message,
            system_message=f"DENIAL: {denial_message}"
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


def inject_context(
    output: Dict[str, Any],
    tool_name: str,
    tool_input: Dict[str, Any],
    command: Optional[str],
    cwd: Optional[str],
    session_id: Optional[str],
    logger: HookLogger
) -> None:
    """Append point-of-action context injections to an already-allowed tool call.

    Only called when `output` already carries an 'allow' decision - see the
    design note in tool_context_injections.yaml for why injections must never
    influence allow/deny/ask. Mutates `output` in place.
    """
    matcher = InjectionMatcher(InjectionConfig(), logger)
    throttle = InjectionThrottle(session_id)

    if tool_name == 'Bash' and command:
        matched_rules = matcher.match_bash(command, cwd)
    else:
        matched_rules = matcher.match_tool(tool_name, tool_input)

    texts = []
    for rule in matched_rules:
        name = rule.get('name', 'unnamed')
        throttle_mode = rule.get('throttle', 'once_per_session')

        if not throttle.should_fire(name, throttle_mode):
            continue

        context_text = (rule.get('context') or '').strip()
        if not context_text:
            continue

        texts.append(context_text)
        throttle.mark_fired(name)
        logger.log(f"  Injected context (rule: {name})")

    if not texts:
        return

    existing = output.get('additionalContext', '')
    output['additionalContext'] = existing + ('\n\n' if existing else '') + '\n\n'.join(texts)
    throttle.save()


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
    session_id = input_data.get('session_id')

    # Handle based on tool type
    command = None
    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        output = handle_bash_tool(command, RuleMatcher(config, logger), logger, cwd)
    else:
        output = handle_general_tool(tool_name, tool_input, RuleMatcher(config, logger), logger)

    # Point-of-action context injection - only on an allow outcome, and never
    # able to change that outcome. See tool_context_injections.yaml.
    if output.get('hookSpecificOutput', {}).get('permissionDecision') == 'allow':
        inject_context(output, tool_name, tool_input, command, cwd, session_id, logger)

    # Write output
    write_hook_output(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
