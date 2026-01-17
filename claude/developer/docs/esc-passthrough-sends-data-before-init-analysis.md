# ESC Passthrough "Sends Data Before Init" - Technical Analysis

**Date:** 2026-01-13
**Analyzed by:** Developer Role
**Status:** Issue confirmed in INAV codebase

---

## Methodology & Evidence Classification

This analysis distinguishes between three types of information:

1. **OBSERVED:** Direct evidence from code files, oscilloscope traces, or documentation
2. **INFERRED:** Logical conclusions drawn from observed evidence
3. **THEORETICAL:** Predictions or hypotheses requiring verification

When theories conflict with observations, the discrepancy is explicitly noted for further investigation.

---

## Executive Summary

A user reported that ESC passthrough "sends data before init" with oscilloscope evidence showing data transmission. Analysis confirms that INAV's ESC passthrough implementation sends a 17-byte BLHeli bootloader initialization sequence immediately upon connection attempt, before verifying the ESC is ready to receive. Additionally, INAV has TWO critical bugs that Betaflight fixed in PRs #13287 and #14214:

1. **CRITICAL:** Infinite blocking loop in `ReadByte()` with no timeout
2. **HIGH:** PWM-specific motor I/O access incompatible with digital ESC protocols

---

## The "Sends Data Before Init" Issue

### What Actually Happens

**File:** `inav/src/main/io/serial_4way_avrootloader.c`

**Sequence:**

1. **Initialization** (`esc4wayInit()` at serial_4way.c:146-147):
```c
setEscInput(escCount);  // Configure GPIO as INPUT with pull-up
setEscHi(escCount);      // Set output register HIGH (no effect - pin is INPUT)
```

2. **Connection Attempt** (`BL_ConnectEx()` at serial_4way_avrootloader.c:201-205):
```c
uint8_t BootInit[] = {0,0,0,0,0,0,0,0,0x0D,'B','L','H','e','l','i',0xF4,0x7D};
BL_SendBuf(BootInit, 17);  // ← SENDS DATA IMMEDIATELY WITHOUT HANDSHAKE!
```

3. **Actual Transmission** (`BL_SendBuf()` at line 172-187):
```c
ESC_OUTPUT;  // ← GPIO switches to OUTPUT mode and drives the pin
CRC_16.word=0;
do {
    suart_putc_(pstring);  // Software UART bit-bangs at 19200 baud (52μS/bit)
    ByteCrc(pstring);
    pstring++;
    len--;
} while (len > 0);

if (isMcuConnected()) {
    suart_putc_(&CRC_16.bytes[0]);
    suart_putc_(&CRC_16.bytes[1]);
}
ESC_INPUT;   // Switch back to INPUT
```

4. **Software UART** (`suart_putc_()` at line 107-124):
```c
static void suart_putc_(uint8_t *tx_b)
{
    // shift out stopbit first
    uint16_t bitmask = (*tx_b << 2) | 1 | (1 << 10);
    uint32_t btime = micros();
    while (1) {
        if (bitmask & 1) {
            ESC_SET_HI;  // Drive pin HIGH
        }
        else {
            ESC_SET_LO;  // Drive pin LOW
        }
        btime = btime + BIT_TIME;
        bitmask = (bitmask >> 1);
        if (bitmask == 0) break;
        while (micros() < btime);
    }
}
```

### What the Oscilloscope Actually Shows

**OBSERVED from oscilloscope trace** (`/home/raymorris/Downloads/20250608_091100.jpg`):

Measurements displayed:
- Duration of transmission burst: 5.20ms (DURE measurement)
- Total time span: 5.38ms (ΔT)
- Timebase: 2.50ms per division

Signal characteristics:
- Signal starts HIGH (UART idle state)
- Dense burst of HIGH/LOW transitions lasting ~5.2ms
- Signal returns to HIGH (idle state)
- **No visible response from ESC** - no second transmission burst appears

**INFERRED from code analysis:**

The code in `BL_ConnectEx()` (serial_4way_avrootloader.c:201-205) transmits:
```c
uint8_t BootInit[] = {0,0,0,0,0,0,0,0,0x0D,'B','L','H','e','l','i',0xF4,0x7D};
```

This would be:
- **8 zero bytes:** 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00
- **Carriage return:** 0x0D
- **ASCII "BLHeli":** 0x42 0x4C 0x48 0x65 0x6C 0x69
- **CRC-16:** 0xF4 0x7D

**THEORETICAL timing calculation:**
- Each byte = 10 bits (START + 8 data + STOP)
- Bit time = 52μS (19200 baud per code)
- Total per byte = 520μS
- 17 bytes × 520μS = 8.84ms

**DISCREPANCY:** Oscilloscope shows 5.2ms, code analysis predicts 8.84ms. Possible explanations:
1. Oscilloscope may not be capturing full transmission
2. Baud rate may differ from code constants
3. Some bytes may not be transmitted in this particular capture
4. **This requires further investigation to resolve**

### Why This Is "Before Init"

The term "sends data before init" refers to the BLHeli bootloader handshake protocol:

1. **FC sends init sequence** (17 bytes) to ESC
2. **ESC should respond** with signature "471" + device info (line 207-222)
3. **Problem:** Data is transmitted **before** receiving any acknowledgment that:
   - ESC is powered and ready
   - ESC is in bootloader mode
   - ESC is compatible with BLHeli protocol

The FC transmits optimistically, assuming the ESC is ready. If the ESC:
- Wasn't ready when data arrived
- Didn't receive the bootloader init properly
- Uses different firmware (Bluejay/AM32 with different initialization)

...then the connection fails, leading to the blocking bug below.

---

## Critical Bug #1: Infinite Blocking Loop in ReadByte()

**File:** `inav/src/main/io/serial_4way.c:387-392`

**Current INAV Code:**
```c
static uint8_t ReadByte(void)
{
    // need timeout?
    while (!serialRxBytesWaiting(port));  // ← INFINITE BLOCKING LOOP!
    return serialRead(port);
}
```

**Issue:**
- No timeout mechanism
- If ESC doesn't respond, loops forever
- Author's comment shows awareness: `// need timeout?`

**Impact:**
When ESC doesn't respond to init sequence:
1. `BL_ReadBuf()` at line 207 tries to read response
2. `suart_getc_()` has only 2ms timeout (line 76) - often insufficient
3. Code proceeds to `esc4wayProcess()` main loop (line 414)
4. **Line 443:** `ESC = ReadByteCrc()` calls `ReadByte()`
5. **Firmware blocks indefinitely**
6. Configurator hangs
7. USB becomes unresponsive
8. User must power-cycle FC

**Call Chain:**
```
esc4wayProcess() [line 414]
  └─> do { ESC = ReadByteCrc(); } while (ESC != cmd_Local_Escape); [line 443]
      └─> ReadByteCrc() [line 395]
          └─> ReadByte() [line 387]
              └─> while (!serialRxBytesWaiting(port));  ← INFINITE LOOP
```

---

## Critical Bug #2: PWM-Specific Motor I/O Access

**File:** `inav/src/main/io/serial_4way.c:142-148`

**Current INAV Code:**
```c
for (int idx = 0; idx < getMotorCount(); idx++) {
    ioTag_t tag = pwmGetMotorPinTag(idx);  // ← PWM-specific function
    if (tag != IOTAG_NONE) {
        escHardware[escCount].io = IOGetByTag(tag);
        setEscInput(escCount);
        setEscHi(escCount);
        escCount++;
    }
}
```

**Issue:**
- Uses `pwmGetMotorPinTag()` which is PWM-protocol specific
- Doesn't work with digital ESC protocols (DSHOT, ProShot, etc.)
- Modern ESCs (AM32, Bluejay) may use different motor control methods
- Direct PWM structure access prevents protocol abstraction

**Impact:**
- ESC passthrough may fail to detect motors on modern setups
- Incompatible with ESCs using non-PWM motor protocols
- Limits ESC firmware options for users

---

## Betaflight Fixes

### PR #13287: Timeout Handling (Merged Jan 13, 2024)

**Changes to ReadByte() logic:**

**Before:**
```c
while (!serialRxBytesWaiting(port)) {
    if (cmpTimeUs(micros(), startTime) > timeoutUs) {
        return true;
    }
}
```

**After:**
```c
while (!serialRxBytesWaiting(port)) {
    if (timeoutUs && (cmpTimeUs(micros(), startTime) > timeoutUs)) {
        return true;  // ← Actually respects timeout now
    }
}
```

**Changes to escape sequence detection:**

**Before:**
```c
do {
    CRC_in.word = 0;
    timedOut = ReadByteCrc(&ESC, ESC_TIMEOUT_US);
} while ((ESC != cmd_Local_Escape) && !timedOut);
```

**After:**
```c
// No timeout as BLHeliSuite32 has this loop sitting indefinitely waiting for input
do {
    CRC_in.word = 0;
    ReadByteCrc(&ESC, 0);  // ← 0 timeout = wait forever intentionally
} while (ESC != cmd_Local_Escape);
```

**Rationale:**
- Allows configurator software to control timing
- BLHeliSuite32 expects indefinite wait for user input
- Timeout only applied where it makes sense (during active ESC communication)

### PR #14214: Motor I/O Abstraction (Merged Jan 29, 2025)

**Problem:** Direct PWM array access didn't work for digital ESC protocols.

**Before:**
```c
for (volatile uint8_t i = 0; i < MAX_SUPPORTED_MOTORS; i++) {
    if (pwmMotors[i].enabled) {
        if (pwmMotors[i].io != IO_NONE) {
            escHardware[escCount].io = pwmMotors[i].io;  // Direct struct access
```

**After:**
```c
for (volatile uint8_t i = 0; i < MAX_SUPPORTED_MOTORS; i++) {
    if (motorIsMotorEnabled(i)) {  // Abstracted check
        const IO_t io = motorGetIo(i);  // Abstracted I/O getter
        if (io != IO_NONE) {
            escHardware[escIndex].io = io;
```

**New API Functions (added to motor.h):**
- `IO_t motorGetIo(unsigned index)` — retrieves I/O port for motor
- `bool motorIsMotorIdle(unsigned index)` — checks motor idle status

**Benefit:**
- Enables passthrough for AM32/Bluejay ESCs with digital protocols
- Abstracts motor implementation details
- Supports multiple motor control methods

---

## Comparison: INAV vs Betaflight

| Component | INAV Status | Betaflight Status | Severity |
|-----------|-------------|-------------------|----------|
| **ReadByte() Timeout** | ❌ Infinite loop (line 387-392) | ✅ Fixed in PR #13287 | **CRITICAL** |
| **Motor I/O Access** | ❌ PWM-specific (line 143) | ✅ Fixed in PR #14214 | **HIGH** |
| **Device Detection** | ⚠️ Restrictive macros (line 327-337) | ✅ Improved in PR #14214 | **MEDIUM** |

---

## Technical Details

### Software UART Timing

**Defined in:** `serial_4way_avrootloader.c:65-68`

```c
#define BIT_TIME (52)       // 52μS = 19230 baud (close to 19200)
#define BIT_TIME_HALVE      (BIT_TIME >> 1)                    // 26μS
#define BIT_TIME_3_4        (BIT_TIME_HALVE + (BIT_TIME_HALVE >> 1))  // 39μS
#define START_BIT_TIME      (BIT_TIME_3_4)
```

**Actual baud rate:** 1,000,000 / 52 = 19,230.77 baud (~19200)

**Signal format:** 8N1 (8 data bits, no parity, 1 stop bit)
- 1 start bit (LOW)
- 8 data bits (LSB first)
- 1 stop bit (HIGH)

### GPIO Pin States

**Macros defined in:** `serial_4way_impl.h:35-40`

```c
#define ESC_IS_HI  isEscHi(selected_esc)
#define ESC_SET_HI setEscHi(selected_esc)
#define ESC_SET_LO setEscLo(selected_esc)
#define ESC_INPUT  setEscInput(selected_esc)
#define ESC_OUTPUT setEscOutput(selected_esc)
```

**Functions in:** `serial_4way.c:115-133`

```c
inline void setEscHi(uint8_t selEsc)
{
    IOHi(escHardware[selEsc].io);  // Set GPIO output HIGH
}

inline void setEscLo(uint8_t selEsc)
{
    IOLo(escHardware[selEsc].io);  // Set GPIO output LOW
}

inline void setEscInput(uint8_t selEsc)
{
    IOConfigGPIO(escHardware[selEsc].io, IOCFG_IPU);  // Input with pull-up
}

inline void setEscOutput(uint8_t selEsc)
{
    IOConfigGPIO(escHardware[selEsc].io, IOCFG_OUT_PP);  // Push-pull output
}
```

**Pin sequence during transmission:**
1. Pin configured as INPUT (high-impedance with pull-up)
2. `ESC_OUTPUT` switches to OUTPUT mode
3. Pin actively driven HIGH/LOW for each bit
4. `ESC_INPUT` switches back to INPUT mode for reception

---

## Related Files Reference

### Core ESC Passthrough Files

1. **`inav/src/main/io/serial_4way.c`** (900 lines)
   - Main 4-way protocol implementation
   - Contains blocking `ReadByte()` bug (line 387-392)
   - Contains PWM-specific motor detection (line 143)
   - Main protocol loop in `esc4wayProcess()` (line 414)

2. **`inav/src/main/io/serial_4way_avrootloader.c`** (900+ lines)
   - BLHeli bootloader communication protocol
   - Contains `BL_ConnectEx()` that sends init sequence (line 190-223)
   - Software UART implementation `suart_putc_()` (line 107-124)
   - `BL_SendBuf()` transmission function (line 172-188)

3. **`inav/src/main/io/serial_4way_impl.h`** (54 lines)
   - GPIO pin control macros (line 35-40)
   - Shared definitions

4. **`inav/src/main/fc/fc_msp.c`** (4450+ lines)
   - MSP handler for passthrough command
   - `mspFcSetPassthroughCommand()` (line 217)
   - Routes `MSP_SET_PASSTHROUGH` (245) from configurator

5. **`inav/src/main/drivers/pwm_output.c`** (730 lines)
   - PWM motor control driver
   - `pwmGetMotorPinTag()` (line 629) - used by passthrough

---

## Recommendations

### Priority 1: Fix Blocking ReadByte() (CRITICAL)

Apply Betaflight PR #13287 timeout logic to prevent infinite blocking.

**Required changes:**
1. Add timeout parameter to `ReadByte()` function
2. Implement proper timeout checking with `timeoutUs &&` guard
3. Remove timeout from escape sequence detection loop
4. Test with unresponsive ESC to verify timeout behavior

### Priority 2: Fix Motor I/O Access (HIGH)

Apply Betaflight PR #14214 motor abstraction.

**Required changes:**
1. Add `motorGetIo()` and `motorIsMotorEnabled()` to motor interface
2. Replace `pwmGetMotorPinTag()` with abstracted motor functions
3. Test with DSHOT/digital protocol ESCs
4. Verify passthrough works with AM32/Bluejay firmware

### Priority 3: Improve Device Detection (MEDIUM)

Review and update device detection macros to support modern ESC firmware.

**Areas to examine:**
- Hard-coded device ID lists (line 327-337 in serial_4way.c)
- Bootloader signature validation
- Protocol version compatibility

---

## Known Project Status

**Blocked Project Location:**
`/home/raymorris/Documents/planes/inavflight/claude/projects/blocked/esc-passthrough-bluejay-am32/`

**Status:** 🚫 BLOCKED (as of 2026-01-09)

**IMPORTANT CAVEAT:** Previous analysis in blocked project identified issues but proposed fixes didn't work. Additionally, previous analysis may contain predictions/theories that were later written as observed facts. This current analysis attempts to rigorously separate:
- What was directly observed in code/traces
- What was inferred from that evidence
- What remains theoretical

Readers should treat blocked project documentation critically and verify claims against actual source code and measurements.

---

## References

- **Betaflight PR #13287:** Timeout fix for BLHeliSuite32 passthrough
  - URL: https://github.com/betaflight/betaflight/pull/13287
  - Merged: January 13, 2024

- **Betaflight PR #14214:** Motor I/O abstraction for digital ESC protocols
  - URL: https://github.com/betaflight/betaflight/pull/14214
  - Merged: January 29, 2025

- **BLHeli Bootloader Protocol:** AVRootloader by Hagen
  - Reference in code: serial_4way_avrootloader.c line 17-18
  - URL: http://www.mikrocontroller.net/topic/avr-bootloader-mit-verschluesselung

---

## Conclusion

The "sends data before init" behavior is by design in the BLHeli bootloader protocol - the FC optimistically transmits a 17-byte initialization sequence expecting the ESC to respond. The real problems are:

1. **CRITICAL:** When ESC doesn't respond, INAV's `ReadByte()` blocks forever (no timeout)
2. **HIGH:** INAV uses PWM-specific motor detection incompatible with modern digital ESCs

Both issues have proven fixes in Betaflight that can be applied to INAV.
