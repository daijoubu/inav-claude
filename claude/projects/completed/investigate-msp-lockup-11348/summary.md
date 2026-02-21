# Project: investigate-msp-lockup-11348

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Investigation
**Created:** 2026-02-20
**Assigned:** 2026-02-20
**Estimated Effort:** 4-8 hours

## Overview

Investigate a critical FC lock-up issue caused by MSP communication combined with LOG_DEBUG usage. The FC freezes completely when MSP reader is disconnected, potentially due to an infinite loop in serial/MSP code.

## Problem

When using LOG_DEBUG statements and disconnecting the MSP reader:
- FC locks up completely (controls, telemetry stop)
- Motors continue at last commanded state
- Cannot disarm
- FC resumes normal operation when MSP reader reconnects

This has caused 6 plane crashes for the reporter. The behavior strongly suggests an infinite loop rather than a hard fault.

## Scope

**In Scope:**
- Investigate `msp_serial.c` and `serial.c` for infinite while loops
- Check buffer handling when MSP connection closes
- Identify root cause of lock-up
- Document findings and propose fix

**Out of Scope:**
- Implementing the fix (separate project)

## Investigation Areas

1. **msp_serial.c** - MSP serial protocol handling
2. **serial.c** - Low-level serial communication
3. **LOG_DEBUG implementation** - Buffer and output handling
4. **Buffer overflow/underflow conditions** - Edge cases when reader disconnects

## Root Cause Analysis

**Status:** ✅ IDENTIFIED

The lockup is caused by **4 interconnected bugs** that create a deadlock when MSP reader disconnects with LOG_DEBUG active:

### BUG #1 (CRITICAL): `serialIsConnected()` Missing Return Statement
- **File:** `src/main/drivers/serial.c:111-118`
- **Issue:** Function calls `isConnected()` callback but ignores the return value
- **Result:** Always returns `true` even when port is disconnected
- **Impact:** Connection checks fail, prevents detection of disconnected ports

### BUG #2 (CRITICAL): Infinite Loop in `waitForSerialPortToFinishTransmitting()`
- **File:** `src/main/io/serial.c:505-510`
- **Issue:** No timeout - spins forever if TX buffer never empties
- **Called from:** `src/main/msp/msp_serial.c:480`
- **Result:** When port disconnected, DMA can't drain buffer → infinite loop → system deadlock
- **Impact:** **Direct cause of firmware lock-up**

### BUG #3 (HIGH): Infinite Busy-Wait in `printf.c`
- **File:** `src/main/common/printf.c:229, 288`
- **Issue:** Busy-wait loops with no timeout
- **Impact:** Printf debug output also causes lockups

### BUG #4 (HIGH): `mspLogPort` Never Cleared on Disconnection
- **File:** `src/main/common/log.c:140-141`
- **Issue:** Port set once, never cleared when disconnected
- **Impact:** LOG system unaware of disconnection, keeps pushing to dead port

## Lockup Sequence

1. User connects via USB (MSP/VCP port)
2. User enables LOG_DEBUG for diagnostics
3. High-frequency logging starts (10-100+ Hz)
4. **User disconnects** (USB unplugged, Configurator crashes, network issue)
5. DMA TX buffer has pending log data, no receiver to drain it
6. `serialIsConnected()` returns TRUE despite disconnection (BUG #1)
7. More LOG_DEBUG messages queued to dead port
8. `mspSerialProcessOnePort()` calls `waitForSerialPortToFinishTransmitting()`
9. **Function enters infinite loop** waiting for buffer to empty (BUG #2)
10. Scheduler blocked, firmware frozen
11. No response to inputs, motors stuck at last commanded state
12. Watchdog fires (~5 sec) or manual power cycle needed

## Proposed Fixes

### FIX #1: Return Connection Status
```c
bool serialIsConnected(const serialPort_t *instance)
{
    if (instance->vTable->isConnected)
        return instance->vTable->isConnected(instance);  // Return the result!
    return true;
}
```

### FIX #2: Add Timeout to TX Wait
```c
void waitForSerialPortToFinishTransmitting(serialPort_t *serialPort)
{
    uint32_t startTime = millis();
    const uint32_t timeout = 100;

    while (!isSerialTransmitBufferEmpty(serialPort)) {
        if (millis() - startTime > timeout) break;  // Escape if buffer stuck
        delay(10);
    }
}
```

### FIX #3: Add Timeout to Printf
```c
// In printf.c fputc():
uint32_t startTime = millis();
while (!isSerialTransmitBufferEmpty(printfSerialPort)) {
    if (millis() - startTime > 100) break;  // Escape if port stuck
}
```

### FIX #4: Check Port Connection in Log
```c
// In log.c logPrint():
} else if (mspLogPort && serialIsConnected(mspLogPort->port)) {
    mspSerialPushPort(MSP_DEBUGMSG, (uint8_t*)buf, size, mspLogPort, MSP_V2_NATIVE);
}
```

## Success Criteria

- [x] Root cause identified (4 bugs found)
- [x] Affected code paths documented
- [x] Proposed fix documented (4 fixes detailed)
- [x] Findings reported in summary.md

## Related

- **Issue:** [#11348](https://github.com/iNavFlight/inav/issues/11348)
- **Reporter:** mstrakl
- **Severity:** Critical (6 fatal crashes reported)
- **Affected Version:** 9.0.1
- **Board:** MATEK F405 Wing V2

## Branch

**Base:** `maintenance-9.x`
