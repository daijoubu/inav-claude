# Project: Port INAV-Claude to OpenCode

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Migration / Research
**Created:** 2026-05-15
**Estimated Effort:** 3-5 hours

## Overview

Review the INAV-Claude project structure and create a migration plan to port it from Claude Code to OpenCode. Identify all Claude-specific components (agents, skills, prompts) and map them to their OpenCode equivalents.

## Problem

The user wants to migrate from Claude Code to OpenCode as the AI coding assistant for this project. This requires understanding what customizations exist in the current setup and how to translate them to OpenCode's architecture.

## Objectives

1. **Inventory current Claude Code setup**
   - List all custom agents in `.claude/agents/`
   - List all skills in `.claude/skills/` and available_skills
   - Document custom configurations in `.claude/settings.json`
   - Review role-specific configurations in `claude/*/`

2. **Research OpenCode equivalents**
   - Understand OpenCode's agent architecture
   - Understand OpenCode's skill/plugin system
   - Map Claude-specific concepts to OpenCode equivalents
   - Identify gaps that require workarounds

3. **Create migration plan**
   - Document mapping table (Claude concept → OpenCode equivalent)
   - Identify files that need modification
   - Identify files that can be copied/adapted
   - Estimate effort for each component

4. **Document findings**
   - Create MIGRATION.md with the complete plan
   - Include step-by-step instructions for the port

## Scope

**In Scope:**
- `.claude/agents/` - Custom agent definitions
- `.claude/skills/` - Custom skill definitions
- `.claude/settings.json` - Claude Code configuration
- `claude/*/` - Role-specific configurations (manager, developer, etc.)
- Any claude-related README or documentation files
- Environment variables and shell integrations

**Out of Scope:**
- Actual implementation of the port (this is a research/planning project)
- Modifying the actual source code (inav/, inav-configurator/)
- Creating OpenCode configurations (future phase)

## Implementation Steps

1. Read and understand OpenCode's architecture (docs, existing configs)
2. Inventory all Claude-specific components in this project
3. Map each component to OpenCode equivalent
4. Document any gaps or limitations
5. Write MIGRATION.md with findings and recommendations

## Success Criteria

- [ ] Complete inventory of Claude Code customizations
- [ ] Research on OpenCode equivalents complete
- [ ] Mapping table created
- [ ] MIGRATION.md document written with findings
- [ ] Recommendations for next steps provided

## Priority Justification

This is a medium-high priority because:
- The user has explicitly requested this migration
- It affects the development workflow for all future work
- There's value in completing this before the codebase diverges further