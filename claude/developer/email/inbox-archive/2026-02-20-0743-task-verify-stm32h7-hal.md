# Task Assignment: Verify and Update STM32H7xx HAL and CMSIS

**Date:** 2026-02-20 07:43
**From:** Manager
**To:** Developer
**Project:** verify-stm32h7-hal
**Priority:** MEDIUM
**Estimated Effort:** 4-8 hours
**Branch:** From maintenance-9.x

## Task

Determine the current STM32H7xx HAL and CMSIS versions and update if more than 2 versions behind the latest release (V1.11.5).

## Background

The STM32H7xx HAL version is currently unknown. Need to determine the current version and update if significantly behind. INAV has H7-specific workarounds (HSE_SLOW, HSE_TIMEOUT, HandleStuckSysTick) that may need adjustment based on HAL version.

## What to Do

1. Check HAL version in `lib/main/STM32H7/Drivers/STM32H7xx_HAL_Driver/Inc/stm32h7xx_hal.h`
2. Check CMSIS version in `lib/main/STM32H7/Drivers/CMSIS/Device/ST/STM32H7xx/Include/stm32h7xx.h`
3. Compare with latest STM32CubeH7 release (V1.11.5)
4. If > 2 versions behind, update both HAL and CMSIS
5. Review H7-specific workarounds (USE_H7_HSERDY_SLOW_WORKAROUND, USE_H7_HSE_TIMEOUT_WORKAROUND, HandleStuckSysTick)
6. Build and test if updated

## Success Criteria

- [ ] Current HAL version documented
- [ ] Current CMSIS version documented
- [ ] Decision documented: update or skip
- [ ] If updated: builds and tests pass
- [ ] H7 workarounds reviewed for necessity

## Project Directory

`claude/projects/active/verify-stm32h7-hal/`

---
**Manager**
