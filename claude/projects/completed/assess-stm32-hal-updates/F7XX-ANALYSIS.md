# STM32F7xx HAL Analysis

**Date:** 2026-02-20
**Analyst:** Developer

## Current State Summary

### Version Information

| Property | Current | Latest (2025) | Gap |
|----------|---------|---------------|-----|
| HAL Version | V1.2.2 | V1.3.3 | 8+ years |
| Release Date | 14-April-2017 | 23-July-2025 | ~99 months |

**Critical Finding:** INAV's STM32F7xx HAL is **8+ years outdated**.

### File Statistics

| Metric | Count |
|--------|-------|
| Source files (.c) | 88 |
| Header files (.h) | 97 |
| TODO/FIXME comments | 0 |

### Location

```
inav/lib/main/STM32F7/Drivers/STM32F7xx_HAL_Driver/
├── Inc/   (97 headers)
└── Src/   (88 source files)
```

### HAL Configuration

INAV uses a custom `stm32f7xx_hal_conf.h` at:
```
inav/src/main/target/stm32f7xx_hal_conf.h
```

**Enabled Modules:**
- HAL_ADC_MODULE
- HAL_RTC_MODULE
- HAL_SD_MODULE
- HAL_SPI_MODULE
- HAL_TIM_MODULE
- HAL_UART_MODULE
- HAL_USART_MODULE
- HAL_PCD_MODULE (USB)
- HAL_GPIO_MODULE
- HAL_DMA_MODULE
- HAL_RCC_MODULE
- HAL_FLASH_MODULE
- HAL_PWR_MODULE
- HAL_I2C_MODULE
- HAL_CORTEX_MODULE

**Disabled Modules:** CAN, CEC, CRC, CRYP, DAC, DCMI, DMA2D, ETH, NAND, NOR, SRAM, SDRAM, HASH, I2S, IWDG, LPTIM, LTDC, QSPI, RNG, SAI, MMC, SPDIFRX, IRDA, SMARTCARD, WWDG, HCD, DFSDM, DSI, JPEG, MDIOS, SMBUS

## Peripheral Modules Available

### HAL Drivers
adc, adc_ex, can, cec, cortex, crc, crc_ex, cryp, cryp_ex, dac, dac_ex, dcmi, dcmi_ex, dfsdm, dma, dma2d, dma_ex, dsi, eth, flash, flash_ex, gpio, hash, hash_ex, hcd, i2c, i2c_ex, i2s, irda, iwdg, jpeg, lptim, ltdc, ltdc_ex, mdios, mmc, nand, nor, pcd, pcd_ex, pwr, pwr_ex, qspi, rcc, rcc_ex, rng, rtc, rtc_ex, sai, sai_ex, sd, sdram, smartcard, smartcard_ex, smbus, spdifrx, spi, sram, tim, tim_ex, uart, usart, wwdg

### LL (Low-Level) Drivers
ll_adc, ll_crc, ll_dac, ll_dma, ll_dma2d, ll_exti, ll_fmc, ll_gpio, ll_i2c, ll_lptim, ll_pwr, ll_rcc, ll_rng, ll_rtc, ll_sdmmc, ll_spi, ll_tim, ll_usart, ll_usb, ll_utils

## Code Quality Observations

1. **No TODO/FIXME comments** - Clean baseline, no known issues documented in code
2. **Standard ST structure** - Follows STM32Cube HAL conventions
3. **No local modifications** - Appears to be stock ST distribution

## Missing from Latest HAL (V1.3.3)

Based on STM32CubeF7 release notes, the following updates are missing:

### Bug Fixes (V1.2.3 - V1.3.3)
- Multiple CAN driver fixes
- ETH driver improvements
- USB PCD/HCD fixes
- I2C timing calculations
- SPI DMA handling
- SD card reliability improvements
- Flash write protection fixes

### Enhancements
- Improved error handling
- Better DMA integration
- Power optimization improvements
- Updated for newer silicon revisions

## Known STM32F7xx Errata

The STM32F7 series has documented silicon errata that may require HAL workarounds:
- ADC accuracy issues
- CAN FD mode limitations
- USB OTG issues on certain revisions
- Ethernet MAC bugs
- Flash latency requirements

## CMSIS Device Status

CMSIS Device headers must be updated alongside HAL:

| Component | Current Version | Current Date | Latest Version |
|-----------|-----------------|--------------|----------------|
| CMSIS Device | V1.2.0 | 30-December-2016 | V1.3.0+ |
| HAL Driver | V1.2.2 | 14-April-2017 | V1.3.3 |

**Location:** `inav/lib/main/STM32F7/Drivers/CMSIS/Device/ST/STM32F7xx/`

**CMSIS Includes:**
- `stm32f7xx.h` — Main device header
- `stm32f722xx.h` through `stm32f779xx.h` — Device-specific headers
- `system_stm32f7xx.h` — System initialization

**Why Update CMSIS:**
1. Register definitions may include errata workarounds
2. New peripheral bit definitions
3. Updated device variant support
4. Maintains compatibility with updated HAL

## Risk Assessment for F7xx Update

| Risk | Level | Description |
|------|-------|-------------|
| API compatibility | LOW | ST maintains HAL API stability within major versions |
| Binary size | LOW | HAL is modular, only enabled modules affect size |
| Testing effort | MEDIUM | Need to verify all peripheral drivers |
| Breaking changes | LOW | V1.2.2 → V1.3.3 is minor version update |
| CMSIS compatibility | LOW | Update CMSIS from same STM32Cube package |

## Recommendations for F7xx

1. **HIGH PRIORITY:** Update to V1.3.3 for bug fixes and security
2. **Update CMSIS Device** from same STM32CubeF7 package release
3. Enable HAL_CAN_MODULE if DroneCAN is used
4. Review errata workarounds in newer HAL
5. Test all enabled modules after update
6. **Optional:** Replace `GPIO_SPEED_HIGH` with `GPIO_SPEED_FREQ_VERY_HIGH` in `vcp_hal/usbd_conf_stm32f7xx.c`

## API Compatibility Verification

All HAL APIs used by INAV are compatible with V1.3.3:

| API Category | Functions | Compatible |
|--------------|-----------|------------|
| HAL_GPIO_* | Init, WritePin, ReadPin, TogglePin | ✅ |
| HAL_UART_* | Init, IRQHandler, etc. | ✅ |
| HAL_I2C_* | Init, Mem_Read/Write, IRQHandler | ✅ |
| HAL_TIM_* | Base_Init, PWM_Start, etc. | ✅ |
| HAL_PCD_* | USB device functions | ✅ |
| HAL_QSPI_* | Command, Transmit, Receive | ✅ |
| HAL_SD_* | IRQHandler | ✅ |
| HAL_RCC_* | ClockConfig, OscConfig, etc. | ✅ |
| __HAL_* macros | All interrupt/flag macros | ✅ |

**Zero code changes required** for HAL library update.
