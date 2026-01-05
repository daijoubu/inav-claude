# Claude Code Hooks

This directory contains hooks that control Claude Code's behavior.

## Files

- **tool_permissions.yaml** - Main configuration file controlling tool permissions
- **pre_tool_use_hook.py** - PreToolUse hook (runs before each tool call)
- **permission_request_hook.py** - PermissionRequest hook (handles permission requests)
- **hook_common.py** - Shared utilities for hooks
- **bash_parser.py** - Bash command parser
- **validate_config.py** - Configuration validation script

## Quick Start

### Validate Configuration

Before making changes, validate your configuration:

```bash
python3 validate_config.py
```

This checks for:
- ✅ Required sections
- ✅ Valid regex patterns
- ✅ Proper rule structure
- ⚠️ Rule ordering issues
- ⚠️ Duplicate rules
- ⚠️ Unreachable rules

### Common Operations

**Allow a new command:**
```yaml
bash_rules:
  - name: "Allow my-command"
    command_pattern: "^my-command$"
    category: read
    decision: allow
```

**Block a dangerous pattern:**
```yaml
bash_rules:
  - name: "Block dangerous operation"
    command_pattern: "^rm$"
    argument_pattern: ".*-rf /.*"
    category: write
    decision: deny
    message: "Recursive delete of root paths is not allowed"
```

**Allow command with specific arguments:**
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
tool_permissions.yaml
    ↓
hook_common.py (HookConfig)
    ↓
bash_parser.py (parse commands)
    ↓
hook_common.py (RuleMatcher)
    ↓
pre_tool_use_hook.py (make decision)
    ↓
Claude Code (execute or ask)
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

See the top of `tool_permissions.yaml` for documented common patterns:
- Allow command except with dangerous arguments
- Different treatment based on arguments
- Runtime condition checking
- Path-based permissions

## Support

For issues or questions:
- Check the log: `~/inavflight/.claude/hooks/tool_permissions.log`
- Run validator: `python3 validate_config.py`
- Review documentation in `tool_permissions.yaml` header
