# Project: STM32F4 HAL Macro Redefinition Warnings Fix

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-05-15
**Estimated Effort:** 1-2 hours

## Overview

Apply the `SYSTEM_INCLUDE_DIRECTORIES` fix to `cmake/stm32f4.cmake` to eliminate `__FPU_PRESENT` and related macro redefinition warnings exposed by the HAL update. This is the same fix already applied to `cmake/stm32f7.cmake` in commit `37e6b23ea`.

## Problem

PR #11514 (STM32F7 HAL v1.3.3 update) causes `__FPU_PRESENT` redefinition warnings across all STM32F4 compilation units. The F4 cmake file was not updated alongside the F7 fix. This is currently causing `SPEEDYBEEF405WING` (F4) builds to fail, blocking #11514 from landing — which in turn blocks #11560 (CAN TX ISR PR).

## Solution

Apply the same `SYSTEM_INCLUDE_DIRECTORIES` treatment to `cmake/stm32f4.cmake` that was applied to `cmake/stm32f7.cmake` in commit `37e6b23ea`. The fix suppresses the HAL headers' macro redefinitions by marking the HAL include paths as system includes (which silences redefinition warnings from system headers under GCC).

## Implementation

- File to modify: `cmake/stm32f4.cmake`
- Reference fix: `cmake/stm32f7.cmake` — commit `37e6b23ea`
- Commit onto branch `feature/stm32f7-hal-v1.3.3-update` (the PR #11514 branch), or as a separate fixup commit to that PR

## Success Criteria

- [ ] `cmake/stm32f4.cmake` updated with `SYSTEM_INCLUDE_DIRECTORIES` treatment matching F7 fix
- [ ] `SPEEDYBEEF405WING` (F4) builds cleanly with no `__FPU_PRESENT` redefinition warnings
- [ ] Existing F7/H7/SITL builds still pass
- [ ] Fix committed to `feature/stm32f7-hal-v1.3.3-update` branch (PR #11514)

## Related

- **Blocks:** PR #11514 (STM32F7 HAL v1.3.3 update)
- **Blocks (transitively):** PR #11560 (CAN TX ISR — depends on #11514)
- **Prior art:** `fix-stm32f7-hal-redefinition-warnings` (completed 2026-04-20) — same fix for F7
- **Repository:** inav (firmware) | **Branch:** `feature/stm32f7-hal-v1.3.3-update`
- **Assignment:** `manager/email/sent/2026-05-15-task-fix-stm32f4-hal-redefinition-warnings.md`
