# Task Assignment: Fix Cortex-M7 SD Card Write Ordering

**Date:** 2026-05-16 14:15
**From:** Manager
**To:** Developer
**Project:** fix-cortex-m7-sd-write-ordering
**Priority:** MEDIUM
**Estimated Effort:** 1-2 hours

## Task

Implement the two-line fix identified in your Cortex-M7 SD card write ordering investigation. See your investigation report in `claude/developer/investigations/cortex-m7-sd-write-ordering-2026-05-15.md` for details.

Two defects to fix in `src/main/drivers/sdcard/sdmmc_sdio_hal.c`:
1. Add `static volatile` to `sdReadParameters`
2. Reorder `HAL_SD_RxCpltCallback`: move `RXCplt = 1` after `SCB_InvalidateDCache_by_Addr()` with `__DMB()` barrier

## Background

Investigation completed on 2026-05-15 found two MEDIUM-severity memory-ordering defects. Both are safe on current single-core targets but would be race conditions on multi-core. Manager decision: implement on maintenance-10.x only; no backport to 9.x needed. Low regression risk — same DMB barrier pattern as CAN TX ISR work.

## What to Do

1. Check out `fix/cortex-m7-sd-write-ordering` branch (already exists from investigation)
2. Implement the two-line fix
3. Build for affected F7 targets (MATEKF765SE etc.)
4. Create PR targeting `maintenance-10.x`
5. Reference GitHub issue #11562 in PR description

## Success Criteria

- [ ] Both fixes applied to `sdmmc_sdio_hal.c`
- [ ] Builds clean for F7 targets
- [ ] PR created, references #11562

## Project Directory

`claude/projects/active/fix-cortex-m7-sd-write-ordering/`

---
**Manager**
