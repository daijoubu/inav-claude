# Hook System Architecture

## Overview

The Claude Code hook system provides fine-grained control over tool permissions through:
- YAML configuration with regex-based rule matching
- Bash command parsing with quote and redirection handling
- Logging and validation capabilities
- Runtime conditional evaluation

## Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code (CLI)                         │
└───────────────────────────────┬─────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Tool Call Request    │
                    └───────────┬───────────┘
                                │
        ┌───────────────────────▼───────────────────────┐
        │   pre_tool_use_hook.py (PreToolUse Hook)      │
        │   - Intercepts all tool calls                 │
        │   - Returns: allow / deny / ask               │
        └───────────────────────┬───────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   hook_common.py       │
                    │   - HookConfig         │
                    │   - RuleMatcher        │
                    │   - HookLogger         │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  bash_parser.py        │
                    │  - Parse compound cmds │
                    │  - Handle quotes       │
                    │  - Handle redirections │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │ tool_permissions.yaml  │
                    │ - Rules (ordered list) │
                    │ - Defaults by category │
                    └────────────────────────┘
```

## Data Flow

### 1. Tool Call Interception

```python
# Claude Code calls a tool
Tool: Bash
Input: { command: "git status && git diff" }

↓

# Hook receives JSON
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git status && git diff"
  },
  "cwd": "/path/to/project"
}
```

### 2. Command Parsing (Bash Only)

```python
# BashCommandParser splits compound commands
"git status && git diff"

↓ parse()

[
  ParsedCommand(command="git", arguments="status", operator_before=None),
  ParsedCommand(command="git", arguments="diff", operator_before="&&")
]
```

### 3. Rule Matching

```python
# For each subcommand, find first matching rule
for parsed_cmd in parsed_commands:
    for rule in bash_rules:
        if matches(rule, parsed_cmd):
            return rule.decision  # "allow", "deny", or "ask"

# If no rule matches, use category default
return defaults[category]
```

### 4. Decision Return

```python
# Hook returns decision to Claude
{
  "hookSpecificOutput": {
    "permissionDecision": "allow"  # or "deny" or "ask"
  },
  "additionalContext": "..."  # Optional context for Claude
}
```

## Key Design Decisions

### 1. First-Match-Wins Rule Processing

**Why:** Simplicity and predictability
- Easy to understand: read rules top to bottom
- Clear precedence: specific before general

**Trade-off:** Requires careful rule ordering
- Solution: Extensive documentation and validation script

### 2. Separate Bash Rules from General Tool Rules

**Why:** Different matching semantics
- Bash: Parse into subcommands, match each
- General tools: Match tool name and input fields

**Benefit:** More powerful bash command analysis

### 3. Quote-Aware Parsing

**Why:** Preserve command semantics
- `echo "test; ls"` should be ONE command, not two
- `grep "foo bar" file` should parse correctly

**Implementation:** Custom `_split_respecting_quotes()` method

### 4. Redirection Handling

**Why:** Bash operators like `&` conflict with `2>&1`
- `find . 2>&1` should NOT split on `&`
- `cmd1 && cmd2` SHOULD split on `&&`

**Solution:** `_is_redirection()` method to detect redirection operators

### 5. Runtime Conditional Rules (precondition_script)

**Why:** Some decisions depend on filesystem state
- `mkdir existing_dir` → allow (safe, idempotent)
- `mkdir new_dir` → ask (creates something new)

**Implementation:** Execute bash script, capture stdout

## Performance Characteristics

### Config Loading
- **When:** Once per hook invocation (each tool call)
- **Cost:** ~5-10ms (YAML parse + regex compilation)
- **Optimization:** Could cache in memory if needed

### Command Parsing
- **When:** Every Bash tool call
- **Cost:** ~1ms for simple commands, ~5ms for complex
- **Complexity:** O(n) where n = command length

### Rule Matching
- **When:** For each parsed subcommand
- **Cost:** O(r) where r = number of rules (typically 20-30)
- **Early exit:** First match returns immediately

### Total Overhead
- Typical: 10-20ms per tool call
- Complex bash: 30-50ms per tool call
- Negligible compared to actual tool execution

## Configuration File Structure

### Logical Organization

```yaml
# 1. Metadata
logging: {...}
defaults: {...}

# 2. General Tool Rules (Read, Write, Edit, etc.)
rules:
  - Always-allow tools (TodoWrite, Skill, Read)
  - Deny rules
  - Ask rules

# 3. Bash-Specific Rules
bash_rules:
  - Path safety (project-specific)
  - Git safety (deny dangerous, allow safe)
  - Find command (specific → general)
  - Echo command (block redirect, allow general)
  - Cat/heredoc (allow claude/, ask other)
  - Dangerous operations (rm -r, etc.)
  - Build tools (cmake, gcc, etc.)
  - Common read commands (broad allow list)
  - Shell syntax (control structures, parser artifacts)
  - GitHub CLI
  - Runtime conditionals (precondition_script)
```

### Rule Ordering Strategy

```yaml
# Pattern: Specific → General

# ✓ GOOD
- Block: find -exec rm        # Very specific
- Allow: find -exec grep      # Specific, safe subset
- Ask:   find -exec *         # Broader
- Allow: find                 # General

# ✗ BAD
- Allow: find                 # Too general, matches everything!
- Block: find -exec rm        # Never reached
```

## Extension Points

### Adding New Commands

1. **Read-only command:**
   - Add to common read commands regex
   - No additional rules needed

2. **Write command:**
   - Add specific allow/deny rules before general rules
   - Consider argument patterns

3. **Complex command:**
   - May need multiple rules for different argument patterns
   - Use precondition_script for runtime checks

### Adding New Tool Types

1. Add to `rules:` section (not `bash_rules:`)
2. Use `tool_name_pattern` for tool name
3. Use `tool_input_patterns` for input fields

### Custom Preconditions

```yaml
- name: "Custom check"
  command_pattern: "^mycmd$"
  precondition_script: |
    # Available variables:
    # {COMMAND} - command name
    # {ARGS} - arguments
    # {FULL_COMMAND} - full command string

    # Your logic here
    if condition; then
      echo "allow"
    else
      echo "ask"
    fi
```

## Validation

### Automated Checks (validate_config.py)

1. **Syntax validation**
   - YAML structure
   - Required sections
   - Valid regex patterns

2. **Semantic validation**
   - Rule ordering issues
   - Duplicate rules
   - Unreachable rules
   - Precondition script structure

3. **Output**
   - Errors (must fix)
   - Warnings (advisory)
   - Info (helpful context)

### Manual Review

- Check rule ordering for new commands
- Test with representative commands
- Review logs after configuration changes

## Security Considerations

### Defense in Depth

1. **Deny rules** for known dangerous patterns
2. **Specific allow** for verified safe operations
3. **Ask by default** for unknown operations
4. **Logging** for audit trail

### Attack Surface

**Trusted:**
- YAML config (user-controlled)
- Hook scripts (user-controlled)
- Config file paths (hardcoded)

**Potential Issues:**
- Regex catastrophic backtracking (mitigated: simple patterns)
- Precondition script injection (mitigated: user controls config)
- Parser bugs splitting commands (mitigated: comprehensive tests)

### Best Practices

1. **Specific over general** - Whitelist specific patterns
2. **Deny dangerous patterns** - Don't rely on category defaults
3. **Test before deploy** - Use validation script
4. **Review logs** - Monitor what's being allowed/denied
5. **Update regularly** - Add new safe commands as discovered

## Maintenance

### Adding Commands Over Time

As you use the system, you'll encounter commands that need approval.

**Process:**
1. Command triggers "ask"
2. User approves
3. Add to config if it should auto-allow
4. Decide: specific rule or add to broad allow list
5. Run validator
6. Test command

**Example workflow:**
```bash
# Command asks for approval
> arm-none-eabi-size firmware.elf
[Hook asks for approval]

# After approval, add to config
# Option 1: Add to common read commands
command_pattern: "^(...|arm-none-eabi-size)$"

# Option 2: Specific rule
- name: "Allow ARM binary tools"
  command_pattern: "^arm-none-eabi-(size|nm|objdump|objcopy)$"
  decision: allow

# Validate
python3 validate_config.py

# Test
echo "Command should now auto-allow"
```

### Config Organization

- Use section headers (`# ===...===`)
- Group related rules together
- Comment WHY rules exist
- Reference issue numbers if applicable
- Keep specific rules before general rules

## Future Enhancements

### Potential Improvements

1. **Priority field** - Explicit rule ordering
2. **Command groups** - Reusable command lists
3. **Separate deny/allow/ask sections** - Clearer structure
4. **Config includes** - Split large configs
5. **Rule testing framework** - Unit tests for rules
6. **Performance optimization** - Cache compiled regexes
7. **Better error messages** - Suggest which rule to add

### Non-Goals

- Complex state machines (keep it simple)
- Natural language processing (regex is sufficient)
- Learning/AI (explicit rules are better)
- Runtime modification (reload on change is fine)
