# Project: Cortex-M7 SD Card Write Ordering Investigation

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-05-15
**Estimated Effort:** 2-4 hours

## Overview

Systematic audit of the STM32F7 SD card driver for Cortex-M7 write-buffer and memory-ordering hazards — the same class of issues found and fixed during the CAN TX ISR migration (DMB barriers, volatile qualifiers, DMA cache coherency).

## Problem

The Cortex-M7 has a large write buffer and an out-of-order capable L1 cache. Without explicit DMB/DSB barriers and volatile qualifiers, memory accesses can appear reordered between execution contexts (ISR vs main loop). During the STM32F7 CAN TX ISR migration, we added DMB barriers to the SPSC queue and volatile qualifiers to RxBuffer index declarations to address this.

The SD card driver (STM32F7 HAL-based) uses DMA and ISR callbacks — the same architectural hazards may be present. In addition, the Cortex-M7 D-cache can cause DMA to read stale data if cache lines are not invalidated/cleaned before/after DMA transfers (AN4748).

## Suggested Scope

1. Audit SD card driver ISR/DMA callback paths for missing `volatile` qualifiers and DMB/DSB barriers
2. Check DMA descriptor setup for cache coherency (D-cache invalidation/clean before/after DMA transfers)
3. Review any SPSC or shared-data structures between SD ISR and main task
4. Compare against STM32 AN4748 (cache management on STM32F7/H7)

## Why Now

The CAN TX work confirmed these hazards are real and architectural to Cortex-M7 — not theoretical. Proactive review before HAL v1.3.3 ships prevents field stability issues.

## Success Criteria

- [ ] All ISR/DMA callback paths audited for missing `volatile` and DMB/DSB
- [ ] DMA descriptor cache coherency reviewed against AN4748
- [ ] Any SPSC/shared-data structures between SD ISR and main task identified and checked
- [ ] Findings documented (no issues found OR list of fixes needed)
- [ ] If fixes needed: separate fix PR created or appended to existing HAL update PR

## Related

- **Requested by:** Developer — `manager/email/inbox/2026-05-14-1045-task-cortex-m7-sdcard-investigation.md`
- **Prior work:** `feature-stm32f7-can-tx-isr` (DMB barrier pattern established)
- **Reference:** STM32 AN4748 — Cache management on STM32F7/H7
- **Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
