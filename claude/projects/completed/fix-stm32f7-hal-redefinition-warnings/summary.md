# Project: Fix STM32F7 HAL Macro Redefinition Warnings

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-04-20
**Estimated Effort:** 1-2 hours

## Overview

Two macro redefinition warnings appear across every STM32F7 compilation unit on the `feature/stm32f7-hal-v1.3.3-update` branch. Since warnings are treated as errors in this project, these must be resolved before the HAL update can ship.

## Problem

The build produces two warnings that repeat across all 528 compilation units:

1. **`__FPU_PRESENT` redefined** — defined via cmake command-line flag `-D__FPU_PRESENT=1` AND again in `stm32f765xx.h:178`
2. **`ART_ACCLERATOR_ENABLE` redefined** — defined in `stm32f7xx_hal_conf.h:162` AND again in `stm32_hal_legacy.h:4402`

These are pre-existing warnings introduced or exposed by the HAL v1.2.2 → v1.3.3 update, not by the DroneCAN driver changes.

## Solution

Investigate root cause of each and fix without breaking the build:
- `__FPU_PRESENT`: likely remove the `-D` cmake flag or add `#ifndef` guard
- `ART_ACCLERATOR_ENABLE`: likely add `#ifndef` guard in `stm32f7xx_hal_conf.h` or `stm32_hal_legacy.h`

## Success Criteria

- [ ] Zero warnings in MATEKF765SE build
- [ ] Build still succeeds (no regressions)
- [ ] Fix committed to `feature/stm32f7-hal-v1.3.3-update`

## Related

- **Branch:** `feature/stm32f7-hal-v1.3.3-update`
- **Files:** `src/main/target/stm32f7xx_hal_conf.h`, cmake build files
- **Assignment:** `claude/manager/email/sent/`
