# FrSky F405 FC - Pin Mapping Analysis

**Date:** 2026-01-16
**MCU:** STM32F405RGT6 (64-pin LQFP)
**Source:** claude/developer/workspace/frsky_f405_fc.pdf

---

## MCU Pin Assignments (from Page 2 - MCU.SchDoc)

### Timer/PWM Outputs

From Page 1 (CONN.SchDoc) cross-referenced with Page 2 (MCU.SchDoc):

| Output | Signal | MCU Pin | GPIO | Timer Channel | Function |
|--------|--------|---------|------|---------------|----------|
| S1 | T2_1 | 15 | PA1 | TIM2_CH2 | Motor 1 |
| S2 | T12_1 | 35 | PB14 | TIM12_CH1 | Motor 2 |
| S3 | T12_2 | 36 | PB15 | TIM12_CH2 | Motor 3 |
| S4 | T1_1 | 41 | PA8 | TIM1_CH1 | Motor 4 |
| S5 | T3_3 | 26 | PB0 | TIM3_CH3 | Motor 5 |
| S6 | T3_4 | 27 | PB1 | TIM3_CH4 | Motor 6 |
| S7 | T8_3 | 39 | PC8 | TIM8_CH3 | Motor 7 |
| S8 | T8_4 | 40 | PC9 | TIM8_CH4 | Motor 8 |
| S9 | T4_2 | 59 | PB7 | TIM4_CH2 | Motor 9 |

**Total timer channels:** 9 motor outputs - all confirmed ✅

**Connector Labeling Clarification:**
R1-R6 and T1-T6 labels on connectors are UART RX/TX signal names, NOT servo outputs:
- **R** = Receive (RX)
- **T** = Transmit (TX)
- Numbers = UART number (R1/T1 = UART1, R2/T2 = UART2, etc.)

See UART section below for complete UART pin mappings.

---

### SPI Buses

#### SPI1 (Gyro - IIM-42688P)
| Signal | MCU Pin | GPIO |
|--------|---------|------|
| SPI1_NSS | 20 | PA4 |
| SPI1_CLK | 21 | PA5 |
| SPI1_MISO | 22 | PA6 |
| SPI1_MOSI | 23 | PA7 |
| GYRO.INT1 | 24 | PC4 |

#### SPI2 (OSD - AT7456E)
| Signal | MCU Pin | GPIO |
|--------|---------|------|
| SPI2_NSS | 33 | PB12 |
| SPI2_CLK | 34 | PB13 |
| SPI2_MISO | 10 | PC2 |
| SPI2_MOSI | 11 | PC3 |

#### SPI3 (SD Card)
| Signal | MCU Pin | GPIO |
|--------|---------|------|
| SPI3_NSS | 3 | PC14 |
| SPI3_CLK | 51 | PC10 |
| SPI3_MISO | 52 | PC11 |
| SPI3_MOSI | 53 | PC12 |

⚠️ **ISSUE:** PC14 for SPI3_NSS is unusual - this pin is typically OSC32_IN (32kHz RTC crystal input)!

---

### I2C Buses

#### I2C1 (Barometer - SPL06)
| Signal | MCU Pin | GPIO | Notes |
|--------|---------|------|-------|
| IIC1_SCL | 61 | PB8 | |
| IIC1_SDA | 62 | PB9 | |

SPL06 Address: 0x76

#### I2C2
| Signal | MCU Pin | GPIO | Notes |
|--------|---------|------|-------|
| IIC2_SCL | 29 | PB10 | ⚠️ Conflicts with USART3_TX |
| IIC2_SDA | 30 | PB11 | ⚠️ Conflicts with USART3_RX |

---

### UART Assignments

| UART | TX Pin | TX GPIO | RX Pin | RX GPIO | Notes |
|------|--------|---------|--------|---------|-------|
| USART1 | 42 | PA9 | 43 | PA10 | |
| USART2 | 16 | PA2 | 17 | PA3 | SBUS input via inverter |
| USART3 | 29 | PB10 | 30 | PB11 | ⚠️ Conflicts with I2C2! |
| UART4 | 14 | PA0 | 25 | PC5 | RX shares with RSSI_IN |
| UART5 | 53 | PC12 | 54 | PD2 | ⚠️ TX conflicts with SPI3_MOSI! |
| USART6 | 37 | PC6 | 38 | PC7 | |

---

### ADC Channels

| Signal | MCU Pin | GPIO | ADC Channel |
|--------|---------|------|-------------|
| VBAT_ADC | 8 | PC0 | ADC123_IN10 |
| CURR_ADC | 9 | PC1 | ADC123_IN11 |
| RSSI_IN | 25 | PC5 | ADC12_IN15 |

**Note:** Current sensor uses INA139 with 0.25mΩ shunt resistor

---

### Other Peripherals

| Function | MCU Pin | GPIO | Notes |
|----------|---------|------|-------|
| BUZZ-_MCU | 4 | PC15 | Buzzer control (active low) |
| LED (Blue) | 49 | PA14 | Status LED via R34 1K, **shares SWCLK** |
| LED (Green) | 46 | PA13 | Status LED via R35 1K, **shares SWDIO** |
| LED (Red) | - | - | Likely power indicator (VCC), no GPIO control |
| LED (CON23) | 50 | PA15 | LED strip output (T2_1), TIM2_CH1 |
| SWDIO | 46 | PA13 | SWD debug (**shared with Green LED**) |
| SWCLK | 49 | PA14 | SWD debug (**shared with Blue LED**) |
| USB_DD_P | 44 | PA11 | USB D+ |
| USB_DD_N | 45 | PA12 | USB D- |
| BOOT0 | 60 | BOOT0 | Boot mode selection |
| NRST | 7 | NRST | Reset |

---

## Critical Issues Found

### 1. Missing Timer Channels
- **Expected:** 15 PWM outputs (9 motors + 6 servos/LEDs)
- **Found:** Only 10 timer channels defined in schematic
- **Impact:** Cannot support all advertised outputs without additional timer mapping

### 2. PC13 Used for SPI3_NSS
- **Issue:** PC13 is typically RTC/battery-backup domain
- **Risk:** May cause issues with SD card reliability
- **Recommendation:** Consider alternative CS pin if possible

### 3. Pin Conflicts

#### USART3 vs I2C2 (PB10/PB11)
- Both peripherals share the same pins
- **Likely intent:** User must choose between USART3 OR I2C2 (can't use both)
- **Common pattern:** Many FCs have this limitation

#### UART5_TX vs SPI3_MOSI (PC12)
- Both share PC12
- **Likely intent:** User must choose between UART5 OR SD card (can't use both)
- **Impact:** Limits simultaneous peripheral usage

#### UART4_RX vs RSSI (PC5)
- May be intentional - RSSI might come via UART protocol
- **Typical use:** RSSI on UART4 RX pin

### 4. Connector Mapping Incomplete
- Page 1 shows connectors CON1-CON23
- Page 2 shows MCU pins
- **Missing:** Clear mapping of which timer channel goes to which output connector
- **Need:** Cross-reference signal names between pages

---

## Next Steps

1. ✅ Extract MCU pin assignments (DONE)
2. ⏳ Map timer signals to output connectors (IN PROGRESS)
3. ⏳ Determine which 10 of 15 outputs actually have timer support
4. ⏳ Document all pin conflicts and alternatives
5. ⏳ Create target.h file with conditional compilation for conflicts
6. ⏳ Add clear documentation about limitations

---

## Questions/Uncertainties

1. **Which 10 outputs get PWM?** Need to trace S1-S9 and T1-T6 signals to see which are connected to timers
2. **Are some outputs GPIO-only?** Possible that 5 outputs are just on/off, not PWM
3. **LED output pins?** Schematic mentions LED output but pins not clearly identified
4. **Timer conflicts?** Need to check if any timers share DMA streams
