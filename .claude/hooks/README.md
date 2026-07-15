# Claude Code Hooks

This directory contains hooks that control Claude Code's behavior.

## Configuration Files

The tool permissions configuration is split into three files (automatically merged by `hook_common.py`):

- **tool_permissions_defaults.yaml** - Logging configuration and default behaviors by category
- **tool_permissions_rules.yaml** - Rules for non-Bash tools (Read, Write, Edit, etc.)
- **tool_permissions_bash.yaml** - Rules for Bash commands

⚠️ **Important:** Edit the appropriate split file based on rule type:
- Adding rules for **Bash commands**? → Edit `tool_permissions_bash.yaml`
- Adding rules for **other tools** (Write, Edit, etc.)? → Edit `tool_permissions_rules.yaml`
- Changing **defaults or logging**? → Edit `tool_permissions_defaults.yaml`
- Adding a **point-of-action reminder** for the model (not a permission decision)? →
  Edit `tool_context_injections.yaml` instead - see "Context Injection" below.

## Hook Files

- **pre_tool_use_hook.py** - PreToolUse hook (runs before each tool call)
- **permission_request_hook.py** - PermissionRequest hook (handles permission requests)
- **hook_common.py** - Shared utilities for hooks
- **bash_parser.py** - Bash command parser
- **validate_config.py** - Configuration validation script

## Context Injection

`tool_context_injections.yaml` is a **fourth**, deliberately separate config file:
short (1-3 line) reminders appended to the model's context at the moment a matching
tool call is about to run - e.g. a reminder about commit message rules right as
`git add` runs, predicting a `git commit` is coming soon.

**Why separate from the three permission files above:** permission rules are
first-match-wins and security-ordered; injection rules are additive (every match
fires, not just the first) and never influence the allow/deny/ask decision. Mixing
them risked an injection rule accidentally shadowing a more specific deny.

**Flow:** `pre_tool_use_hook.py` first computes the permission decision (allow/deny/
ask) from the three files above. Only if that decision is `allow` does it separately
evaluate `tool_context_injections.yaml` (via `InjectionMatcher`, reusing the same
`command_pattern`/`argument_pattern`/`tool_name_pattern`/`tool_input_patterns`
matching semantics as the permission files) and append any matching rules' text to
`additionalContext`. A denied or ask-gated call never gets an injection.

**⚠️ `additionalContext` vs `systemMessage`:** `additionalContext` is what actually
reaches the model. `systemMessage` is human-UI-only. `pre_tool_use_hook.py` has an
existing special case (used by the "Warn on large Read operations" rule above) that
reroutes any message starting with the literal string `WARNING:` from
`additionalContext` to `systemMessage` - so an injection whose text happens to start
with `WARNING:` would silently never reach the model. Don't start injection `context`
text with that prefix.

**Throttling:** each rule has `throttle: once_per_session` (default) or `always`.
State is a small JSON marker file per session under
`~/.claude/hooks/injected_context/`, outside the repo. These files are pruned
automatically after 30 days on load (`InjectionThrottle._prune_stale_markers`) since
nothing ever explicitly closes a session to trigger cleanup otherwise.

**Precondition scripts** on injection rules use a different contract than permission
precondition scripts: echo `"fire"` to inject, anything else means skip. They never
return `allow`/`deny`/`ask` - an injection rule can't make that decision. A
`{HARNESS_ROOT}` variable (the repo root) is always available in addition to the
usual `{COMMAND}`/`{ARGS}`/`{FULL_COMMAND}`/tool-input-field substitutions.

See the header comment in `tool_context_injections.yaml` for the full schema and
worked examples, including the two design questions to ask before adding a rule
(is the target command already rejected with a reason elsewhere? if accepted and
it runs immediately, is there an earlier, reliable predictor command to attach the
substantive guidance to instead?).

## Quick Start

### Validate Configuration

Before making changes, validate your configuration:

```bash
cd ~/.claude/hooks
python3 validate_config.py
```

The validator automatically detects and loads all three split configuration files (`tool_permissions_defaults.yaml`, `tool_permissions_rules.yaml`, `tool_permissions_bash.yaml`).

This checks for:
- ✅ Required sections
- ✅ Valid regex patterns
- ✅ Proper rule structure
- ⚠️ Rule ordering issues
- ⚠️ Duplicate rules
- ⚠️ Unreachable rules

### Common Operations

**Allow a new bash command:** Edit `tool_permissions_bash.yaml`
```yaml
bash_rules:
  - name: "Allow my-command"
    command_pattern: "^my-command$"
    category: read
    decision: allow
```

**Block a dangerous bash pattern:** Edit `tool_permissions_bash.yaml`
```yaml
bash_rules:
  - name: "Block dangerous operation"
    command_pattern: "^rm$"
    argument_pattern: ".*-rf /.*"
    category: write
    decision: deny
    message: "Recursive delete of root paths is not allowed"
```

**Allow a tool (Write, Edit, Read, etc.):** Edit `tool_permissions_rules.yaml`
```yaml
rules:
  - name: "Allow my tool"
    tool_name_pattern: "^MyTool$"
    category: read
    decision: allow
```

**Allow bash command with specific arguments:** Edit `tool_permissions_bash.yaml`
```yaml
bash_rules:
  # IMPORTANT: Specific rule FIRST
  - name: "Allow git status"
    command_pattern: "^git$"
    argument_pattern: "^status.*"
    decision: allow

  # General rule AFTER
  - name: "Ask for other git commands"
    command_pattern: "^git$"
    decision: ask
```

## Rule Ordering

⚠️ **CRITICAL: Rules are processed in order, first match wins!**

### Correct Order (Specific → General)
```yaml
1. Block:   echo >file       (very specific, dangerous)
2. Allow:   echo             (general, safe)
```

### Wrong Order (General → Specific)
```yaml
1. Allow:   echo             (matches first - BLOCKS rule #2!)
2. Block:   echo >file       (never reached!)
```

### Best Practice Order
1. **DENY** rules (highest priority)
2. **Specific ALLOW** rules
3. **General ALLOW** rules
4. **ASK** rules (fallback)

## Architecture

```
┌─ tool_permissions_defaults.yaml  ─┐
├─ tool_permissions_rules.yaml      ├─→ hook_common.py (HookConfig - merges files)
└─ tool_permissions_bash.yaml       ─┘
    ↓
bash_parser.py (parse bash commands)
    ↓
hook_common.py (RuleMatcher - evaluates rules)
    ↓
pre_tool_use_hook.py (makes final decision)
    ↓
Claude Code (executes or asks user)
```

## Debugging

### Check what rule matched

View the log file:
```bash
tail -f ~/inavflight/.claude/hooks/tool_permissions.log
```

### Test a command

```python
from hook_common import HookConfig, RuleMatcher, HookLogger

config = HookConfig()
logger = HookLogger(config)
matcher = RuleMatcher(config, logger)

results = matcher.match_bash("your command here", None)
for r in results:
    print(f"{r['subcommand']}: {r['decision']} ({r['rule_name']})")
```

### Common Issues

**Problem: Command always asks for approval**
- Check if a general rule matches before your specific rule
- Reorder rules (specific before general)

**Problem: Rule not matching**
- Test your regex: `python3 -c "import re; print(re.match(r'^pattern$', 'test'))"`
- Check logs: `grep "your-command" ~/inavflight/.claude/hooks/tool_permissions.log`

**Problem: Parser splits command incorrectly**
- Check for shell operators: `&&`, `||`, `;`, `|`
- Check for redirections: `>`, `>>`, `2>&1`
- Check quotes are balanced

## Categories

Commands are categorized as:
- **read**: Only reads data (grep, ls, git status)
- **write**: Modifies data (rm, git commit, echo >file)
- **other**: Everything else (build tools, network ops)

Categories have default behaviors in `defaults:` section.

## Advanced Features

### Runtime Conditions (precondition_script)

Execute a bash script to decide at runtime:

```yaml
- name: "Allow mkdir if exists"
  command_pattern: "^mkdir$"
  precondition_script: |
    DIR=$(echo "{ARGS}" | awk '{print $1}')
    [ -d "$DIR" ] && echo "allow" || echo "ask"
```

Variables available:
- `{COMMAND}` - The command (e.g., "mkdir")
- `{ARGS}` - The arguments (e.g., "-p /path/to/dir")
- `{FULL_COMMAND}` - Full command string

### Pattern Matching Examples

**Match specific command:**
```yaml
command_pattern: "^git$"
```

**Match multiple commands:**
```yaml
command_pattern: "^(git|gh|svn)$"
```

**Match command with specific args:**
```yaml
command_pattern: "^git$"
argument_pattern: "^(status|log|diff).*"
```

**Match any argument containing flag:**
```yaml
argument_pattern: ".*--force.*"
```

## Safety Guidelines

1. **Always validate** after editing: `python3 validate_config.py`
2. **Test carefully** when allowing write operations
3. **Be specific** with deny rules to avoid blocking too much
4. **Use ask** when uncertain about safety
5. **Document** why rules exist (use comments)

## Common Patterns Reference

See the header comments in the appropriate split file:
- **Bash patterns:** Top of `tool_permissions_bash.yaml`
  - Allow command except with dangerous arguments
  - Different treatment based on arguments
  - Runtime condition checking
  - Path-based permissions

- **Tool patterns:** Top of `tool_permissions_rules.yaml`
  - Tool name matching
  - Input field pattern matching

## Support

For issues or questions:
- Check the log: `~/inavflight/.claude/hooks/tool_permissions.log`
- Run validator: `python3 validate_config.py`
- Review documentation in `tool_permissions.yaml` header
