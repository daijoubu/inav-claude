# Task Assignment: Cortex-M7 SD Card Write Ordering Investigation

**Date:** 2026-05-15 12:15
**From:** Manager
**To:** Developer
**Project:** investigate-cortex-m7-sd-write-ordering
**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours

## Task

Systematically audit the STM32F7 SD card driver for Cortex-M7 write-buffer and memory-ordering hazards — the same class of issues found and fixed during the CAN TX ISR migration.

## Background

During `feature-stm32f7-can-tx-isr`, we confirmed that the Cortex-M7's large write buffer and out-of-order L1 cache require explicit DMB/DSB barriers and volatile qualifiers to prevent memory access reordering between ISR and main-loop contexts. The SD card driver (STM32F7 HAL-based) uses DMA and ISR callbacks — the same architectural hazards may be present. Additionally, the Cortex-M7 D-cache can cause DMA to read stale data if cache lines aren't invalidated/cleaned before/after transfers (see STM32 AN4748).

This is a proactive review ahead of HAL v1.3.3 shipping.

## What to Do

1. **Audit ISR/DMA callback paths** — check for missing `volatile` qualifiers and DMB/DSB barriers in the SD card driver
2. **Check DMA descriptor setup** — verify D-cache coherency (cache line invalidation/clean before and after DMA transfers), compare against STM32 AN4748
3. **Review shared data structures** — identify any SPSC or shared-data structures between SD ISR and main task; verify they are correctly guarded
4. **Document findings** — write an investigation report in `claude/developer/investigations/`. If issues found, list them with severity. If clean, document as a clean audit.
5. **Fix if needed** — implement any fixes and create a PR, or append to the existing HAL update PR

## Success Criteria

- [ ] All ISR/DMA callback paths audited for missing `volatile` and DMB/DSB
- [ ] DMA descriptor cache coherency reviewed against AN4748
- [ ] Shared data structures between SD ISR and main task identified and checked
- [ ] Investigation report written in `claude/developer/investigations/`
- [ ] If fixes needed: PR created or appended to existing HAL update PR

## Project Directory

`claude/projects/active/investigate-cortex-m7-sd-write-ordering/`

## Reference

- Prior art: `feature-stm32f7-can-tx-isr` — DMB barrier pattern established there
- STM32 AN4748: Cache management on STM32F7/H7
- Base branch: `maintenance-10.x`

---
**Manager**
