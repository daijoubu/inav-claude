# Target Testing Template

Template for testing PRs that add new hardware targets to INAV firmware.

---

## Phase 1: PR Analysis

- [ ] Review PR on GitHub
  - [ ] Read PR description and objectives
  - [ ] Check related issues and discussions

- [ ] Analyze code changes
  - [ ] Review `src/main/target/<TARGET>/` directory structure
  - [ ] Verify CMakeLists.txt uses correct MCU variant
  - [ ] Review target.h pin definitions
  - [ ] Review target.c timer/DMA configuration
  - [ ] Check for any non-target code changes

- [ ] Map hardware specifications from PR
  - [ ] MCU model and flash size
  - [ ] Gyro/IMU type and bus (SPI/I2C)
  - [ ] Barometer type and bus
  - [ ] Flash/SD card storage
  - [ ] OSD chip (if applicable)
  - [ ] UART assignments
  - [ ] Motor/servo outputs

---

## Phase 2: Build Verification

- [ ] Checkout PR branch
- [ ] Build target
  ```bash
  make TARGET=<TARGETNAME>
  ```
  - [ ] Build succeeds without errors
  - [ ] No unexpected warnings
  - [ ] Flash size within limits

- [ ] Verify build artifacts exist

---

## Phase 3: Hardware Testing

### 3.1 Flash and Boot

- [ ] Flash firmware via DFU/Configurator
- [ ] FC boots normally
- [ ] USB enumeration works
- [ ] Configurator connects
- [ ] Correct target name shows

### 3.2 IMU/Gyro

- [ ] Sensor detected in Configurator
- [ ] Correct sensor name shown
- [ ] Orientation correct (verify alignment)
- [ ] Gyro values reasonable
- [ ] Accel values reasonable (~1g on Z)
- [ ] No SPI/I2C errors

### 3.3 Barometer

- [ ] Sensor detected in Configurator
- [ ] Correct sensor name shown
- [ ] Altitude reads reasonable value
- [ ] Altitude changes when moving FC
- [ ] No I2C errors (if applicable)

### 3.4 Flash/SD Storage

- [ ] Storage detected in Configurator
- [ ] Correct size shown
- [ ] Blackbox logging works
- [ ] Log file readable after download

### 3.5 UARTs

- [ ] Each UART configured and tested
- [ ] TX/RX work correctly
- [ ] No pin conflicts

### 3.6 Motor/Servo Outputs

- [ ] Outputs map correctly
- [ ] Motors spin in correct direction
- [ ] Servos respond to commands
- [ ] DShot/OneShot works (if applicable)

### 3.7 OSD (if applicable)

- [ ] OSD chip detected
- [ ] OSD displays correctly
- [ ] No video corruption

### 3.8 ADC

- [ ] Voltage reading accurate
- [ ] Current reading accurate (if supported)
- [ ] RSSI reading works (if configured)

### 3.9 Other Peripherals

- [ ] LED status correct
- [ ] Beeper works (if applicable)
- [ ] VTX control (if applicable)

---

## Phase 4: SITL Testing

- [ ] SITL builds with PR changes
- [ ] No build regressions

---

## Phase 5: Regression Testing

- [ ] Similar targets still build
- [ ] No impact on other targets
- [ ] Core functionality unaffected

---

## Phase 6: Documentation Check

- [ ] Board identifier unique
- [ ] Comments explain choices
- [ ] No debugging code left

---

## Phase 7: Reporting

- [ ] Document all test results
- [ ] Comment on PR with findings
- [ ] Recommend merge or changes

---

## Test Environment

| Item | Details |
|------|---------|
| Hardware | <Target FC Name> |
| Test Date | YYYY-MM-DD |
| Configurator Version | X.X.X |
| PR Branch | pr-XXXX |
| Base Commit | maintenance-X.x |
