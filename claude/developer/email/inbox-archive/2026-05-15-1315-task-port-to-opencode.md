# Task Assignment: Port INAV-Claude to OpenCode

**Date:** 2026-05-15 13:15
**From:** Manager
**To:** Developer
**Project:** port-to-opencode
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 3-5 hours

## Task

Review the INAV-Claude project structure and create a migration plan to port it from Claude Code to OpenCode. Identify all Claude-specific components (agents, skills, prompts) and map them to their OpenCode equivalents.

## Background

The user wants to migrate from Claude Code to OpenCode as the AI coding assistant for this project. This requires understanding what customizations exist in the current setup and how to translate them to OpenCode's architecture.

## What to Do

1. **Research OpenCode architecture**
   - Review OpenCode documentation (webfetch from opencode.ai or docs)
   - Understand agent, skill, and plugin systems
   - Identify configuration file formats

2. **Inventory Claude Code setup**
   - List custom agents in `.claude/agents/`
   - List custom skills in `.claude/skills/`
   - Review `.claude/settings.json`
   - Review role-specific configs in `claude/*/`

3. **Create mapping and documentation**
   - Create a mapping table (Claude concept → OpenCode equivalent)
   - Identify gaps or limitations
   - Write `claude/docs/MIGRATION.md` with findings and step-by-step instructions

## Success Criteria

- [ ] Complete inventory of Claude Code customizations
- [ ] Research on OpenCode equivalents complete
- [ ] Mapping table created
- [ ] MIGRATION.md document written with findings
- [ ] Recommendations for next steps provided

## Project Directory

`claude/projects/active/port-to-opencode/`

---

**Manager**