# Task Assignment: Fix STM32F7 HAL Macro Redefinition Warnings

**Date:** 2026-04-20 00:00
**From:** Manager
**To:** Developer
**Project:** fix-stm32f7-hal-redefinition-warnings
**Priority:** HIGH
**Estimated Effort:** 1-2 hours

## Task

Investigate and fix two macro redefinition warnings in the STM32F7 HAL build. Warnings are treated as errors in this project — the build cannot ship with these present.

## Background

During the HAL v1.2.2 → v1.3.3 update on branch `feature/stm32f7-hal-v1.3.3-update`, two redefinition warnings were exposed that repeat across all 528 compilation units:

1. **`__FPU_PRESENT` redefined** — cmake passes `-D__FPU_PRESENT=1` on the command line, but `stm32f765xx.h:178` also defines it
2. **`ART_ACCLERATOR_ENABLE` redefined** — defined in `stm32f7xx_hal_conf.h:162` and again in `stm32_hal_legacy.h:4402`

## What to Do

1. Trace the source of each conflict and determine the correct fix
2. For `__FPU_PRESENT`: check if the cmake `-D` flag can be removed, or add an `#ifndef` guard
3. For `ART_ACCLERATOR_ENABLE`: add an `#ifndef` guard in `stm32f7xx_hal_conf.h` or the legacy header
4. Verify no other redefinition warnings remain after fixing
5. Commit fixes to `feature/stm32f7-hal-v1.3.3-update`

## Success Criteria

- [ ] Zero warnings in full MATEKF765SE build
- [ ] Build succeeds with no regressions
- [ ] Fix committed to `feature/stm32f7-hal-v1.3.3-update`

## Project Directory

`claude/projects/active/fix-stm32f7-hal-redefinition-warnings/`

---
**Manager**
