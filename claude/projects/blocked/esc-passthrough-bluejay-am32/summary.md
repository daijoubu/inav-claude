# Project: ESC Passthrough Compatibility for Bluejay/AM32

**Status:** 📋 TODO
**Priority:** High
**Type:** Bug Fix / Feature Parity
**Created:** 2026-01-09
**Assigned:** 2026-01-09
**Assignment Email:** `claude/manager/email/sent/2026-01-09-1900-task-esc-passthrough-bluejay-am32.md`
**Branch:** From `maintenance-9.x`

## Overview

ESC passthrough (4-way interface) works in Betaflight with both BLHeli32 and Bluejay/AM32 ESCs, but fails intermittently in INAV with Bluejay and AM32 firmware. This project aims to bring INAV's 4-way interface implementation to parity with Betaflight.

## Problem

Users report that ESC passthrough in INAV:
- Sometimes fails to connect to Bluejay ESCs
- Fails to read/configure AM32 ESCs
- Works with BLHeli32 but not open-source ESC firmware

Betaflight resolved similar issues through PRs #13287 and #14214.

## Root Cause Analysis

### Key Differences Found Between Betaflight and INAV

#### 1. Protocol Version (Minor)
| Item | Betaflight | INAV |
|------|------------|------|
| SERIAL_4WAY_PROTOCOL_VER | 108 | 107 |
| SERIAL_4WAY_VER_SUB_2 | 06 | 05 |

#### 2. Timeout Handling (CRITICAL - from BF PR #13287)

**Betaflight** has proper timeout handling:
```c
// serial_4way.c lines 392-411
static bool ReadByte(uint8_t *data, timeDelta_t timeoutUs)
{
#ifdef USE_TIMEOUT_4WAYIF
    timeUs_t startTime = micros();
    while (!serialRxBytesWaiting(port)) {
        if (timeoutUs && (cmpTimeUs(micros(), startTime) > timeoutUs)) {
            return true;  // timeout
        }
    }
#else
    UNUSED(timeoutUs);
    while (!serialRxBytesWaiting(port));  // Wait indefinitely
#endif
    *data = serialRead(port);
    return false;
}
```

**INAV** lacks timeout - blocks indefinitely:
```c
// serial_4way.c lines 387-392
static uint8_t ReadByte(void)
{
    // need timeout?   <-- NOTE THE COMMENT!
    while (!serialRxBytesWaiting(port));
    return serialRead(port);
}
```

#### 3. Motor IO Access (CRITICAL - from BF PR #14214)

**Betaflight** uses new motor interface functions:
```c
// serial_4way.c esc4wayInit()
for (volatile uint8_t i = 0; i < MAX_SUPPORTED_MOTORS; i++) {
    if (motorIsMotorEnabled(i)) {
        const IO_t io = motorGetIo(i);
        if (io != IO_NONE) {
            escHardware[escIndex].io = io;
            ...
        }
    }
}
```

**INAV** uses older PWM-based approach:
```c
// serial_4way.c esc4wayInit()
for (int idx = 0; idx < getMotorCount(); idx++) {
    ioTag_t tag = pwmGetMotorPinTag(idx);
    if (tag != IOTAG_NONE) {
        escHardware[escCount].io = IOGetByTag(tag);
        ...
    }
}
```

This is problematic because the PWM approach may not work correctly with digital protocols (DSHOT).

#### 4. SILABS Device Matching

**Betaflight** uses range-based detection:
```c
#define SILABS_DEVICE_MATCH ((pDeviceInfo->words[0] > 0xE800) && (pDeviceInfo->words[0] < 0xF900))
```

**INAV** uses explicit device ID list:
```c
#define SILABS_DEVICE_MATCH ((pDeviceInfo->words[0] == 0xF310)||(pDeviceInfo->words[0] == 0xF330) || \
        (pDeviceInfo->words[0] == 0xF410) || (pDeviceInfo->words[0] == 0xF390) || \
        (pDeviceInfo->words[0] == 0xF850) || (pDeviceInfo->words[0] == 0xE8B1) || \
        (pDeviceInfo->words[0] == 0xE8B2))
```

#### 5. ESC Reboot Logic in cmd_DeviceReset

**Betaflight** has additional ESC reboot handling:
```c
case cmd_DeviceReset:
{
    bool rebootEsc = false;
    if (ParamBuf[0] < escCount) {
        selected_esc = ParamBuf[0];
        if (ioMem.D_FLASH_ADDR_L == 1) {
            rebootEsc = true;
        }
    }
    ...
    if (rebootEsc) {
        ESC_OUTPUT;
        setEscLo(selected_esc);
        timeMs_t m = millis();
        while (millis() - m < 300);
        setEscHi(selected_esc);
        ESC_INPUT;
    }
}
```

**INAV** lacks this reboot logic entirely.

## Objectives

1. Add timeout handling to INAV's 4-way interface (parity with BF PR #13287)
2. Evaluate and potentially update motor IO access method (parity with BF PR #14214)
3. Update SILABS_DEVICE_MATCH to use range-based detection
4. Add ESC reboot logic to cmd_DeviceReset
5. Update protocol version to 108

## Scope

**In Scope:**
- `inav/src/main/io/serial_4way.c`
- `inav/src/main/io/serial_4way.h`
- `inav/src/main/io/serial_4way_avrootloader.c` (if needed)
- Testing with Bluejay and AM32 ESCs

**Out of Scope:**
- Configurator changes (should work with existing BLHeliSuite32/Bluejay Configurator)
- DSHOT protocol changes
- ESC telemetry changes

## Implementation Steps

### Phase 1: Timeout Handling
1. Add `USE_TIMEOUT_4WAYIF` define
2. Add timeout constants (CMD_TIMEOUT_US, ARG_TIMEOUT_US, DAT_TIMEOUT_US, CRC_TIMEOUT_US)
3. Modify `ReadByte()` to accept timeout parameter
4. Update `ReadByteCrc()` to use timeout
5. Update `esc4wayProcess()` to use timeouts in read operations

### Phase 2: Motor IO Access
1. Investigate if INAV needs `motorGetIo()` and `motorIsMotorEnabled()` equivalents
2. If DSHOT motors work with current PWM approach, this may not be needed
3. If issues persist with DSHOT, implement motor interface functions

### Phase 3: Device Detection & Reset
1. Update `SILABS_DEVICE_MATCH` to range-based detection
2. Add ESC reboot logic to `cmd_DeviceReset`
3. Update protocol version to 108

### Phase 4: Testing
1. Test with BLHeli32 ESCs (regression test)
2. Test with Bluejay ESCs
3. Test with AM32 ESCs
4. Test with BLHeliSuite32, Bluejay Configurator, AM32 Configurator

## Success Criteria

- [ ] ESC passthrough connects reliably to Bluejay ESCs
- [ ] ESC passthrough connects reliably to AM32 ESCs
- [ ] No regression with BLHeli32 ESCs
- [ ] All configurator tools (BLHeliSuite32, Bluejay Configurator, AM32 Configurator) work
- [ ] Protocol version reports 108

## References

- Betaflight PR #13287: Timeout fix - https://github.com/betaflight/betaflight/pull/13287
- Betaflight PR #14214: Motor IO refactor - https://github.com/betaflight/betaflight/pull/14214
- Betaflight Issue #14208: AM32 Configurator can't read ESC settings

## Files to Compare

```
betaflight/src/main/io/serial_4way.c      vs  inav/src/main/io/serial_4way.c
betaflight/src/main/io/serial_4way.h      vs  inav/src/main/io/serial_4way.h
betaflight/src/main/io/serial_4way_avrootloader.c  vs  inav/src/main/io/serial_4way_avrootloader.c
betaflight/src/main/drivers/motor.c       (for motorGetIo, motorIsMotorEnabled)
```

## Priority Justification

High priority because:
1. Bluejay and AM32 are popular open-source ESC firmware
2. Users cannot configure their ESCs without this fix
3. Clear path to fix based on Betaflight's work
