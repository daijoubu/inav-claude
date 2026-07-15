#!/usr/bin/env python3
"""
Regression tests for the heredoc fail-open bypass fix in pre_tool_use_hook.py
and the companion env-var-assignment-prefix fix in bash_parser.py.

Run directly: python3 .claude/hooks/test_pre_tool_use_hook.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hook_common import HookConfig, HookLogger, RuleMatcher
from bash_parser import BashCommandParser
from pre_tool_use_hook import handle_bash_tool, _strip_heredoc_bodies


def make_matcher() -> RuleMatcher:
    config = HookConfig()
    logger = HookLogger(config)
    return RuleMatcher(config, logger)


def bash_decision(command: str) -> str:
    """Run the full handle_bash_tool() path and return the permissionDecision."""
    matcher = make_matcher()
    logger = matcher.logger
    output = handle_bash_tool(command, matcher, logger, cwd=str(Path(__file__).resolve().parents[2]))
    return output['hookSpecificOutput']['permissionDecision']


class TestHeredocFailOpenBypass(unittest.TestCase):
    """The original security finding: heredoc-allow + trailing git add -A bypassed deny rules."""

    def test_heredoc_allow_then_git_add_dash_a_denies(self):
        command = "cat <<'EOF' > /tmp/x.txt\nsome content\nEOF\ngit add -A"
        self.assertEqual(bash_decision(command), 'deny')

    def test_heredoc_ask_case_still_asks(self):
        # 'mystery_tool' matches no bash rule -> category 'other' -> ask default.
        command = "mystery_tool <<'EOF'\nfoo\nEOF"
        self.assertEqual(bash_decision(command), 'ask')

    def test_heredoc_only_no_trailing_command_still_allowed(self):
        # No redirect target -> 'cat' stays a read op -> allow, unchanged from before.
        command = "cat <<'EOF'\nhello\nEOF"
        self.assertEqual(bash_decision(command), 'allow')

    def test_heredoc_plus_trailing_allow_command_still_allows(self):
        command = "cat <<'EOF'\nhello\nEOF\ngit status"
        self.assertEqual(bash_decision(command), 'allow')

    def test_heredoc_plus_multiple_trailing_commands_all_evaluated(self):
        command = "cat <<'EOF'\nhello\nEOF\ngit status && git add -A"
        self.assertEqual(bash_decision(command), 'deny')

    def test_heredoc_with_redirect_on_delimiter_line_no_regression(self):
        # Covers the earlier (already-fixed) delimiter-line-has-more-after-it case,
        # still followed here by a denied trailing command.
        command = "python3 <<'EOF' > /tmp/out.txt\nprint('hi')\nEOF\ngit add -A"
        self.assertEqual(bash_decision(command), 'deny')

    def test_two_heredocs_then_denied_command(self):
        command = (
            "cat <<'A'\nbody one\nA\n"
            "cat <<'B'\nbody two\nB\n"
            "git add -A"
        )
        self.assertEqual(bash_decision(command), 'deny')


class TestStripHeredocBodies(unittest.TestCase):
    """Unit tests for the extracted helper, independent of rule matching."""

    def test_strips_body_keeps_invocation_and_trailing(self):
        command = "cat <<'EOF' > /tmp/x\nline one\nline two\nEOF\ngit add -A"
        stripped = _strip_heredoc_bodies(command)
        self.assertNotIn('line one', stripped)
        self.assertNotIn('line two', stripped)
        self.assertIn("cat <<'EOF' > /tmp/x", stripped)
        self.assertIn('git add -A', stripped)

    def test_dash_variant_strips_leading_tabs_on_terminator(self):
        command = "cat <<-EOF\n\tbody\n\tEOF\ngit status"
        stripped = _strip_heredoc_bodies(command)
        self.assertNotIn('body', stripped)
        self.assertIn('git status', stripped)

    def test_no_heredoc_is_unchanged(self):
        command = "git status && git add -A"
        self.assertEqual(_strip_heredoc_bodies(command), command)


class TestEnvVarPrefixParserGap(unittest.TestCase):
    """Companion fix: VAR=value prefixes must not hide the real command."""

    def setUp(self):
        self.parser = BashCommandParser()

    def test_env_prefixed_git_status_is_recognized_as_git(self):
        parsed = self.parser.parse("VAR=x git status")
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].command, 'git')
        self.assertEqual(parsed[0].arguments, 'status')
        self.assertEqual(parsed[0].raw, 'VAR=x git status')

    def test_env_prefixed_git_add_dash_a_is_recognized_as_git(self):
        parsed = self.parser.parse("VAR=x git add -A")
        self.assertEqual(parsed[0].command, 'git')
        self.assertEqual(parsed[0].arguments, 'add -A')

    def test_multiple_env_assignments_stripped(self):
        parsed = self.parser.parse("A=1 B=2 git add -A")
        self.assertEqual(parsed[0].command, 'git')
        self.assertEqual(parsed[0].arguments, 'add -A')
        self.assertEqual(parsed[0].raw, 'A=1 B=2 git add -A')

    def test_bare_assignment_with_no_command_untouched(self):
        parsed = self.parser.parse("FOO=bar")
        self.assertEqual(parsed[0].command, 'FOO=bar')

    def test_env_prefixed_git_add_dash_a_hits_real_deny_rule(self):
        matcher = make_matcher()
        results = matcher.match_bash("VAR=x git add -A")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['decision'], 'deny')
        self.assertEqual(results[0]['rule_name'], 'Block git add -A')

    def test_env_prefixed_git_status_resolves_read_allow(self):
        matcher = make_matcher()
        results = matcher.match_bash("VAR=x git status")
        self.assertEqual(results[0]['decision'], 'allow')
        self.assertEqual(results[0]['category'], 'read')

    def test_env_prefixed_command_end_to_end_denies(self):
        self.assertEqual(bash_decision("VAR=x git add -A"), 'deny')


if __name__ == '__main__':
    unittest.main()
