# HAL Update Impact Analysis

**Date:** 2026-02-20
**Analyst:** Developer

## INAV HAL Usage Patterns

### Hybrid HAL/LL Architecture

INAV uses a hybrid approach:
- **HAL** for initialization and configuration
- **LL (Low-Layer)** for performance-critical operations
- **Direct register access** for IRQ handlers

This reduces HAL update risk since most hot paths bypass HAL state machine.

## Impact by Peripheral

### HAL_UART (HIGH IMPACT AREA)

**Current Usage:**
```c
// Initialization via HAL
HAL_UART_Init(), HAL_UART_DeInit(), HAL_HalfDuplex_Init()

// IRQ handling - Direct register access
huart->Instance->RDR  // RX data register
huart->Instance->TDR  // TX data register
huart->Instance->CR1  // Control register
huart->Instance->CR3  // Control register

// Flag manipulation
__HAL_UART_ENABLE_IT()
__HAL_UART_GET_FLAG()
__HAL_UART_CLEAR_IDLEFLAG()
```

**Impact Assessment:**
| Version Change | API Change | Risk |
|----------------|------------|------|
| V1.2.2 → V1.3.3 | UART_RxEvent_Callback signature | LOW |
| V1.2.2 → V1.3.3 | DMA abort procedure fix | MEDIUM |
| V1.2.2 → V1.3.3 | ReceptionToIdle DMA fixes | LOW |

**Recommendation:** Test all UART-based protocols after update (CRSF, MSP, GPS, telemetry)

### HAL_I2C (MEDIUM IMPACT AREA)

**Current Usage:**
```c
HAL_I2C_Init()
HAL_I2C_Master_Transmit(), HAL_I2C_Master_Receive()
HAL_I2C_Mem_Write(), HAL_I2C_Mem_Read()
HAL_I2C_ER_IRQHandler(), HAL_I2C_EV_IRQHandler()
HAL_I2CEx_ConfigAnalogFilter()

// Custom TIMINGR calculation
i2cClockTIMINGR()  // Computes I2C timing based on PCLK
```

**Impact Assessment:**
| Version Change | API Change | Risk |
|----------------|------------|------|
| V1.2.2 → V1.3.3 | IsDeviceReady() trial count fix | LOW |
| V1.2.2 → V1.3.3 | Transmission stalled workaround | HIGH |
| V1.2.2 → V1.3.3 | 10-bit addressing fix | LOW |

**Recommendation:** The "transmission stalled after first byte" fix is critical - verify I2C sensors work correctly.

### HAL_SPI (LOW IMPACT - USES LL)

**Current Usage:**
```c
// Uses LL API instead of HAL
LL_SPI_Init()
LL_SPI_TransmitData8()
LL_SPI_ReceiveData8()
LL_SPI_SetTransferDirection()
```

**Impact Assessment:**
HAL SPI updates have minimal impact since INAV uses LL API.

**Risk:** LL API changes could affect SPI driver - verify LL stability across versions.

### HAL_TIM (HIGH IMPACT AREA)

**Current Usage:**
```c
// HAL for configuration
HAL_TIM_Base_Init(), HAL_TIM_Base_Start()
HAL_TIM_PWM_ConfigChannel(), HAL_TIM_PWM_Start()
HAL_TIM_IC_ConfigChannel()
HAL_TIMEx_MasterConfigSynchronization()

// LL for DMA operations
LL_TIM_EnableDMAReq_CCx(), LL_TIM_DisableDMAReq_CCx()
LL_TIM_CC_EnableChannel()
LL_DMA_Init()
```

**Impact Assessment:**
| Version Change | API Change | Risk |
|----------------|------------|------|
| V1.2.2 → V1.3.3 | UIF clearing fix | MEDIUM |
| V1.2.2 → V1.3.3 | Encoder mode fixes | LOW |
| V1.2.2 → V1.3.3 | DMA request source selection | MEDIUM |

**Recommendation:** Test all timer-based functions (PWM, PPM, DSHOT, servo outputs)

### HAL_GPIO (LOW IMPACT)

**Current Usage:**
```c
HAL_GPIO_Init()
HAL_GPIO_ReadPin()
HAL_GPIO_WritePin()
HAL_GPIO_TogglePin()
```

**Impact Assessment:**
Standard HAL usage with stable API. Low risk.

### HAL_CAN (DISABLED)

**Current Status:**
`HAL_CAN_MODULE_ENABLED` is commented out in hal_conf.h.

**DroneCAN Note:** INAV uses external libcanard library for CAN, not HAL_CAN. Update has no impact.

### HAL_USB (MEDIUM IMPACT)

**Current Usage:**
```c
HAL_PCD_MODULE_ENABLED  // USB Device
// HCD (USB Host) disabled
```

**Impact Assessment:**
| Version Change | API Change | Risk |
|----------------|------------|------|
| V1.2.2 → V1.3.3 | Connection/disconnect fixes | MEDIUM |
| V1.2.2 → V1.3.3 | Channel halt fixes | MEDIUM |

**Recommendation:** Test USB MSC and CLI functionality.

### HAL_SD/SDMMC (MEDIUM IMPACT)

**Current Usage:**
```c
HAL_SD_MODULE_ENABLED
```

**Impact Assessment:**
| Version Change | API Change | Risk |
|----------------|------------|------|
| V1.2.2 → V1.3.3 | SD card reliability fixes | HIGH |
| V1.2.2 → V1.3.3 | Timeout handling fixes | MEDIUM |

**Recommendation:** Critical - test blackbox SD card logging extensively.

## STM32H7-Specific Workarounds

INAV has H7-specific workarounds that may need adjustment:

```c
// inav/src/main/system_stm32h7xx.c
USE_H7_HSERDY_SLOW_WORKAROUND   // HSE ready >10s issue
USE_H7_HSE_TIMEOUT_WORKAROUND   // Force reset on HSE timeout
HandleStuckSysTick()            // SysTick recovery
```

**Impact:** These workarounds interact with HAL_RCC_OscConfig(). Verify after update.

## Breaking Change Analysis

### V1.2.2 → V1.3.3 Breaking Changes: NONE

ST maintains API compatibility within major versions. All changes are:
- Bug fixes
- Internal improvements
- New optional features

### HAL API Compatibility Verification

Analysis of all HAL API calls in INAV source code (`inav/src/main/`):

```
┌─────────────────────────────────────────────────────────────────┐
│ HAL API COMPATIBILITY                                           │
├─────────────────────────────────────────────────────────────────┤
│ Deprecated APIs:      1 (GPIO_SPEED_HIGH)                      │
│ Removed APIs:         0                                         │
│ Renamed APIs:         0                                         │
│ Breaking changes:     0                                         │
├─────────────────────────────────────────────────────────────────┤
│ STATUS: FULLY COMPATIBLE                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Deprecated API Found:**
| API | Location | Occurrences | Replacement | Deprecated In |
|-----|----------|-------------|-------------|---------------|
| `GPIO_SPEED_HIGH` | `vcp_hal/usbd_conf_stm32f7xx.c` | 4 | `GPIO_SPEED_FREQ_VERY_HIGH` | V1.2.8 |

**Note:** `GPIO_SPEED_HIGH` remains functional via `stm32_hal_legacy.h` alias. No immediate action required.

**HAL APIs Used by INAV (all compatible):**

| Category | Functions/Macros | Usage Count |
|----------|------------------|-------------|
| GPIO | `HAL_GPIO_Init`, `HAL_GPIO_WritePin`, etc. | ~30 |
| UART | `HAL_UART_*`, `__HAL_UART_*` | ~30 |
| I2C | `HAL_I2C_*`, `HAL_I2CEx_*` | 8 |
| TIM | `HAL_TIM_*`, `__HAL_TIM_*` | 10 |
| USB (PCD) | `HAL_PCD_*` | 40+ |
| QSPI | `HAL_QSPI_*` | 18 |
| SD | `HAL_SD_*` | 2 |
| RCC | `HAL_RCC_*`, `__HAL_RCC_*` | 30+ |
| DMA | `HAL_DMA_*` | 5 |
| NVIC | `HAL_NVIC_*` | 32 |

### CMSIS Device Updates

CMSIS Device updates are **required** alongside HAL updates:

| Component | Impact | Notes |
|-----------|--------|-------|
| Register definitions | LOW | May include new reserved bits |
| Peripheral structures | LOW | Usually stable |
| Bit macros | LOW | New definitions added, rarely removed |
| Device variants | LOW | New chip variants supported |

**Recommendation:** Update CMSIS Device from the same STM32Cube package release to ensure HAL/CMSIS compatibility.

### Migration Path

1. Download complete STM32CubeF7 package (includes HAL + CMSIS)
2. Replace HAL library files (no code changes required)
3. Replace CMSIS Device headers
4. Update stm32f7xx_hal_conf.h if new modules added
5. Test all peripherals
6. Verify errata workarounds still needed

## Testing Matrix

| Peripheral | Test Command | Pass Criteria |
|------------|--------------|---------------|
| UART (CRSF) | Connect CRSF RX | Telemetry displays |
| UART (GPS) | Connect GPS | Fix acquired |
| UART (MSP) | Connect Configurator | Device connects |
| I2C (Baro) | Power on | Altitude reads |
| I2C (Mag) | Compass enabled | Heading reads |
| SPI (Gyro) | Power on | IMU data valid |
| SPI (Flash) | Read flash | Data correct |
| SD Card | Start blackbox | Log writes |
| USB MSC | Connect USB | Mounts as drive |
| PWM Out | Motor test | Motors spin |
| DSHOT | DSHOT test | ESC responds |

## Update Sequence Recommendation

### Phase 1: F7xx Update
1. Backup current HAL
2. Replace with V1.3.3
3. Build and test on F7 target
4. Run full hardware test suite

### Phase 2: F4xx Update  
1. Same process as F7xx
2. Test on F4 target

### Phase 3: H7xx Review
1. Determine current version
2. Update if more than 2 versions behind
3. Verify workarounds still needed

## Conclusion

The HAL update is **low-risk** from an API perspective but requires **thorough testing** due to:
1. Custom register access in IRQ handlers
2. Mixed HAL/LL usage in timers
3. H7-specific workarounds
4. SD card reliability improvements needed

Estimated testing effort: 16-26 hours per platform.
