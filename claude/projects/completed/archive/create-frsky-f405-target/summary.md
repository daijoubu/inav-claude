# Project: Create FrSky F405 FC Target Configuration

**Status:** ✅ COMPLETED
**Priority:** MEDIUM
**Type:** Target Development
**Created:** 2026-01-16
**Completed:** 2026-01-16
**Actual Effort:** ~3.5 hours
**Branch:** feature-frsky-f405-target (no commits - documentation only)

## Overview

Create a partial INAV target configuration for the FrSky F405 flight controller based on the schematic located in `claude/developer/workspace/frsky_f405_fc.pdf`.

## Hardware Specifications

### Core Components
- **MCU:** STM32F405RGT6 (64-pin LQFP)
- **Gyro:** IIM-42688P on SPI1
- **Barometer:** SPL06 on I2C1 (address 0x76)
- **OSD:** AT7456E on SPI2
- **Flash:** SD Card on SPI3
- **USB:** Type-C connector

### Peripherals
- **Motor Outputs:** 9 outputs (S1-S9)
  - S1-S4: Connected to T1_1, T2_1, T3_3, T3_4
  - S5-S9: Connected to T8_3, T8_4, T4_1, T4_2, T12_1, T12_2
- **Servo/LED Outputs:** 6 additional outputs (labeled R1-R6/T1-T6)
- **UARTs:**
  - USART1 (U1_TX, U1_RX)
  - USART2 (USART2_TX, USART2_RX)
  - USART3 (USART3_TX, USART3_RX)
  - UART4 (U4_TX, U4_RX)
  - UART5 (U5_TX, U5_RX)
  - USART6 (U6_TX, U6_RX)
- **I2C:**
  - I2C1 (IIC1_SCL, IIC1_SDA) - Barometer
  - I2C2 (IIC2_SCL, IIC2_SDA) - External connector
- **SBUS:** Inverted input on USART2_RX
- **RSSI:** Analog input (RSSI_IN)
- **LED:** Single LED output
- **Buzzer:** Switched output via Q2 (2N7002E)

### Power System
- **Current Sensor:** INA139 with 0.25mΩ shunt (CURR_ADC)
- **Voltage Monitor:** VBAT_ADC with voltage divider
- **Regulators:**
  - 3.3V for MCU (ME6211C33)
  - 5V @ 2A (MP9943A)
  - 9V/12V switchable (MP9943A)
  - VBEC 5A (MP9447)
  - 1.8V for gyro (ME6211A18M3G)

## Objectives

1. **Create target.h file** with pin mappings from schematic
2. **Define timer allocations** for motor/servo outputs
3. **Configure SPI buses** for gyro, OSD, and SD card
4. **Configure I2C buses** for barometer and external devices
5. **Map UARTs** to physical connectors
6. **Configure ADC** for current and voltage monitoring
7. **Document any uncertainties** or assumptions

## Implementation Approach

1. Use the **target-developer agent** to analyze the schematic and extract pin assignments
2. Create a partial target.h file with:
   - MCU definition
   - SPI pin mappings (SPI1 for gyro, SPI2 for OSD, SPI3 for SD)
   - I2C pin mappings
   - UART pin mappings
   - Timer/PWM output mappings
   - ADC channel assignments
   - LED and buzzer pins
3. Identify and document any:
   - Pin conflicts or resource conflicts
   - Timer/DMA conflicts
   - Missing information from schematic

## Key Pin Assignments from Schematic

From the MCU schematic (page 2), key pins include:
- **SPI1:** PA5 (CLK), PA6 (MISO), PA7 (MOSI), PA4 (NSS)
- **SPI2:** PB13 (CLK), PB14 (MISO), PB15 (MOSI), PB12 (NSS)
- **SPI3:** PC10 (CLK), PC11 (MISO), PC12 (MOSI), PC13 or similar (NSS)
- **I2C1:** PB6 (SCL), PB7 (SDA)
- **I2C2:** PB10 (SCL), PB11 (SDA)
- **Timers:** Multiple timer channels for motor/servo outputs
- **ADC:** PC0 (VBAT_ADC), PC1 (CURR_ADC), PC2 (RSSI)

## Success Criteria

- [x] Target.h file created with all pin mappings
- [x] Timer allocations defined for all motor/servo outputs
- [x] SPI buses correctly configured
- [x] I2C buses correctly configured
- [x] UART assignments documented
- [x] ADC channels mapped
- [x] LED and buzzer pins configured
- [x] Documentation includes any assumptions or missing information

## Resources

- **Schematic:** `claude/developer/workspace/frsky_f405_fc.pdf`
- **Reference targets:** Similar F405 targets in `inav/src/main/target/`
- **Agent:** target-developer (`.claude/agents/target-developer.md`)
- **Documentation:** `claude/developer/docs/targets/`

## Notes

- This is a **partial** target configuration - focus on extracting and documenting pins from the schematic
- The developer should use the target-developer agent to assist with analysis
- Don't worry about making it compile - focus on accurate pin extraction
- Document any ambiguities or missing information clearly
- Reference similar F405 targets for timer allocation patterns

## Completion Summary

**Completed:** 2026-01-16 13:30

### Deliverables Created

1. **target.h** (225 lines) - Complete pin definitions for all peripherals
2. **target.c** (92 lines) - Timer definitions with DMA limitation documentation
3. **completion-report.md** (369 lines) - Comprehensive analysis
4. **pin-mapping-analysis.md** (184 lines) - Detailed schematic analysis
5. **STM32F405-TIM12-findings.md** (104 lines) - TIM12 DMA research
6. **dma_conflict_analyzer.py** (193 lines) - Reusable DMA analyzer tool

### Critical Findings

1. ✅ **TIM12 exists but has NO DMA support**
   - Motors S7/S8 (PB14/PB15) cannot use Dshot protocols
   - Standard PWM/OneShot works fine
   - This is a hardware limitation of STM32F405

2. ✅ **No DMA conflicts** - Automated analysis confirmed all timer outputs validated

3. ✅ **Pin conflicts identified and documented:**
   - UART3 vs I2C2 (PB10/PB11) - Default: UART3 enabled
   - UART5 TX vs SD Card (PC12) - Default: SD card enabled
   - Status LEDs share SWD pins - Handled with conditional compilation

4. ✅ **Design corrections:**
   - R1-R6/T1-T6 are UART signals, not PWM outputs (clarified)
   - 9 motor outputs total (S1-S9), not 15
   - PC14 for SD CS is fine (no 32kHz crystal on board)

### Tools Created

Added **dma_conflict_analyzer.py** to `claude/developer/scripts/analysis/`:
- Automated DMA conflict checking for F405 targets
- Validates timer DMA stream assignments
- Checks peripheral conflicts (UART/ADC/SPI)
- Documented and reusable for future targets

### Next Steps (When Hardware Available)

1. Build firmware using inav-builder agent
2. Flash and test all peripherals
3. Verify gyro orientation
4. Test all 9 motor outputs (note S7/S8 Dshot limitation)
5. Create manufacturer PR

**Completion Report:** `claude/manager/email/inbox-archive/2026-01-16-1330-completed-create-frsky-f405-target.md`
