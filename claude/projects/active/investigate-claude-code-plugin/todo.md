# Todo: Investigate Claude Code Plugin Packaging

## Phase 1: Setup

- [ ] Clone https://github.com/sensei-hacker/inav-claude to a fresh working directory (NOT ~/inavflight)
- [ ] Review Claude Code plugin/extension documentation

## Phase 2: Component Inventory

- [ ] Inventory `.claude/` directory (settings, hooks, agents, skills, keybindings, MCP)
- [ ] Inventory `claude/` directory (role system, email system, projects structure, install script)
- [ ] Inventory `CLAUDE.md` and role-specific CLAUDE.md files
- [ ] Note any components that reference absolute paths or machine-specific config

## Phase 3: Feasibility Assessment

- [ ] Map each component to a plugin equivalent (or flag as incompatible)
- [ ] Identify what Claude Code plugins CAN contain
- [ ] Identify what must be left out (e.g. filesystem-dependent email system, absolute paths)
- [ ] Assess complexity of any required changes

## Phase 4: Report

- [ ] Write feasibility verdict (Yes / Partial / No)
- [ ] Create component mapping table
- [ ] Document migration plan if feasible
- [ ] Document limitations and exclusions
- [ ] Send completion report to manager

## Completion

- [ ] No code changes made to ~/inavflight
- [ ] Completion report sent to manager
