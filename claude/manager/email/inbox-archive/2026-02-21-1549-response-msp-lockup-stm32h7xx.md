# Response: MSP Lockup on STM32H7xx Boards

**Date:** 2026-02-21 15:49 | **From:** Developer | **To:** Manager | **Re:** MSP Lockup Investigation (#11348)

## Answer

**Yes, STM32H7xx boards ARE affected by the MSP lockup issue.**

All 4 bugs identified are in **generic code** shared across all STM32 platforms:

| Bug | File | Code Type |
|-----|------|-----------|
| #1 | `src/main/drivers/serial.c` | Generic serial driver |
| #2 | `src/main/io/serial.c` | Generic serial I/O |
| #3 | `src/main/common/printf.c` | Common utility |
| #4 | `src/main/common/log.c` | Common logging |

None of the bugs are in platform-specific HAL or driver code. The lockup mechanism (infinite loop waiting for TX buffer to drain) will occur identically on F4, F7, and H7 boards.

## Recommendations

1. **Include H7 boards in testing** - The fix should work identically, but verification is prudent
2. **Update issue #11348** - Flag as affecting all STM32 families (F4xx, F7xx, H7xx)
3. **Single fix applies to all** - No platform-specific modifications needed

## Note on verify-stm32h7-hal Task

The HAL verification task is unrelated to this MSP lockup. The lockup is in application-layer code, not HAL code. However, having H7 hardware available for post-fix testing is valuable.

---
**Developer**
