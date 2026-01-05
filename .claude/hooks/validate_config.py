#!/usr/bin/env python3
"""
Validation script for tool_permissions.yaml

Checks for common mistakes and potential issues in the configuration file.

Usage:
    python3 validate_config.py [config_file]

If no config file is specified, looks for tool_permissions.yaml in the same directory.
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import yaml


class ConfigValidator:
    """Validates tool permissions configuration."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = None
        self.errors = []
        self.warnings = []
        self.info = []

    def validate(self) -> bool:
        """
        Run all validation checks.

        Returns:
            True if validation passed, False otherwise
        """
        # Load config
        if not self._load_config():
            return False

        # Run validation checks
        self._check_required_sections()
        self._check_rule_patterns()
        self._check_rule_ordering()
        self._check_duplicate_rules()
        self._check_regex_validity()
        self._check_precondition_scripts()
        self._check_unreachable_rules()

        # Print results
        self._print_results()

        return len(self.errors) == 0

    def _load_config(self) -> bool:
        """Load and parse YAML config file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.info.append(f"✓ Loaded config from {self.config_path}")
            return True
        except FileNotFoundError:
            self.errors.append(f"✗ Config file not found: {self.config_path}")
            return False
        except yaml.YAMLError as e:
            self.errors.append(f"✗ YAML syntax error: {e}")
            return False

    def _check_required_sections(self):
        """Check that required sections exist."""
        required = ['defaults', 'rules', 'bash_rules', 'logging']
        for section in required:
            if section not in self.config:
                self.errors.append(f"✗ Missing required section: {section}")
            else:
                self.info.append(f"✓ Found required section: {section}")

    def _check_rule_patterns(self):
        """Check that rules have valid structure."""
        # Check general rules
        rules = self.config.get('rules', [])
        for i, rule in enumerate(rules):
            self._validate_rule(rule, f"rules[{i}]", is_bash=False)

        # Check bash rules
        bash_rules = self.config.get('bash_rules', [])
        for i, rule in enumerate(bash_rules):
            self._validate_rule(rule, f"bash_rules[{i}]", is_bash=True)

    def _validate_rule(self, rule: Dict, path: str, is_bash: bool):
        """Validate a single rule."""
        # Check required fields
        if 'name' not in rule:
            self.errors.append(f"✗ {path}: Missing 'name' field")

        if is_bash:
            if 'command_pattern' not in rule:
                self.errors.append(f"✗ {path}: Missing 'command_pattern' field")
        else:
            if 'tool_name_pattern' not in rule:
                self.warnings.append(f"⚠ {path}: Missing 'tool_name_pattern' field")

        # Check decision field
        decision = rule.get('decision')
        if decision and decision not in ['allow', 'deny', 'ask']:
            self.errors.append(f"✗ {path}: Invalid decision '{decision}' (must be allow/deny/ask)")

        # Check category field
        category = rule.get('category')
        if category and category not in ['read', 'write', 'other']:
            self.errors.append(f"✗ {path}: Invalid category '{category}' (must be read/write/other)")

    def _check_rule_ordering(self):
        """Check for potential rule ordering issues."""
        bash_rules = self.config.get('bash_rules', [])

        # Track commands and their rules
        command_rules: Dict[str, List[Tuple[int, Dict]]] = {}

        for i, rule in enumerate(bash_rules):
            pattern = rule.get('command_pattern', '')

            # Extract simple command names from patterns like "^echo$" or "^(git|gh)$"
            # This is a heuristic - won't catch all cases
            commands = self._extract_commands_from_pattern(pattern)

            for cmd in commands:
                if cmd not in command_rules:
                    command_rules[cmd] = []
                command_rules[cmd].append((i, rule))

        # Check for potential ordering issues
        for cmd, rules in command_rules.items():
            if len(rules) <= 1:
                continue

            # Check if general rules come before specific rules
            for i in range(len(rules) - 1):
                idx1, rule1 = rules[i]
                idx2, rule2 = rules[i + 1]

                # If first rule is less specific (no argument_pattern or broader pattern)
                # and second rule is more specific, warn about ordering
                if self._is_less_specific(rule1, rule2):
                    self.warnings.append(
                        f"⚠ Potential ordering issue for '{cmd}':\n"
                        f"    Rule #{idx1} ('{rule1.get('name')}') is less specific\n"
                        f"    Rule #{idx2} ('{rule2.get('name')}') is more specific\n"
                        f"    Consider moving the more specific rule earlier"
                    )

    def _extract_commands_from_pattern(self, pattern: str) -> List[str]:
        """Extract command names from a regex pattern (heuristic)."""
        commands = []

        # Handle patterns like "^echo$", "^(git|gh)$", "^find$"
        # Remove anchors and parentheses
        cleaned = pattern.replace('^', '').replace('$', '').replace('(', '').replace(')', '')

        # Split on | for alternatives
        parts = cleaned.split('|')

        for part in parts:
            # Remove regex special chars (backslashes, brackets, etc.)
            cmd = re.sub(r'[\\[\].*+?]', '', part).strip()
            if cmd and cmd.isalnum() or '-' in cmd or '_' in cmd:
                commands.append(cmd)

        return commands

    def _is_less_specific(self, rule1: Dict, rule2: Dict) -> bool:
        """
        Check if rule1 is less specific than rule2.

        Heuristic: A rule with no argument_pattern is less specific than one with it.
        """
        has_arg1 = 'argument_pattern' in rule1 and rule1['argument_pattern']
        has_arg2 = 'argument_pattern' in rule2 and rule2['argument_pattern']

        return not has_arg1 and has_arg2

    def _check_duplicate_rules(self):
        """Check for duplicate rules (same command and argument patterns)."""
        seen_bash = set()
        bash_rules = self.config.get('bash_rules', [])

        for i, rule in enumerate(bash_rules):
            cmd_pattern = rule.get('command_pattern', '')
            arg_pattern = rule.get('argument_pattern', '')
            key = (cmd_pattern, arg_pattern)

            if key in seen_bash:
                self.warnings.append(
                    f"⚠ bash_rules[{i}]: Potential duplicate of earlier rule\n"
                    f"    Pattern: {cmd_pattern} with args: {arg_pattern}"
                )
            seen_bash.add(key)

    def _check_regex_validity(self):
        """Check that regex patterns are valid."""
        # Check bash rules
        bash_rules = self.config.get('bash_rules', [])
        for i, rule in enumerate(bash_rules):
            cmd_pattern = rule.get('command_pattern')
            if cmd_pattern:
                try:
                    re.compile(cmd_pattern)
                except re.error as e:
                    self.errors.append(
                        f"✗ bash_rules[{i}] ('{rule.get('name')}'): Invalid command_pattern regex: {e}"
                    )

            arg_pattern = rule.get('argument_pattern')
            if arg_pattern:
                try:
                    re.compile(arg_pattern)
                except re.error as e:
                    self.errors.append(
                        f"✗ bash_rules[{i}] ('{rule.get('name')}'): Invalid argument_pattern regex: {e}"
                    )

        # Check general rules
        rules = self.config.get('rules', [])
        for i, rule in enumerate(rules):
            tool_pattern = rule.get('tool_name_pattern')
            if tool_pattern:
                try:
                    re.compile(tool_pattern)
                except re.error as e:
                    self.errors.append(
                        f"✗ rules[{i}] ('{rule.get('name')}'): Invalid tool_name_pattern regex: {e}"
                    )

    def _check_precondition_scripts(self):
        """Check precondition scripts for common issues."""
        bash_rules = self.config.get('bash_rules', [])

        for i, rule in enumerate(bash_rules):
            script = rule.get('precondition_script')
            if not script:
                continue

            # Check if script returns valid values
            if 'echo "allow"' not in script and 'echo "deny"' not in script and 'echo "ask"' not in script:
                self.warnings.append(
                    f"⚠ bash_rules[{i}] ('{rule.get('name')}'): precondition_script should echo 'allow', 'deny', or 'ask'"
                )

            # Check if script uses available variables
            if '{COMMAND}' not in script and '{ARGS}' not in script and '{FULL_COMMAND}' not in script:
                self.info.append(
                    f"ℹ bash_rules[{i}] ('{rule.get('name')}'): precondition_script doesn't use available variables"
                )

    def _check_unreachable_rules(self):
        """Check for rules that may never be reached due to earlier broad rules."""
        bash_rules = self.config.get('bash_rules', [])

        # Track patterns that match everything
        broad_matchers = []

        for i, rule in enumerate(bash_rules):
            cmd_pattern = rule.get('command_pattern', '')
            arg_pattern = rule.get('argument_pattern')
            decision = rule.get('decision')

            # Check if a previous rule would always match first
            for prev_idx, prev_pattern in broad_matchers:
                if self._patterns_overlap(prev_pattern, cmd_pattern):
                    self.warnings.append(
                        f"⚠ bash_rules[{i}] ('{rule.get('name')}') may be unreachable\n"
                        f"    Rule #{prev_idx} has broader pattern that matches first"
                    )

            # Track broad patterns (no argument_pattern and decision is allow/deny)
            if not arg_pattern and decision in ['allow', 'deny']:
                broad_matchers.append((i, cmd_pattern))

    def _patterns_overlap(self, pattern1: str, pattern2: str) -> bool:
        """
        Check if two regex patterns overlap (heuristic).

        Returns True if pattern1 might match strings that pattern2 matches.
        """
        # Simple heuristic: if patterns are identical or pattern1 is more general
        if pattern1 == pattern2:
            return True

        # If pattern1 has no specific command requirements, it's very broad
        if pattern1 in ['^.*$', '.*']:
            return True

        return False

    def _print_results(self):
        """Print validation results."""
        print("\n" + "=" * 70)
        print("Tool Permissions Config Validation Results")
        print("=" * 70)

        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.info:
            print("\nℹ️  INFO:")
            for info in self.info:
                print(f"  {info}")

        print("\n" + "=" * 70)
        print(f"Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")

        if len(self.errors) == 0 and len(self.warnings) == 0:
            print("✅ Configuration is valid!")
        elif len(self.errors) == 0:
            print("✅ No errors found (warnings are advisory)")
        else:
            print("❌ Configuration has errors that should be fixed")
        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    # Determine config file path
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Default to tool_permissions.yaml in same directory as script
        script_dir = Path(__file__).parent
        config_path = script_dir / 'tool_permissions.yaml'

    # Validate
    validator = ConfigValidator(str(config_path))
    success = validator.validate()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
