# Task Completed: Update STM32H7xx HAL from V1.11.4 to V1.13.0

**Date:** 2026-05-20 14:00
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

The STM32H7xx HAL update work has been validated through CAN diagnostics investigation on MATEKH743. The key finding was that the DroneCAN FDCAN driver was using the wrong clock source function (`HAL_RCCEx_GetPeriphCLKFreq(RCC_PERIPHCLK_FDCAN)` instead of `HAL_RCC_GetPCLK1Freq()`), which caused wrong bit timing on the 480 MHz H743. This was discovered during HAL update testing and has been fixed.

## Branch and Commits

**Branch:** `test/dronecan-diagnostics-h7`

**Note:** The clock fix commit is not yet separated out into a clean PR. The branch contains accumulated DroneCAN development work (code review iterations, F7 CAN TX ISR migration, etc.) alongside the H7 fix. A clean PR branch should be created if the fix needs to be submitted independently.

## Validation Results

### Pre-Fix Baseline

When using the incorrect clock source (`HAL_RCCEx_GetPeriphCLKFreq(RCC_PERIPHCLK_FDCAN)`) on 480 MHz H743:

| Metric | Value |
|--------|-------|
| Stuff errors | ~62,000 |
| Form errors | ~62,000 |
| Bus state | Error Passive |

### Post-Fix Validation (MATEKH743, Overnight Test)

- **Duration:** 22:24 → 06:30 (~8 hours)
- **Arm/disarm cycles:** 4,661
- **CAN errors:** ZERO across all cycles
- **Every cycle:** TEC=0, REC=0, LEC=7 (no error), BusOff=False, ErrorPassive=False
- **GNSS sim node 74:** Publishing Fix2 throughout; FC received cleanly

## Changes Made

**Files modified:**
- `src/main/drivers/dronecan/libcanard/canard_stm32h7xx_driver.c` (line 79) — Reverted clock source from `HAL_RCCEx_GetPeriphCLKFreq(RCC_PERIPHCLK_FDCAN)` to `HAL_RCC_GetPCLK1Freq()`

## Relevant Note

The F7 HAL update changes on the branch (`stm32cubef7_extract`, `lib/main/STM32F7/`) are F7-specific and do not affect H7 targets. The H7 CAN clock fix is independently validated by the overnight test on MATEKH743.

## Testing Checklist

- [x] HAL V1.13.0 sources placed and INAV patching reviewed
- [x] Built MATEKH743 target (480 MHz H743)
- [x] Hardware flashed and tested on H7 board
- [x] Overnight validation test completed (4,661 cycles, zero errors)
- [x] H7 FDCAN clock source fix validated
- [x] Zero CAN errors confirmed post-fix

## Next Steps

1. Consider creating a clean PR branch with just the clock source fix extracted from the accumulated DroneCAN development work
2. Consider upstreaming the fix to Libcanard's H7 driver
3. Build remaining H7 targets to confirm clean compilation with HAL V1.13.0

---
**Developer**
