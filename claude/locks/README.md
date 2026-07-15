# Repository Locks

This directory contains lock files to prevent multiple developers from working in the same repository simultaneously.

## Lock Files

- `inav.lock` - Locks the firmware repository (`inav/`)
- `inav2.lock` - Locks the second firmware worktree/clone (`inav2/`), if present
- `inav3.lock` - Locks the third firmware worktree/clone (`inav3/`), if present
- `inav-configurator.lock` - Locks the configurator repository (`inav-configurator/`)
- `inav-configurator2.lock` - Locks the second configurator worktree/clone (`inav-configurator2/`), if present

Some setups only have a single `inav/` checkout — in that case only `inav.lock`
applies. If `inav2/` and/or `inav3/` exist as separate worktrees/clones, they
allow parallel firmware tasks and use their own numbered lock file. Each lock
file governs only its matching directory; holding `inav.lock` does not block
work in `inav2/` or `inav3/`. The same numbered-worktree pattern applies to the
configurator: `inav-configurator2/` (and beyond, if ever needed) gets its own
lock file the same way, independent of `inav-configurator.lock`.

## Rules

1. **One developer per directory** - Only one developer can hold a lock on a given repo directory (`inav/`, `inav2/`, `inav3/`, `inav-configurator/`, `inav-configurator2/`) at a time
2. **Parallel work allowed** - A developer can work in `inav2/` while another works in `inav/`, `inav3/`, `inav-configurator/`, or `inav-configurator2/`
3. **Check before starting** - Before starting a firmware task, check `inav.lock`; if `inav/` is busy and `inav2/` exists, check/use `inav2.lock`; if that's also busy and `inav3/` exists, check/use `inav3.lock`. Same idea for configurator tasks: check `inav-configurator.lock` first, then `inav-configurator2.lock` if busy and that worktree exists
4. **Release when done** - Remove your lock file when task is complete

## Lock File Format

```
LOCKED_BY: Developer
TASK: <project-name or task description>
LOCKED_AT: YYYY-MM-DD HH:MM
BRANCH: <branch-name>
SESSION_ID: <$CLAUDE_CODE_SESSION_ID>
```

`SESSION_ID` is the acquiring session's `$CLAUDE_CODE_SESSION_ID` environment
variable.

## How to Use

### Acquiring a Lock (Developer)

Before starting work that modifies a repository:

1. Check if lock exists: `cat claude/locks/inav.lock` or `cat claude/locks/inav-configurator.lock`
2. For firmware tasks, if `inav.lock` is held and `inav2/` exists, check/use `claude/locks/inav2.lock` instead; if `inav2.lock` is also held and `inav3/` exists, check/use `claude/locks/inav3.lock`
3. For configurator tasks, if `inav-configurator.lock` is held and `inav-configurator2/` exists, check/use `claude/locks/inav-configurator2.lock` instead
4. If no lock, create one with your details
5. If locked by someone else, wait or ask manager

### Releasing a Lock (Developer)

When task is complete:

1. Remove the lock file for the directory you used, e.g. `rm claude/locks/inav.lock` (or `inav2.lock` / `inav3.lock` / `inav-configurator2.lock`)
2. Include in completion report: "Released inav.lock" (or the matching numbered lock)

### Manager Responsibilities

- Include lock acquisition in task assignments
- Verify locks are released in completion reports
- Resolve conflicts if two tasks need same repo
