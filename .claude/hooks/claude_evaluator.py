#!/usr/bin/env python3
"""
Claude-powered evaluator for permission system "ask" decisions.

When a tool call matches an "ask" rule, this evaluator uses Claude to
intelligently determine if the operation is clearly safe, or if user
approval should be requested.

Safety-first bias: If Claude is uncertain, asks the user rather than
auto-allowing.
"""

import json
import os
import re
import sys
import time
from typing import Dict, Any, Optional

try:
    from anthropic import Anthropic, APIError, APITimeoutError
except ImportError:
    print("ERROR: anthropic package not installed", file=sys.stderr)
    sys.exit(1)

from hook_common import HookLogger


class ClaudeEvaluator:
    """Evaluates tool calls using Claude for safety assessment."""
    
    MODEL = "claude-3-5-sonnet-20241022"
    TIMEOUT_SECONDS = 10
    MAX_RETRIES = 1
    
    def __init__(self, logger: Optional[HookLogger] = None):
        """Initialize Claude evaluator with optional logger."""
        self.logger = logger
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Anthropic client from environment."""
        try:
            self.client = Anthropic()
        except Exception as e:
            self._log(f"WARNING: Failed to initialize Anthropic client: {e}")
            self.client = None
    
    def _log(self, message: str, level: str = "info") -> None:
        """Log message if logger is available."""
        if self.logger:
            self.logger.log_output(level, message)
        else:
            print(f"[ClaudeEvaluator] {message}")
    
    def get_safety_rules_text(self) -> str:
        """
        Extract enforceable CRITICAL rules for Claude evaluation.
        
        Returns text describing what operations are unsafe.
        """
        return """## CRITICAL RULES - ENFORCEABLE VIOLATIONS

### Lock File Violations
- DO NOT allow operations that would write code when lock files exist
  Lock files: claude/locks/inav.lock, claude/locks/inav-configurator.lock
  If lock files exist, the repository is locked by another session

### Git Branch Violations
- DO NOT allow branching or pushing to 'master' branch
- DO NOT allow branching from 'master' (should branch from maintenance-9.x, maintenance-10.x, etc.)
- DO NOT allow pushing to maintenance-* branches (those are for releases only)
- Feature branches should be named: feature/*, fix/*, etc.

### Direct Tool Usage Violations
- DO NOT allow 'cmake ..' or 'make TARGETNAME' directly
  Use the inav-builder agent instead
- DO NOT allow 'npm start' or direct npm build commands
  Use the inav-builder agent instead
- DO NOT allow 'npm install' or direct npm build on inav-configurator
  Use the inav-builder agent instead

### PR/Push Violations
- DO NOT allow 'gh pr create' targeting 'master' branch
- DO NOT allow PR/push that includes "Claude" or "noreply@anthropic.com" in commit messages

## SAFE OPERATIONS - ALLOW IF CLEARLY SAFE

### Read-Only Operations (Always Safe)
- Any grep, cat, find, or other read operations
- File viewing and inspection
- Information gathering with no modifications

### Common Safe Patterns
- Git operations on feature branches (checkout, status, diff, log)
- Creating lock files (acquiring lock, not violating it)
- Documentation updates (markdown, comments)
- Building with proper agents (inav-builder, test-engineer)
"""
    
    def evaluate_with_claude(
        self,
        tool_name: str,
        command: str,
        category: str,
        rule_reason: str,
        cwd: Optional[str] = None
    ) -> str:
        """
        Use Claude to evaluate if a tool call is clearly safe.
        
        Args:
            tool_name: Name of the tool (e.g., 'Bash', 'Edit')
            command: The command or operation being requested
            category: Category (read, write, other)
            rule_reason: Why the rule requires asking
            cwd: Current working directory (if relevant)
        
        Returns:
            "allow" if clearly safe
            "ask_user" if uncertain or potentially unsafe
        """
        if not self.client:
            self._log("Claude client not available, requesting user approval")
            return "ask_user"
        
        safety_rules = self.get_safety_rules_text()
        
        prompt = f"""You are a safety evaluator for a software development permission system.

Tool: {tool_name}
Command: {command}
Category: {category}
Reason for approval: {rule_reason}
{f'Working Directory: {cwd}' if cwd else ''}

{safety_rules}

## YOUR TASK

Evaluate if this command is CLEARLY SAFE to execute. Use conservative bias:
- If you're unsure or uncertain, respond "ask_user"
- ONLY respond "allow" if you're confident there are NO safety violations
- Check against the CRITICAL RULES above

Return ONLY one of:
- "allow" - clearly safe operation
- "ask_user" - uncertain or potentially unsafe

Do not explain, just return the single word decision."""

        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=50,
                timeout=self.TIMEOUT_SECONDS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            decision = response.content[0].text.strip().lower()
            
            # Validate response
            if decision not in ["allow", "ask_user"]:
                self._log(f"Claude returned invalid decision: {decision}, requesting user approval")
                return "ask_user"
            
            self._log(f"Claude evaluation: {decision} (tool={tool_name}, category={category})")
            return decision
            
        except APITimeoutError:
            self._log(f"Claude API timeout (>{self.TIMEOUT_SECONDS}s), requesting user approval")
            return "ask_user"
        except APIError as e:
            self._log(f"Claude API error: {e}, requesting user approval")
            return "ask_user"
        except Exception as e:
            self._log(f"Unexpected error during Claude evaluation: {e}, requesting user approval", "error")
            return "ask_user"


def get_evaluator(logger: Optional[HookLogger] = None) -> ClaudeEvaluator:
    """Factory function to get a Claude evaluator instance."""
    return ClaudeEvaluator(logger=logger)
