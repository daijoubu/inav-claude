# Task Completed: Fix STM32F7 HAL Macro Redefinition Warnings

**Date:** 2026-04-20 20:00
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Fixed both macro redefinition warnings on branch `feature/stm32f7-hal-v1.3.3-update`. MATEKF765SE builds cleanly with zero warnings. The HAL upgrade is ready for the testing phase.

## Branch and Commits

**Branch:** `feature/stm32f7-hal-v1.3.3-update`
**Commits:**
- `327be5bbf` - fix: eliminate STM32F7 HAL macro redefinition warnings

## Changes Made

**Files modified:**
- `cmake/cortex-m7.cmake` — Changed `__FPU_PRESENT=1` → `__FPU_PRESENT=1U`. GCC treats `1` and `1U` as different token strings and warns on redefinition against the device header's `1U`. The cmake flag must be kept as CMSIS DSP requires it.
- `cmake/cortex-m4f.cmake` — Same fix applied for consistency.
- `src/main/target/stm32f7xx_hal_conf.h` — Corrected misspelled `ART_ACCLERATOR_ENABLE` → `ART_ACCELERATOR_ENABLE` to eliminate conflict with legacy alias added in HAL v1.3.3 (`stm32_hal_legacy.h:4402`).

## Note: Remote was ahead — rebased cleanly

The remote branch had two commits ahead when I fetched (CAN driver port to HAL v1.3.x API). My fix rebased cleanly on top of those. The CAN driver issue I flagged in my earlier report has already been resolved upstream.

## Testing

- [x] Clean MATEKF765SE build — SUCCESS
- [x] Zero `__FPU_PRESENT` redefinition warnings
- [x] Zero `ART_ACCLERATOR_ENABLE` redefinition warnings
- [x] No regressions — ITCM/DTCM/SRAM usage normal

## Ready for Testing Phase

The HAL upgrade branch is now in a buildable, warning-free state. All known blockers resolved:
- ✅ Macro redefinition warnings eliminated
- ✅ CAN driver updated for HAL v1.3.x API (done upstream)
- ✅ Clean MATEKF765SE firmware produced

Ready to hand off to testing for hardware validation.

---
**Developer**
