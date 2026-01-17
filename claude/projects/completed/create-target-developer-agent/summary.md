# Project: Create Target Developer Agent with Documentation

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Documentation / Agent Development / Knowledge Base
**Created:** 2026-01-12
**Estimated Effort:** 6-8 hours

## Overview

Document how INAV hardware targets work by researching historical target fixes via git history, then create a specialized "target-developer" agent that helps with writing and troubleshooting hardware targets.

## Problem

Target configuration is complex and error-prone. We need:
- Comprehensive documentation on how targets work
- Understanding of common target problems and their solutions
- A specialized agent that can help with target development
- A knowledge base of target-related patterns and fixes

## Objectives

### Phase 1: Research Target System (2-3 hours)

**Goal:** Understand target architecture and common issues by examining git history

1. **Study target structure:**
   - How target.h, target.cmake, config.c work together
   - Flash memory configuration
   - Feature flag system
   - Pin mappings and peripheral configuration
   - Build system integration

2. **Use git blame/log to find target fixes:**
   ```bash
   # Find commits that modified target files
   git log --all --oneline -- "src/main/target/*/target.h" | head -50
   git log --all --oneline -- "src/main/target/*/target.cmake" | head -50

   # Look for fix/bug commits
   git log --all --grep="target" --grep="fix" --oneline | head -50
   git log --all --grep="flash" --grep="size" --oneline | head -50
   ```

3. **Categorize common target problems:**
   - Flash size issues
   - Pin conflicts
   - Feature incompatibilities
   - Peripheral configuration errors
   - Build system problems
   - Sensor initialization issues
   - Timer allocation conflicts

4. **Document fix patterns:**
   - How each problem type was solved
   - What files were changed
   - Common mistakes to avoid

### Phase 2: Write Documentation (2-3 hours)

**Create documentation in:** `claude/developer/docs/targets/`

**Documents to create:**

1. **`overview.md`** - Target system architecture
   - Directory structure
   - File purposes (target.h, target.cmake, config.c, etc.)
   - How targets are selected during build
   - Relationship between target files and build system

2. **`common-issues.md`** - Problem catalog from git history
   - Flash overflow (causes and solutions)
   - Pin mapping conflicts
   - Feature flag issues
   - Timer allocation problems
   - Peripheral configuration errors
   - Real examples from git history with commit references

3. **`creating-targets.md`** - Step-by-step guide
   - How to create a new target
   - What to copy from reference targets
   - Checklist of required settings
   - Testing new targets

4. **`troubleshooting-guide.md`** - Debugging targets
   - Build errors and what they mean
   - Runtime issues (sensors not working, etc.)
   - Flash size optimization techniques
   - How to compare targets to find issues

5. **`examples.md`** - Real-world fixes
   - Extract 5-10 interesting target fixes from git history
   - Show before/after
   - Explain what was wrong and why the fix worked

### Phase 3: Create Target Developer Agent (2 hours)

**Use the create-agent agent:**

```
Task tool: subagent_type="create-agent"
Prompt: "Create a target-developer agent for INAV firmware. This agent
specializes in writing and troubleshooting hardware target configurations.

Knowledge base:
- Target system architecture (target.h, target.cmake, config.c)
- Common target issues (flash size, pin conflicts, features)
- Git history of target fixes
- F4, F7, H7 MCU differences
- Build system integration

Agent should help with:
- Creating new targets from reference
- Debugging target build errors
- Fixing flash overflow issues
- Resolving pin/timer conflicts
- Comparing target configurations
- Optimizing target feature sets

Tools: Read, Grep, Glob, Bash (for git commands)"
```

**Agent capabilities should include:**

1. **Knowledge base access:**
   - Read target documentation in `claude/developer/docs/targets/`
   - Reference common issues catalog
   - Access git history for similar problems

2. **Target analysis:**
   - Compare target configurations
   - Identify feature bloat
   - Find pin conflicts
   - Calculate flash usage

3. **Problem diagnosis:**
   - Parse build errors
   - Suggest fixes based on historical patterns
   - Check for common mistakes

4. **Code generation:**
   - Generate target.h boilerplate
   - Suggest feature flags for hardware
   - Create pin mapping tables

### Phase 4: Create Knowledge Base Library (1 hour)

**Create reference library in:** `claude/developer/docs/targets/knowledge-base/`

**Structure:**
```
knowledge-base/
├── mcu-families/
│   ├── stm32f4.md
│   ├── stm32f7.md
│   └── stm32h7.md
├── peripherals/
│   ├── timers.md
│   ├── uart-config.md
│   ├── spi-config.md
│   └── i2c-config.md
├── common-sensors/
│   ├── gyro-config.md
│   ├── baro-config.md
│   └── mag-config.md
└── git-fixes/
    └── historical-fixes.md (extracted from git history)
```

Each file contains:
- Technical details
- Configuration patterns
- Common pitfalls
- Examples from real targets

## Implementation Approach

### Step 1: Research Phase

1. **Explore target directory structure:**
   ```bash
   ls -la inav/src/main/target/
   # Pick 3-4 representative targets to study
   ```

2. **Study reference targets:**
   - Simple F4 target
   - Complex F7 target with many features
   - Minimal target for comparison

3. **Mine git history:**
   ```bash
   # Last 100 target-related commits
   git log --all --oneline --grep="target" | head -100 > target_commits.txt

   # Commits fixing target issues
   git log --all --oneline --grep="fix" -- "src/main/target/" | head -50

   # Flash size related commits
   git log --all --oneline --grep="flash" -- "src/main/target/"
   ```

4. **Examine specific fix commits:**
   ```bash
   git show <commit-hash>
   ```

5. **Categorize findings** into problem types

### Step 2: Write Documentation

Create documentation files with clear structure:
- Problem description
- How to detect
- How to fix
- Real examples with git commit references
- Code snippets

### Step 3: Create Agent

Use create-agent to build the target-developer agent:
- Specify capabilities
- Define knowledge base locations
- Set up tool access
- Write clear instructions

### Step 4: Test Agent

Create test cases:
- Give it a broken target configuration
- Ask it to create a new target
- Test its troubleshooting abilities

## Success Criteria

- [ ] Comprehensive target documentation written
- [ ] 5+ git commits analyzed with problem/solution documented
- [ ] Knowledge base directory created with organized references
- [ ] target-developer agent created and functional
- [ ] Agent can access and use documentation library
- [ ] Agent tested on sample target problems
- [ ] All documentation in `claude/developer/docs/targets/`
- [ ] Agent file in `.claude/agents/target-developer.md`
- [ ] Completion report sent to manager

## Files to Create

### Documentation Files
- `claude/developer/docs/targets/overview.md`
- `claude/developer/docs/targets/common-issues.md`
- `claude/developer/docs/targets/creating-targets.md`
- `claude/developer/docs/targets/troubleshooting-guide.md`
- `claude/developer/docs/targets/examples.md`
- `claude/developer/docs/targets/knowledge-base/` (directory with subdocs)

### Agent File
- `.claude/agents/target-developer.md`

## Git Commands Reference

Useful commands for research:

```bash
# Find all target-related commits
git log --all --oneline -- "src/main/target/"

# Search commit messages
git log --all --grep="flash" --grep="size" --all-match
git log --all --grep="target" --grep="fix"

# See what changed in a specific commit
git show <commit-hash>

# Blame a file to see who changed what
git blame src/main/target/MATEKF722/target.h

# Find when a line was added
git log -S "some text" -- path/to/file

# See file at specific commit
git show commit:path/to/file
```

## Related

- **Current Issue:** AIKONF7 flash size problem (fix-aikonf7-flash-size project)
- **Assignment:** `claude/manager/email/sent/2026-01-12-1530-task-create-target-developer-agent.md`
