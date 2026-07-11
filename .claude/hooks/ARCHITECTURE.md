# Hook System Architecture

## Overview

The Claude Code hook system provides fine-grained control over tool permissions, plus
point-of-action context delivery to the model, through:
- YAML configuration with regex-based rule matching
- Bash command parsing with quote and redirection handling
- Logging and validation capabilities
- Runtime conditional evaluation
- Additive context injection on top of (never influencing) the permission decision

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
        │   - Step 1: permission decision                │
        │     (allow / deny / ask)                       │
        │   - Step 2: IF allow, evaluate injections      │
        │     and append to additionalContext            │
        └───────────────────────┬───────────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                    │
   ┌──────────▼───────────┐          ┌─────────────▼──────────────┐
   │   hook_common.py     │          │      hook_common.py         │
   │   - HookConfig       │          │  - InjectionConfig          │
   │   - RuleMatcher      │          │  - InjectionMatcher         │
   │   - HookLogger       │          │  - InjectionThrottle        │
   │   (permission path)  │          │  (injection path)           │
   └──────────┬───────────┘          └─────────────┬──────────────┘
              │                                    │
              └─────────────────┬─────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  bash_parser.py        │
                    │  - Parse compound cmds │
                    │  - Handle quotes       │
                    │  - Handle redirections │
                    │  (shared by both paths)│
                    └───────────┬────────────┘
                                │
            ┌───────────────────▼──────────────────┐
            │   Configuration Files:               │
            ├──────────────────────────────────────┤
            │ ✓ tool_permissions_defaults.yaml     │
            │   (logging & category defaults)      │
            │                                      │
            │ ✓ tool_permissions_rules.yaml        │
            │   (non-Bash tool rules)              │
            │                                      │
            │ ✓ tool_permissions_bash.yaml         │
            │   (Bash command rules)               │
            │   -- the three above are merged --   │
            │                                      │
            │ ✓ tool_context_injections.yaml       │
            │   (context injection rules - kept    │
            │    separate; loaded independently,   │
            │    never merged with the above)      │
            └──────────────────────────────────────┘
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

### 4. Context Injection (allow outcomes only)

```python
# Only reached if permissionDecision == 'allow'. Matches tool_context_injections.yaml
# rules against the same parsed command (or tool_name/tool_input for general tools).
# Every matching rule fires - not first-match-wins - subject to per-rule throttling.
for rule in injection_rules:
    if matches(rule, parsed_cmd) and precondition_fires(rule) and throttle.should_fire(rule):
        texts.append(rule.context)

# Appended to additionalContext, never able to change the decision above.
```

### 5. Decision Return

```python
# Hook returns decision to Claude
{
  "hookSpecificOutput": {
    "permissionDecision": "allow"  # or "deny" or "ask"
  },
  "additionalContext": "..."  # Permission-path message and/or injected reminders
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

### 6. Context Injection as a Separate Config File and Code Path

**Why:** Injections have different properties than permission rules - additive
(every match fires) rather than first-match-wins, advisory rather than
security-critical, and stateful (per-session throttling) rather than stateless.
Mixing them into the permission files risked an injection rule accidentally
shadowing a more specific deny rule, and would force advisory-content edits through
the same file as security-critical deny rules.

**Implementation:** `tool_context_injections.yaml`, loaded and matched independently
by `InjectionConfig`/`InjectionMatcher`/`InjectionThrottle` in `hook_common.py`.
Reuses `RuleMatcher`'s matching predicates (`_matches_rule`, `_matches_bash_rule` -
`@staticmethod` for exactly this reuse) so pattern semantics stay identical between
the two systems, but never touches the permission decision itself. Only evaluated
when that decision is already `allow`.

**Precondition contract difference:** permission `precondition_script`s return
`allow`/`deny`/`ask` (or a `WARNING:`-prefixed message). Injection
`precondition_script`s echo `"fire"` or nothing - they select whether a match
actually injects, never a permission outcome.

## Performance Characteristics

### Config Loading
- **When:** Once per hook invocation (each tool call)
- **Cost:** ~5-10ms (load + merge three files + regex compilation)
- **Optimization:** Could cache in memory if needed
- **Process:** HookConfig loads and merges three split files automatically

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

### Split Files Organization

Permission decisions are configured by **three separate YAML files** (automatically
merged by `HookConfig`). Context injection is configured by a **fourth**, kept
separate on purpose (loaded independently by `InjectionConfig`, never merged with
the three below) - see "Context Injection" in README.md for why.

⚠️ **IMPORTANT: Edit the correct file based on your rule type!**

| File | Edit For | Contains |
|------|----------|----------|
| **tool_permissions_defaults.yaml** | Logging settings or category defaults | `logging:` and `defaults:` sections |
| **tool_permissions_rules.yaml** | Rules for non-Bash tools (Read, Write, Edit, TaskCreate, etc.) | `rules:` section with tool_name_pattern |
| **tool_permissions_bash.yaml** | Rules for Bash commands (git, rm, find, etc.) | `bash_rules:` section with command_pattern |
| **tool_context_injections.yaml** | Point-of-action reminders for the model (not a permission decision) | `injections:` section - see its own header comment for the schema |

**1. tool_permissions_defaults.yaml**
```yaml
logging: {...}      # Log file location and settings
defaults: {...}     # Default behaviors by category (read/write/other)
```

**2. tool_permissions_rules.yaml**
```yaml
rules:
  - Always-allow tools (TaskCreate, TaskUpdate, TaskList, TaskOutput, Skill, Read, etc.)
  - Deny rules (block dangerous patterns)
  - Allow rules (specific safe operations)
  - Ask rules (fallback for unknown tools)
```

**3. tool_permissions_bash.yaml**
```yaml
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

**4. tool_context_injections.yaml**
```yaml
injections:
  - Leading-indicator rules (fire on a command that predicts a later one)
  - Terminal-action safety nets (fire on the action itself)
  - Domain-specific reminders (e.g. INAV settings.yaml design philosophy)
```

### Why Split?

- **Defaults:** Rarely changes, good to isolate
- **Tool Rules:** Different semantics from Bash rules
- **Bash Rules:** Large section, specific to command parsing
- **Context Injections:** Additive and advisory rather than first-match-wins and
  security-critical - mixing it with the permission files risked an injection rule
  shadowing a more specific deny (see Key Design Decision 6 above)

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

### Adding New Injection Rules

Edit `tool_context_injections.yaml`, not the files above - see its header comment
for the schema and the two design questions to ask before adding a rule (is the
target already rejected elsewhere with a reason? if accepted and it runs
immediately, is there an earlier predictor command to attach the guidance to
instead?). Precondition scripts on injection rules use a different contract than
the one above: echo `"fire"` to inject, anything else to skip - never
`allow`/`deny`/`ask`.

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
- Parser bugs splitting commands - **NOT fully mitigated.** Two confirmed gaps
  (2026-07-11, reported to Manager): (1) `handle_bash_tool()`'s heredoc branch
  checks only the heredoc's first line and returns `allow` for the entire
  command, never evaluating anything on a line after the heredoc terminator -
  a command like `cat > allowed/path << 'EOF' ... EOF` followed by `git add -A`
  on the next line bypasses that rule's hard deny entirely; (2)
  `BashCommandParser._parse_simple_command()` treats `VAR=value cmd args` as
  `command='VAR=value'`, so any env-var-prefixed invocation (`GIT_EDITOR=x git
  commit ...`) never matches a `command_pattern` rule at all. Both affect
  `tool_permissions_bash.yaml` deny rules, not just `tool_context_injections.yaml`.
  Fix tracked separately, not yet applied as of this writing.

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

## Self-Improvement: Lessons Learned

When you discover something important about HOOK DEVELOPMENT that will likely help
in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future hook changes, not one-off situations
- **About the hook system itself** - output schema, delivery mechanics, testing approach
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

- **A hook's logged/returned JSON is not proof content reached the model**: the hook
  process's own stdout and the harness's transcript logging of that stdout (a
  `"hook_success"` attachment record) can be completely correct while the actual
  `tool_result` delivered to the model contains none of it - confirmed for
  `additionalContext` placed at the wrong JSON nesting level. Before trusting that a
  hook output field works, read the raw session transcript
  (`~/.claude/projects/.../<session-id>.jsonl`) for the actual `tool_result` message,
  or better, trigger a real tool call and check what you yourself receive.

<!-- Add new lessons above this line -->
