# Todo: Update STM32H7xx HAL from V1.11.4 to V1.13.0

## Phase 1: HAL Source Replacement

- [ ] Download STM32CubeH7 V1.13.0 package
- [ ] Replace `lib/main/STM32H7xx_HAL_Driver/` with V1.13.0 sources
- [ ] Replace `lib/main/CMSIS/Device/ST/STM32H7xx/` with V1.13.0 sources
- [ ] Identify any INAV-specific patches in current HAL files (git log/history)
- [ ] Re-apply INAV-specific patches to new HAL (if any)

## Phase 2: Workaround Review

- [ ] Evaluate `USE_H7_HSERDY_SLOW_WORKAROUND` against V1.13.0
- [ ] Evaluate `USE_H7_HSE_TIMEOUT_WORKAROUND` against V1.13.0
- [ ] Evaluate `HandleStuckSysTick` against V1.13.0

## Phase 3: Build and Test

- [ ] Build all H7 targets — verify clean compilation
- [ ] Build SITL — verify no H7 HAL changes broke the build
- [ ] Hardware test on at least one H7 board (flash + fly sensors)
- [ ] Check SD card detection on H7 (SDMMC V1.x fix)

## Completion

- [ ] PR created referencing issue #11563
- [ ] Completion report sent to manager
