# Project: Create AIKONF4V3 Target

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** New Target / Hardware Support
**Created:** 2026-01-22
**Estimated Effort:** 4-6 hours

## Overview

Use the target engineer agent and the test engineer agent to create a proper INAV target configuration for the Aikon F405 V3 flight controller board using reference files from Betaflight and physical board information.

## Problem

The AIKONF4V3 (Aikon F405 V3) is a different hardware variant from the existing AIKONF4 target in INAV. Key differences may be:

**Existing AIKONF4 target:**
- MPU6000/MPU6500 gyro
- LED on PB5, Beeper on PB4
- No onboard flash or OSD specified

**AIKONF4V3 (this board):**
- ICM42688P gyro (newer, better performance)
- LED on PB4, Beeper on PB5 (swapped!)
- W25Q128FV flash chip
- BMP280/DPS310 barometer support
- MAX7456 OSD chip
- PINIO1 (PB7) for 10V BEC control
- PINIO2 (PB3) for camera control
- Servo outputs on PB0, PB1

The existing target configuration will not work correctly for this board.

## Solution

Create a new target: **AIKONF4V3** using the reference files and Betaflight target configuration as a guide.

**Reference Files Available:**
- `/home/raymorris/Documents/planes/inavflight/aikonf405v3/betaflight_config.h` - Complete Betaflight target
- `/home/raymorris/Documents/planes/inavflight/aikonf405v3/BTFL__cli_20260122_223151.txt` - Betaflight resource mapping
- `/home/raymorris/Documents/planes/inavflight/aikonf405v3/INAV_9.0.0_cli_20260122_223658.txt` - Current INAV config (using wrong target)

## Implementation

### Phase 1: Target Directory Setup (30 min)

1. Create target directory: `inav/src/main/target/AIKONF4V3/`
2. Create required files:
   - `target.h` - Main hardware definitions
   - `target.c` - Timer mappings and initialization
   - `config.c` - Default configuration (optional)

### Phase 2: Hardware Configuration (2-3 hours)

**Use target-developer agent to help with:**
- Pin mapping verification
- Timer/DMA conflict detection and resolution
- Flash memory optimization
- Resource conflict checking (especially UART3 vs I2C potential conflicts)

**Key Components to Configure:**

1. **MCU and Basic Info:**
   ```c
   #define TARGET_BOARD_IDENTIFIER "AKV3"
   #define USBD_PRODUCT_STRING "AIKONF4V3"
   ```

2. **IMU - ICM42688P:**
   ```c
   #define USE_IMU_ICM42605  // ICM42688P uses ICM42605 driver
   #define IMU_ICM42605_ALIGN CW270_DEG
   #define ICM42605_SPI_BUS BUS_SPI1
   #define ICM42605_CS_PIN PA4
   #define ICM42605_EXTI_PIN PC4
   ```

3. **Flash - W25Q128FV:**
   ```c
   #define USE_FLASH_CHIP
   #define USE_FLASH_W25Q128FV
   #define FLASH_CS_PIN PB12
   #define FLASH_SPI_BUS BUS_SPI2
   #define ENABLE_BLACKBOX_LOGGING_ON_SPIFLASH_BY_DEFAULT
   ```

4. **OSD - MAX7456:**
   ```c
   #define USE_OSD
   #define USE_MAX7456
   #define MAX7456_SPI_BUS BUS_SPI3
   #define MAX7456_CS_PIN PA15
   ```

5. **Barometer:**
   ```c
   #define USE_BARO
   #define BARO_I2C_BUS DEFAULT_I2C_BUS
   #define USE_BARO_BMP280
   #define USE_BARO_DPS310
   ```

6. **UARTs:**
   - UART1: TX=PA9, RX=PA10
   - UART2: TX=PA2, RX=PA3
   - UART3: TX=PB10, RX=PB11 (check for I2C conflict)
   - UART4: TX=PA0, RX=PA1
   - UART5: RX=PD2 (RX only)

7. **I2C:**
   - I2C1: SCL=PB8, SDA=PB9

8. **Motor Outputs:**
   - M1: PC6, M2: PC7, M3: PC8, M4: PC9

9. **Servo Outputs:**
   - S1: PB0, S2: PB1

10. **LED Strip:** PB6

11. **PINIO:**
    - PINIO1: PB7 (10V BEC control)
    - PINIO2: PB3 (Camera control)

12. **ADC:**
    - VBAT: PC2, CURRENT: PC1, RSSI: PC3

### Phase 3: Timer Configuration (1-2 hours)

**CRITICAL:** Use target-developer agent to verify timer/DMA assignments.

From Betaflight config:
```c
TIMER_PIN_MAP( 0, PC6 , 2,  1)  // M1 - TIM8 CH1
TIMER_PIN_MAP( 1, PC7 , 2,  1)  // M2 - TIM8 CH2
TIMER_PIN_MAP( 2, PC8 , 2,  1)  // M3 - TIM8 CH3
TIMER_PIN_MAP( 3, PC9 , 2,  0)  // M4 - TIM8 CH4
TIMER_PIN_MAP( 4, PB6 , 1,  0)  // LED - TIM4 CH1
TIMER_PIN_MAP( 5, PB0 , 2, -1)  // S1 - TIM3 CH3
TIMER_PIN_MAP( 6, PB1 , 2, -1)  // S2 - TIM3 CH4
```

Convert to INAV timer def format in `target.c`.

### Phase 4: Build and Test (1-2 hours)

**Use test-engineer agent to:**
1. Build the firmware: `inav-builder agent build AIKONF4V3`
2. Verify flash size fits (target < 480 KB for F405)
3. Check for build errors or warnings
4. Analyze resource assignments

**Test checklist:**
- [ ] Firmware builds without errors
- [ ] Flash usage acceptable (<95%)
- [ ] Timer assignments verified (no conflicts)
- [ ] All resources mapped correctly
- [ ] No UART3/I2C conflicts detected

### Phase 5: Documentation (conditional)

**Only document if:**
- UART3 conflicts with I2C (resource sharing issues)
- Unusual timer/DMA conflicts requiring workarounds
- Special PINIO setup required
- Flash size near limit requiring feature tradeoffs
- Non-standard gyro orientation or calibration needed

Otherwise skip documentation - standard F405 target needs no special docs.

## Success Criteria

- [ ] Target builds successfully
- [ ] All hardware components properly configured
- [ ] Timer/DMA assignments conflict-free
- [ ] Flash usage under 95%
- [ ] Resource mapping matches Betaflight reference
- [ ] Gyro orientation correct (CW270_DEG)
- [ ] Default features configured (OSD, blackbox, telemetry)
- [ ] No UART3/I2C conflicts
- [ ] PINIO pins configured for BEC and camera control
- [ ] Documentation created ONLY if unusual conflicts exist

## Related

- **Reference Target:** AIKONF4 (`inav/src/main/target/AIKONF4/`)
- **Similar F405 Targets:** FLASHHOBBYF405, FOXEERF405 (for ICM42605 examples)
- **Reference Files:** `/home/raymorris/Documents/planes/inavflight/aikonf405v3/`
- **Betaflight Target:** AIKONF4V3

## Notes

**MCU:** STM32F405RGT6
- Flash: 1024 KB
- RAM: 192 KB

**PINIO Usage:**
- PINIO1 (PB7): Controls 10V BEC
- PINIO2 (PB3): Controls cameras 1 & 2

It is possible that some of the above technical details may be incorrect. THose were the result of the manager role over-stepping and micro-managing withotu full knowledge.

**Recommended Workflow:**
1. Use target-developer agent for pin mapping and conflict detection
2. Reference similar F405 targets with ICM42605/ICM42688P
3. Use test-engineer agent for build validation
4. Only document if conflicts or unusual issues found
