# Projects Directory

Central project registry for tracking all INAV-related projects.

## Quick Links

| Link | Description |
|------|-------------|
| **[INDEX.md](INDEX.md)** | Active projects (TODO, IN PROGRESS, BACKBURNER) |
| **[completed/INDEX.md](completed/INDEX.md)** | Completed and cancelled projects |

## Directory Structure

```
projects/
├── INDEX.md                 # Active projects index (keep concise!)
├── README.md                # This file
│
├── active/                  # Projects being worked on
│   └── <project-name>/
│       ├── summary.md       # Full details
│       └── todo.md          # Task tracking
│
├── backburner/              # Paused projects (will resume)
│   └── <project-name>/
│
└── completed/               # Finished projects
    ├── INDEX.md             # Completed projects index
    └── <project-name>/      # Archived project directories
```

## Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  CREATE                                                     │
│  ├─ Create active/<project-name>/ with summary.md, todo.md  │
│  └─ Add entry to INDEX.md                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  WORK                                                       │
│  ├─ Update todo.md as tasks complete                        │
│  └─ Status in INDEX.md: 📋 TODO → 🚧 IN PROGRESS            │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌──────────────────────────┐  ┌──────────────────────────────┐
│  PAUSE (optional)        │  │  COMPLETE                    │
│  ├─ mv to backburner/    │  │  ├─ mv to completed/         │
│  └─ Status: ⏸️ BACKBURNER │  │  ├─ Remove from INDEX.md     │
└──────────────────────────┘  │  └─ Add to completed/INDEX.md│
              │               └──────────────────────────────┘
              ▼
┌──────────────────────────┐
│  RESUME                  │
│  ├─ mv to active/        │
│  └─ Status: 🚧 IN PROGRESS│
└──────────────────────────┘
```

## Skills

Use these skills for common operations:

| Skill | Description |
|-------|-------------|
| `/start-task` | Create new project with directory and assignment email |
| `/finish-task` | Mark project complete, move to completed/, update indexes |

## Key Rules

### INDEX.md is Navigation Only

Each entry should be 10-15 lines max:
- Status, type, priority, dates
- One-sentence summary
- Directory location
- Links (issue, PR, email)

**Details go in the project's summary.md, not INDEX.md.**

### Before Condensing INDEX Entries

1. READ the project's summary.md
2. VERIFY all details exist there
3. If missing, ADD to summary.md first
4. THEN condense the INDEX entry

### Single Source of Truth

- Project details → `<project-name>/summary.md`
- Task tracking → `<project-name>/todo.md`
- INDEX.md → Navigation and status only

---

## Detailed Reference

### Creating a New Project

1. **Create project directory:**
   ```bash
   mkdir -p claude/projects/active/<project-name>
   ```

2. **Create summary.md** using template below

3. **Create todo.md** using template below

4. **Add to INDEX.md** (concise entry only)

5. **Send assignment email** (if assigning to developer)

### INDEX.md Entry Format

```markdown
### 📋 project-name

**Status:** TODO | **Type:** Bug Fix | **Priority:** MEDIUM
**Created:** 2025-12-29 | **Assignee:** Developer

One-sentence summary of what this project accomplishes.

**Directory:** `active/project-name/`
**Issue:** [#12345](url) | **Assignment:** `manager/email/sent/...`

---
```

### summary.md Template

```markdown
# Project: <Name>

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Bug Fix | Feature | Refactor | Investigation
**Created:** YYYY-MM-DD
**Estimated Effort:** X-Y hours

## Overview

<What this project accomplishes in 2-3 sentences>

## Problem

<What issue this solves>

## Solution

<High-level approach>

## Implementation

<Technical details, phases, files to modify>

## Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Related

- **Issue:** #XXXXX
- **PR:** #XXXXX (when created)
- **Assignment:** `path/to/email`
```

### todo.md Template

```markdown
# Todo: <Project Name>

## Phase 1: <Name>

- [ ] Task 1
- [ ] Task 2

## Phase 2: <Name>

- [ ] Task 3
- [ ] Task 4

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created
- [ ] Completion report sent
```

### Completing a Project

1. **Update summary.md:**
   - Set status to ✅ COMPLETED
   - Add PR number and completion date

2. **Move directory:**
   ```bash
   mv claude/projects/active/<project>/ claude/projects/completed/
   ```

3. **Update INDEX.md:**
   - Remove the project entry
   - Update counts

4. **Update completed/INDEX.md:**
   - Add entry at top of current year section
   - Update total count

### Cancelling a Project

When abandoning a project (not just pausing):

1. **Update summary.md:**
   - Set status to ❌ CANCELLED
   - Add cancellation reason and date

2. **Move directory:**
   ```bash
   mv claude/projects/active/<project>/ claude/projects/completed/
   ```

3. **Update INDEX.md:**
   - Remove the project entry
   - Update counts

4. **Update completed/INDEX.md:**
   - Add entry with ❌ status:
   ```markdown
   ### ❌ project-name (2026-01-09)
   **Cancelled:** <brief reason>
   ```

**When to cancel vs backburner:**
- **Cancel:** Requirements changed, no longer needed, blocked permanently, superseded
- **Backburner:** Still valuable, lower priority, waiting on external dependency

### Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| 📋 | TODO | Defined, not started |
| 🚧 | IN PROGRESS | Actively being worked on |
| ⏸️ | BACKBURNER | Paused, will resume |
| ✅ | COMPLETED | Finished and merged |
| ❌ | CANCELLED | Abandoned |

### Priority Levels

| Priority | When to Use |
|----------|-------------|
| CRITICAL | Blocking issue, fix immediately |
| HIGH | Important, work on soon |
| MEDIUM-HIGH | Should do, good to complete |
| MEDIUM | Normal priority |
| LOW | Nice to have |

### Naming Conventions

Use kebab-case with descriptive prefixes:

- `feature-<description>` - New functionality
- `fix-<description>` - Bug fixes
- `refactor-<description>` - Code restructuring
- `investigate-<description>` - Research/analysis
- `reproduce-<description>` - Bug reproduction

---

## Not To Be Confused With

| Directory | Purpose |
|-----------|---------|
| `claude/projects/` | Persistent project tracking (this directory) |
| `claude/developer/workspace/` | Temporary working files (gitignored) |
| `claude/developer/investigations/` | Research and analysis reports |
| `claude/developer/reports/` | Completed analysis documents |
