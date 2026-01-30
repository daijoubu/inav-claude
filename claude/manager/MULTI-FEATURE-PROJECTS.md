# Multi-Feature Project Management Guide

**For:** Development Manager
**Purpose:** Standard approach for tracking projects with multiple sub-features
**Date:** 2026-01-26

---

## When to Use Multi-Feature Structure

Use this approach when a project consists of **3 or more related features** that:
- Share a common goal or user story
- Can be implemented incrementally
- Are independently testable
- May be completed at different times

**Examples:**
- Debugging tools with multiple features (highlighting, sync status, variable display)
- Major UI overhaul with multiple components
- Feature set requiring phased rollout

---

## Directory Structure

```
claude/projects/active/<project-name>/
├── summary.md                    # Parent project overview
├── todo.md                       # Parent-level tracking (optional)
├── feature-1-<name>/
│   ├── summary.md               # Feature-specific details
│   └── todo.md                  # Feature-specific tasks
├── feature-2-<name>/
│   ├── summary.md
│   └── todo.md (optional)
└── feature-3-<name>/
    └── summary.md
```

**Naming Convention:**
- Parent: `<project-name>`
- Sub-features: `feature-N-<descriptive-name>`

---

## INDEX.md Format (Option 3: Hybrid)

Use single entry with inline sub-feature tracking:

```markdown
### 🚧 project-name (1/3 complete)

**Status:** IN PROGRESS | **Type:** Feature Implementation | **Priority:** MEDIUM
**Created:** YYYY-MM-DD | **Assignee:** Developer | **Assignment:** ✉️ Assigned

Brief description of the overall project goal.

**Sub-features:**
- ✅ Feature 1: Name (Xh) - COMPLETED (brief description)
- 🚧 Feature 2: Name (Yh) - IN PROGRESS (brief description)
- 📋 Feature 3: Name (Zh) - TODO (brief description)

**Directory:** `active/project-name/` (3 sub-feature directories)
**Repository:** repo-name
**Total Effort:** X-Y hours across all features
```

**Status Icons:**
- 🚧 = IN PROGRESS
- 📋 = TODO
- ✅ = COMPLETED

**Progress Counter:** `(N/Total complete)` in project title

---

## Parent summary.md Format

```markdown
# Project: <Name>

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM
**Type:** Feature Implementation (N features)
**Created:** YYYY-MM-DD
**Updated:** YYYY-MM-DD
**Total Estimated Effort:** X-Y hours (N features)

## Overview

High-level description of what this multi-feature project accomplishes.

## Sub-Features

### ✅ Feature 1: <Name> (Xh) - COMPLETED (YYYY-MM-DD)
Brief description. Key achievement.
**Directory:** `feature-1-<name>/`
**PR:** #XXXXX

### 🚧 Feature 2: <Name> (Yh) - IN PROGRESS
Brief description. Current status.
**Directory:** `feature-2-<name>/`

### 📋 Feature 3: <Name> (Zh) - TODO
Brief description.
**Directory:** `feature-3-<name>/`

## Overall Goals

- Goal 1
- Goal 2

## Success Criteria

- [ ] All sub-features complete
- [ ] Integration tested
- [ ] Documentation updated
- [ ] PR(s) merged

## Related

- **Assignment:** `manager/email/sent/...`
- **Repository:** repo-name
- **Base Branch:** branch-name
```

---

## Sub-Feature summary.md Format

```markdown
# Feature N: <Name>

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature Implementation
**Created:** YYYY-MM-DD
**Estimated Effort:** X-Y hours
**Parent Project:** project-name

## Overview

Specific description of this feature.

## Technical Approach

How this feature will be implemented.

## User Experience

What the user sees and how they interact with it.

## Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies

**Requires:**
- Feature 1 complete (if dependent)

**No Dependencies On:**
- Feature 3 (if independent)

## Integration with Other Features

How this feature works with other sub-features.

## Related

- **Parent Project:** `project-name`
- **Other Features:** Feature 1, Feature 3

---

**Last Updated:** YYYY-MM-DD
```

---

## Workflow

### Creating a Multi-Feature Project

1. **Create parent directory:**
   ```bash
   mkdir -p claude/projects/active/<project-name>
   ```

2. **Create parent files:**
   - `summary.md` - Overall project description
   - `todo.md` - Parent-level tracking (optional)

3. **Create sub-feature directories:**
   ```bash
   mkdir -p claude/projects/active/<project-name>/feature-1-<name>
   mkdir -p claude/projects/active/<project-name>/feature-2-<name>
   mkdir -p claude/projects/active/<project-name>/feature-3-<name>
   ```

4. **Create sub-feature files:**
   - Each gets `summary.md`
   - Optionally `todo.md` for complex features

5. **Add to INDEX.md:**
   - Single entry using hybrid format
   - List all sub-features with status icons
   - Show progress counter: `(0/N complete)`

### Updating Progress

**When a sub-feature completes:**

1. **Update sub-feature status:**
   ```markdown
   ### ✅ Feature 1: Name (Xh) - COMPLETED (YYYY-MM-DD)
   ```

2. **Update parent summary.md:**
   - Change feature status to ✅
   - Add completion date
   - Add PR link if applicable

3. **Update INDEX.md:**
   - Change icon: 🚧/📋 → ✅
   - Update progress counter: `(0/3 complete)` → `(1/3 complete)`
   - Add completion note to feature line

4. **Archive completion report:**
   - Move developer's completion report to inbox-archive

### Completing the Entire Project

**When all sub-features are complete:**

1. **Update parent summary.md:**
   - Change status to ✅ COMPLETED
   - Add completion date
   - Add final PR links

2. **Move to completed:**
   ```bash
   mv claude/projects/active/<project-name> claude/projects/completed/
   ```

3. **Update INDEX.md:**
   - Remove from active section
   - Add to completed/INDEX.md with summary

4. **Update completed/INDEX.md:**
   ```markdown
   ### ✅ project-name

   **Status:** COMPLETED (YYYY-MM-DD)
   **Type:** Feature Implementation (3 features)
   **Priority:** MEDIUM
   **Created:** YYYY-MM-DD
   **Completed:** YYYY-MM-DD
   **Total Effort:** X hours
   **Assignee:** Developer
   **PR:** #XXXXX

   Brief description. Three features: Feature 1 (PR #XXX), Feature 2 (PR #YYY), Feature 3 (PR #ZZZ).
   ```

---

## Task Assignment Strategy

**Option A: Assign all features upfront**
- Send single email describing all features
- Developer works through sequentially
- Pro: Clear scope from start
- Con: Less flexibility

**Option B: Assign features incrementally**
- Assign Feature 1 → complete → assign Feature 2 → etc.
- Pro: Can adjust based on learnings
- Con: More coordination overhead

**Recommended:** **Option B** - Assign features incrementally for complex projects, **Option A** for straightforward sequential work.

---

## Communication

### Task Assignment Template

```markdown
# Task Assignment: Feature N - <Name>

**Date:** YYYY-MM-DD
**From:** Manager
**To:** Developer
**Project:** <project-name> (Feature N of M)
**Priority:** MEDIUM
**Estimated Effort:** X-Y hours

## Task

Implement Feature N of the <project-name> project: **<Feature Name>**

## Context

[Explain where this fits in the overall project]

This is part of a M-feature project:
- ✅ Feature 1: Name - Complete
- 🚧 Feature N: Name - START HERE
- 📋 Feature N+1: Name - TODO

## What to Implement

[Detailed description]

## Success Criteria

[Criteria]

## Project Structure

**Parent project:** `claude/projects/active/<project-name>/`
**This feature:** `claude/projects/active/<project-name>/feature-N-<name>/`

[Rest of standard task assignment]
```

---

## Best Practices

### Do's

✅ **Keep features independent** - Each should be testable standalone
✅ **Clear dependencies** - Document which features depend on others
✅ **Incremental value** - Each feature should provide user value
✅ **Update progress regularly** - Keep INDEX.md counter current
✅ **Comprehensive parent summary** - Good overview helps coordination

### Don'ts

❌ **Don't create too many sub-features** - 3-5 is ideal, 7+ gets unwieldy
❌ **Don't make features too small** - Merge trivial features (<1h)
❌ **Don't mix unrelated work** - Keep project scope focused
❌ **Don't forget progress updates** - Update counter after each completion
❌ **Don't lose track of PRs** - Link PRs in both parent and sub-feature summaries

---

## Examples

### Good Multi-Feature Projects

- **Debugging Tools** (3 features: highlighting, sync status, variable display)
- **SITL WASM Integration** (6 phases: compilation, runtime, MSP, etc.)
- **Major UI Redesign** (4 features: navigation, layouts, themes, accessibility)

### Better as Single Projects

- **Bug fix with testing** (1 main task, testing is part of completion)
- **Simple feature** (even with 2-3 steps, keep as one project)
- **Quick investigation** (research + report = single deliverable)

---

## Summary

Multi-feature projects use:
- **Directory structure:** Parent + sub-feature directories
- **INDEX.md format:** Single entry with inline sub-feature list (Option 3: Hybrid)
- **Progress tracking:** Counter `(N/Total complete)` in title
- **Status icons:** 🚧 IN PROGRESS, 📋 TODO, ✅ COMPLETED
- **Incremental completion:** Update after each feature, move to completed/ when all done

This approach provides clear visibility while keeping INDEX.md manageable.

---

**Last Updated:** 2026-01-26
