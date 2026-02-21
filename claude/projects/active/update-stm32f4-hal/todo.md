# Todo: Update STM32F4xx HAL and CMSIS

## Phase 1: Preparation

- [ ] Backup current HAL directory: `lib/main/STM32F4/Drivers/STM32F4xx_HAL_Driver/`
- [ ] Backup current CMSIS directory: `lib/main/STM32F4/Drivers/CMSIS/Device/ST/STM32F4xx/`
- [ ] Record current versions for rollback if needed

## Phase 2: Download and Replace

- [ ] Clone or download STM32CubeF4 from GitHub
- [ ] Identify latest HAL version (V1.8.5) and CMSIS version
- [ ] Replace `lib/main/STM32F4/Drivers/STM32F4xx_HAL_Driver/` with new version
- [ ] Replace `lib/main/STM32F4/Drivers/CMSIS/Device/ST/STM32F4xx/` with new version
- [ ] Verify `stm32f4xx_hal_conf.h` references correct modules

## Phase 3: Build Verification

- [ ] Clean build directory
- [ ] Build for MATEKF405 target
- [ ] Build for OMNIBUSF4 target
- [ ] Verify no new compiler warnings
- [ ] Compare binary size with previous build

## Phase 4: Hardware Testing

- [ ] UART (CRSF, GPS, MSP)
- [ ] I2C sensors (baro, mag)
- [ ] SPI gyro/flash
- [ ] SD card blackbox logging
- [ ] USB MSC
- [ ] PWM/DSHOT outputs

## Phase 5: Completion

- [ ] All tests passing
- [ ] Send completion report to manager
