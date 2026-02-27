# Claude Evaluator Implementation Guide

## Overview

The permission system now includes intelligent Claude-based evaluation for "ask" decisions, increasing autonomy while maintaining safety guardrails.

## How It Works

### Permission Flow

Tool Call → Deterministic Rules → Allow/Deny/Ask
If Ask → Claude Evaluation → Allow (safe) or Ask User (uncertain)

## Implementation Details

### Files Modified

1. **.claude/hooks/claude_evaluator.py** (NEW)
   - ClaudeEvaluator class - Main evaluation logic
   - Uses Anthropic SDK (claude-3-5-sonnet model)
   - Implements fail-safe: timeouts and errors return "ask_user"
   - Logs all evaluations for audit trail

2. **.claude/hooks/pre_tool_use_hook.py** (MODIFIED)
   - handle_bash_tool() - Bash command evaluation
   - handle_general_tool() - Non-Bash tool evaluation
   - Both now call Claude evaluator for "ask" decisions

## Safety Rules Evaluated

Claude checks against enforceable rules from CRITICAL-BEFORE-CODE.md and CRITICAL-BEFORE-PR.md:

**Lock File Violations:**
- Repository already locked by another session

**Git Branch Violations:**
- Branching from master
- Pushing to maintenance branches
- Creating branches in wrong locations

**Direct Tool Violations:**
- Using cmake/make directly (should use inav-builder)
- Using npm directly (should use inav-builder)

**PR/Commit Violations:**
- PR targeting master
- Commits mentioning Claude/AI

**Safe Operations:**
- Read-only commands (grep, cat, file inspection)
- Git operations on feature branches
- Documentation updates

## How Claude Evaluates

### Decision Logic

Claude returns only: "allow" or "ask_user"

- "allow": Clearly safe operation with no rule violations
- "ask_user": Uncertain, unsafe, or violates rules (fail-safe)

### Error Handling

If Claude API fails:
- Timeout (>10 seconds) → ask_user
- Invalid response → ask_user
- Authentication error → ask_user

Principle: Always ask user when uncertain

## Logging

All evaluations logged to tool_permissions.log:

[claude_evaluator] Claude evaluation: allow (tool=Bash, category=read)
[claude_evaluator] Claude evaluation: ask_user (tool=Bash, category=write)

## Environment Requirements

- Anthropic API key (provided by Claude Code automatically)
- Python 3.6+
- anthropic library (already installed)

## Configuration

No configuration needed. Evaluator uses:
- Model: claude-3-5-sonnet-20241022
- Timeout: 10 seconds
- Fail-safe: Always ask user on error

## Testing

Quick test:
  cd .claude/hooks
  python3 -c "from claude_evaluator import get_evaluator; print(get_evaluator())"

Integration test passes if all imports work and components initialize.

## References

- Plan: ~/.claude/plans/keen-dancing-perlis.md
- Config: .claude/hooks/tool_permissions.yaml
- Log: .claude/hooks/tool_permissions.log
