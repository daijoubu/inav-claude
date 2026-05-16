# Project: Fix Cortex-M7 SD Card Write Ordering

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Bug Fix
**Created:** 2026-05-16
**Estimated Effort:** 1-2 hours

## Overview

Apply a two-line fix to `src/main/drivers/sdcard/sdmmc_sdio_hal.c` addressing two MEDIUM-severity memory-ordering defects found during the Cortex-M7 SD card investigation. Same store-release pattern as the CAN TX ISR work.

## Problem

Investigation (completed project `investigate-cortex-m7-sd-write-ordering`) found two defects:

1. **`sdReadParameters` missing `volatile`** — struct written in main context, read in ISR context without volatile qualifier. Compiler could cache fields; cache invalidation could use stale buffer address.
2. **`RXCplt` flag cleared before cache invalidation** — main loop signals "done" before `SCB_InvalidateDCache_by_Addr()` completes. Safe on single-core due to ISR atomicity; real race on multi-core.

## Solution

Two-line fix on `fix/cortex-m7-sd-write-ordering` branch:
1. Add `static volatile` to `sdReadParameters`
2. Reorder `HAL_SD_RxCpltCallback` with `__DMB()` between cache invalidation and flag store

## Success Criteria

- [ ] Two-line fix implemented on maintenance-10.x
- [ ] Builds clean for affected F7 targets
- [ ] PR references issue #11562

## Related

- **Investigation:** `completed/investigate-cortex-m7-sd-write-ordering/`
- **Issue:** [#11562](https://github.com/iNavFlight/inav/issues/11562)
- **Prior art:** `feature-stm32f7-can-tx-isr` (same DMB barrier pattern)
- **Repository:** inav (firmware)
- **Branch:** `maintenance-10.x`
