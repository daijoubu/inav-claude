# Project: Investigate Claude Code Plugin Packaging

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Investigation / Feasibility Study
**Created:** 2026-02-17
**Estimated Effort:** 4-8 hours
**Assignee:** Developer

## Overview

Investigate whether the INAV Claude Code workflow (agents, skills, email system, role system, hooks, etc.) can be packaged as a Claude Code plugin, making it easier to install and share. Work is done in a fresh clone of the upstream repo — do NOT modify files in `~/inavflight`.

## Problem

The current setup requires cloning `sensei-hacker/inav-claude` and running `./claude/install.sh`. Packaging it as a Claude Code plugin could make it more portable, installable, and maintainable. We need to understand what's feasible, what can't be included, and what the migration effort would look like.

## Repo to Investigate

**Fresh clone of:** https://github.com/sensei-hacker/inav-claude

Do NOT modify any files in `~/inavflight` (the live workspace). Use a separate working directory for this investigation.

## Objectives

1. Understand the Claude Code plugin system — what can it contain?
2. Map each component of the current setup to plugin equivalents (or flag as incompatible)
3. Produce a feasibility verdict with a clear plan if feasible
4. Document anything that would have to be left out or worked around

## Scope

**In Scope:**
- `.claude/` directory contents (settings.json, hooks, agents, skills, keybindings)
- `claude/` directory contents (manager/developer/release-manager roles, email system, projects, templates)
- `CLAUDE.md` role-routing instructions
- Install script logic
- Any MCP server configurations (`.mcp.json`)

**Out of Scope:**
- Actual firmware code (inav/, inav-configurator/, etc.)
- Making code changes — analysis only

## Deliverables

1. **Feasibility verdict:** Yes / Partial / No, with rationale
2. **Component mapping table:** each major component → plugin equivalent or "cannot include, reason"
3. **Migration plan** (if feasible): step-by-step how to package it
4. **Issues/limitations list:** what would have to be left out, changed, or documented as manual steps

## Success Criteria

- [ ] Fresh clone obtained and examined
- [ ] Claude Code plugin documentation reviewed
- [ ] Every major component assessed
- [ ] Feasibility verdict delivered with clear rationale
- [ ] If feasible: concrete migration plan documented
- [ ] Completion report sent to manager

## Related

- **Repo:** https://github.com/sensei-hacker/inav-claude
- **Assignment:** `manager/email/sent/2026-02-17-HHMM-task-investigate-claude-code-plugin.md`
