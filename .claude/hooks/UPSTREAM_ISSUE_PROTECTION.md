# GitHub Upstream Issue Protection

## Overview

This document describes the permission rules that prevent accidental issue creation on upstream repositories while allowing intentional submissions after user confirmation.

## What It Prevents

The system blocks the following commands by default and requires user confirmation:

```bash
gh issue create
gh issue new
```

When you run either of these commands:

1. **The hook intercepts the command** and checks which repository you're in
2. **If in an upstream repository**, you get prompted with three confirmation questions
3. **If in your fork**, the command runs automatically without approval
4. **If approved**, you can optionally add a permanent override rule

## Upstream Repositories Protected

### Explicitly Listed
- `iNavFlight/inav` - Main INAV firmware repository
- `iNavFlight/inav-configurator` - Configuration GUI repository
- `DroneCAN/pydronecan` - DroneCAN Python library

### Pattern-Based
Any repository matching `*/inav*` pattern that is NOT owned by the current user.

Examples:
- `someone-else/inav-fork` → PROTECTED
- `your-username/inav-fork` → ALLOWED (your fork)
- `iNavFlight/inav-docs` → PROTECTED (matches pattern, not your repo)

## What Happens When You Trigger It

### Scenario 1: Issue Creation on Upstream

```
You run: gh issue create -t "New feature" -b "Description"
While in: iNavFlight/inav directory

Hook responds:
┌─────────────────────────────────────────────────────────────┐
│ SAFETY CHECK: Creating issues on upstream repositories       │
│                                                              │
│ Before creating an issue, please confirm:                   │
│ 1. Did you mean to create this issue on a fork instead?     │
│ 2. Is this the correct repository for this issue?           │
│ 3. Should this be reported to upstream or to a local fork?  │
│                                                              │
│ If you're sure... confirm and I can add an override rule.   │
└─────────────────────────────────────────────────────────────┘
```

### Scenario 2: Issue Creation on Your Fork

```
You run: gh issue create -t "New feature" -b "Description"
While in: your-username/inav-fork directory

Hook responds:
✓ ALLOWED - Issue creation proceeds without approval
```

### Scenario 3: After User Confirmation

If you confirm you want to create the issue on upstream:

```
You: "Yes, I want to create this issue on the upstream repo"

Claude Code response:
"I can add a rule to allow this in the future. Would you like me to:

1. Create a temporary override for this session?
2. Add a permanent rule to tool_permissions.yaml?
3. Or should I leave it as 'ask' for safety?"
```

## How It Works Technically

### Rule Matching

The rule uses a `precondition_script` that:

1. Queries the GitHub API to get the current repository
2. Extracts the owner and repository name
3. Checks against known upstream repositories
4. Checks the pattern: `*/inav*` with non-matching owner
5. Returns either `ask` or `allow`

### Decision Flow

```
┌─────────────────────────┐
│  gh issue create        │
│  (in some directory)    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Rule: Block gh issue create on upstream │
│ Precondition: Check current repo        │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
[Upstream repo]   [User's fork]
    │                 │
    ▼                 ▼
[ASK user]        [ALLOW command]
    │
    ▼
User confirms or denies
```

## File Location

**Configuration file:**
```
/home/robs/Projects/inav-claude/.claude/hooks/tool_permissions.yaml
```

**Relevant section:**
```yaml
bash_rules:
  - name: "Block gh issue create on upstream repositories"
    command_pattern: "^gh$"
    argument_pattern: "^issue\\s+(create|new).*"
    decision: ask
    precondition_script: |
      # Checks repository and returns "ask" or "allow"
```

## Adding Override Rules

If you frequently need to create issues on upstream and want to skip confirmation:

### Option 1: Add Repository-Specific Rule

```yaml
bash_rules:
  - name: "Allow issue creation on trusted upstream repo"
    command_pattern: "^gh$"
    argument_pattern: "^issue\\s+(create|new).*"
    precondition_script: |
      REPO=$(gh api repository --jq '.nameWithOwner' 2>/dev/null)
      if [ "$REPO" = "iNavFlight/inav" ]; then
        echo "allow"
      else
        echo "ask"
      fi
    decision: allow
```

### Option 2: Prompt-Based Confirmation

Keep the current rule as-is. When you confirm, you can optionally ask Claude Code to add a permanent rule.

## Testing the Rule

To test the rule without creating actual issues:

```bash
# Test in upstream repo
cd /path/to/inav
gh issue create --dry-run  # If available
# Or just test the hook directly

# Test in your fork
cd /path/to/your-fork/inav
gh issue create --dry-run
```

## Edge Cases

### No GitHub Authentication

If `gh auth` is not configured:
- The precondition_script will fail silently
- The hook will default to "ask" (safest option)
- You'll be prompted to confirm

### Multiple Upstream Forks

If you have multiple forks of INAV:
- `your-username/inav` → ALLOWED (yours)
- `org-name/inav-fork` → PROTECTED (not yours)
- `iNavFlight/inav` → PROTECTED (upstream)

### New Upstream Repositories

If new upstream repos are discovered:
1. Add to the explicitly-listed section in `tool_permissions.yaml`
2. Run `python3 .claude/hooks/validate_config.py`
3. Commit the change
4. The rule will apply immediately

## Configuration Maintenance

### Updating Protected Repositories

Edit `/home/robs/Projects/inav-claude/.claude/hooks/tool_permissions.yaml`:

```yaml
# Known upstream repositories to protect
case "$REPO" in
  iNavFlight/inav|iNavFlight/inav-configurator|DroneCAN/pydronecan|YOUR_NEW_REPO)
    echo "ask"
    exit 0
    ;;
esac
```

### Validation

After making changes:

```bash
cd /home/robs/Projects/inav-claude
python3 .claude/hooks/validate_config.py
```

## Benefits

1. **Prevents Accidental Issues** - Blocks most accidental upstream issues
2. **Allows Intentional Submissions** - User can override with confirmation
3. **Smart Detection** - Uses GitHub API to identify repository context
4. **Fork-Friendly** - Automatically allows your own forks
5. **Extensible** - Can add new repos or rules as needed
6. **Auditable** - All decisions logged in tool_permissions.log

## Limitations

1. **Requires GitHub CLI** - Must have `gh` installed and authenticated
2. **Context-Sensitive** - Works based on current working directory
3. **Not Foolproof** - User can still force through after confirmation
4. **No Undo** - Doesn't prevent issue creation if user confirms

## Related Documentation

- **Hook Architecture:** `.claude/hooks/ARCHITECTURE.md`
- **Configuration Guide:** `.claude/hooks/tool_permissions.yaml` (inline comments)
- **Validation Tool:** `.claude/hooks/validate_config.py`
- **Permission Logs:** `.claude/hooks/tool_permissions.log`

## Examples

### Creating an Issue on Your Fork

```bash
$ cd ~/Projects/my-inav-fork
$ gh issue create -t "Bug fix" -b "Description of issue"
# Hook checks: owner is "your-username", repo is "my-inav-fork"
# Pattern doesn't match (owner=your-username)
# Decision: ALLOW
# Result: Issue created without approval ✓
```

### Creating an Issue on Upstream

```bash
$ cd ~/Projects/inav
$ gh issue create -t "Bug report" -b "I found a bug"
# Hook checks: owner is "iNavFlight", repo is "inav"
# Known upstream repo matches
# Decision: ASK
# Prompt: Three confirmation questions
# If user confirms:
#   - Issue created (if they say yes)
#   - Option to add permanent rule
```

### Creating an Issue on Community Fork

```bash
$ cd ~/Projects/someone-elses-inav
$ gh issue create -t "Feature idea" -b "Consider adding..."
# Hook checks: owner is "someone-else", repo matches */inav*
# Owner is not current user
# Decision: ASK
# Prompt: Three confirmation questions
```
