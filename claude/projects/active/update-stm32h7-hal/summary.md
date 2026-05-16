# Project: Update STM32H7xx HAL from V1.11.4 to V1.13.0

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Maintenance / Bug Fix
**Created:** 2026-05-16
**Estimated Effort:** 4-6 hours

## Overview

Update STM32H7xx HAL (V1.11.4 → V1.13.0) and CMSIS Device (V1.10.5 → V1.13.0) from the same STM32CubeH7 V1.13.0 package. Several high-severity fixes in the gap directly affect INAV on H7 targets.

## Problem

The STM32H7xx HAL is at V1.11.4 (CMSIS at V1.10.5) — 2-3 minor versions behind latest V1.13.0. Critical fixes in V1.12.0-V1.13.0 are missing, including DMA IRQHandler CT bit inversion, SPI TX buffer overflow in ISR, FDCAN overflow prevention, and HCLK frequency calculation bugs. These cause silent data corruption, missed DMA callbacks, and misconfigured peripherals on all 20+ H7 targets.

## Solution

Replace the STM32H7xx HAL and CMSIS source files with V1.13.0 versions from the official STM32CubeH7 package. Review and re-apply any INAV-specific patches. Test on H7 hardware to verify no regressions.

## Implementation

1. Download STM32CubeH7 V1.13.0 from ST
2. Replace HAL source files under `lib/main/STM32H7xx_HAL_Driver/`
3. Replace CMSIS device files under `lib/main/CMSIS/Device/ST/STM32H7xx/`
4. Review and re-apply INAV-specific patches (if any)
5. Re-evaluate 3 H7 workarounds in `system_stm32h7xx.c`
6. Build all H7 targets
7. Hardware test on at least one H7 board

## Success Criteria

- [ ] HAL updated to V1.13.0, CMSIS to V1.13.0 (matched versions)
- [ ] All H7 targets build cleanly (no new warnings or errors)
- [ ] INAV-specific patches re-applied correctly
- [ ] H7 workarounds reviewed against new HAL
- [ ] Hardware tested on at least one H7 board (MATEKH743 or similar)
- [ ] Issue #11563 referenced in PR

## Related

- **Issue:** [#11563](https://github.com/iNavFlight/inav/issues/11563)
- **Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
- **Verification project:** `completed/verify-stm32h7-hal/`
- **F4 HAL Update Bug (analogous):** PR [#11514](https://github.com/iNavFlight/inav/pull/11514)
