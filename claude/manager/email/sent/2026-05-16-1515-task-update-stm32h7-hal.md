# Task Assignment: Update STM32H7xx HAL from V1.11.4 to V1.13.0

**Date:** 2026-05-16 15:15
**From:** Manager
**To:** Developer
**Project:** update-stm32h7-hal
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 4-6 hours

## Task

Update the STM32H7xx HAL driver from V1.11.4 to V1.13.0 and CMSIS Device from V1.10.5 to V1.13.0, using the official STM32CubeH7 V1.13.0 package as the source.

## Background

Your verification report (May 15) confirmed both are significantly out of date. Several high-severity fixes in the gap directly affect INAV on H7 targets:

- **DMA IRQHandler CT bit inversion (V1.13.0)** — wrong callbacks, affects SPI/UART/SDMMC
- **SPI TX buffer overflow in ISR (V1.13.0)** — silent corruption on gyro/baro/OSD
- **FDCAN overflow prevention (V1.13.0)** — DroneCAN on H7 affected
- **HCLK frequency calculation (V1.12.1)** — all peripheral baud rates misconfigured

Issue #11563 has the full list.

## What to Do

1. Download STM32CubeH7 V1.13.0 package
2. Replace HAL sources in `lib/main/STM32H7xx_HAL_Driver/`
3. Replace CMSIS device files in `lib/main/CMSIS/Device/ST/STM32H7xx/`
4. Identify and re-apply any INAV-specific patches (check git history)
5. Review the 3 H7 workarounds in `system_stm32h7xx.c`
6. Build all H7 targets
7. Hardware test on at least one H7 board

## Branch

From `maintenance-10.x`, PR targets `maintenance-10.x`.

## Success Criteria

- [ ] HAL V1.13.0, CMSIS V1.13.0 (matched versions from same Cube package)
- [ ] All H7 targets build cleanly
- [ ] INAV-specific patches re-applied
- [ ] Workarounds reviewed
- [ ] Hardware tested on H7 board
- [ ] PR created referencing issue #11563

## Files to Check

- `lib/main/STM32H7xx_HAL_Driver/`
- `lib/main/CMSIS/Device/ST/STM32H7xx/`
- `src/main/target/system_stm32h7xx.c`
- `src/main/target/system_stm32h7xx.c` (workarounds)

## Project Directory

`claude/projects/active/update-stm32h7-hal/`

---
**Manager**
