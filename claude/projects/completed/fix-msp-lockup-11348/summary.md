# Project: Fix MSP Lock-up Issue #11348

**Status:** 📋 TODO
**Priority:** CRITICAL
**Type:** Bug Fix
**Created:** 2026-02-20
**Estimated Effort:** 8-12 hours
**Base Branch:** `maintenance-9.x`

## Overview

Implement 4 critical bug fixes for MSP/Serial communication deadlock issue that causes FC lock-ups when MSP reader disconnects while LOG_DEBUG is active. Investigation identified root cause as combination of missing error handling, infinite loops without timeouts, and improper resource cleanup.

## Problem

Flight controller freezes completely when MSP reader (Configurator) disconnects while LOG_DEBUG is enabled:
- Controls become unresponsive
- Telemetry stops
- Motors continue at last commanded state
- Cannot disarm or recover without watchdog timeout (~5 seconds) or manual power cycle

**Impact:** 6 plane crashes reported by user mstrakl on MATEK F405 Wing V2
**Issue:** https://github.com/iNavFlight/inav/issues/11348
**Affected Version:** 9.0.1

## Root Cause

4 interconnected bugs create deadlock scenario:

### BUG #1 (CRITICAL): `serialIsConnected()` Missing Return Statement
- **File:** `src/main/drivers/serial.c:111-118`
- **Problem:** Function calls `isConnected()` callback but ignores return value
- **Result:** Always returns `true` even when port is disconnected
- **Impact:** Connection detection fails, enabling further bugs

### BUG #2 (CRITICAL): Infinite Loop in `waitForSerialPortToFinishTransmitting()`
- **File:** `src/main/io/serial.c:505-510`
- **Problem:** No timeout - spins forever if TX buffer never empties
- **Called from:** `src/main/msp/msp_serial.c:480`
- **Result:** When port disconnected, DMA can't drain buffer → infinite loop → system deadlock
- **Impact:** Direct cause of firmware lock-up

### BUG #3 (HIGH): Infinite Busy-Wait in `printf.c`
- **File:** `src/main/common/printf.c:229, 288`
- **Problem:** Busy-wait loops with no timeout
- **Impact:** Printf debug output also causes lockups

### BUG #4 (HIGH): `mspLogPort` Never Cleared on Disconnection
- **File:** `src/main/common/log.c:140-141`
- **Problem:** Port reference set once, never cleared when disconnected
- **Impact:** LOG system keeps pushing to dead port

## Implementation Plan

### Phase 1: Apply Critical Fixes (FIX #1 + #2)
1. Fix `serialIsConnected()` return statement (1 line)
2. Add timeout to `waitForSerialPortToFinishTransmitting()` (5 lines)
3. Compile and basic testing

### Phase 2: Apply Secondary Fixes (FIX #3 + #4)
1. Add timeout to `printf.c` busy-wait (3 lines)
2. Add connection check in `log.c` (1 line)
3. Compile and integration testing

### Phase 3: Testing and Validation
1. Reproduce original issue (should fail with original code)
2. Apply fixes incrementally
3. Verify fix on MATEK F405 hardware
4. Test on additional H7-based boards (pending developer feedback)
5. Run full SITL tests

### Phase 4: Finalization
1. Code review
2. Create pull request
3. Ensure CI passes
4. Get review approval

## Proposed Fixes

### FIX #1: Return Connection Status
**File:** `src/main/drivers/serial.c:111-118`

```c
bool serialIsConnected(const serialPort_t *instance)
{
    if (instance->vTable->isConnected)
        return instance->vTable->isConnected(instance);  // ← Add return statement
    return true;
}
```

**Impact:** 1-line fix, enables proper disconnection detection

---

### FIX #2: Add Timeout to TX Wait
**File:** `src/main/io/serial.c:505-510`

```c
void waitForSerialPortToFinishTransmitting(serialPort_t *serialPort)
{
    uint32_t startTime = millis();
    const uint32_t timeout = 100;  // 100ms max wait

    while (!isSerialTransmitBufferEmpty(serialPort)) {
        if (millis() - startTime > timeout) {
            break;  // Escape if buffer stuck (port likely disconnected)
        }
        delay(10);
    }
}
```

**Impact:** Prevents infinite loop, allows firmware to continue

---

### FIX #3: Add Timeout to Printf
**File:** `src/main/common/printf.c`

Lines 229 and 288 should be updated:

```c
// BEFORE:
while (!isSerialTransmitBufferEmpty(printfSerialPort));

// AFTER:
{
    uint32_t startTime = millis();
    while (!isSerialTransmitBufferEmpty(printfSerialPort)) {
        if (millis() - startTime > 100) break;
    }
}
```

**Impact:** Prevents printf from causing lockups

---

### FIX #4: Check Port Connection in Log
**File:** `src/main/common/log.c:140-141`

```c
// BEFORE:
} else if (mspLogPort) {
    mspSerialPushPort(MSP_DEBUGMSG, (uint8_t*)buf, size, mspLogPort, MSP_V2_NATIVE);
}

// AFTER:
} else if (mspLogPort && serialIsConnected(mspLogPort->port)) {
    mspSerialPushPort(MSP_DEBUGMSG, (uint8_t*)buf, size, mspLogPort, MSP_V2_NATIVE);
}
```

**Impact:** Prevents sending to disconnected port (works after FIX #1 is applied)

---

## Testing Strategy

### Reproduction Test
1. Build firmware with LOG_DEBUG enabled
2. Connect MATEK F405 via USB (Configurator)
3. Enable one DEBUG topic (e.g., `DEBUG_GPS`)
4. Observe: High-frequency logging via MSP
5. **Disconnect USB cable suddenly**
6. **Expected (before fix):** Firmware freezes, watchdog reboot in ~5s
7. **Expected (after fix):** Firmware continues running, can be reconnected

### Verification Test
1. Apply FIX #1 + #2
2. Repeat reproduction test
3. **Expected:** Firmware should handle disconnection gracefully
4. Apply FIX #3 + #4
5. Repeat test for robustness

### Additional Tests
- Rapid connect/disconnect cycles
- Test with different LOG_DEBUG topics
- SITL testing with simulated serial port disconnect
- H7 board testing (pending developer confirmation of H7 applicability)

## Success Criteria

- [ ] All 4 bugs fixed (code changes applied)
- [ ] Code compiles without warnings
- [ ] SITL tests pass
- [ ] Reproduction test passes on MATEK F405
- [ ] Rapid connect/disconnect cycles don't cause issues
- [ ] Code review completed
- [ ] Pull request created and merged
- [ ] Issue #11348 marked as resolved

## Risk Assessment

**Risk Level:** LOW
- All fixes are defensive (add timeout, add return statement, add check)
- No behavior changes when port is connected normally
- Fixes only activate in error scenarios
- Changes are isolated to serial/LOG modules

**Testing Requirement:** HIGH
- Must test on actual hardware (MATEK F405)
- Must test rapid disconnections
- Should test on H7 boards if determined to be affected

## Related

- **Issue:** [#11348](https://github.com/iNavFlight/inav/issues/11348)
- **Reporter:** mstrakl
- **Investigation:** `investigate-msp-lockup-11348` (completed 2026-02-20)
- **Investigation Branch:** `investigate/issue-11348-msp-lockup`
- **Severity:** CRITICAL (6 fatal crashes)
- **Affected Version:** 9.0.1
- **Board:** MATEK F405 Wing V2 (primary), STM32H7xx boards (pending confirmation)

## Implementation Notes

1. **Start with FIX #1 + #2** - These are the critical fixes that prevent the lockup
2. **Order matters** - FIX #4 depends on FIX #1 working correctly
3. **Compile frequently** - Each fix should compile cleanly
4. **Test after each phase** - Verify fixes work incrementally
5. **Use investigation branch** as reference for exact code locations

## Files to Modify

1. `src/main/drivers/serial.c` - FIX #1
2. `src/main/io/serial.c` - FIX #2
3. `src/main/common/printf.c` - FIX #3
4. `src/main/common/log.c` - FIX #4

---

**Created:** 2026-02-20
**Base Branch:** `maintenance-9.x`
