# Task Completed: Verify STM32H7xx HAL and CMSIS Versions

**Date:** 2026-05-15 14:00
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED (verification only — update scheduled for this weekend)

## Summary

Verified current STM32H7xx HAL and CMSIS versions against the latest STM32CubeH7 release. Both are significantly out of date and should be updated. Several of the fixes in the newer versions are directly relevant to INAV on H7 targets. GitHub issue filed. Update work planned for this weekend.

## Versions

| Component | Current | Latest | Gap |
|-----------|---------|--------|-----|
| STM32H7xx HAL | V1.11.4 | V1.13.0 | 2 minor versions |
| CMSIS Device | V1.10.5 | V1.13.0 | 3 minor versions, mismatched from HAL |

Note: HAL and CMSIS are mismatched — they should come from the same STM32CubeH7 package but were updated independently at some point.

## Relevant Fixes (HIGH severity)

- **DMA IRQHandler CT bit inversion (V1.13.0)** — inverted bit check causes wrong DMA callback execution. Affects SPI (gyro/barometer/OSD), UART, SDMMC.
- **SPI TX buffer overflow in ISR (V1.13.0)** — silent corruption on SPI TX. Affects gyro, barometer, OSD, external flash.
- **FDCAN overflow prevention (V1.13.0)** — HAL_FDCAN_GetRxMessage() and ConfigFilter() fixes. Affects DroneCAN on H7.
- **HCLK frequency calculation (V1.12.1)** — wrong clock frequencies silently misconfigure all peripheral baud rates and timers.

## Relevant Fixes (MEDIUM severity)

- UART DMA Rx abort, buffer boundary, RxEventCallback fixes (V1.12.0, V1.13.0)
- I2C errata I2C2-190208 transmission stall workaround (V1.12.0)
- SDMMC SD card V1 support (V1.13.0) — older SD cards not detected
- Timer UIF spurious interrupt on init (V1.12.0)
- Timer complementary channel disable fix (V1.13.0) — affects DSHOT on H7

## Workarounds to Re-evaluate

Three H7-specific workarounds in system_stm32h7xx.c should be reviewed against V1.13.0:
- USE_H7_HSERDY_SLOW_WORKAROUND
- USE_H7_HSE_TIMEOUT_WORKAROUND
- HandleStuckSysTick

## Artifacts

- GitHub issue: (see below — filed today)
- Branch: `maintenance-9.x` per original task assignment
- Lock: released — no code changes made

## Next Steps

Update both HAL (V1.11.4 → V1.13.0) and CMSIS (V1.10.5 → V1.13.0) from the same STM32CubeH7 V1.13.0 package. Hardware testing on H7 board required after update. Planned for this weekend.

---
**Developer**
