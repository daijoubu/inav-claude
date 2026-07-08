# Task Assignment: Investigate OpenCode Startup Role Prompt

**Date:** 2026-05-16 14:10
**From:** Manager
**To:** Developer
**Project:** investigate-opencode-startup-prompt
**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours

## Task

Investigate how to implement a startup role selection prompt in OpenCode, equivalent to what CLAUDE.md provided in Claude Code (the "Which role should I take on today?" prompt).

## Background

During the OpenCode port, the startup role prompt was lost. In Claude Code, the CLAUDE.md file's "MANDATORY FIRST ACTION" instruction forced the model to ask the user which role they want. OpenCode's AGENTS.md is context injection only and doesn't support interactive prompts. The investigation is needed to restore this capability.

## What to Investigate

1. **Plugin hooks**: Check if OpenCode's plugin system supports intercepting session start or similar lifecycle events
2. **Skill system**: Can a skill prompt for role on first use?
3. **AGENTS.md**: Are there undocumented mechanisms for first-action prompts?
4. **OpenCode CLI**: Startup flags or configuration options for initial prompts

## Deliverables

- [ ] Document findings from all investigation paths
- [ ] If possible: working prototype
- [ ] Recommendation: which approach to implement
- [ ] Send completion report with findings

## Success Criteria

- [ ] All investigation paths explored and documented
- [ ] Recommendation with clear rationale
- [ ] Working prototype if feasible

## Project Directory

`claude/projects/active/investigate-opencode-startup-prompt/`

---
**Manager**
