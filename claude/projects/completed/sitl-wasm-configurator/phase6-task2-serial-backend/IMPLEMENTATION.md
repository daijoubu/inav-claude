# Phase 6 Task 2: Serial Backend Abstraction - Implementation Notes

**Status:** Firmware implementation complete, needs build integration and testing
**Date:** 2026-01-31

---

## Architecture Decision: WASM as Standard Serial Transport

**Key Insight:** WASM should be treated exactly like UART, TCP, UDP, or BLE - just another serial transport.

### Original Approach (Rejected)
- ❌ Parse MSP packets in JavaScript
- ❌ Call `wasm_msp_process_command()` directly
- ❌ Duplicate MSP protocol handling code

### Final Approach (Implemented)
- ✅ WASM implements standard `serialPort_t` interface
- ✅ JavaScript calls `serialWriteByte()` / `serialReadByte()`
- ✅ Reuses ALL existing MSP infrastructure
- ✅ Zero code duplication

---

## Files Created/Modified

### Firmware (INAV)

**New Files:**
1. `inav/src/main/target/SITL/serial_wasm.c` (290 lines)
   - Implements `serialPort_t` interface
   - RX ring buffer (512 bytes) - from JavaScript
   - TX ring buffer (2048 bytes) - to JavaScript
   - Standard vtable implementation

2. `inav/src/main/target/SITL/serial_wasm.h`
   - Public interface for WASM serial port
   - `wasmSerialInit()` - initialize port
   - `wasmSerialGetPort()` - get port instance

**Modified:**
3. `inav/src/main/target/SITL/wasm_msp_bridge.c` (simplified)
   - **Mode 1** (Phase 5): Direct command interface (preserved for backward compat)
     - `wasm_msp_process_command()`
     - `wasm_msp_get_api_version()`
     - `wasm_msp_get_fc_variant()`
   - **Mode 2** (Phase 6 - Recommended): Serial byte interface
     - `wasmMspInit()` - initialize MSP port
     - `wasmMspProcess()` - process MSP (calls standard `mspSerialProcessOnePort()`)
     - Uses `serialWriteByte()` / `serialReadByte()` from serial_wasm.c

### Configurator (INAV Configurator)

**Modified:**
4. `inav-configurator/js/connection/connection.js`
   - Added `ConnectionType.WASM = 4`

5. `inav-configurator/js/connection/connectionFactory.js`
   - Added `ConnectionWasm` import
   - Added WASM case to factory switch

6. `inav-configurator/js/connection/connectionWasm.js` (420 lines)
   - **Approach 1** (commented out): Direct MSP command interface
   - **Approach 2** (active): Serial byte interface
   - Comprehensive documentation for both approaches
   - Easy to switch between approaches if needed

---

## JavaScript Interface (Exported from WASM)

### Mode 2 Functions (Recommended)

```c
// Write MSP packet byte to firmware
void serialWriteByte(uint8_t data);

// Read MSP response byte from firmware
int serialReadByte(void);  // Returns -1 if no data

// Check bytes available
int serialAvailable(void);
```

### Mode 1 Functions (Backward Compatibility)

```c
// Direct MSP command processing
int wasm_msp_process_command(uint16_t cmdId, uint8_t *cmdData, int cmdLen,
                              uint8_t *replyData, int replyMaxLen);

// Convenience functions (deprecated)
uint32_t wasm_msp_get_api_version(void);
const char* wasm_msp_get_fc_variant(void);
```

---

## Data Flow (Mode 2)

```
┌──────────────┐
│  JavaScript  │
│ Configurator │
└──────┬───────┘
       │ serialWriteByte(byte)
       ↓
┌──────────────────────┐
│ WASM RX Ring Buffer  │  <-- serial_wasm.c
│   (512 bytes)        │
└──────┬───────────────┘
       │ serialRead(port)
       ↓
┌──────────────────────┐
│  MSP Parser          │  <-- msp_serial.c (existing!)
│  State Machine       │      mspSerialProcessReceivedData()
└──────┬───────────────┘
       │ MSP packet complete
       ↓
┌──────────────────────┐
│  MSP Handler         │  <-- fc_msp.c (existing!)
│  mspFcProcessCommand │
└──────┬───────────────┘
       │ Build response
       ↓
┌──────────────────────┐
│ MSP Encoder          │  <-- msp_serial.c (existing!)
│ mspSerialEncode()    │
└──────┬───────────────┘
       │ serialWrite(port, byte)
       ↓
┌──────────────────────┐
│ WASM TX Ring Buffer  │  <-- serial_wasm.c
│   (2048 bytes)       │
└──────┬───────────────┘
       │ serialReadByte()
       ↓
┌──────────────┐
│  JavaScript  │
│ Configurator │
└──────────────┘
```

**Key Point:** Everything between RX buffer and TX buffer uses **standard INAV code**. Zero duplication!

---

## Integration Steps (TODO)

### 1. Build System
- [ ] Add `serial_wasm.c` to WASM CMake build
- [ ] Verify exports: `serialWriteByte`, `serialReadByte`, `serialAvailable`
- [ ] Keep existing exports: `wasm_msp_process_command`, etc.

### 2. Main Loop Integration
- [ ] Call `wasmMspProcess()` from SITL main loop
- [ ] Ensure it's called frequently (every loop iteration)

### 3. Configurator Updates
- [ ] Update `connectionWasm.js` `sendImplementation()` to:
  - Call `Module._serialWriteByte()` for each byte
  - Poll `Module._serialAvailable()` for responses
  - Read via `Module._serialReadByte()`
- [ ] Test with live configurator connection

### 4. Testing
- [ ] Test MSP_API_VERSION
- [ ] Test MSP_STATUS
- [ ] Test all configurator tabs
- [ ] Compare behavior with TCP SITL connection

---

## Code Reuse Summary

| Component | Lines | Source | Notes |
|-----------|-------|--------|-------|
| MSP Parser | ~400 | `msp_serial.c` | Reused 100% |
| MSP Handler | ~5000 | `fc_msp.c` | Reused 100% |
| MSP Encoder | ~200 | `msp_serial.c` | Reused 100% |
| WASM Serial Port | 290 | `serial_wasm.c` | **New** (minimal glue) |
| WASM Bridge | 180 | `wasm_msp_bridge.c` | **Simplified** |

**Total new code:** ~470 lines
**Total reused code:** ~5600 lines
**Code reuse ratio:** 92%

---

## Advantages of This Approach

1. **No Code Duplication**
   - All MSP protocol handling reused
   - Same code path as UART/TCP/UDP/BLE
   - Bugs fixed once, benefit all transports

2. **Realistic Simulation**
   - Byte-level serial interface
   - Proper MSP framing/parsing
   - Same timing characteristics as real hardware

3. **Maintainability**
   - Single source of truth for MSP protocol
   - Easy to add new MSP commands (works automatically for WASM)
   - Standard debugging tools work

4. **Flexibility**
   - Mode 1 preserved for backward compatibility
   - Mode 2 recommended for production
   - Easy to switch between modes

5. **Consistency**
   - WASM connection works exactly like TCP connection
   - Same configurator code can handle both
   - Same MSP command set

---

## Next Steps

1. **Build Integration:** Add serial_wasm.c to CMake
2. **Main Loop:** Hook `wasmMspProcess()` into SITL scheduler
3. **Configurator:** Update connectionWasm.js to use serial byte interface
4. **Testing:** Verify with real configurator connection
5. **Documentation:** Update phase 6 README with final implementation

---

## Comparison: Approach 1 vs Approach 2

| Aspect | Approach 1 (Direct) | Approach 2 (Serial) |
|--------|-------------------|-------------------|
| **Parsing** | JavaScript parses MSP | Firmware parses MSP |
| **Code Reuse** | Duplicates parser logic | Reuses all MSP code |
| **Realism** | Function calls | Serial byte stream |
| **Consistency** | Different from other connections | Same as UART/TCP/BLE |
| **Overhead** | Lower (direct calls) | Slightly higher (byte-by-byte) |
| **Maintenance** | Two code paths | One code path |
| **Debugging** | Custom tools needed | Standard MSP tools work |

**Recommendation:** Use Approach 2 (Serial). The slight overhead is negligible compared to the benefits of code reuse and consistency.

---

## Questions & Answers

**Q: Why keep Approach 1 (wasm_msp_process_command)?**
A: Backward compatibility. Phase 5 test harness uses it. Can be deprecated later.

**Q: Does this work with MSP V1 and V2?**
A: Yes! The MSP parser handles both automatically.

**Q: What about MSP post-processing callbacks?**
A: Currently ignored (like Phase 5). Future work could handle reboot requests, etc.

**Q: Can we use this for other SITL transports (TCP)?**
A: No need - TCP already has a proper serial port implementation. This is WASM-specific.

**Q: Performance concerns?**
A: Ring buffers are small (2.5KB total). Byte-by-byte processing is fast enough for MSP (low bandwidth protocol).

