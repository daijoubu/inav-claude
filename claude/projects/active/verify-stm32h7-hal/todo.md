# Todo: Verify and Update STM32H7xx HAL and CMSIS

## Phase 1: Version Discovery

- [ ] Check HAL version in `lib/main/STM32H7/Drivers/STM32H7xx_HAL_Driver/Inc/stm32h7xx_hal.h`
- [ ] Check CMSIS version in `lib/main/STM32H7/Drivers/CMSIS/Device/ST/STM32H7xx/Include/stm32h7xx.h`
- [ ] Check for Release_Notes.html or README.md
- [ ] Compare with latest STM32CubeH7 release (V1.11.5)

## Phase 2: Decision

- [ ] Document current versions
- [ ] Calculate version gap
- [ ] Decision: Update if > 2 versions behind, else skip to Phase 5

## Phase 3: Update (if needed)

- [ ] Backup current HAL and CMSIS directories
- [ ] Download STM32CubeH7 latest release
- [ ] Replace HAL driver directory
- [ ] Replace CMSIS Device directory
- [ ] Verify hal_conf.h references correct modules

## Phase 4: Build and Test (if updated)

- [ ] Clean build
- [ ] Build for MATEKH743 target
- [ ] Verify no new compiler warnings
- [ ] Test on H7 hardware if available

## Phase 5: H7 Workaround Review

- [ ] Review `USE_H7_HSERDY_SLOW_WORKAROUND` - still needed?
- [ ] Review `USE_H7_HSE_TIMEOUT_WORKAROUND` - still needed?
- [ ] Review `HandleStuckSysTick()` - still needed?
- [ ] Check if new HAL has built-in fixes for these issues

## Phase 6: Completion

- [ ] Document findings
- [ ] Send completion report to manager