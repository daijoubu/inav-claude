# Backburner Projects Index

Projects paused internally (not blocked by external factors) - will resume when priorities shift.

**Last Updated:** 2026-02-12
**Total Backburner:** 5

> **Active projects:** See [../INDEX.md](../INDEX.md)
> **Blocked projects:** See [../blocked/INDEX.md](../blocked/INDEX.md)
> **Completed projects:** See [../completed/INDEX.md](../completed/INDEX.md)

---

## Backburner Status

⏸️ **BACKBURNER** - Project paused by internal decision:
- Lower priority relative to active work
- Can resume when capacity available
- Not blocked by external factors
- Still valuable, just deprioritized

---

## Backburner Projects

### ⏸️ settings-simplification

**Status:** BACKBURNER | **Type:** Feature / UX Improvement | **Priority:** MEDIUM
**Created:** 2026-01-07

Reduce INAV configuration complexity by ~70% through automatic determination and consolidation of related settings into single controls.

**Directory:** `backburner/settings-simplification/`
**Reason Paused:** Large scope, lower priority than active bug fixes and features

---

### ⏸️ remove-transpiler-backward-compatibility

**Status:** BACKBURNER | **Type:** Refactoring | **Priority:** LOW
**Created:** 2025-12-28

Remove backward compatibility support from the transpiler namespace refactoring, requiring users to update configuration syntax.

**Directory:** `backburner/remove-transpiler-backward-compatibility/`
**Reason Paused:** Breaking change, deprioritized until compatibility period ends

---

### ⏸️ verify-gps-fix-refactor

**Status:** BACKBURNER | **Type:** Code Review / Refactoring | **Priority:** MEDIUM
**Created:** 2025-11-29

The GPS recovery fix (PR #11144) was merged, but collaborator (breadoven) raised valid questions about the refactoring. Needs verification and possible follow-up work.

**Directory:** `backburner/verify-gps-fix-refactor/`
**Reason Paused:** PR merged, follow-up work can wait; monitor for issues from users

---

### 📋 feature-add-function-syntax-support

**Status:** TODO | **Type:** Feature Enhancement | **Priority:** MEDIUM-HIGH
**Created:** 2025-11-24

Add support for traditional JavaScript function syntax to the transpiler, allowing users to write code in standard JS function declaration style.

**Directory:** `backburner/feature-add-function-syntax-support/`
**Reason Paused:** Feature enhancement, lower priority than bug fixes

---

### 📋 feature-auto-alignment-tool

**Status:** TODO (Research Complete) | **Type:** Feature Enhancement | **Priority:** MEDIUM
**Created:** 2025-12-12

Wizard-style tool that automatically detects and sets flight controller and compass alignment by measuring sensor responses to known rotations and detecting orientation patterns.

**Directory:** `backburner/feature-auto-alignment-tool/`
**Status Note:** Extensive research completed (7 analysis documents), implementation pending
**Reason Paused:** Large feature scope, deferred until resources available

---

## Summary

- **Total Backburner:** 5
- **In Pause:** 3 projects (⏸️ actively paused)
- **TODO:** 2 projects (📋 defined but not started)
- **By Priority:**
  - MEDIUM-HIGH: 1 (feature-add-function-syntax-support)
  - MEDIUM: 3 (settings-simplification, feature-auto-alignment-tool, verify-gps-fix-refactor)
  - LOW: 1 (remove-transpiler-backward-compatibility)
