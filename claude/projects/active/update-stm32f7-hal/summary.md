# Project: Update STM32F7xx HAL and CMSIS

**Status:** 🚫 BLOCKED - DroneCAN HAL Compatibility
**Priority:** CRITICAL (fixes #11299 lockup)
**Type:** Maintenance / Security Update
**Created:** 2026-02-20
**Started:** 2026-02-22
**Blocked:** 2026-04-15 (DroneCAN driver API incompatibility with HAL v1.3.3)
**Estimated Effort:** 16-26 hours (HAL update complete; +4-6 hours for DroneCAN driver fix)

## Overview

Update STM32F7xx HAL driver and CMSIS Device headers from V1.2.2 (2017) to V1.3.3 (2025) to incorporate 8+ years of bug fixes, security patches, and errata workarounds.

## Problem

Current HAL version is nearly 9 years old, missing critical fixes:
- SD card reliability improvements (affects blackbox logging)
- I2C transmission stalled workaround
- UART DMA race condition fixes
- USB connection/disconnect handling
- ETH receive process rework

## Solution

Drop-in replacement of HAL and CMSIS libraries from STM32CubeF7 package (v1.3.3 / v1.17.4). 

**Note:** DroneCAN driver requires API updates for HAL v1.3.3 compatibility (separate task).

## Implementation

1. Backup current HAL and CMSIS directories
2. Download STM32CubeF7 latest release
3. Replace HAL driver directory
4. Replace CMSIS Device directory
5. Build for F7 targets
6. Test all peripherals

## Scope

**In Scope:**
- HAL driver update (V1.2.2 → V1.3.3)
- CMSIS Device update (V1.2.0 → V1.3.0+)
- Build verification on F7 targets
- Peripheral testing

**Out of Scope:**
- Code modifications (none required)
- F4xx or H7xx updates (separate tasks)

## Success Criteria

- [ ] HAL and CMSIS updated to latest versions
- [ ] Firmware builds without errors
- [ ] UART (CRSF, GPS, MSP) functions correctly
- [ ] I2C sensors work correctly
- [ ] SPI gyro/flash work correctly
- [ ] SD card blackbox logging stable
- [ ] USB MSC and CLI work correctly
- [ ] PWM/DSHOT motor outputs work

## Related

- **Assessment:** `completed/assess-stm32-hal-updates/`
- **Source:** STM32CubeF7 (https://github.com/STMicroelectronics/STM32CubeF7)
- **Assignment:** `manager/email/sent/2026-02-20-0743-task-update-stm32f7-hal.md`
- **Branch:** `feature/stm32f7-hal-v1.3.3-update` (pushed to GitHub)
- **Blocking Issue:** DroneCAN API incompatibility with HAL v1.3.3 (see DRONECAN_COMPATIBILITY.md)

## Directory

`active/update-stm32f7-hal/`
