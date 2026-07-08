# Re: MSP Lockup Board Compatibility - H7 and F7 Assessment

**Date:** 2026-02-20 08:42 | **From:** Developer | **To:** Manager | **Type:** Question Response

## Answer

YES, both STM32F7xx and STM32H7xx boards are affected by the MSP lockup issue #11348.

## Assessment

The 4 bugs identified in my investigation are in generic, non-board-specific code layers:

- **BUG #1:** `serialIsConnected()` in `src/main/drivers/serial.c`
- **BUG #2:** `waitForSerialPortToFinishTransmitting()` in `src/main/io/serial.c`
- **BUG #3:** `printf.c` busy-wait loops
- **BUG #4:** `mspLogPort` in `src/main/common/log.c`

These are all generic serial/MSP communication modules used across all STM32 families (F4, F7, H7). The root cause is not board-specific hardware behavior, but rather timing and infinite loop issues in the communication layer.

## Implications

- **STM32F7xx boards:** Should be able to reproduce the issue under the same conditions
- **STM32H7xx boards:** Should be able to reproduce the issue under the same conditions
- **All affected boards:** Would benefit from the same 4-fix solution

## Conclusion

This expands the scope of the fix but also confirms it will benefit multiple board families once implemented. I can proceed with implementation knowing the fixes address a cross-platform issue.

---
**Developer**
