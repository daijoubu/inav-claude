# Task Assignment: Update STM32F4xx HAL and CMSIS

**Date:** 2026-02-20 07:43
**From:** Manager
**To:** Developer
**Project:** update-stm32f4-hal
**Priority:** HIGH
**Estimated Effort:** 16-26 hours
**Branch:** From maintenance-9.x

## Task

Update the STM32F4xx HAL and CMSIS libraries from V1.7.1 to V1.8.5+ in the INAV firmware codebase.

## Background

The STM32F4xx HAL is 8 years outdated (V1.7.1 → V1.8.5). This is a drop-in replacement with zero code changes required (API verified compatible). This update brings the same critical bug fixes that were applied to F7xx targets.

## What to Do

1. Backup current HAL and CMSIS directories in `lib/main/STM32F4/Drivers/`
2. Download STM32CubeF4 latest release from GitHub
3. Replace `STM32F4xx_HAL_Driver` directory
4. Replace `CMSIS/Device/ST/STM32F4xx` directory
5. Build for F4 targets (MATEKF405, OMNIBUSF4)
6. Test all peripherals

## Success Criteria

- [ ] HAL and CMSIS updated to V1.8.5+
- [ ] Firmware builds without errors
- [ ] All peripherals function correctly

## Project Directory

`claude/projects/active/update-stm32f4-hal/`

---
**Manager**
