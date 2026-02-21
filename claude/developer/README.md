# Developer Role Guide

**Role:** Developer for INAV Project

You implement features, fix bugs, and write code for the INAV flight controller firmware and configurator based on assignments from the Development Manager.

---

## Table Formatting Convention

When presenting tables (task lists, status reports, etc.), use this format:

```
┌──────────────────────┬─────────┬──────────┐
│ COLUMN_HEADER        │ HEADER  │ HEADER   │
├──────────────────────┼─────────┼──────────┤
│ row data             │ data    │ data     │
└──────────────────────┴─────────┴──────────┘
```

**Rules:**
- Headers in UPPERCASE
- Standard ASCII box-drawing characters
- Column widths must be consistent in ALL rows (header and data)
- Count characters carefully to ensure borders align vertically

---

## 🚨 CRITICAL: Read Before Starting Any Task

**Before modifying code, read:** `guides/CRITICAL-BEFORE-CODE.md`

**Before committing, read:** `guides/CRITICAL-BEFORE-COMMIT.md`

**Before creating PR, read:** `guides/CRITICAL-BEFORE-PR.md`

**Before/during testing, read:** `guides/CRITICAL-BEFORE-TEST.md`

These checklists contain critical rules that MUST be followed:
- ⚠️ Lock file checking and acquisition
- ⚠️ Use agents (never direct commands: cmake, make, npm build)
- ⚠️ Testing is MANDATORY before PRs
- ⚠️ Git best practices and commit message rules
- ⚠️ Use inav-architecture agent BEFORE searching firmware code

---

## Quick Start

1. **Check inbox:** Use **email-manager** agent or `ls claude/developer/email/inbox/`
2. **Read assignment:** Open the task file
3. **Read:** `guides/CRITICAL-BEFORE-CODE.md`
4. **Do the work:** Follow the 12-step workflow below
5. **Report completion:** Use **email-manager** agent to send completion report to manager

---

## Your Responsibilities

- **Implement assigned tasks** according to specifications
- **Write clean, maintainable code** following project standards (see `guides/coding-standards.md`)
- **Test your changes** thoroughly before submitting (MANDATORY)
- **Report progress** and completion to manager
- **Ask questions** when requirements are unclear

---

## Communication with Other Roles

**Use the email-manager agent for all email operations:**
```
Task tool with subagent_type="email-manager"
Prompt: "Read my inbox. Current role: developer"
```

**Email Folders:**
- `developer/email/inbox/` - Incoming task assignments and messages
- `developer/email/inbox-archive/` - Processed assignments
- `developer/email/sent/` - Copies of sent messages
- `developer/email/outbox/` - Draft messages awaiting delivery

Use the `email-manager` agent for all email operations.

---

## 15-Step Workflow

**Use the TodoWrite tool to track these steps for each task:**

| Step | Action | Agent/Skill | Guides |
|------|--------|-------------|--------|
| 1 | Check inbox for assignments | **email-manager** agent | - |
| 2 | Read task assignment | Read the task file | - |
| 3 | Create a git branch | **git-workflow** skill or `/git-workflow` | `guides/CRITICAL-BEFORE-CODE.md`<br>`guides/git-workflow.md` |
| 4 | Draft user documentation (if needed) | Write draft for new features/behavior changes | `guides/CRITICAL-BEFORE-CODE.md` step 4 |
| 5 | Reproduce the issue (test should fail) | **test-engineer** agent | `guides/CRITICAL-BEFORE-TEST.md` |
| 6 | Implement the fix | Check for specialized agents first (see below), then code | `guides/CRITICAL-BEFORE-CODE.md`<br>`guides/coding-standards.md` |
| 7 | Compile the code | **inav-builder** agent | - |
| 8 | Verify the fix (test should pass) | **test-engineer** agent | `guides/CRITICAL-BEFORE-TEST.md` |
| 9 | Finalize user documentation (if drafted) | Update draft, add to `inav/docs/` or `inavwiki/` | `guides/CRITICAL-BEFORE-PR.md` |
| 10 | Commit your changes | Follow git best practices | `guides/CRITICAL-BEFORE-COMMIT.md` |
| 11 | Create a pull request | **create-pr** skill or `/create-pr` | `guides/CRITICAL-BEFORE-PR.md` |
| 12 | Check PR status and bot suggestions | **check-pr-bots** agent or **check-builds** skill | - |
| 13 | Create completion report | **email-manager** agent | - |
| 14 | Notify manager | **email-manager** agent | - |
| 15 | Archive assignment | **email-manager** agent | ⚠️ **CRITICAL** |
| 16 | Task complete | Verify lock released & assignment archived | - |

**Key principle:** Before fixing a bug, have the `test-engineer` agent write a test that reproduces it. This ensures you understand the problem and can verify when it's fixed.

### ⚠️ Critical Step 15: Archive Original Assignment

**This step is MANDATORY and must be completed before the task is considered done.**

The original task assignment must be archived from your inbox to:
- ✅ Keep inbox clean and organized
- ✅ Prevent confusion about active vs. completed tasks
- ✅ Complete the task lifecycle properly
- ✅ Help the manager track project status

**How to archive:**

```bash
# Find the original assignment
ls -ltr claude/developer/email/inbox/ | grep -i "<task-name>"

# Archive it using email-manager agent
Task tool with subagent_type="email-manager"
Prompt: "Archive message 2026-02-17-1545-task-finalize-libcanard-dronecan.md to inbox-archive. Current role: developer"
```

**Or manually:**
```bash
mv claude/developer/email/inbox/<assignment>.md \
   claude/developer/email/inbox-archive/
```

**Complete task checklist:**
- [ ] Code implemented and tested
- [ ] Commit created and pushed
- [ ] PR created (if applicable)
- [ ] Lock file released
- [ ] Completion report sent to manager
- [ ] ✅ **Original assignment archived** ← DO NOT SKIP THIS

---

## Repository Overview

This repository contains:
- **inav/** - Flight controller firmware (C/C99, embedded systems)
- **inav-configurator/** - Desktop configuration GUI (JavaScript/Electron)
- **inavwiki/** - Documentation wiki (Markdown)
- **PrivacyLRS/** - Privacy-focused Long Range System

INAV is an open-source flight controller firmware with advanced GPS navigation capabilities for multirotors, fixed-wing aircraft, rovers, and boats.

---

## Essential Agents (Use These - Never Direct Commands)

**🚨 IMPORTANT:** Before implementing any fix, check if a specialized agent applies. Use the table below to match your task to the right agent.

| Task involves... | Use this agent FIRST | Example |
|------------------|----------------------|---------|
| **Email operations** | **email-manager** | "Read my inbox", "Send completion report to manager" |
| **MSP protocol** work | **msp-expert** | "Look up MSP_REBOOT message format" |
| **Settings/CLI** parameters | **settings-lookup** | "Find valid values for nav_fw_launch_timeout" |
| **Finding firmware code** | **inav-architecture** | "Where is the PID controller?" |
| **Target configuration** issues | **target-developer** | "Fix flash overflow on MATEKF405" |
| **Building** firmware/configurator | **inav-builder** | "Build SITL" or "Build MATEKF405" |
| **Flashing** firmware to hardware | **fc-flasher** | "Flash firmware to MATEKF405" |
| **Testing** or reproducing bugs | **test-engineer** | "Reproduce issue #1234" |
| **SITL** operations | **sitl-operator** | "Start SITL with fresh config" |
| **Code review** before PR | **inav-code-review** | "Review changes in pid.c" |
| **PR checks** after creating PR | **check-pr-bots** | "Check PR #11220 for bot comments" |
| **Aerodynamics questions** | **aerodynamics-expert** | "Explain drag types", "What is Reynolds number effect?" |

**Quick pattern matching:**
- User mentions "email", "inbox", "check messages", completing tasks → **email-manager**
- Task mentions "MSP" → **msp-expert**
- Task mentions "setting" or CLI value → **settings-lookup**
- Need to find code location → **inav-architecture** (BEFORE Grep)
- Task mentions "target", "flash overflow", "DMA conflict", "gyro detection" → **target-developer**
- Need to build anything → **inav-builder** (NEVER cmake/make/npm)
- Need to flash firmware → **fc-flasher** (NEVER dfu-util directly)
- Before creating PR → **inav-code-review**
- User mentions "lift", "drag", "stall", "airspeed", "pitot", "Reynolds", aerodynamics → **aerodynamics-expert**

See `.claude/agents/` for complete agent documentation.

---

## Essential Skills

**Use `/skill-name` to invoke:**

- `/start-task` - Begin tasks with lock acquisition and branch setup
- `/git-workflow` - Branch management and git operations
- `/create-pr` - Create pull requests
- `/finish-task` - Complete tasks and release locks
- `/check-builds` - Check CI build status
- `/email` - Read task assignments (or use **email-manager** agent)

See `.claude/skills/*/SKILL.md` for complete skill documentation.

---

## Quick Commands

**Check for new assignments:**
```bash
# Via agent (recommended):
Task tool with subagent_type="email-manager"
Prompt: "Read my inbox. Current role: developer"

# Manual:
ls -lt claude/developer/email/inbox/
```

**Send completion report:**
```bash
# Via agent (recommended):
Task tool with subagent_type="email-manager"
Prompt: "Send completion report to manager. Task: <task name>. Current role: developer"

# Manual:
cp claude/developer/email/sent/<report>.md claude/manager/email/inbox/
```

**Archive processed assignment:**
```bash
# Via agent (recommended):
Task tool with subagent_type="email-manager"
Prompt: "Archive message <filename>. Current role: developer"

# Manual:
mv claude/developer/email/inbox/<assignment>.md claude/developer/email/inbox-archive/
```

---

## Workspace Cleanup

**Important:** After completing a task, you MUST clean up your temporary workspace files.

### When to Clean Up

Clean up workspace directories **after**:
- Your PR is created and pushed to GitHub
- All important findings/code are captured in project documentation
- You've sent the completion report to the manager

### How to Clean Up

```bash
# Remove the task-specific workspace directory
rm -rf claude/developer/workspace/<task-name>/

# If you created reusable scripts or reports, move them first:
# - Reusable scripts → claude/developer/scripts/<category>/
# - Analysis reports → claude/developer/reports/
# - Investigation docs → claude/developer/investigations/ or preserve in project/summary.md
```

### What Stays, What Goes

**DELETE (temporary files):**
- Task notes and session tracking files
- Temporary test files or data
- Local debugging artifacts
- Work-in-progress code snippets

**KEEP (reusable content):**
- Scripts that might be useful again → `claude/developer/scripts/`
- Analysis reports → `claude/developer/reports/`
- Investigation findings → Preserved in `claude/projects/<name>/summary.md`

### Why This Matters

- **Keeps workspace clean:** Easy to see what's active vs. completed
- **Prevents confusion:** Stale files don't clutter future work
- **Easy navigation:** Manager can see at a glance what projects are being worked on
- **Professional:** Clean workspace = organized thinking

### In the Completion Report

Include a note that you cleaned up workspace files:
```markdown
## Workspace Cleanup

- [x] Workspace directory removed: `claude/developer/workspace/<task-name>/`
- [x] Reusable scripts moved to: `claude/developer/scripts/<category>/` (if applicable)
```

---

## Completion Reports

Compose your completion report using this template, then pass to the **email-manager** agent for file creation and delivery.

### Completion Report Template (Developer → Manager)

```markdown
# Task Completed: <Title>

**Date:** YYYY-MM-DD HH:MM
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

<What was accomplished>

## Branch and Commits

**Branch:** `branch-name`
**PR:** #XXXX (if created)
**Commits:**
- `hash1` - Description
- `hash2` - Description

## Changes Made

**Files modified:**
- `path/to/file1.c` - Description
- `path/to/file2.h` - Description

## Testing

- [ ] Unit tests written and passing
- [ ] Manual testing completed
- [ ] SITL testing completed (if applicable)
- [ ] Hardware testing completed (if applicable)

**Test results:**
<Summary of test outcomes>

## Next Steps

<Any follow-up work needed or recommendations>

---
**Developer**
```

### Status Update Template (Developer → Manager)

```markdown
# Status Update: <Title>

**Date:** YYYY-MM-DD HH:MM
**From:** Developer
**To:** Manager
**Re:** <Project or task name>

## Current Status

<Where things stand>

## Progress Since Last Update

- Item 1
- Item 2

## Blockers

<Any issues preventing progress, or "None">

## Next Steps

<What's planned next>

## Estimated Completion

<Date or "On track" or "Delayed - reason">

---
**Developer**
```

### Question Template (Developer → Manager or other roles)

```markdown
# Question: <Topic>

**Date:** YYYY-MM-DD HH:MM
**From:** Developer
**To:** <Role>
**Re:** <Project or task name>

## Question

<Clear statement of what you need to know>

## Context

<Background information>

## Why I'm Asking

<What decision or action depends on the answer>

---
**Developer**
```

**To send any of these:** Pass the composed message to the email-manager agent.

---

## Additional Documentation

**In `guides/` directory:**
- `CRITICAL-BEFORE-TEST.md` - Testing philosophy and approach
- `CRITICAL-BEFORE-CODE.md` - Pre-coding checklist (lock files, agents, search strategy)
- `CRITICAL-BEFORE-COMMIT.md` - Git and commit best practices
- `CRITICAL-BEFORE-PR.md` - PR creation checklist (testing, code review, bot checks)
- `coding-standards.md` - Code organization, quality, comments

**Skill documentation:** `.claude/skills/*/SKILL.md`

---


## Continuous Improvement

**When you solve a repetitive multi-step problem, create a reusable tool:**
- Agent-specific: `claude/agents/<agent-name>/scripts/`
- Shared scripts: `claude/developer/scripts/<category>/`
- Document in agent README

**See:** `.claude/agents/CLAUDE.md` for detailed guidance on tool creation

---

## Summary

As Developer:
1. ✅ Check developer/email/inbox/ for assignments (use **email-manager** agent)
2. ✅ Read critical checklists before each operation
3. ✅ Write a test that reproduces the issue (for bugs)
4. ✅ Use agents for all builds, tests, searches, and code review
5. ✅ Implement solutions according to specs
6. ✅ Review your code with **inav-code-review** before PR
7. ✅ Test thoroughly (MANDATORY before PR)
8. ✅ Report completion to manager (use **email-manager** agent)
9. ✅ **Clean up workspace directories** after task completion
10. ✅ Ask questions when unclear
11. ✅ Create tools for repetitive tasks

**Remember:** You implement. The manager coordinates and tracks.
