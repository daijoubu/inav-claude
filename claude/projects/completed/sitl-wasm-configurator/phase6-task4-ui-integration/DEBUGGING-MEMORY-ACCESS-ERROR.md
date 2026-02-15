# Debugging Memory Access Out of Bounds Error

**Date:** 2026-02-01
**Issue:** WASM crashes with "memory access out of bounds" after successful initial MSP connection

---

## Observations from Console Log

### What Works ✅
- WASM module loads successfully
- Initial MSP connection succeeds
- Multiple MSP commands process correctly:
  - MSP 1 (API version): Success
  - MSP 2 (FC variant): Success
  - MSP 3 (FC version): Success
  - MSP 10 (Name): Success
  - MSP 5 (Build info): Success
  - MSP 4 (Board info): Success
  - MSP 160 (Status): Success
  - MSP 119 (Config): Success
  - MSP 70 (Attitude): Success ← **Last successful command before crash**

### The Crash 💥
- **Location:** `SITL.wasm:0xaf4e` (function $func208)
- **Timing:** After successful MSP 70 response (line 134 in console log)
- **Call Stack:**
  ```
  $func208 @ 0xaf4e  ← Memory access out of bounds HERE
  $func673 @ 0x287e0
  $func669 @ 0x270f1
  $func694 @ 0x29599
  $func1230 @ 0x54ac3
  $func1227 @ 0x540d7
  $func30 @ 0x2cbc
  $func77 @ 0x4447
  callUserCallback @ SITL.elf:4512
  runIter @ SITL.elf:4634
  MainLoop_runner @ SITL.elf:4735  ← Main loop
  ```

### Main Loop Structure
```c
// main.c:68-73
static void mainLoopIteration(void)
{
    wasmMspProcess();  // ✅ Works - MSP processing successful
    scheduler();       // ❓ Likely crash location
    processLoopback(); // ❓ Or here
}
```

---

## Previous Fix Attempt

### Fix #1: Deadlock in waitForSerialPortToFinishTransmitting()
**Problem:** WASM would block waiting for TX buffer to empty, but JS couldn't read until WASM yielded
**Solution:** Made `wasmSerialIsTransmitBufferEmpty()` always return `true`
**Result:** ✅ Fixed the deadlock, but revealed a different memory access error

**Code Changed:** `serial_wasm.c:191-197`
```c
static bool wasmSerialIsTransmitBufferEmpty(const serialPort_t *instance)
{
    // For WASM, always return true to avoid blocking
    UNUSED(instance);
    return true;
}
```

---

## Current Issue Analysis

### What We Know
1. **Not a deadlock** - MSP commands complete successfully
2. **Not in MSP processing** - wasmMspProcess() completes before crash
3. **Happens in main loop** - After MSP processing, during scheduler() or processLoopback()
4. **Consistent address** - Always crashes at 0xaf4e (same function)
5. **Timing** - Happens after ~9 successful MSP exchanges

### Buffer Status at Crash
From debug logs (line 111):
```
RX: 0 bytes, TX: 0 bytes (head/tail: RX 54 / 54  TX 104 / 104 )
```
- RX buffer: 54 bytes processed (well under 512 byte limit)
- TX buffer: 104 bytes sent (well under 2048 byte limit)
- No buffer overflow

### Hypothesis
The crash occurs in `scheduler()` or `processLoopback()` which try to access:
- Hardware peripherals (sensors, motors, etc.) that don't exist in WASM
- Memory-mapped I/O addresses
- Uninitialized function pointers
- Arrays with incorrect bounds

---

## Investigation Plan

### Step 1: Identify Crashing Function
Add debug logging to narrow down:
```c
static void mainLoopIteration(void)
{
    wasmMspProcess();
    EM_ASM({ console.log('[WASM DEBUG] wasmMspProcess done, calling scheduler'); });
    scheduler();
    EM_ASM({ console.log('[WASM DEBUG] scheduler done, calling processLoopback'); });
    processLoopback();
    EM_ASM({ console.log('[WASM DEBUG] processLoopback done'); });
}
```

### Step 2: Check WASM Stubs
Review `wasm_stubs.c` to ensure all hardware functions are properly stubbed

### Step 3: Disable Scheduler Tasks
Temporarily disable scheduler tasks one by one to find which task crashes

### Step 4: Check Sensor Initialization
Verify that sensors/peripherals are properly marked as unavailable in WASM build

---

## Related Files

- `inav/src/main/main.c` - Main loop (lines 66-73)
- `inav/src/main/target/SITL/wasm_stubs.c` - WASM hardware stubs
- `inav/src/main/target/SITL/serial_wasm.c` - Serial interface
- `inav/src/main/scheduler/scheduler.c` - Task scheduler
- `inav/src/main/common/maths.c` - processLoopback()

---

## Notes
- The initial connection succeeds, proving the WASM→JS→WASM data flow works
- The fix for `wasmSerialIsTransmitBufferEmpty()` should be kept (prevents deadlock)
- Need to add note about potential TX buffer overflow if responses pile up faster than JS reads them
