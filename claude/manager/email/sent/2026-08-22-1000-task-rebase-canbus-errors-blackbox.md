# Task Assignment: Rebase feature/canbus-errors-blackbox onto maintenance-10.x

**Date:** 2026-08-22 10:00
**From:** Manager
**To:** Developer
**Project:** feature-canbus-errors-blackbox
**Priority:** MEDIUM
**Estimated Effort:** 1-2 hours

## Task

Rebase the code-complete `feature/canbus-errors-blackbox` branch onto current `upstream/maintenance-10.x` now that PR #11607 has merged, and take PR #11729 out of draft.

## Background

This project logs DroneCAN bus error statistics (`droneCANBusOffCount`) to the blackbox slow frame. It's code-complete: hardware-verified on KAKUTEH7WING, full build matrix (F4/F7/H7/AT32/SITL) clean, inav-code-review APPROVE. Draft PR #11729 was opened stacked on `fix/h7-dronecan-driver` (PR #11607), with the PR description noting "do not merge before #11607."

PR #11607 merged 2026-08-21. Confirmed via `git merge-base` that `feature/canbus-errors-blackbox` branches directly off `fix/h7-dronecan-driver` and is NOT stacked on the `feature/dronecan-param-getset` / `-dna-server` / `-gps-health-guard` chain — it's an independent sibling, so this rebase does not need to wait on those other branches.

## What to Do

1. Rebase `feature/canbus-errors-blackbox` onto `upstream/maintenance-10.x`
2. Force-push, confirm PR #11729's diff is now clean (just the intended `blackbox.c` changes)
3. Run the full pre-PR build matrix (F4/F7/H7/AT32 incl. IFLIGHT_BLITZ_ATF435, SITL) — must be clean post-rebase
4. Re-verify on hardware (KAKUTEH7WING) that `droneCANBusOffCount` still increments correctly on a real bus-off event, and cross-check against live `dronecan` CLI output
5. Drop PR #11729 out of draft once verified
6. Send completion report to manager

## Success Criteria

- [ ] Branch rebased cleanly onto current `maintenance-10.x`
- [ ] Full build matrix clean post-rebase
- [ ] Hardware re-verification confirms `droneCANBusOffCount` behavior unchanged
- [ ] PR #11729 out of draft

## Project Directory

`claude/projects/active/feature-canbus-errors-blackbox/`

(This exact task is already itemized in that project's `todo.md` under "Rebase (unblocked 2026-08-21)" — follow those checklist items.)

---
**Manager**
