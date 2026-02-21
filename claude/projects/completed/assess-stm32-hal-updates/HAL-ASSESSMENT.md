# STM32 HAL Assessment - Final Report

**Date:** 2026-02-20
**Project:** assess-stm32-hal-updates
**Analyst:** Developer

---

## Executive Summary

INAV's STM32 HAL libraries are **significantly outdated**, with F7xx and F4xx versions nearly **9 years behind** current releases. This assessment identifies critical updates needed, evaluates cross-platform impacts, and provides a prioritized roadmap for HAL modernization.

### Key Findings

| Finding | Severity | Impact |
|---------|----------|--------|
| F7xx HAL is 9 years outdated (V1.2.2 → V1.3.3) | HIGH | Missing bug fixes, errata workarounds |
| F4xx HAL is 8 years outdated (V1.7.1 → V1.8.5) | HIGH | Same as F7xx |
| H7xx HAL version unclear but likely recent | MEDIUM | Verify version, update if needed |
| SD card reliability improvements missing | HIGH | Affects blackbox logging |
| I2C transmission stalled fix missing | HIGH | Affects I2C sensors |
| UART DMA race condition fixes missing | MEDIUM | Affects CRSF, GPS, MSP |

### Recommendation

**Proceed with HAL updates in priority order:**
1. STM32F7xx (highest priority - most targets)
2. STM32F4xx (high priority - legacy targets)
3. STM32H7xx (review and update if needed)

---

## Detailed Analysis Documents

| Document | Description |
|----------|-------------|
| [F7XX-ANALYSIS.md](F7XX-ANALYSIS.md) | STM32F7xx HAL current state and version gap |
| [UPDATE-MATRIX.md](UPDATE-MATRIX.md) | Cross-platform comparison matrix |
| [RISK-ASSESSMENT.md](RISK-ASSESSMENT.md) | Impact analysis and testing requirements |

---

## Version Gap Summary

### HAL Driver Versions

```
┌─────────────┬──────────────┬────────────────┬──────────────┬───────────┐
│ MCU FAMILY  │ CURRENT VER  │ CURRENT DATE   │ LATEST VER   │ GAP       │
├─────────────┼──────────────┼────────────────┼──────────────┼───────────┤
│ STM32F7xx   │ V1.2.2       │ 14-April-2017  │ V1.3.3       │ ~9 years  │
│ STM32F4xx   │ V1.7.1       │ 14-April-2017  │ V1.8.5       │ ~8 years  │
│ STM32H7xx   │ Unknown      │ ~2020-2022     │ V1.11.5      │ ~1-4 years│
└─────────────┴──────────────┴────────────────┴──────────────┴───────────┘
```

### CMSIS Device Versions

CMSIS Device headers must be updated alongside HAL for compatibility:

```
┌─────────────┬──────────────┬─────────────────┬──────────────┐
│ MCU FAMILY  │ CMSIS VER    │ DATE            │ STATUS       │
├─────────────┼──────────────┼─────────────────┼──────────────┤
│ STM32F7xx   │ V1.2.0       │ 30-Dec-2016     │ ~9 years old │
│ STM32F4xx   │ Unknown*     │ —               │ Likely old   │
│ STM32H7xx   │ Unknown*     │ —               │ —            │
└─────────────┴──────────────┴─────────────────┴──────────────┘
```

**CMSIS Locations:**
- `inav/lib/main/STM32F7/Drivers/CMSIS/Device/ST/STM32F7xx/`
- `inav/lib/main/STM32F4/Drivers/CMSIS/Device/ST/STM32F4xx/`
- `inav/lib/main/STM32H7/Drivers/CMSIS/Device/ST/STM32H7xx/`

**Why Update CMSIS:**
1. Register definitions may include errata workarounds
2. New peripheral bit definitions
3. Updated device variant support
4. HAL/CMSIS compatibility maintained

---

## Critical Missing Updates

### F7xx V1.2.2 → V1.3.3 (11 releases)

**Bug Fixes:**
- UART: DMA race conditions, reception to idle fixes
- I2C: Transmission stalled workaround, timeout fixes
- SPI: DMA handling improvements
- SD/SDMMC: Reliability improvements
- USB: Connection/disconnect handling
- ETH: Receive process reworked (V1.3.0)

**Enhancements:**
- MISRA-C 2012 compliance
- Code quality improvements
- Errata workarounds integrated

### F4xx V1.7.1 → V1.8.5 (14 releases)

Similar scope of fixes as F7xx.

---

## Risk Assessment

| Risk Category | Level | Mitigation |
|---------------|-------|------------|
| API Breaking Changes | **NONE** | All HAL APIs verified compatible |
| Deprecated API Usage | LOW | 1 deprecated constant (GPIO_SPEED_HIGH) |
| Binary Size Impact | LOW | HAL is modular |
| Regression Testing | MEDIUM | Requires thorough peripheral testing |
| H7 Workarounds | MEDIUM | Verify workarounds still needed |
| Build System | LOW | No cmake changes required |

### API Compatibility Verification

Complete analysis of HAL API usage in INAV source code:

```
┌─────────────────────────────────────────────────────────────────┐
│ HAL API COMPATIBILITY ANALYSIS                                  │
├─────────────────────────────────────────────────────────────────┤
│ Deprecated APIs:      1 (GPIO_SPEED_HIGH)                      │
│ Removed APIs:         0                                         │
│ Renamed APIs:         0                                         │
│ Breaking changes:     0                                         │
├─────────────────────────────────────────────────────────────────┤
│ RESULT: ZERO MODULES REQUIRE CODE CHANGES                       │
└─────────────────────────────────────────────────────────────────┘
```

**Single Deprecated Usage:**
- `GPIO_SPEED_HIGH` → `GPIO_SPEED_FREQ_VERY_HIGH`
- Location: `vcp_hal/usbd_conf_stm32f7xx.c` (4 occurrences)
- Status: Still functional via `stm32_hal_legacy.h` alias

---

## Implementation Roadmap

### Phase 1: STM32F7xx Update (Priority: HIGH)

**Estimated Effort:** 16-26 hours

1. Backup current HAL and CMSIS directories
2. Download STM32CubeF7 latest release (includes HAL + CMSIS)
3. Replace `inav/lib/main/STM32F7/Drivers/STM32F7xx_HAL_Driver/`
4. Replace `inav/lib/main/STM32F7/Drivers/CMSIS/Device/ST/STM32F7xx/`
5. Verify no new modules need enabling in hal_conf.h
6. Build for F7 target (e.g., MATEKF722)
7. Test all peripherals:
   - UART (CRSF, GPS, MSP, telemetry)
   - I2C (baro, mag, OLED)
   - SPI (gyro, flash)
   - SD card (blackbox)
   - USB (MSC, CLI)
   - PWM/DSHOT (motors)

### Phase 2: STM32F4xx Update (Priority: HIGH)

**Estimated Effort:** 16-26 hours

Same process as F7xx, including CMSIS Device update.

### Phase 3: STM32H7xx Review (Priority: MEDIUM)

**Estimated Effort:** 4-8 hours

1. Determine current HAL and CMSIS versions
2. If > 2 versions behind, update both from STM32CubeH7
3. Verify HSE workarounds still needed
4. Test on H7 target (e.g., MATEKH743)

---

## Testing Checklist

After each HAL update, verify:

- [ ] **UART** - CRSF, GPS, MSP, SmartPort, LTM
- [ ] **I2C** - Barometer, compass, OLED display
- [ ] **SPI** - Gyro/IMU, external flash, max7456 OSD
- [ ] **SD Card** - Blackbox logging (stress test)
- [ ] **USB** - MSC mode, CLI, firmware update
- [ ] **PWM** - Motor outputs, servo outputs
- [ ] **DSHOT** - DSHOT600/1200 output
- [ ] **LED** - WS2812 LED strip
- [ ] **ADC** - Battery voltage, current sensor

---

## Deliverables

- [x] F7XX-ANALYSIS.md - STM32F7xx detailed analysis
- [x] UPDATE-MATRIX.md - Cross-platform impact matrix
- [x] RISK-ASSESSMENT.md - Risk analysis and testing requirements
- [x] HAL-ASSESSMENT.md - This main report

---

## Conclusion

The STM32 HAL libraries in INAV require urgent updates. The F7xx and F4xx HALs are nearly 9 years outdated, missing critical bug fixes and errata workarounds. The update process is straightforward (library replacement) but requires comprehensive testing.

**Recommended Action:** Create follow-up tasks to implement HAL updates for each platform.

---

## References

- [STM32CubeF7 HAL Driver](https://github.com/STMicroelectronics/stm32f7xx_hal_driver)
- [STM32CubeF4 HAL Driver](https://github.com/STMicroelectronics/stm32f4xx_hal_driver)
- [STM32CubeH7 HAL Driver](https://github.com/STMicroelectronics/stm32h7xx_hal_driver)
- [STM32CubeF7 Release Notes](https://github.com/STMicroelectronics/stm32f7xx_hal_driver/blob/master/Release_Notes.html)
