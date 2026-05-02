# Project: Update STM32F4xx HAL and CMSIS

**Status:** 📋 TODO (✉️ Assigned)
**Priority:** HIGH
**Type:** Maintenance / Security Update
**Created:** 2026-02-20
**Assigned:** 2026-02-20
**Estimated Effort:** 16-26 hours

## Overview

Update STM32F4xx HAL driver and CMSIS Device headers from V1.7.1 (2017) to V1.8.5 (2025) to incorporate 8+ years of bug fixes, security patches, and errata workarounds.

## Problem

Current HAL version is nearly 8 years old, missing critical fixes:
- SD card reliability improvements
- I2C transmission stalled workaround
- UART DMA race condition fixes
- USB connection/disconnect handling

## Solution

Drop-in replacement of HAL and CMSIS libraries from STM32CubeF4 package. No code changes required (API verified compatible).

## Implementation

1. Backup current HAL and CMSIS directories
2. Download STM32CubeF4 latest release
3. Replace HAL driver directory
4. Replace CMSIS Device directory
5. Build for F4 targets
6. Test all peripherals

## Scope

**In Scope:**
- HAL driver update (V1.7.1 → V1.8.5)
- CMSIS Device update
- Build verification on F4 targets
- Peripheral testing

**Out of Scope:**
- Code modifications (none required)
- F7xx or H7xx updates (separate tasks)

## Success Criteria

- [ ] HAL and CMSIS updated to latest versions
- [ ] Firmware builds without errors
- [ ] All peripherals function correctly
- [ ] No regressions compared to previous version

## Related

- **Assessment:** `completed/assess-stm32-hal-updates/`
- **F7xx Update:** `active/update-stm32f7-hal/`
- **Source:** STM32CubeF4 (https://github.com/STMicroelectronics/STM32CubeF4)

## Directory

`active/update-stm32f4-hal/`
