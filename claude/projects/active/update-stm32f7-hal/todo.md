# Todo: Update STM32F7xx HAL and CMSIS

## Phase 0: Baseline Testing (HAL 1.2.2)

- [x] Create baseline test suite (Tests 1-11)
- [x] SD card detection and write verification
- [x] MSP protocol verification
- [x] ST-Link debugger connectivity
- [x] HAL 1.2.2 baseline metrics established (136.5 KB/s write speed)
- [ ] FC lockup root cause analysis (Tests 2-6, 8-10 trigger lockup)
- [ ] Debug tool `debug_lockup.py` validation

## Phase 1: Preparation

- [x] Backup current HAL directory: `lib/main/STM32F7/Drivers/STM32F7xx_HAL_Driver/`
- [x] Backup current CMSIS directory: `lib/main/STM32F7/Drivers/CMSIS/Device/ST/STM32F7xx/`
- [x] Record current versions for rollback if needed

## Phase 2: Download and Replace

- [x] Clone or download STM32CubeF7 from GitHub
- [x] Identify latest HAL version (V1.3.3) and CMSIS version
- [x] Replace `lib/main/STM32F7/Drivers/STM32F7xx_HAL_Driver/` with new version
- [x] Replace `lib/main/STM32F7/Drivers/CMSIS/Device/ST/STM32F7xx/` with new version
- [x] Verify `stm32f7xx_hal_conf.h` references correct modules (at src/main/target/)

## Phase 3: Build Verification

- [x] Clean build directory
- [x] Build for MATEKF722 target (721 KB, 97.97% flash)
- [x] Build for MATEKF765 target (888 KB, 32.36% flash)
- [x] Verify no new compiler warnings (4 benign HAL header warnings, no errors)
- [x] Compare binary size with previous build (no significant change)

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
