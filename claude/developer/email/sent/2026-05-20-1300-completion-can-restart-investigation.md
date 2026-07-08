# Task Completed: Investigate DroneCAN/CAN Bus Communication Failures on MATEKH743

**Date:** 2026-05-20 13:00
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Investigated and resolved root cause of FDCAN communication failures on STM32H7 (MATEKH743) after FC reboot. Root cause was an incorrect clock source function in `canard_stm32h7xx_driver.c` — the driver used `HAL_RCCEx_GetPeriphCLKFreq(RCC_PERIPHCLK_FDCAN)` instead of `HAL_RCC_GetPCLK1Freq()`. On 480 MHz H743, the wrong function returned an incorrect clock value, producing incorrect FDCAN bit timing that caused ~62k Stuff+Form errors and Error Passive state.

## Root Cause

- **Driver:** `src/main/drivers/dronecan/libcanard/canard_stm32h7xx_driver.c`
- **Line 79:** Clock source selected `HAL_RCCEx_GetPeriphCLKFreq(RCC_PERIPHCLK_FDCAN)`
- **Effect on 480 MHz H743:** Returns wrong clock value → incorrect FDCAN bit timing → massive CAN bus errors
- **Symptom:** ~62,000 Stuff+Form errors, TEC=216, REC=127, Error Passive state
- **Fix:** Reverted to `HAL_RCC_GetPCLK1Freq()` which returns the correct FDCAN peripheral clock

## Changes Made

**Files modified:**
- `src/main/drivers/dronecan/libcanard/canard_stm32h7xx_driver.c` — Clock source function reverted to `HAL_RCC_GetPCLK1Freq()` on line 79

## Testing

### Pre-Fix Baseline (Stock INAV 9.0-RC1)
| Metric | Value |
|--------|-------|
| Stuff errors | 61,970 |
| Form errors | 61,982 |
| TEC | 216 |
| REC | 127 |
| Bus state | Error Passive |

### Post-Fix Validation (MATEKH743, overnight)
- **Duration:** 22:24 → 06:30 (~8 hours)
- **Arm/disarm cycles:** 4,661
- **CAN errors:** ZERO across all cycles
- **Every cycle:** TEC=0, REC=0, LEC=7 (no error), BusOff=False, ErrorPassive=False
- **GNSS sim node 74:** Publishing Fix2 throughout; FC received cleanly

### Relevant Note

The F7 HAL update changes (`stm32cubef7_extract`, `lib/main/STM32F7/`) are F7-specific and do not affect H7 targets. The H7 CAN clock fix is independently validated by the overnight test on MATEKH743.

- [x] Root cause identified and documented
- [x] Fix implemented and compiled
- [x] Built MATEKH743 target
- [x] Hardware flashed by user
- [x] Overnight validation test completed successfully
- [x] Zero CAN errors confirmed

## Next Steps

- Consider upstreaming the fix to Libcanard's H7 driver
- No further action needed on this specific issue

---
**Developer**
