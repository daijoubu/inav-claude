#!/usr/bin/env python3
"""
Validation script for tool permissions configuration.

Checks for common mistakes and potential issues in the configuration files.
Supports both split configuration files (defaults, rules, bash_rules) and
monolithic tool_permissions.yaml for backwards compatibility.

Usage:
    python3 validate_config.py                    # Auto-detect split files
    python3 validate_config.py path/to/config.yaml  # Validate specific file

If no config file is specified, looks for split files in the same directory:
  - tool_permissions_defaults.yaml
  - tool_permissions_rules.yaml
  - tool_permissions_bash.yaml

If split files found, they are loaded and merged. Otherwise falls back to
looking for tool_permissions.yaml.
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
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
        if 'injections' in self.config:
            self._check_injections()

        # Print results
        self._print_results()

        return len(self.errors) == 0

    def _load_config(self) -> bool:
        """Load and parse YAML config file(s).

        Handles both split files and monolithic configuration.
        """
        # If explicit path provided, load that file
        if self.config_path and self.config_path != 'auto':
            return self._load_single_file(self.config_path)

        # Otherwise, try to load split files
        script_dir = Path(__file__).parent
        split_files = [
            ('tool_permissions_defaults.yaml', 'defaults'),
            ('tool_permissions_rules.yaml', 'rules'),
            ('tool_permissions_bash.yaml', 'bash_rules'),
        ]

        split_found = []
        for filename, _ in split_files:
            filepath = script_dir / filename
            if filepath.exists():
                split_found.append(filepath)

        if len(split_found) == 3:
            # Load and merge split files
            self.config = {
                'defaults': {},
                'rules': [],
                'bash_rules': [],
                'logging': {}
            }

            try:
                for filename, section_name in split_files:
                    filepath = script_dir / filename
                    with open(filepath, 'r') as f:
                        file_data = yaml.safe_load(f) or {}

                    if section_name == 'defaults':
                        self.config['logging'] = file_data.get('logging', {})
                        self.config['defaults'] = file_data.get('defaults', {})
                    elif section_name == 'rules':
                        self.config['rules'] = file_data.get('rules', [])
                    elif section_name == 'bash_rules':
                        self.config['bash_rules'] = file_data.get('bash_rules', [])

                self.info.append(f"✓ Loaded and merged 3 split config files from {script_dir}")

                # Optional 4th file - point-of-action context injections. Separate
                # from the 3 permission files on purpose (see its own header), so
                # it's absent from "required sections" and only validated if present.
                injections_path = script_dir / 'tool_context_injections.yaml'
                if injections_path.exists():
                    with open(injections_path, 'r') as f:
                        injections_data = yaml.safe_load(f) or {}
                    self.config['injections'] = injections_data.get('injections', [])
                    self.info.append(
                        f"✓ Loaded {len(self.config['injections'])} injection rules from {injections_path.name}"
                    )

                return True
            except yaml.YAMLError as e:
                self.errors.append(f"✗ YAML syntax error in split files: {e}")
                return False

        # Fall back to monolithic file
        monolithic_path = script_dir / 'tool_permissions.yaml'
        return self._load_single_file(str(monolithic_path))

    def _load_single_file(self, config_path: str) -> bool:
        """Load a single YAML configuration file."""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.info.append(f"✓ Loaded config from {config_path}")
            return True
        except FileNotFoundError:
            self.errors.append(f"✗ Config file not found: {config_path}")
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
                # BUT only if the decisions differ (ordering matters)
                if self._is_less_specific(rule1, rule2):
                    decision1 = rule1.get('decision', 'ask')
                    decision2 = rule2.get('decision', 'ask')

                    # Only warn if decisions differ - when both allow/deny, order doesn't matter
                    if decision1 != decision2:
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

    def _check_injections(self):
        """Check tool_context_injections.yaml rules.

        Distinct rules from _validate_rule() above: injections have no 'decision'
        field (they can't influence allow/deny/ask), and their matcher may be
        EITHER the bash shape (command_pattern) OR the general-tool shape
        (tool_name_pattern) - exactly one, not necessarily either alone required
        the way tool_permissions_rules.yaml treats tool_name_pattern as optional.
        """
        injections = self.config.get('injections', [])
        seen_names = set()

        for i, rule in enumerate(injections):
            path = f"injections[{i}]"
            name = rule.get('name')

            if not name:
                self.errors.append(f"✗ {path}: Missing 'name' field")
            elif name in seen_names:
                self.errors.append(f"✗ {path} ('{name}'): Duplicate name - throttling is keyed by name")
            else:
                seen_names.add(name)

            context = str(rule.get('context', '')).strip()
            if not context:
                self.errors.append(f"✗ {path} ('{name}'): Missing 'context' field")

            has_bash_matcher = bool(rule.get('command_pattern'))
            has_tool_matcher = bool(rule.get('tool_name_pattern'))
            if has_bash_matcher and has_tool_matcher:
                self.errors.append(
                    f"✗ {path} ('{name}'): Has both command_pattern and tool_name_pattern - "
                    f"pick one matcher shape, not both"
                )
            elif not has_bash_matcher and not has_tool_matcher:
                self.errors.append(
                    f"✗ {path} ('{name}'): Must have 'command_pattern' (Bash) or "
                    f"'tool_name_pattern' (general tool)"
                )

            for pattern_field in ('command_pattern', 'argument_pattern', 'tool_name_pattern'):
                pattern = rule.get(pattern_field)
                if pattern:
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        self.errors.append(f"✗ {path} ('{name}'): Invalid {pattern_field} regex: {e}")

            for pattern in (rule.get('tool_input_patterns') or {}).values():
                try:
                    re.compile(pattern)
                except re.error as e:
                    self.errors.append(f"✗ {path} ('{name}'): Invalid tool_input_patterns regex: {e}")

            throttle = rule.get('throttle', 'once_per_session')
            if throttle not in ('once_per_session', 'always'):
                self.errors.append(
                    f"✗ {path} ('{name}'): Invalid throttle '{throttle}' "
                    f"(must be once_per_session/always)"
                )

            script = rule.get('precondition_script')
            if script and 'echo "fire"' not in script and "echo 'fire'" not in script:
                self.warnings.append(
                    f"⚠ {path} ('{name}'): precondition_script should echo \"fire\" to inject "
                    f"(this contract is different from permission rules' allow/deny/ask)"
                )

            if context.startswith('WARNING:'):
                self.errors.append(
                    f"✗ {path} ('{name}'): context starts with 'WARNING:' - pre_tool_use_hook.py "
                    f"routes that prefix to systemMessage (human-only), so this would silently "
                    f"never reach the model"
                )

            line_count = len([l for l in context.splitlines() if l.strip()])
            if line_count > 5:
                self.warnings.append(f"⚠ {path} ('{name}'): context is {line_count} lines (target 1-3, max 5)")

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
        # Auto-detect: use 'auto' to signal split file detection
        config_path = 'auto'

    # Validate
    validator = ConfigValidator(config_path)
    success = validator.validate()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
