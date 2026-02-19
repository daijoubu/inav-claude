# Project: Add INAV Target for SDMODELH7V2

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Target Port
**Created:** 2026-02-16
**Estimated Effort:** 4-8 hours
**Repository:** inav (firmware)
**Branch:** `maintenance-9.x`

## Overview

Create an INAV target for the SDMODEL SDH7 V2 flight controller. Hardware definitions are available from both Betaflight and ArduPilot.

## Hardware Summary

- **MCU:** STM32H743
- **IMU:** MPU6000 (SPI4, CS=PE4, EXTI=PE1, CW270 alignment)
- **Baro:** BMP280 (I2C1) + MS5611 support
- **Mag:** IST8310 (I2C1, addr 0x0E)
- **OSD:** AT7456E / MAX7456 (SPI2, CS=PB12)
- **Blackbox:** SD card via SPI (SPI1, CS=PA4, detect=PA3 inverted)
- **UARTs:** 6 (UART1-4, UART6, UART7 RX-only)
- **Motors:** 8 outputs (PB0, PB1, PB3, PB10, PA0, PA2, PC8, PC9)
- **LED strip:** PD12
- **ADC:** VBAT=PC0, Current=PC1, RSSI=PC5
- **I2C:** I2C1 (SCL=PB6, SDA=PB7)
- **Beeper:** PC13 (inverted)
- **Camera control:** PE9
- **PINIO:** PE13, PB11
- **LED:** PC2

## Reference Data

- **Betaflight:** `betaflight/src/config/configs/SDMODELH7V2/config.h`
- **ArduPilot:** `ardupilot/libraries/AP_HAL_ChibiOS/hwdef/SDMODELH7V2/`

## Success Criteria

- [ ] INAV target compiles for SDMODELH7V2
- [ ] Pin mappings match BF/AP reference data
- [ ] Timer/DMA assignments verified conflict-free
- [ ] All peripherals defined (gyro, baro, mag, OSD, SD card, UARTs, ADC)
- [ ] Default features set appropriately (OSD, GPS, telemetry, LED strip)

## Related

- **Assignment:** `manager/email/sent/2026-02-16-task-add-target-sdmodelh7v2.md`
