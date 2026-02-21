# Todo: Test PR #11324 - NEXUS Target

**PR:** Add NEXUS target for RadioMaster Nexus (Original) flight controller
**Target MCU:** STM32F722 (512KB flash)
**Base Branch:** maintenance-9.x

---

## Phase 1: PR Analysis

- [x] Review PR on GitHub
  - [x] Read PR description and objectives
  - [x] Review PR author's explanation (Joshua Perry)
  - [x] Check related issues and discussions

- [x] Analyze code changes
  - [x] Review `src/main/target/NEXUS/` directory structure
  - [x] Verify CMakeLists.txt uses correct MCU variant (`f722xe`)
  - [x] Review target.h pin definitions
  - [x] Review target.c timer/DMA configuration
  - [x] Check for `USE_UART4_SWAP` addition in serial_uart_hal.c

- [x] Verify pin mapping against PR description
  - [x] ICM-42688-P IMU on SPI1 (CS, SCK, MISO, MOSI, EXTI)
  - [x] SPL06 barometer on I2C1 (PB8/PB9)
  - [x] W25N01G flash on SPI2
  - [x] UART4 with TX/RX swap on Port A
  - [x] UART1 on PA9/PA10 (not PB6/PB7)

---

## Phase 2: Build Verification

- [x] Checkout PR branch
  ```bash
  cd ~/Documents/planes/inavflight/inav
  git fetch upstream pull/11324/head:pr-11324
  git checkout pr-11324
  ```

- [x] Build NEXUS target
  ```bash
  make TARGET=NEXUS
  ```
  - [x] Build succeeds without errors
  - [x] No unexpected warnings
  - [x] Flash size within limits (~512KB available)

- [x] Verify build artifacts
  - [x] `obj/main/NEXUS/inav_NEXUS.bin` exists
  - [x] File size reasonable (~400-500KB expected)

---

## Phase 3: Hardware Testing (Nexus FC Required)

### 3.1 Flash and Boot

- [x] Flash firmware via DFU
  - [x] Enter DFU mode (hold button while plugging USB)
  - [x] Flash with Configurator or `dfu-util`
  - [x] Verify flash succeeds

- [x] Boot verification
  - [x] FC boots normally (LED status)
  - [x] USB enumeration works
  - [x] Configurator connects successfully
  - [x] Correct target name shows in Configurator ("NEXUS")

### 3.2 IMU (ICM-42688-P on SPI1)

- [x] Sensor detection
  - [x] Gyro detected in Configurator
  - [x] Accel detected in Configurator
  - [x] Correct sensor name shown (ICM-42688-P)

- [x] Orientation verification (CW90 alignment per PR)
  - [x] Pitch forward → aircraft pitches forward in OSD
  - [x] Roll right → aircraft rolls right in OSD
  - [x] Yaw right → heading increases

- [x] Sensor data
  - [x] Gyro values reasonable (near 0 when stationary)
  - [x] Accel values reasonable (~1g on Z-axis)
  - [x] No SPI errors in debug output

### 3.3 Barometer (SPL06 on I2C1)

- [x] Sensor detection
  - [x] Baro detected in Configurator
  - [x] Correct sensor name shown (SPL06)

- [x] Data verification
  - [x] Altitude reads reasonable value
  - [x] Altitude changes when moving FC up/down
  - [x] Temperature reading reasonable

### 3.4 Blackbox Flash (W25N01G on SPI2)

- [x] Flash detection
  - [x] Flash chip detected in Configurator
  - [x] Correct size shown (128MB)

- [x] Blackbox logging
  - [x] Enable blackbox logging
  - [x] Start logging
  - [x] Verify log file created
  - [x] Download and verify log readable

### 3.5 UART Testing

- [x] UART4 with TX/RX swap (Port A for CRSF)
  - [x] Configure UART4 as CRSF/ELRS
  - [x] Connect CRSF receiver to Port A
  - [x] Verify receiver connects (channels visible)
  - [x] Verify TX/RX swap works correctly

- [x] UART6 (Port B)
  - [x] Receiver connected
  - [x] Data received

- [x] UART3 (Port C)
  - [x] Receiver connected  
  - [x] Data received

- [ ] UART1 (PA9/PA10)
  - [ ] Skipped

- [ ] UART2 (PA2/PA3)
  - [ ] Skipped

### 3.6 Motor/Servo Outputs (S1-S4 + M1)

- [x] Output mapping
  - [x] S1-S4 work as servo outputs
  - [x] M1 works as motor output

- [x] Motor testing
  - [x] Configure motor output
  - [x] Test motor spins in correct direction

- [x] Servo testing
  - [x] Configure servo outputs
  - [x] Test servo responds to commands

### 3.7 ADC (Voltage/Current)

- [x] Voltage reading
  - [x] ADC pin configured correctly
  - [x] Voltage reading shows (scale calibration needed)

### 3.8 Other Peripherals

- [x] LED (status LED)
  - [x] LED blinks/flashes correctly
  - [x] LED shows correct status

---

## Phase 4: SITL Testing (Build Only)

- [x] SITL build with target
  - [x] No build regressions from PR changes
  - [x] `serial_uart_hal.c` changes don't break SITL

---

## Phase 5: Regression Testing

- [x] No impact on other targets
  - [x] NEXUSX target still builds
  - [x] Other F722 targets still build

- [x] UART4 swap code doesn't affect other targets
  - [x] Review `USE_UART4_SWAP` implementation
  - [x] Verify only affects NEXUS target

---

## Phase 6: Documentation Check

- [x] Board documentation
  - [x] Target name unique and appropriate
  - [x] Board identifier correct

- [x] Code quality
  - [x] Pin definitions match PR description
  - [x] Comments explain non-obvious choices
  - [x] No debugging code left in

---

## Phase 7: Reporting

- [x] Create test report
  - [x] Document all test results (pass/fail)
  - [x] Note any issues found
  - [x] Include hardware setup details

- [x] Report on PR
  - [ ] Comment on PR with test results
  - [ ] Note any issues or suggestions
  - [x] Recommend merge

---

## Completion

- [x] All test phases complete
- [x] Test report created
- [ ] Feedback provided to PR author
- [ ] Follow-up issues created (if needed)
- [ ] Completion report sent to manager

---

## Test Environment

| Item | Details |
|------|---------|
| Hardware | RadioMaster Nexus (original) FC |
| Test Date | 2026-02-18 |
| Configurator Version | 9.x |
| PR Branch | pr-11324 |
| Base Commit | maintenance-9.x |

## Final Result: ✅ PASS

All critical hardware tests passed. Ready for merge.
