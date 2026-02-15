# Component: MSP Protocol Integration (Phase 5)

**Status:** ✅ Complete (Proof of Concept - Superseded by Phase 6 Mode 2)
**Branch:** websocket-sitl-support
**Key Deliverable:** Direct JavaScript ↔ WASM MSP communication working

---

## ⚠️ Architecture Evolution Notice

**This document describes Mode 1 (Direct Command Interface)** - the initial proof of concept from Phase 5.

**Production Implementation:** Phase 6 Task 2 implemented **Mode 2 (Byte-Level Serial Transport)** instead, which treats WASM like UART/TCP/UDP/BLE with byte-level ring buffers. This achieves:
- 92% code reuse (5,600 lines of existing MSP code)
- Zero MSP duplication (single source of truth)
- Consistent architecture with all other serial transports

**Mode 1 Status:**
- ✅ Validated the concept works
- ✅ Preserved for Phase 5 test harness compatibility
- ❌ Not recommended for production (duplicates MSP logic in JavaScript)
- 📁 Archived in `../phase6-task2-serial-backend/mode1-fallback-archive/`

See `../phase6-task2-serial-backend/` for the production byte-level serial architecture.

---

## Overview (Mode 1 - Proof of Concept)

Phase 5 implements direct MSP communication between JavaScript and WASM SITL, eliminating the need for WebSocket overhead. JavaScript can call MSP commands directly via exported WASM functions.

**Note:** While this works, Phase 6 discovered that a byte-level serial transport (Mode 2) is superior for production use.

## What This Solves

**Original Problem:** SITL acts as WebSocket server, but browsers cannot create socket servers.

**Solution Evolution:**
1. **Phase 2 Discovery:** Identified WebSocket server blocker
2. **Phase 2b Planning:** Proposed proxy server architecture (deferred to Phase 6)
3. **Phase 5 Innovation:** Discovered direct function calls work even better!

## Architecture

### Direct Function Call Approach (Chosen)

```
JavaScript (Browser)
    ↓ Direct function call
    Module._wasm_msp_process_command(cmdId, cmdData, replyBuffer)
    ↓
wasm_msp_bridge.c (EMSCRIPTEN_KEEPALIVE exports)
    ↓
mspFcProcessCommand() (Existing INAV MSP handler)
    ↓
Flight Controller Logic
```

**Advantages:**
- Zero serialization overhead
- No WebSocket server needed
- Runs entirely in browser
- Simpler than proxy architecture

## Implementation

### MSP Bridge Function

**Location:** `src/main/target/SITL/wasm_msp_bridge.c`

**Signature:**
```c
EMSCRIPTEN_KEEPALIVE
int wasm_msp_process_command(
    uint16_t cmdId,      // MSP command ID (e.g., 1 = MSP_API_VERSION)
    uint8_t *cmdData,    // Command input data
    int cmdLen,          // Command data length
    uint8_t *replyData,  // Reply output buffer
    int replyMaxLen      // Reply buffer size
)
```

**Return Values:**
- `>= 0`: Reply length in bytes
- `-1`: MSP_RESULT_ERROR
- `-2`: Reply buffer too small
- `-3`: Invalid parameters

### JavaScript Usage

**Example: Get API Version**
```javascript
const MSP_API_VERSION = 1;
const replyBuffer = Module._malloc(256);
const replyLen = Module._wasm_msp_process_command(MSP_API_VERSION, 0, 0, replyBuffer, 256);

if (replyLen > 0) {
    const data = new Uint8Array(replyLen);
    for (let i = 0; i < replyLen; i++) {
        data[i] = Module.getValue(replyBuffer + i, 'i8') & 0xFF;
    }

    const protocolVer = data[0];
    const apiMajor = data[1];
    const apiMinor = data[2];
    console.log(`API: ${apiMajor}.${apiMinor}`);
}

Module._free(replyBuffer);
```

**Example: Get Flight Controller Status**
```javascript
const MSP_STATUS = 101;
const replyBuffer = Module._malloc(256);
const replyLen = Module._wasm_msp_process_command(MSP_STATUS, 0, 0, replyBuffer, 256);

if (replyLen >= 11) {
    const data = new Uint8Array(replyLen);
    for (let i = 0; i < replyLen; i++) {
        data[i] = Module.getValue(replyBuffer + i, 'i8') & 0xFF;
    }

    const cycleTime = data[0] | (data[1] << 8);
    const sensors = data[4] | (data[5] << 8);
    const flightMode = data[6] | (data[7] << 8) | (data[8] << 16) | (data[9] << 24);

    console.log(`Cycle: ${cycleTime}µs, Mode: 0x${flightMode.toString(16)}`);
}

Module._free(replyBuffer);
```

### Build Configuration

**Exported Functions (cmake/sitl.cmake):**
```cmake
-sEXPORTED_FUNCTIONS=_main,_wasm_msp_process_command,_malloc,_free

-sEXPORTED_RUNTIME_METHODS=ccall,cwrap,UTF8ToString,stringToUTF8,
                           lengthBytesUTF8,getValue,setValue
```

**Phase 5 MVP Decision:** Disabled pthreads to simplify development
- Removes COOP/COEP header requirements
- Single-threaded execution sufficient for MSP testing
- Can be re-enabled for full simulator in Phase 6

## Testing

**Test Harness:** `src/test/wasm/msp_test_harness.html`

**Validated Commands:**
- ✅ MSP_API_VERSION (1)
- ✅ MSP_FC_VARIANT (2)
- ✅ MSP_FC_VERSION (3)
- ✅ MSP_STATUS (101)
- ✅ MSP_RAW_GPS (106)
- ✅ MSP_ATTITUDE (108)

**Results:**
- All commands return correct response structures
- Response lengths match MSP protocol specification
- Data parsing works correctly in JavaScript
- Zero crashes or memory corruption

## Files Created/Modified

**New Files:**
- `src/main/target/SITL/wasm_msp_bridge.c` - MSP bridge with exported functions
- `src/test/wasm/msp_test_harness.html` - Interactive testing interface

**Modified Files:**
- `cmake/sitl.cmake` - Added MSP bridge to build, configured exports

## Success Metrics

✅ JavaScript can call MSP commands directly
✅ All tested MSP commands work correctly
✅ Response parsing matches protocol specification
✅ No WebSocket server needed
✅ Simpler architecture than Phase 2b proxy proposal

## Impact on Phase 6

**Critical Simplification:** Direct MSP calls eliminate the need for complex proxy architecture.

**Configurator Integration Path:**
1. Create WASM backend class implementing serial interface
2. Replace WebSocket connection with direct `_wasm_msp_process_command()` calls
3. Map MSP protocol to JavaScript API
4. Bundle WASM binary with Configurator

**Estimated Effort Reduction:** ~40% compared to WebSocket proxy approach

## Documentation

- **Complete Implementation:** `wasm-sitl-phase5-msp-integration.md` (this directory)
- **Test Results:** See `msp_test_harness.html` for interactive examples

## Next Component

→ **06-configurator-integration/** - Integrate WASM SITL with Configurator UI
