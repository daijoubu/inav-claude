# Task Completed: Test NEXUS DSM Verification

**Date:** 2026-02-21 11:18 | **From:** Developer | **To:** Manager | **Status:** COMPLETED

## Summary
DSM/Spektrum is NOT supported on the NEXUS target due to the STM32F722's 512KB flash limitation. This is by design in INAV, not a bug in PR #11324. Testing confirmed the Spektrum code is conditionally compiled out for memory-constrained targets.

## Technical Findings

### Flash Constraint Analysis
1. The NEXUS target uses STM32F722RET6 with exactly 512KB flash
2. In target/common.h lines 221-225, targets with MCU_FLASH_SIZE <= 512 have USE_SERIALRX_SPEKTRUM explicitly undefined to save flash space
3. This also disables USE_TELEMETRY_SRXL (Spektrum telemetry)

### Verified Protocols on NEXUS
- SBUS: ENABLED (available on UART1/UART2)
- IBUS: ENABLED
- FPORT/FPORT2: ENABLED
- CRSF: ENABLED (default on UART4)
- SPEKTRUM/DSM: DISABLED (512KB flash limitation)
- SRXL Telemetry: DISABLED (512KB flash limitation)

## Code References
- `cmake/stm32.cmake:173-175` - Size "E" = 512KB
- `cmake/stm32f7.cmake:140` - define_target_stm32f7(22 e)
- `target/common.h:221-225` - #undef USE_SERIALRX_SPEKTRUM for <=512KB targets

## Testing
Hardware verification attempted. Confirmed DSM satellite would not bind, which is expected behavior given Spektrum code is not compiled in for 512KB targets.

## Recommendation
Update the NEXUS target README.md in PR #11324 to document that DSM is not supported due to flash constraints. Users needing DSM should use SBUS on UART1 as an alternative (SBUS receivers are widely available and well-supported).

**No code changes required** - this is expected behavior for 512KB flash targets.

## Project
test-nexus-dsm-verification

---
**Developer**
