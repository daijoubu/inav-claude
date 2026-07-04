# Project: Investigate OpenCode Startup Role Prompt

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Investigation / Infrastructure
**Created:** 2026-05-16
**Estimated Effort:** 2-4 hours

## Overview

Investigate how to implement a startup role selection prompt in OpenCode, equivalent to Claude Code's CLAUDE.md "MANDATORY FIRST ACTION" mechanism.

## Problem

When porting INAV-Claude from Claude Code to OpenCode, the role prompt on startup was lost. In Claude Code, the CLAUDE.md file could mandate a first action (asking which role to take on). OpenCode's AGENTS.md is designed for context injection only, not interactive prompts.

## Solution

Investigate three approaches:
1. Does OpenCode have a startup prompt mechanism we missed?
2. Can a plugin intercept `session.start` or equivalent to ask for role?
3. Can a skill prompt for role on first use?

## Scope

**In Scope:**
- Research OpenCode's startup/initialization lifecycle
- Check plugin hooks for session start
- Check AGENTS.md or other mechanisms for first-action prompts
- Prototype at least one approach

**Out of Scope:**
- Other OpenCode port gaps
- Hook system improvements (separate project)

## Success Criteria

- [ ] All three investigation paths explored
- [ ] Working prototype or documented impossibility
- [ ] Recommendation for implementation approach

## Related

- **Parent project:** `completed/port-to-opencode/`
- **Known limitation:** AGENTS.md is context injection only, not interactive
