# Response: MSP Lockup Testing on STM32F7xx Boards

**Date:** 2026-02-21 15:50 | **From:** Developer | **To:** Manager | **Re:** MSP Lockup Investigation (#11348)

## Answer

**Yes, the MSP lockup can be reproduced and tested on STM32F7xx boards.**

The bugs are in generic code that executes identically across all STM32 families. The F7 board can be used for:

1. **Reproducing the lockup** (before fix)
2. **Verifying the fix** (after implementation)

## Reproduction Steps (for F7 or any board)

1. Connect FC via USB
2. Enable LOG_DEBUG output to MSP port
3. Generate high-frequency log output (e.g., sensor readings)
4. Abruptly disconnect USB cable
5. **Result:** FC should lock up (motors stuck, no response)
6. Reconnect USB → FC resumes

## Testing Plan

Since you have an F7 board available, I recommend:

1. **Baseline test:** Reproduce lockup on current firmware
2. **Apply fix:** Build patched firmware for F7 target
3. **Verification test:** Repeat disconnect scenario - FC should NOT lock up
4. **Stress test:** Multiple rapid connect/disconnect cycles

This multi-platform testing (F4 original report + F7 verification) will give us confidence the fix is robust.

---
**Developer**
