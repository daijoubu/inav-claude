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
from deterministic_checks import lock_file_precheck


def _strip_heredoc_bodies(command: str) -> str:
    """
    Remove heredoc body content (and terminator lines) from a bash command,
    leaving invocation lines and anything that follows the terminator intact.

    The generic bash parser splits on every newline, so feeding it a raw
    heredoc body (e.g. a Python script) makes it misinterpret each body line
    as its own bash subcommand. Keeping everything outside the body - the
    invocation line(s) and anything after the terminator - means a trailing
    command (e.g. `git add -A` on the next line) still reaches the normal
    evaluation path instead of being dropped.
    """
    heredoc_start_re = re.compile(r'<<(-?)\s*([\'"]?)(\w+)\2')
    lines = command.split('\n')
    result_lines = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        result_lines.append(line)
        match = heredoc_start_re.search(line)
        if match:
            dash, delimiter = match.group(1) == '-', match.group(3)
            j = i + 1
            while j < n:
                candidate = lines[j].lstrip('\t') if dash else lines[j]
                if candidate == delimiter:
                    break
                j += 1
            # Drop the body (i+1..j) and the terminator line itself (j) - an
            # unadorned delimiter line would otherwise be mis-parsed as a
            # bogus bash subcommand of its own.
            i = j + 1
            continue
        i += 1
    return '\n'.join(result_lines)


def handle_bash_tool(command: str, matcher: RuleMatcher, logger: HookLogger, cwd: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle Bash tool with special compound command parsing.

    Args:
        command: Bash command string
        matcher: RuleMatcher object
        logger: HookLogger object

    Returns:
        Hook output dict
    """
    # Heredocs need special handling before the command reaches the generic
    # parser: strip out heredoc body content so it isn't split line-by-line
    # into bogus subcommands, then evaluate what's left (invocation line(s)
    # plus any trailing commands after the terminator) through the SAME
    # match_bash() path as any other command, so deny/ask rules apply to
    # everything in the command, not just the heredoc's own invocation line.
    if re.search(r'<<-?\s*[\'"]?\w+[\'"]?', command):
        stripped_command = _strip_heredoc_bodies(command)
        logger.log_output('info', f'Heredoc detected, evaluating stripped command: {stripped_command!r}')
        results = matcher.match_bash(stripped_command, cwd)
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
        evaluator = get_evaluator(logger=logger)

        # Resolve each ask_result: a deterministic pre-check first (no API
        # call), falling back to Claude only for genuinely gray-zone cases.
        decisions_by_subcommand = {}
        for ask_result in ask_results:
            subcommand = ask_result['subcommand']
            category = ask_result.get('category', 'other')
            rule_name = ask_result.get('rule_name')
            rule_message = ask_result.get('message', 'Operation requires approval')

            precheck = lock_file_precheck(cwd, category, rule_name, session_id)
            if precheck is not None:
                precheck_decision, precheck_message = precheck
                logger.log_output(
                    'allow' if precheck_decision == 'allow' else 'ask',
                    f"PRECHECK absorbed (no API call) - {precheck_message}",
                    rule_name
                )
                decisions_by_subcommand[subcommand] = {
                    'decision': precheck_decision,
                    'rule_message': precheck_message
                }
                continue

            logger.log(f"PRECHECK escalated to evaluator: {subcommand}")
            decision = evaluator.evaluate_with_claude(
                tool_name='Bash',
                command=subcommand,
                category=category,
                rule_reason=rule_message,
                cwd=cwd
            )
            decisions_by_subcommand[subcommand] = {
                'decision': decision,
                'rule_message': rule_message
            }

        user_approval_needed = any(d['decision'] == 'ask_user' for d in decisions_by_subcommand.values())

        if user_approval_needed:
            commands_to_ask = [s for s, d in decisions_by_subcommand.items() if d['decision'] == 'ask_user']
            logger.log_output('ask', f"User approval needed for: {', '.join(commands_to_ask)}")

            # Show every subcommand's disposition, not just the ones needing
            # approval - a compound command can include already-allowed steps
            # (e.g. a build command) that are easy to mistake for the actual
            # trigger if only the flagged part is shown.
            command_details = []
            for r in results:
                sub = r['subcommand']
                resolved = decisions_by_subcommand.get(sub)
                if resolved is None:
                    command_details.append(f"  - {sub} [✓ auto-allowed]")
                elif resolved['decision'] == 'allow':
                    command_details.append(f"  - {sub} [✓ safe]")
                else:
                    line = f"  - {sub} [⚠ needs approval]"
                    if resolved.get('rule_message'):
                        line += f"\n      Reason: {resolved['rule_message']}"
                    command_details.append(line)

            additional_context = (
                "This command has multiple parts. Only the parts marked "
                "'⚠ needs approval' below require your decision - the rest "
                "were already resolved automatically:\n" + "\n".join(command_details) + "\n\n"
                "Approve or deny the highlighted operations.\n\n"
                "If approved, you can update .claude/hooks/tool_permissions.yaml to automatically "
                "allow similar patterns in the future."
            )

            return HookOutputGenerator.generate_pretooluse_output(
                decision='ask',
                reason=f"User approval needed for: {', '.join(commands_to_ask)}",
                additional_context=additional_context
            )
        else:
            approved = [s for s, d in decisions_by_subcommand.items() if d['decision'] == 'allow']
            logger.log_output('allow', f"All commands approved - {', '.join(approved)}")
            return HookOutputGenerator.generate_pretooluse_output(decision='allow')

    # All commands are allowed
    logger.log_output('allow', 'All commands approved')
    return HookOutputGenerator.generate_pretooluse_output(decision='allow')


def handle_general_tool(tool_name: str, tool_input: Dict[str, Any], matcher: RuleMatcher, logger: HookLogger, session_id: Optional[str] = None) -> Dict[str, Any]:
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
        # Categorize tool if not already known
        if tool_name in ['Read', 'Glob', 'Grep', 'WebSearch', 'WebFetch']:
            category = 'read'
        elif tool_name in ['Write', 'Edit', 'NotebookEdit']:
            category = 'write'
        else:
            category = 'other'

        input_summary = json.dumps(tool_input, indent=2) if tool_input else "N/A"

        file_path = tool_input.get('file_path') if tool_input else None
        precheck = lock_file_precheck(file_path, category, rule_name, session_id)
        if precheck is not None:
            claude_decision, precheck_message = precheck
            logger.log_output(
                'allow' if claude_decision == 'allow' else 'ask',
                f"PRECHECK absorbed (no API call) - {precheck_message}",
                rule_name
            )
            reason_text = precheck_message
        else:
            logger.log(f"PRECHECK escalated to evaluator: {tool_name}")
            evaluator = get_evaluator(logger=logger)
            claude_decision = evaluator.evaluate_with_claude(
                tool_name=tool_name,
                command=f"Tool: {tool_name}\nInput: {input_summary}",
                category=category,
                rule_reason=message or f"Tool '{tool_name}' requires approval"
            )
            reason_text = message or f"Tool {tool_name} requires approval"

        if claude_decision == 'allow':
            logger.log_output('allow', f"{tool_name} approved as safe")
            return HookOutputGenerator.generate_pretooluse_output(decision='allow')
        else:
            # Uncertain (or pre-check couldn't confirm safety) - ask the user
            logger.log_output('ask', f"User approval needed for {tool_name}")

            additional_context = (
                f"Tool '{tool_name}' requires approval.\n"
                f"Reason: {reason_text}\n"
                f"Tool input:\n{input_summary}\n\n"
                "Please approve or deny this operation.\n"
                "If approved, you can update .claude/hooks/tool_permissions.yaml to automatically "
                "allow similar patterns in the future."
            )

            return HookOutputGenerator.generate_pretooluse_output(
                decision='ask',
                reason=reason_text,
                additional_context=additional_context
            )
    else:  # allow
        # WARNING messages go to systemMessage (correctly top-level - shown to
        # the user). Other messages go through additional_context=, which
        # generate_pretooluse_output() nests inside hookSpecificOutput as
        # PreToolUse requires - a top-level additionalContext key is silently
        # discarded by Claude Code.
        if message and message.startswith('WARNING:'):
            output = HookOutputGenerator.generate_pretooluse_output(decision='allow')
            output['systemMessage'] = message
        else:
            output = HookOutputGenerator.generate_pretooluse_output(
                decision='allow',
                additional_context=message or None
            )
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

    # additionalContext must live INSIDE hookSpecificOutput for PreToolUse, per
    # https://code.claude.com/docs/en/hooks.md - a top-level sibling key (what
    # HookOutputGenerator.generate_pretooluse_output() writes elsewhere in this
    # codebase, including the pre-existing ask-path) is silently discarded by
    # Claude Code. Confirmed via direct transcript inspection: the hook's stdout
    # contains the right JSON, logged faithfully as a "hook_success" attachment
    # record, but the tool_result actually delivered to the model has no trace
    # of it when the key is top-level.
    hook_output = output.setdefault('hookSpecificOutput', {})
    existing = hook_output.get('additionalContext', '')
    hook_output['additionalContext'] = existing + ('\n\n' if existing else '') + '\n\n'.join(texts)
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
        output = handle_bash_tool(command, RuleMatcher(config, logger), logger, cwd, session_id)
    else:
        output = handle_general_tool(tool_name, tool_input, RuleMatcher(config, logger), logger, session_id)

    # Point-of-action context injection - only on an allow outcome, and never
    # able to change that outcome. See tool_context_injections.yaml.
    if output.get('hookSpecificOutput', {}).get('permissionDecision') == 'allow':
        inject_context(output, tool_name, tool_input, command, cwd, session_id, logger)

    # Write output
    write_hook_output(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
