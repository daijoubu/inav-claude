# Task Assignment: Update STM32F7xx HAL and CMSIS

**Date:** 2026-02-20 07:43
**From:** Manager
**To:** Developer
**Project:** update-stm32f7-hal
**Priority:** HIGH
**Estimated Effort:** 16-26 hours
**Branch:** From maintenance-9.x

## Task

Update the STM32F7xx HAL and CMSIS libraries from V1.2.2 to V1.3.3+ in the INAV firmware codebase.

## Background

The STM32F7xx HAL is 9 years outdated (V1.2.2 → V1.3.3). This is a drop-in replacement with zero code changes required (API verified compatible). Critical bug fixes are missing for:
- SD card reliability
- I2C transmission issues
- UART DMA race conditions

This update will bring important reliability improvements to F7-based flight controllers.

## What to Do

1. Backup current HAL and CMSIS directories in `lib/main/STM32F7/Drivers/`
2. Download STM32CubeF7 latest release from GitHub
3. Replace `STM32F7xx_HAL_Driver` directory
4. Replace `CMSIS/Device/ST/STM32F7xx` directory
5. Build for F7 targets (MATEKF722, MATEKF765)
6. Test all peripherals (UART, I2C, SPI, SD card, USB, PWM/DSHOT)

## Success Criteria

- [ ] HAL and CMSIS updated to V1.3.3+
- [ ] Firmware builds without errors for F7 targets
- [ ] All peripherals function correctly
- [ ] No regressions in existing functionality

## Project Directory

`claude/projects/active/update-stm32f7-hal/`

## Reference

Assessment available at: `claude/projects/completed/assess-stm32-hal-updates/`

---
**Manager**
