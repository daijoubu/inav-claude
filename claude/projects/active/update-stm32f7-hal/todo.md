# Todo: Update STM32F7xx HAL and CMSIS

## Phase 1: Preparation

- [ ] Backup current HAL directory: `lib/main/STM32F7/Drivers/STM32F7xx_HAL_Driver/`
- [ ] Backup current CMSIS directory: `lib/main/STM32F7/Drivers/CMSIS/Device/ST/STM32F7xx/`
- [ ] Record current versions for rollback if needed

## Phase 2: Download and Replace

- [ ] Clone or download STM32CubeF7 from GitHub
- [ ] Identify latest HAL version (V1.3.3) and CMSIS version
- [ ] Replace `lib/main/STM32F7/Drivers/STM32F7xx_HAL_Driver/` with new version
- [ ] Replace `lib/main/STM32F7/Drivers/CMSIS/Device/ST/STM32F7xx/` with new version
- [ ] Verify `stm32f7xx_hal_conf.h` references correct modules

## Phase 3: Build Verification

- [ ] Clean build directory
- [ ] Build for MATEKF722 target
- [ ] Build for MATEKF765 target
- [ ] Verify no new compiler warnings
- [ ] Compare binary size with previous build

## Phase 4: Hardware Testing

### Communication Peripherals
- [ ] CRSF/ELRS receiver connection
- [ ] GPS connection and fix
- [ ] MSP connection via USB
- [ ] SmartPort telemetry
- [ ] I2C barometer reading
- [ ] I2C compass reading
- [ ] SPI gyro data
- [ ] SPI flash read/write

### Storage Peripherals
- [ ] SD card blackbox logging (stress test)
- [ ] USB MSC mode

### Output Peripherals
- [ ] PWM motor outputs
- [ ] DSHOT motor outputs
- [ ] Servo outputs
- [ ] LED strip (WS2812)

## Phase 5: Documentation

- [ ] Document new HAL version in project notes
- [ ] Note any behavioral differences observed
- [ ] Report completion to manager

## Completion

- [ ] All tests passing
- [ ] No regressions observed
- [ ] Send completion report to manager
