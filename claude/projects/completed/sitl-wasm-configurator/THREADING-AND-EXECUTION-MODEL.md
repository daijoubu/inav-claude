# Threading and Execution Model - WASM SITL

**Last Updated:** 2026-02-01
**Status:** Single-threaded cooperative execution (Phase 5+)
**Threading:** pthreads disabled for MVP (may re-enable if needed)

---

## Executive Summary

**Current Architecture:** WASM SITL firmware and JavaScript configurator **run on the same browser thread** using **cooperative multitasking**.

**Key Points:**
- ✅ Single-threaded execution (pthreads disabled)
- ✅ Cooperative yielding via `emscripten_set_main_loop()`
- ✅ Browser's `requestAnimationFrame` controls scheduling
- ✅ UI remains responsive (~60 Hz yield rate)
- ✅ Ring buffers enable asynchronous-style communication
- ❌ No true concurrency (WASM and JS don't run simultaneously)

---

## Architecture Overview

### The Browser Main Thread

```
┌─────────────────────────────────────────────────────────┐
│                   Browser Main Thread                    │
│                                                           │
│  ┌──────────────────┐         ┌────────────────────┐   │
│  │  JavaScript      │◄───────►│  WASM SITL         │   │
│  │  Configurator    │  Shared │  Firmware          │   │
│  │                  │  Thread │                    │   │
│  └──────────────────┘         └────────────────────┘   │
│           ▲                            ▲                 │
│           │                            │                 │
│           └────────┬───────────────────┘                 │
│                    │                                     │
│        ┌───────────▼──────────────┐                     │
│        │  Browser Event Loop      │                     │
│        │  (requestAnimationFrame) │                     │
│        └──────────────────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

**Everything runs on the single main browser thread.**

---

## Execution Flow

### 1. How WASM and JavaScript Interleave

The firmware doesn't run in a traditional infinite loop. Instead, it uses **cooperative yielding**:

```c
// Traditional Native SITL (BLOCKS BROWSER!)
while (true) {
    scheduler();          // Run all tasks
    processLoopback();    // Process simulator data
}
// ❌ This would freeze the browser - never returns control
```

```c
// WASM SITL (COOPERATIVE)
void mainLoopIteration(void) {
    scheduler();          // Run all tasks
    processLoopback();    // Process simulator data
    // Returns control to browser after each iteration
}

int main(void) {
    init();
    loopbackInit();

    // Register callback with browser event loop
    // FPS=0 means "run as fast as browser allows" (typically 60 Hz)
    // simulate_infinite_loop=1 means main() never returns
    emscripten_set_main_loop(mainLoopIteration, 0, 1);
}
```

**What happens:**
1. Browser calls `mainLoopIteration()` via `requestAnimationFrame`
2. WASM runs one scheduler iteration (~16ms @ 60 Hz)
3. WASM returns control to browser
4. Browser processes JavaScript events, renders UI, etc.
5. Browser calls `mainLoopIteration()` again (next frame)
6. Repeat

**Result:** Browser UI stays responsive, WASM firmware runs smoothly.

---

### 2. Communication Between JavaScript and WASM

Since they share the same thread, communication is **synchronous** but appears asynchronous due to ring buffers.

#### JavaScript Calling WASM (Synchronous)

```javascript
// JavaScript can call WASM functions directly (synchronous call)
Module._serialWriteByte(0x24);  // Immediate execution
Module._serialWriteByte(0x4D);  // Immediate execution
Module._serialWriteByte(0x3C);  // Immediate execution
// Control returns to JavaScript immediately
```

**This is a synchronous function call** - JavaScript blocks until WASM returns.

#### WASM Processing Data (Next Iteration)

```c
// In next mainLoopIteration():
void wasmMspProcess(void) {
    // Check RX ring buffer (written by JavaScript)
    while (serialWasmRxAvailable() > 0) {
        uint8_t byte = serialWasmReadByte();
        // Feed to MSP parser (msp_serial.c)
        mspSerialProcessReceivedData(byte);
    }

    // Check for MSP responses
    if (mspResponseReady()) {
        // Write to TX ring buffer (JavaScript will read)
        serialWasmWriteTxByte(responseByte);
    }
}
```

**Data flows asynchronously via ring buffers:**
- JavaScript writes → RX buffer → WASM reads (next iteration)
- WASM writes → TX buffer → JavaScript reads (when polling)

---

### 3. Timing and Scheduling

#### Browser Timing

WASM uses browser's high-resolution timer:

```c
timeMs_t millis(void) {
    return (timeMs_t)emscripten_get_now();  // performance.now()
}

timeUs_t micros(void) {
    return (timeUs_t)(emscripten_get_now() * 1000.0);
}
```

**Characteristics:**
- Microsecond precision (1000× better than milliseconds)
- Monotonic (never jumps backward)
- Browser-native implementation

#### Scheduler Execution

The INAV scheduler runs on every iteration:

```c
void mainLoopIteration(void) {
    scheduler();  // Runs all enabled tasks based on timing

    // Typical tasks enabled for WASM:
    // - TASK_SERIAL (MSP communication)
    // - TASK_SYSTEM (system monitoring)
    //
    // Disabled hardware tasks:
    // - TASK_GYRO (no physical sensors)
    // - TASK_PID (no motor control needed)
    // - TASK_RX (no physical receiver)
}
```

**Yield Rate:**
- Typical: ~60 Hz (every 16ms) via `requestAnimationFrame`
- Maximum: Browser-dependent (usually capped at 60-120 Hz)
- Actual: Depends on browser workload

---

## Performance Characteristics

### 1. Latency

**MSP Command Round-Trip:**
```
JavaScript sends MSP command
      ↓ (synchronous call)
  _serialWriteByte() × N bytes
      ↓ (immediate)
  Bytes in RX ring buffer
      ↓ (wait for next iteration, ~16ms @ 60 Hz)
  WASM scheduler runs
      ↓
  wasmMspProcess() processes RX buffer
      ↓
  MSP parser decodes packet
      ↓
  MSP handler executes command
      ↓
  MSP encoder builds response
      ↓
  Response goes to TX ring buffer
      ↓ (JavaScript polls)
  JavaScript reads via _serialReadByte()
```

**Typical latency:** 16-33ms (1-2 scheduler iterations)

**Acceptable for configurator use case** (human-interactive, not real-time flight control)

---

### 2. UI Responsiveness

**Can WASM block the UI?**

Yes, but only if a **single scheduler iteration** takes too long.

**Mitigations:**
- Hardware-intensive tasks disabled (TASK_GYRO, TASK_PID, etc.)
- MSP processing is fast (few microseconds per command)
- Scheduler designed for real-time execution (minimal per-iteration work)

**In practice:** WASM iterations complete in < 1ms, so UI stays responsive.

---

### 3. Throughput

**Theoretical Maximum:**
- ~60 MSP commands/second @ 60 Hz (one command per frame)
- Ring buffer capacity: 512 bytes RX, 2048 bytes TX

**Practical Maximum:**
- Configurator sends MSP commands sequentially (wait for response)
- Typical: 10-20 commands/second (plenty for configurator)

**Not a bottleneck** for configurator use case.

---

## Threading: Current Status and Future

### Current: Single-Threaded Execution

**Why pthreads are disabled:**

Phase 5 MVP disabled pthreads to simplify development:

```cmake
# cmake/sitl.cmake
# Phase 5 MVP: Disable pthreads to avoid COOP/COEP header requirements
# -pthread (commented out)
# -sUSE_PTHREADS=1 (commented out)
# -sPTHREAD_POOL_SIZE=8 (commented out)
```

**Reason:** pthreads require:
- Cross-Origin-Opener-Policy (COOP) HTTP headers
- Cross-Origin-Embedder-Policy (COEP) HTTP headers
- SharedArrayBuffer support

**Impact:** Single-threaded execution is **sufficient for configurator use case**.

---

### Native SITL Threading (For Reference)

Native SITL uses **8 pthreads** for UART receive threads:

```c
// Native SITL (NOT WASM)
pthread_t receiveThread[8];  // One per UART

for (int i = 0; i < 8; i++) {
    pthread_create(&receiveThread[i], NULL, uartReceiveThread, &uart[i]);
}
```

**WASM doesn't need this** because:
- No physical UARTs (no blocking I/O)
- MSP comes from JavaScript via ring buffer (non-blocking)
- Single-threaded polling is fast enough

---

### Future: Multi-Threading (If Needed)

If pthreads are ever needed for higher fidelity simulation:

**Emscripten pthreads implementation:**
- Maps POSIX threads to Web Workers
- Uses SharedArrayBuffer for thread communication
- Requires COOP/COEP headers on HTTP server

**How to enable:**

```cmake
# cmake/sitl.cmake
target_compile_options(main.elf PRIVATE
    -pthread                    # Enable pthreads
    -s USE_PTHREADS=1          # Use SharedArrayBuffer
    -s PTHREAD_POOL_SIZE=8     # Pre-allocate 8 threads
)

target_link_options(main.elf PRIVATE
    -pthread
    -s USE_PTHREADS=1
    -s PTHREAD_POOL_SIZE=8
)
```

**HTTP server requirements:**

```python
# serve.py
headers = {
    'Cross-Origin-Opener-Policy': 'same-origin',
    'Cross-Origin-Embedder-Policy': 'require-corp',
    'Cache-Control': 'no-cache'
}
```

**Browser compatibility:**
- Chrome/Edge: Full support
- Firefox: Full support (max 20 threads)
- Safari: Limited support (check compatibility)

**When to enable:**
- If simulation needs multi-threaded I/O
- If performance profiling shows single-thread bottleneck
- If matching native SITL behavior exactly

**Current assessment:** Not needed for configurator integration.

---

## Concurrency Model

### JavaScript ↔ WASM Synchronization

**No race conditions because:**
1. **Single-threaded execution** - only one code path runs at a time
2. **Ring buffers** - provide buffering between JS writes and WASM reads
3. **Polling model** - JavaScript polls for responses (no interrupts)

**Ring Buffer Safety:**

```c
// RX Ring Buffer (JavaScript writes, WASM reads)
volatile uint8_t rxBuffer[512];
volatile uint16_t rxHead = 0;  // Written by JavaScript
volatile uint16_t rxTail = 0;  // Written by WASM

// TX Ring Buffer (WASM writes, JavaScript reads)
volatile uint8_t txBuffer[2048];
volatile uint16_t txHead = 0;  // Written by WASM
volatile uint16_t txTail = 0;  // Written by JavaScript
```

**Why `volatile`?**
- Prevents compiler optimizations that assume single-threaded access
- Not strictly necessary in single-threaded mode
- **Would be critical** if pthreads were enabled

**Memory ordering:**
- Single-threaded: Guaranteed sequential consistency
- Multi-threaded: Would need memory barriers (Emscripten provides atomic ops)

---

## Comparison: WASM vs Native SITL

| Aspect | Native SITL | WASM SITL (Current) |
|--------|-------------|---------------------|
| **Threading** | 8 pthreads (UART threads) | Single-threaded |
| **Main Loop** | `while(true)` infinite loop | Cooperative via `emscripten_set_main_loop()` |
| **Timing** | `clock_gettime()` (POSIX) | `performance.now()` (browser) |
| **Blocking I/O** | Yes (socket accept/recv) | No (all async via ring buffers) |
| **Concurrency** | True multi-threading | Cooperative multitasking |
| **UI Impact** | Separate process (no impact) | Shares browser thread (must yield) |
| **Latency** | Microseconds (direct I/O) | Milliseconds (frame-based) |
| **Throughput** | High (dedicated threads) | Medium (frame-limited) |
| **Complexity** | Higher (thread sync) | Lower (single-threaded) |
| **Best For** | Real-time simulation | Configurator integration |

---

## Debugging and Troubleshooting

### Common Issues

#### 1. Browser Becomes Unresponsive

**Symptom:** UI freezes, "Unresponsive script" warning

**Cause:** WASM iteration taking too long (> ~100ms)

**Debug:**
```javascript
// Add timing measurement
const start = performance.now();
Module._mainLoopIteration();  // Manual call for testing
const elapsed = performance.now() - start;
console.log(`Iteration took ${elapsed}ms`);
```

**Fix:**
- Identify slow task in scheduler
- Disable unnecessary tasks
- Split work across multiple iterations

---

#### 2. MSP Commands Timing Out

**Symptom:** Configurator shows "No response" errors

**Cause:** Response not appearing in TX buffer

**Debug:**
```javascript
// Check if WASM is running
console.log("TX available:", Module._serialAvailable());

// Check if response is being generated
// (Add debug logging in wasmMspProcess())
```

**Fix:**
- Verify `wasmMspProcess()` is called in main loop
- Check MSP command is valid
- Verify ring buffer not full

---

#### 3. Ring Buffer Overflow

**Symptom:** Lost data, corrupted MSP packets

**Cause:** JavaScript writing faster than WASM reads

**Debug:**
```c
// In serial_wasm.c
if (((rxHead + 1) % BUFFER_SIZE) == rxTail) {
    printf("RX buffer full! Dropping byte.\n");
}
```

**Fix:**
- Increase RX buffer size (currently 512 bytes)
- Add flow control in JavaScript (wait for available space)
- Rate-limit JavaScript MSP sends

---

## Performance Profiling

### Browser DevTools

**Chrome/Edge:**
```
F12 → Performance tab → Record → Connect to SITL → Stop
```

Look for:
- `mainLoopIteration` duration (should be < 1ms)
- Frame rate (should be ~60 FPS)
- Long tasks (anything > 50ms)

**Firefox:**
```
F12 → Performance tab → Record → Connect to SITL → Stop
```

Look for:
- WASM execution time per frame
- JavaScript execution time per frame
- Total frame time

---

### Emscripten Profiling

Add profiling flags to build:

```cmake
target_compile_options(main.elf PRIVATE
    --profiling           # Enable function-level profiling
    --profiling-funcs     # Detailed function profiling
)
```

Then use browser profiler to see which C functions are slow.

---

## Best Practices

### For WASM Code

1. **Keep iterations short** - Each `mainLoopIteration()` should complete in < 1ms
2. **Avoid blocking calls** - No `sleep()`, `pthread_join()`, or blocking I/O
3. **Use ring buffers** - For all JavaScript ↔ WASM communication
4. **Profile regularly** - Check that iterations stay fast

### For JavaScript Code

1. **Poll, don't spin** - Use `setInterval()` or `requestAnimationFrame()` to poll TX buffer
2. **Rate limit** - Don't send MSP commands faster than WASM can process
3. **Check availability** - Call `_serialAvailable()` before reading
4. **Handle timeouts** - MSP responses may take 1-2 frames (16-33ms)

### For Both

1. **Trust the ring buffers** - They handle async communication safely
2. **Monitor buffer usage** - Watch for overflow conditions
3. **Test under load** - Verify responsiveness with rapid MSP commands
4. **Measure, don't guess** - Use profiling to find actual bottlenecks

---

## Summary

**Current Architecture:**
- ✅ Single-threaded cooperative execution
- ✅ WASM and JavaScript share browser main thread
- ✅ Yielding via `emscripten_set_main_loop()` (~60 Hz)
- ✅ Ring buffers enable async-style communication
- ✅ UI stays responsive, firmware runs smoothly

**Performance:**
- Latency: 16-33ms per MSP command (acceptable)
- Throughput: 10-20 commands/second (sufficient)
- UI responsiveness: No freezing (< 1ms per iteration)

**Threading:**
- pthreads disabled (simplified MVP)
- Can re-enable if needed (Web Workers + SharedArrayBuffer)
- Not currently necessary for configurator use case

**Key Insight:** Single-threaded cooperative multitasking is **simple, sufficient, and performant** for the WASM SITL configurator integration.

---

## References

- **Phase 4 Implementation:** `email-archive/2025-12-02-wasm-phase4-complete.md`
- **Event Loop Code:** `inav/src/main/main.c` (emscripten_set_main_loop)
- **Timing Code:** `inav/src/main/drivers/time.c` (performance.now wrapper)
- **Ring Buffers:** `inav/src/main/target/SITL/serial_wasm.c`
- **Emscripten Docs:** https://emscripten.org/docs/porting/pthreads.html
- **Phase 5 Threading Decision:** `04-msp-protocol/wasm-sitl-phase5-msp-integration.md`

---

**Last Updated:** 2026-02-01
**Status:** Production architecture documented
