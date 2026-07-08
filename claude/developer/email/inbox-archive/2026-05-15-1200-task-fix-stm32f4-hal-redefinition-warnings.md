# Task Assignment: Fix STM32F4 HAL Macro Redefinition Warnings

**Date:** 2026-05-15 12:00
**From:** Manager
**To:** Developer
**Project:** fix-stm32f4-hal-redefinition-warnings
**Priority:** HIGH
**Estimated Effort:** 1-2 hours

## Task

Apply the `SYSTEM_INCLUDE_DIRECTORIES` fix to `cmake/stm32f4.cmake` to eliminate `__FPU_PRESENT` macro redefinition warnings caused by the HAL v1.3.3 update. This unblocks PR #11514 and transitively PR #11560.

## Background

PR #11514 (STM32F7 HAL v1.3.3 update) exposed `__FPU_PRESENT` redefinition warnings across all STM32F4 compilation units, causing `SPEEDYBEEF405WING` (F4) builds to fail. The identical fix was already applied to `cmake/stm32f7.cmake` in commit `37e6b23ea` — this task applies the same treatment to `cmake/stm32f4.cmake`.

This is a blocker: #11514 cannot land until F4 builds cleanly, and #11560 (CAN TX ISR) cannot land until #11514 merges.

## What to Do

1. Review commit `37e6b23ea` to see the exact `SYSTEM_INCLUDE_DIRECTORIES` change made to `cmake/stm32f7.cmake`
2. Apply the same change to `cmake/stm32f4.cmake`
3. Commit onto the `feature/stm32f7-hal-v1.3.3-update` branch (PR #11514)
4. Build all four MCU families to verify:
   - `SPEEDYBEEF405WING` (F4) — must now pass with no redefinition warnings
   - `MATEKF765SE` (F7) — must still pass
   - `MATEKH743` (H7) — must still pass
   - SITL — must still pass

## Success Criteria

- [ ] `cmake/stm32f4.cmake` updated with `SYSTEM_INCLUDE_DIRECTORIES` treatment
- [ ] `SPEEDYBEEF405WING` (F4) builds cleanly
- [ ] F7, H7, SITL builds still pass
- [ ] Fix committed to `feature/stm32f7-hal-v1.3.3-update` branch

## Project Directory

`claude/projects/active/fix-stm32f4-hal-redefinition-warnings/`

## Base Branch

Branch: `feature/stm32f7-hal-v1.3.3-update` (commit fix directly onto this branch — it is the PR #11514 branch)

---
**Manager**
