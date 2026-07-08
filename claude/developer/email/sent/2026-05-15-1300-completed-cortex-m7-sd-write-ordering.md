# Task Completed: Cortex-M7 SD Card Write Ordering Investigation

**Date:** 2026-05-15 13:00
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Audited `src/main/drivers/sdcard/sdmmc_sdio_hal.c` for Cortex-M7 memory-ordering and D-cache coherency hazards. Found two MEDIUM defects in the DMA read path. Both are safe on all current single-core INAV targets due to ISR atomicity, but would become genuine race conditions on any future multi-core target (e.g. RP2350). No code changes made per task scope (investigation only). Issue posted to iNavFlight/inav for upstream tracking.

## Findings

**FINDING 1 (MEDIUM):** `sdReadParameters` missing `volatile` — struct written in main context, read in ISR context without volatile qualifier. Compiler could cache fields in registers; cache invalidation could use stale buffer address. Also has unnecessary external linkage (should be static).

**FINDING 2 (MEDIUM):** `RXCplt` completion flag cleared before `SCB_InvalidateDCache_by_Addr()` in `HAL_SD_RxCpltCallback`. Semantically wrong: main loop signals "done" before cache is coherent. Safe on single-core due to ISR atomicity and implicit DSB inside CMSIS cache functions; real race on multi-core.

**FINDING 3 (LOW):** No pre-read buffer invalidation before DMA start (AN4748 deviation). Low risk in INAV's usage pattern — documented only.

**FINDING 4 (INFO):** Write path (TXCplt/SCB_CleanDCache ordering) is correct.

**FINDING 5 (INFO):** RXCplt/TXCplt already correctly declared volatile.

## Scope Notes

- Affects all 20 `USE_SDCARD_SDIO` targets (MATEKF765, MATEKH743, KAKUTEH7WING, etc.)
- Same code present verbatim in Betaflight (`src/platform/STM32/sdio_h7xx.c`)
- Does not affect MSC mode (bypasses this driver entirely)
- Does not affect the write path — read path only
- asyncfatfs actively exercises the read path (FAT sector reads at mount and during logging)

## Artifacts

- Investigation report: `claude/developer/investigations/cortex-m7-sd-write-ordering-2026-05-15.md`
- GitHub issue: https://github.com/iNavFlight/inav/issues/11562
- Fix branch created and reverted per task scope: `fix/cortex-m7-sd-write-ordering` (no PR — awaiting decision on whether to implement)

## Proposed Fix (ready to implement on request)

Two-line fix: add `static volatile` to `sdReadParameters`, reorder `HAL_SD_RxCpltCallback` with `__DMB()` between cache invalidation and flag store. Same store-release pattern as CAN TX ISR work. Low regression risk.

## Next Steps

Decision needed: implement fix against maintenance-10.x (and optionally backport to 9.x)?

---
**Developer**
