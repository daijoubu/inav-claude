# Task Assignment: Investigate OpenCode Compaction Context Loss

**Date:** 2026-05-27 11:00
**From:** Manager
**To:** Developer
**Project:** investigate-opencode-compaction-context-loss
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 3-6 hours

## Task

Investigate and fix the issue where OpenCode loses task context during conversation compaction. After compressing earlier conversation history to manage the context window, the agent loses track of the current task and reverts to the first incomplete todo item, causing wasted work and confusion.

## Background

During long coding sessions, OpenCode compresses/compacts earlier conversation turns to free up context window space. When this occurs, the agent appears to lose awareness of the currently active task — it forgets what it was working on and defaults back to the first incomplete todo item in the project. This results in redundant work, incorrect file modifications, and significant time wasted re-establishing context.

This issue directly impacts developer productivity and reliability during extended sessions.

## What to Do

1. **Research compaction mechanism** — Investigate how OpenCode's context compaction works. Look at OpenCode source code, configuration files, and any relevant documentation in the repository.

2. **Reproduce the issue** — Create a test scenario that triggers context compaction and demonstrates the loss of task context. Document the exact steps to reproduce.

3. **Identify root cause** — Determine why the agent loses track of the current task after compaction. Is it a missing state file? A compaction bug? A workflow gap?

4. **Design and implement a fix** — The fix could be one or more of:
   - A skill modification to persist current task state
   - A workflow change (e.g., explicit context save/restore)
   - A documentation update with workarounds
   - A modification to how tasks/state are tracked

5. **Test the fix** — Verify that after compaction, the agent correctly resumes the current task rather than reverting to the first incomplete todo item.

## Success Criteria

- [ ] Root cause of context loss after compaction identified and documented
- [ ] Fix or workaround implemented and tested successfully
- [ ] Documentation updated in relevant `claude/` files

## Project Directory

`claude/projects/active/investigate-opencode-compaction-context-loss/`

## Scope Notes

- All work is within the **inav-claude** repository itself (no firmware or configurator changes)
- This may involve examining OpenCode's source code, skills, agents, and workflow tooling
- The fix should be self-contained within the project's workflow system

## Recommended Agents/Skills

- Use `email-manager` agent for any email communication
- Use Explore or Grep for codebase investigation
- Use Read for examining OpenCode/skill documentation

---
**Manager**
