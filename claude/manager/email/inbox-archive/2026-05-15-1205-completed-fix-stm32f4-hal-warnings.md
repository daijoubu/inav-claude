# Task Completed: Fix STM32F4 HAL Macro Redefinition Warnings

**Date:** 2026-05-15 15:05
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Applied the `SYSTEM_INCLUDE_DIRECTORIES` fix to `cmake/stm32f4.cmake` to eliminate `__FPU_PRESENT` macro redefinition warnings introduced by the HAL v1.3.3 update. All four MCU families verified clean.

## Branch and Commits

**Branch:** `feature/stm32f7-hal-v1.3.3-update`
**Commits:**
- `9737be135` - fix(stm32f4): suppress HAL header redefinition warnings via SYSTEM_INCLUDE_DIRECTORIES

## Changes Made

**Files modified:**
- `cmake/stm32f4.cmake` — changed `INCLUDE_DIRECTORIES` to `SYSTEM_INCLUDE_DIRECTORIES` for `STM32F4_INCLUDE_DIRS` in `target_stm32f4xx()`. This mirrors the identical fix already applied to `cmake/stm32f7.cmake`.

## Testing

- [x] SPEEDYBEEF405WING (F4) — PASS, zero redefinition warnings
- [x] MATEKF765SE (F7) — PASS, zero warnings
- [x] MATEKH743 (H7) — PASS, zero warnings
- [x] SITL — PASS, one pre-existing unrelated warning in fport.c only

## Next Steps

PR #11514 (`feature/stm32f7-hal-v1.3.3-update`) is now unblocked — F4 builds clean. PR #11560 (CAN TX ISR) remains blocked on #11514 merging upstream.

---
**Developer**
