# Task Completed: Fix STM32F7 HAL Macro Redefinition Warnings

**Date:** 2026-04-20 19:00
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Fixed both macro redefinition warnings that were appearing across all 528 STM32F7 compilation units on branch `feature/stm32f7-hal-v1.3.3-update`. Zero redefinition warnings remain in the MATEKF765SE build.

## Branch and Commits

**Branch:** `feature/stm32f7-hal-v1.3.3-update`
**Commits:**
- `38010872c` - fix: eliminate STM32F7 HAL macro redefinition warnings

## Changes Made

**Files modified:**
- `cmake/cortex-m7.cmake` - Removed redundant `-D__FPU_PRESENT=1`; CMSIS device headers already define this per spec
- `cmake/cortex-m4f.cmake` - Same fix (M4F had the same redundant flag)
- `src/main/target/stm32f7xx_hal_conf.h` - Corrected misspelled `ART_ACCLERATOR_ENABLE` → `ART_ACCELERATOR_ENABLE` to avoid conflict with legacy alias added in HAL v1.3.3

## Root Causes

1. **`__FPU_PRESENT`**: cmake was passing `-D__FPU_PRESENT=1` but CMSIS device headers (stm32f765xx.h:178 etc.) unconditionally define it. CMSIS spec says the device header owns this definition. Fix: remove the cmake flag.

2. **`ART_ACCLERATOR_ENABLE`**: HAL v1.3.3 added `stm32_hal_legacy.h:4402` which aliases the misspelled name to the correct spelling `ART_ACCELERATOR_ENABLE`. Our config file used the misspelled name too, causing the collision. Fix: use correct spelling in stm32f7xx_hal_conf.h so HAL finds it directly without the legacy alias.

## Testing

- [x] Clean MATEKF765SE build run — zero `__FPU_PRESENT` warnings
- [x] Zero `ART_ACCLERATOR_ENABLE` warnings
- [x] No new warnings introduced

## Note: Pre-existing Separate Issue

The MATEKF765SE build currently fails due to `canard_stm32f7xx_driver.c` using HAL v1.2.x CAN API types (`CanRxMsgTypeDef`, `HAL_CAN_Receive_IT`, etc.) that were removed in HAL v1.3.x. This is a separate pre-existing issue — the DroneCAN STM32F7 driver needs porting to the new HAL v1.3.x CAN API. This is NOT related to the macro redefinition fixes.

## Next Steps

The DroneCAN STM32F7 CAN driver port to HAL v1.3.x API is needed before this branch can ship.

---
**Developer**
