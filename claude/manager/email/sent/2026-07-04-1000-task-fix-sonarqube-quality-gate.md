# Task Assignment: Fix SonarQube Quality Gate Failure on PR #2671

**Date:** 2026-07-04 10:00
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-configurator-tab
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 2-4 hours

## Task

PR iNavFlight/inav-configurator#2671 is failing its SonarQube Cloud quality gate (Reliability Rating C, required ≥ A). Fix the blocking issues before taking the PR out of draft; address the rest as cleanup where reasonable.

## Background

CI builds are all green (Linux/Mac/Windows) — this is purely a SonarQube static-analysis failure, not a functional break. Full findings pulled from SonarCloud below.

## What to Do

### Blocking (required to pass the quality gate) — 3 BUG-severity issues in `tabs/dronecan.html`:
1. Line 12 — input field missing an associated `<label>`
2. Line 21 — input field missing an associated `<label>`
3. Line 58 — `<table>` missing `<th>` header row

### Should fix — CRITICAL complexity violations in `tabs/dronecan.js`:
4. Line 39 — function cognitive complexity 23 (max allowed 15) — refactor to reduce
5. Line 325 — function cognitive complexity 32 (max allowed 15) — refactor to reduce
6. Lines 308, 320, 328, 350, 355, 368, 377, 403 — functions nested more than 4 levels deep — flatten

### Worth cleaning up — MAJOR issues in `tabs/dronecan.js`:
7. Lines 223, 230, 282, 380 — nested ternaries, extract to independent statements
8. Lines 301, 313 — reassigning `btn` parameter/variable, avoid
9. Lines 78, 79, 252, 305, 317, 336 (+ test file) — prefer optional chaining (`?.`) over manual null checks

### Also flagged (lower priority, your call whether in scope for this PR):
- `js/msp/MSPHelper.js:1660` — function doesn't consistently return the same type (MAJOR)
- `src/css/tabs/dronecan.css` lines 70, 79, 104 — text/background contrast fails WCAG minimum (MAJOR)
- MINOR style items in `tabs/dronecan.js` (lines 13, 46, 177, 190, 326, 335, 338, 345, 364, 365, 397): `.replace()` → `.replaceAll()`, negated conditions, `Number.parseInt`/`Number.isNaN`/`Number.parseFloat` over global equivalents
- MINOR items in `test_dronecan_async_result.mjs`: `String.fromCodePoint()` preference, redundant block (line 329), zero-fraction numbers (264, 269)

## Success Criteria

- [ ] SonarQube quality gate passes (Reliability Rating ≥ A)
- [ ] All 3 BUG-severity accessibility issues in dronecan.html resolved
- [ ] The two CRITICAL-complexity functions refactored under the complexity-15 threshold
- [ ] Full build matrix still clean after changes
- [ ] Re-push and confirm SonarCloud re-scan passes before requesting review / taking PR out of draft

## Project Directory

`claude/projects/backburner/feature-dronecan-configurator-tab/`

---
**Manager**
