#!/usr/bin/env python3
"""
Bash command parser for Claude Code hooks.

Parses compound bash commands into individual subcommands,
extracting the command and arguments for each.
"""

import re
import shlex
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Represents a parsed bash subcommand."""
    command: str
    arguments: str
    raw: str
    operator_before: Optional[str] = None  # The operator before this command (&&, ||, ;, |, etc.)


class BashCommandParser:
    """Parser for breaking down compound bash commands."""

    # Operators that separate commands
    COMMAND_SEPARATORS = [
        '&&',  # AND
        '||',  # OR
        ';;',  # Case statement terminator
        '|&',  # Pipe both stdout and stderr
        '&',   # Background (must come after |&)
        ';',   # Sequential
        '|',   # Pipe
        '\n',  # Newline
    ]

    def __init__(self):
        # Build regex pattern for splitting on operators
        # Escape special regex chars and sort by length (longest first)
        escaped_ops = [re.escape(op) for op in sorted(self.COMMAND_SEPARATORS, key=len, reverse=True)]
        self.separator_pattern = re.compile(f'({"|".join(escaped_ops)})')

    def parse(self, command: str) -> List[ParsedCommand]:
        """
        Parse a bash command into subcommands.

        Args:
            command: The full bash command string

        Returns:
            List of ParsedCommand objects
        """
        if not command or not command.strip():
            return []

        # Handle simple case: no operators
        if not self.separator_pattern.search(command):
            return [self._parse_simple_command(command, None)]

        # Split by operators while preserving them
        parts = self.separator_pattern.split(command)

        parsed_commands = []
        current_operator = None

        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue

            # Check if this part is an operator
            if part in self.COMMAND_SEPARATORS:
                current_operator = part
            else:
                # This is a command
                parsed_cmd = self._parse_simple_command(part, current_operator)
                parsed_commands.append(parsed_cmd)
                current_operator = None

        return parsed_commands

    def _parse_simple_command(self, cmd_str: str, operator: Optional[str]) -> ParsedCommand:
        """
        Parse a single simple command (no operators) into command and arguments.

        Args:
            cmd_str: Single command string
            operator: The operator that preceded this command

        Returns:
            ParsedCommand object
        """
        cmd_str = cmd_str.strip()

        # Handle special cases
        if cmd_str.startswith('for ') or cmd_str.startswith('while ') or cmd_str.startswith('if '):
            # Control structures - treat the whole thing as the command
            return ParsedCommand(
                command=cmd_str.split()[0],
                arguments=cmd_str[len(cmd_str.split()[0]):].strip(),
                raw=cmd_str,
                operator_before=operator
            )

        if cmd_str.startswith('do') or cmd_str.startswith('then') or cmd_str.startswith('else') or cmd_str.startswith('fi') or cmd_str.startswith('done'):
            # Control structure keywords
            return ParsedCommand(
                command=cmd_str,
                arguments='',
                raw=cmd_str,
                operator_before=operator
            )

        try:
            # Use shlex to split respecting quotes
            tokens = shlex.split(cmd_str)
        except ValueError:
            # Shlex can fail on malformed quotes, fall back to simple split
            tokens = cmd_str.split()

        if not tokens:
            return ParsedCommand(
                command='',
                arguments='',
                raw=cmd_str,
                operator_before=operator
            )

        # First token is the command
        command = tokens[0]
        # Rest are arguments
        arguments = ' '.join(tokens[1:]) if len(tokens) > 1 else ''

        return ParsedCommand(
            command=command,
            arguments=arguments,
            raw=cmd_str,
            operator_before=operator
        )

    def categorize_command(self, parsed_cmd: ParsedCommand) -> str:
        """
        Categorize a command as 'read', 'write', or 'other'.

        This is a heuristic categorization based on common command patterns.

        Args:
            parsed_cmd: ParsedCommand object

        Returns:
            Category string: 'read', 'write', or 'other'
        """
        cmd = parsed_cmd.command.lower()
        args = parsed_cmd.arguments.lower()

        # Read operations
        read_commands = {
            'cat', 'head', 'tail', 'less', 'more', 'grep', 'find', 'ls', 'stat',
            'file', 'wc', 'diff', 'cmp', 'test', 'command', 'which', 'type',
            'du', 'df', 'mount', 'lsof', 'ps', 'top', 'netstat', 'ss', 'lsblk',
            'jq', 'awk', 'sed', 'cut', 'sort', 'uniq', 'comm', 'paste', 'xxd',
            'pgrep', 'pkill', 'dmesg', 'journalctl', 'fdisk', 'lsusb', 'objdump',
            'nm', 'size', 'objcopy', 'readelf'
        }

        # Git read operations
        if cmd == 'git':
            git_read_subcmds = [
                'status', 'log', 'diff', 'show', 'branch', 'remote', 'describe',
                'rev-parse', 'rev-list', 'cat-file', 'ls-tree', 'ls-files',
                'grep', 'merge-base', 'blame', 'tag'
            ]
            first_arg = args.split()[0] if args else ''
            if first_arg in git_read_subcmds:
                return 'read'
            # Fetch is read-like (network read)
            if first_arg == 'fetch':
                return 'read'
            # Other git commands are write
            return 'write'

        # Check if command is in read list
        if cmd in read_commands:
            # Even read commands can write if they use redirection
            if '>' in args or '>>' in args:
                return 'write'
            return 'read'

        # Write operations
        write_commands = {
            'rm', 'mv', 'cp', 'mkdir', 'rmdir', 'touch', 'chmod', 'chown',
            'ln', 'dd', 'rsync', 'tar', 'unzip', 'zip', 'gzip', 'gunzip',
            'echo', 'printf', 'tee', 'write'
        }

        if cmd in write_commands:
            return 'write'

        # Build/compile operations (other category)
        build_commands = {
            'make', 'cmake', 'gcc', 'g++', 'clang', 'cc', 'ar', 'ld',
            'npm', 'yarn', 'pip', 'pip3', 'python', 'python3', 'node',
            'cargo', 'rustc', 'go', 'javac', 'java', 'mvn', 'gradle',
            'pio', 'platformio'
        }

        if cmd in build_commands:
            return 'other'

        # Default to 'other' for unknown commands
        return 'other'


def parse_bash_command(command: str) -> List[ParsedCommand]:
    """
    Convenience function to parse a bash command.

    Args:
        command: Bash command string

    Returns:
        List of ParsedCommand objects
    """
    parser = BashCommandParser()
    return parser.parse(command)


if __name__ == '__main__':
    # Test the parser
    import json

    test_commands = [
        "git status",
        "git add . && git commit -m 'message' && git push",
        "ls -la | grep foo",
        "make clean && make all",
        "cat file.txt > output.txt",
        "for i in 1 2 3; do echo $i; done",
        "if test -f foo; then rm foo; fi",
    ]

    parser = BashCommandParser()

    for cmd in test_commands:
        print(f"\n{'='*60}")
        print(f"Command: {cmd}")
        print(f"{'='*60}")

        parsed = parser.parse(cmd)
        for i, p in enumerate(parsed):
            print(f"\nSubcommand {i+1}:")
            print(f"  Operator before: {p.operator_before}")
            print(f"  Command: {p.command}")
            print(f"  Arguments: {p.arguments}")
            print(f"  Category: {parser.categorize_command(p)}")
            print(f"  Raw: {p.raw}")
