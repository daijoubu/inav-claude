# Task Completed: Fix CAN Interrupt Initialization Race Condition

**Date:** 2026-02-18 00:00 | **From:** Developer | **To:** Manager | **Status:** COMPLETED

## Summary

Successfully identified and fixed a critical race condition in the canard STM32F7 CAN driver where the interrupt was being enabled before hardware initialization completed. This vulnerability could cause spurious interrupts on unconfigured hardware, leading to system crashes.

## The Problem

The init function had interrupt enable at the beginning (line 190) but multiple error returns could occur later (lines 240, 248, 252). If any initialization step failed, the interrupt would remain enabled while hardware was unconfigured, causing undefined behavior.

## The Solution

Moved interrupt enable to the END of the init function (after all success checks):
- `HAL_NVIC_SetPriority()` and `HAL_NVIC_EnableIRQ()` now execute only after all hardware initialization succeeds
- If any step fails, function returns early with interrupt never enabled
- Prevents spurious interrupts on unconfigured hardware

## Changes Made

**File:** `src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c`
- Removed interrupt enable from lines 188-190
- Added interrupt enable at end of function with explanatory comment
- Total: 6 insertions, 4 deletions

**Commit:** 00a71a08a - "Fix: Move CAN interrupt enable to end of init function"

## Testing

- ✅ MATEKH743 firmware builds successfully
- ✅ Zero compilation errors
- ✅ Zero compilation warnings
- ✅ Build includes all DroneCAN/libcanard components
- ✅ Change is low-risk: only affects interrupt enable ordering

## Pull Request

- **PR:** #10 (https://github.com/daijoubu/inav/pull/10)
- **Repository:** daijoubu/inav (add-libcanard branch)
- **Status:** Open, ready for review
- **Base Branch:** add-libcanard

## Lock Released

Released inav.lock

## Next Steps

1. Code review approval
2. Merge to add-libcanard when ready
3. Consider backport to maintenance-9.x if applicable

---

**Developer**
