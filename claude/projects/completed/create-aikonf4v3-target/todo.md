# Todo: Create AIKONF4V3 Target

## Phase 1: Preparation

engage target developer agent to help with the following:

- [ ] Review reference files
  - [ ] Read betaflight_config.h completely
  - [ ] Study Betaflight CLI resource dump
  - [ ] Compare with INAV CLI output (wrong target)
- [ ] Examine existing similar targets
  - [ ] AIKONF4 (existing Aikon target)
  - [ ] FLASHHOBBYF405 or FOXEERF405 (ICM42605 examples)
  - [ ] Other F405 targets for reference
- [ ] Use target-developer agent to analyze reference files
  - [ ] Identify potential conflicts
  - [ ] Check timer/DMA assignments
  - [ ] Verify pin compatibility

## Phase 2: Create Target Structure

- [ ] Create target directory: `inav/src/main/target/AIKONF4V3/`
- [ ] target-developer agent should Create `target.h` with hardware definitions
  - [ ] Board identifier and USB string
  - [ ] LED and beeper pins (PB4, PB5)
  - [ ] IMU configuration (ICM42688P)
  - [ ] Flash chip (W25Q128FV)
  - [ ] OSD (MAX7456)
  - [ ] Barometer (BMP280/DPS310)
  - [ ] UART definitions (1-5)
  - [ ] I2C configuration
  - [ ] SPI bus assignments
  - [ ] ADC pins (VBAT, CURRENT, RSSI)
  - [ ] PINIO pins (BEC, camera control)
  - [ ] Default features
- [ ] Create `target.c` with timer mappings
  - [ ] Convert Betaflight timer map to INAV format
  - [ ] Motors (PC6, PC7, PC8, PC9)
  - [ ] Servos (PB0, PB1)
  - [ ] LED strip (PB6)
  - [ ] Verify timer/DMA assignments with target-developer agent
- [ ] Create `config.c` if needed
  - [ ] PINIO configuration
  - [ ] Default settings

## Phase 3: Conflict Detection

- [ ] Use target-developer agent to check:
  - [ ] UART3 (PB10/PB11) vs I2C1 (PB8/PB9) conflicts
  - [ ] Timer/DMA conflicts
  - [ ] Pin alternate function conflicts
  - [ ] SPI bus sharing issues
- [ ] Resolve any conflicts found
- [ ] Document conflicts ONLY if unusual

## Phase 4: Build and Validate

- [ ] Use inav-builder agent to build target
  - [ ] Build firmware: AIKONF4V3
  - [ ] Check for compilation errors
  - [ ] Verify flash size (<95% of 1024KB)
- [ ] Use test-engineer agent to validate
  - [ ] Check resource assignments
  - [ ] Verify gyro detection
  - [ ] Check flash chip detection
  - [ ] Verify OSD configuration
- [ ] Review build output
  - [ ] Flash usage percentage
  - [ ] RAM usage
  - [ ] Warning messages

## Phase 5: Testing

- [ ] Flash firmware to board
- [ ] Verify all UARTs functional
- [ ] Test gyro (ICM42688P should be detected)
- [ ] Test flash chip (should detect W25Q128FV)
- [ ] Test OSD (MAX7456)
- [ ] Test barometer detection
- [ ] Verify motor outputs
- [ ] Test servo outputs
- [ ] Test PINIO functionality
- [ ] Test ADC readings (voltage, current)

## Phase 6: Documentation (CONDITIONAL)

**Only complete this if there are unusual conditions that should be docuemtned for this board, such as:**
- [ ] Conflicts such as UART3 conflicts with I2C
- [ ] Unusual timer/DMA workarounds needed
- [ ] Non-standard gyro orientation issues
- [ ] Special PINIO setup required

**If documentation needed:**
- [ ] Create/update docs explaining the issue
- [ ] Document workarounds or limitations
- [ ] Add to board-specific notes

## Completion

- [ ] Target builds successfully
- [ ] All hardware properly configured
- [ ] No conflicts detected (or documented if found)
- [ ] Flash usage acceptable
- [ ] Test build verified (if hardware available)
- [ ] Send completion report to manager
