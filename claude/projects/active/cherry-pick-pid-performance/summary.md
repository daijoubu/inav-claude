# Project: Cherry-pick PID Performance Improvements

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Performance / Cherry-pick
**Created:** 2026-02-18
**Estimated Effort:** 0.5–1 hour
**Assignee:** Developer

## Overview

Cherry-pick two performance improvement commits to a new branch off `maintenance-9.x` and open a PR to `inavflight/inav`.

## Commits (apply in order)

1. `35b9eb5c9ade53d37b39b6d966b710bdde0215ad`
   - **Message:** `pid/filter: add FAST_CODE to pidController callees`
   - **What it does:** Adds `FAST_CODE` attribute to functions called from `pidController()` so they are placed in ITCM (fast RAM) rather than flash, avoiding trampoline jumps from ITCM to flash on STM32 targets.
   - **Files:** `filter.c`, `maths.c`, `fc_core.c`, `pid.c`, `smith_predictor.c`

2. `2b933be0820b0f4b416dda4b0959f9a76e895129`
   - **Message:** `fc/pid: avoid recomputing values that change at lower rates`
   - **What it does:** Caches RC command computations and `pidSumLimit` so they are only recalculated when new RX data arrives (~50 Hz) rather than every PID loop iteration (~1000 Hz). Also gates `failsafeUpdateRcCommandValues()` behind the new-data check.
   - **Files:** `fc_core.c`, `pid.c`

## Target

- **Repository:** `inavflight/inav` (upstream)
- **Base Branch:** `maintenance-9.x`
- **No specific reviewer requested**

## Success Criteria

- [ ] New branch created from `maintenance-9.x`
- [ ] Both commits cherry-picked cleanly, in order
- [ ] Clean build
- [ ] PR opened targeting `inavflight/inav` `maintenance-9.x`
- [ ] Completion report sent to manager with PR link

## Related

- **Assignment:** `manager/email/sent/2026-02-18-HHMM-task-cherry-pick-pid-performance.md`
