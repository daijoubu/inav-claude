# Phase 6 Task 2: Serial Backend Abstraction - Resume

**Last Session:** 2026-01-31
**Status:** Firmware implementation complete, needs build integration and testing
**Next:** Build integration, main loop hookup, configurator updates

---

## Quick Start

When resuming this task:

1. **Verify files exist:**
   ```bash
   ls -l inav/src/main/target/SITL/serial_wasm.c
   ls -l inav/src/main/target/SITL/serial_wasm.h
   ls -l inav/src/main/target/SITL/wasm_msp_bridge.c
   ls -l inav-configurator/js/connection/connectionWasm.js
   ```

2. **Current branch:**
   - Firmware: `feature/wasm-sitl-firmware`
   - Configurator: `feature/wasm-sitl-configurator`

3. **Read implementation notes:**
   - See `IMPLEMENTATION.md` in this directory for architecture details

---

## What's Completed ✅

### Architecture Decision
- ✅ **WASM is a standard serial transport** (like UART/TCP/UDP/BLE)
- ✅ Reuses ALL existing MSP infrastructure (zero code duplication)
- ✅ 92% code reuse ratio (~5600 lines reused, ~470 new)

### Firmware (INAV) - Code Written

**New Files:**
1. ✅ `inav/src/main/target/SITL/serial_wasm.c` (290 lines)
   - Implements standard `serialPort_t` interface
   - RX ring buffer (512 bytes) - JavaScript → firmware
   - TX ring buffer (2048 bytes) - firmware → JavaScript
   - Exports: `serialWriteByte()`, `serialReadByte()`, `serialAvailable()`

2. ✅ `inav/src/main/target/SITL/serial_wasm.h`
   - Public interface: `wasmSerialInit()`, `wasmSerialGetPort()`

**Modified Files:**
3. ✅ `inav/src/main/target/SITL/wasm_msp_bridge.c` (simplified)
   - Mode 1 (Phase 5): Direct command interface - preserved
   - Mode 2 (Phase 6): Serial byte interface - active
   - Exports `wasmMspProcess()` for main loop integration

### Configurator - Code Written

4. ✅ `inav-configurator/js/connection/connection.js`
   - Added `ConnectionType.WASM = 4`

5. ✅ `inav-configurator/js/connection/connectionFactory.js`
   - Added `ConnectionWasm` import and factory case

6. ✅ `inav-configurator/js/connection/connectionWasm.js` (420 lines)
   - Approach 1 (Direct MSP) - commented out, preserved
   - Approach 2 (Serial bytes) - active implementation skeleton
   - Both approaches documented for easy switching

---

## What's NOT Done ❌

### 1. Build System Integration (Firmware)

**File to modify:** `inav/cmake/sitl.cmake` or WASM-specific CMake file

**What to do:**
```cmake
# Add serial_wasm.c to WASM SITL build sources
# Find the section that lists SITL source files and add:
target_sources(SITL PRIVATE
    # ... existing files ...
    src/main/target/SITL/serial_wasm.c
    src/main/target/SITL/wasm_msp_bridge.c  # already exists
)
```

**Verification:**
- Build WASM: Use `inav-builder` agent to build SITL with WASM toolchain
- Check exports: `nm inav/build_wasm/bin/SITL.wasm | grep serial`
- Should see: `_serialWriteByte`, `_serialReadByte`, `_serialAvailable`

### 2. Main Loop Integration (Firmware)

**File to modify:** `inav/src/main/target/SITL/sitl.c` or main scheduler

**What to do:**
```c
// Add include at top
#include "serial_wasm.h"
#include "wasm_msp_bridge.h"

// In main loop or scheduler, add:
#ifdef __EMSCRIPTEN__
    wasmMspProcess();  // Process WASM MSP serial port
#endif
```

**Purpose:**
- Calls `mspSerialProcessOnePort()` to process incoming bytes
- Generates MSP responses
- Should be called every loop iteration (not just on timer)

### 3. Configurator sendImplementation() (Configurator)

**File to modify:** `inav-configurator/js/connection/connectionWasm.js`

**Current state:** Lines 146-194 have placeholder implementation

**What to do:**
```javascript
sendImplementation(data, callback) {
    if (!this._connectionId || !this._loader || !this._loader.isLoaded()) {
        console.error('[WASM Connection] Cannot send: not connected');
        if (callback) callback({ bytesSent: 0, resultCode: 1 });
        return;
    }

    try {
        const bytes = new Uint8Array(data);
        const module = this._loader.getModule();

        // Write each byte to WASM serial
        for (let i = 0; i < bytes.length; i++) {
            module._serialWriteByte(bytes[i]);
        }

        // Poll for response (async)
        setTimeout(() => {
            this._pollSerialResponse();
        }, 10);  // Small delay for WASM to process

        if (callback) {
            callback({ bytesSent: bytes.length, resultCode: 0 });
        }

    } catch (error) {
        console.error('[WASM Connection] Send error:', error);
        this._onReceiveErrorListeners.forEach(listener => {
            listener(error.message);
        });
        if (callback) {
            callback({ bytesSent: 0, resultCode: 1 });
        }
    }
}
```

### 4. Configurator _pollSerialResponse() (Configurator)

**File to modify:** `inav-configurator/js/connection/connectionWasm.js`

**Current state:** Lines 200-229 have placeholder implementation

**What to do:**
```javascript
_pollSerialResponse() {
    const module = this._loader.getModule();

    // Check if response data available
    const available = module._serialAvailable();
    if (available <= 0) {
        return;  // No data yet
    }

    // Read all available bytes
    const responseBytes = new Uint8Array(available);
    for (let i = 0; i < available; i++) {
        const byte = module._serialReadByte();
        if (byte >= 0) {
            responseBytes[i] = byte;
        }
    }

    // Trigger receive callbacks
    this._onReceiveListeners.forEach(listener => {
        listener({
            connectionId: this._connectionId,
            data: responseBytes.buffer
        });
    });
}
```

---

## Testing Checklist

### Phase 1: Build Verification
- [ ] WASM build completes without errors
- [ ] `SITL.wasm` and `SITL.elf` generated
- [ ] Exports verified: `_serialWriteByte`, `_serialReadByte`, `_serialAvailable`
- [ ] Copy binaries to `inav-configurator/resources/sitl/`

### Phase 2: Basic Connection
- [ ] Start configurator dev server: `cd inav-configurator && yarn start`
- [ ] Open configurator, select "SITL (Browser)" connection
- [ ] Click Connect
- [ ] Check DevTools console for connection messages
- [ ] Verify no errors

### Phase 3: MSP Communication
- [ ] MSP_API_VERSION received (should see version 2.5 or similar)
- [ ] MSP_FC_VARIANT received (should see "INAV")
- [ ] Status tab loads without errors
- [ ] Sensor data updates

### Phase 4: Full Configurator Test
- [ ] All tabs accessible (Setup, Configuration, Ports, etc.)
- [ ] Can read settings
- [ ] Can write settings
- [ ] OSD tab works
- [ ] CLI tab works (if implemented)

---

## File Locations

### Documentation
```
claude/projects/active/sitl-wasm-configurator/
├── phase6-task1-completed/          # Previous work (WASM loader)
│   ├── README.md
│   └── RESUME.md
└── phase6-task2-serial-backend/     # Current work
    ├── IMPLEMENTATION.md            # Architecture details
    └── RESUME.md                    # This file
```

### Firmware
```
inav/src/main/target/SITL/
├── serial_wasm.c         # NEW - Virtual serial port
├── serial_wasm.h         # NEW - Public interface
├── wasm_msp_bridge.c     # MODIFIED - MSP bridge with Mode 1 & 2
└── sitl.c                # TO MODIFY - Main loop hookup
```

### Configurator
```
inav-configurator/js/connection/
├── connection.js          # MODIFIED - Added WASM type
├── connectionFactory.js   # MODIFIED - Added WASM case
├── connectionWasm.js      # NEW - WASM connection backend
├── connectionTcp.js       # Reference implementation
└── connectionSerial.js    # Reference implementation
```

---

## Key Architecture Points

### Data Flow
```
JavaScript → serialWriteByte() → RX Buffer →
MSP Parser (msp_serial.c) → MSP Handler (fc_msp.c) →
MSP Encoder (msp_serial.c) → TX Buffer →
serialReadByte() → JavaScript
```

### Code Reuse
- MSP Parser: 100% reused from `msp_serial.c`
- MSP Handler: 100% reused from `fc_msp.c`
- MSP Encoder: 100% reused from `msp_serial.c`
- **Only new code:** Virtual serial port glue (~290 lines)

### JavaScript Exports (WASM)
```c
void serialWriteByte(uint8_t data);  // Write one byte to firmware
int serialReadByte(void);            // Read one byte from firmware (-1 if none)
int serialAvailable(void);           // Check bytes available
```

### Backward Compatibility
Mode 1 (Phase 5) functions still exported:
```c
int wasm_msp_process_command(...);   // Direct MSP processing
uint32_t wasm_msp_get_api_version(); // Convenience function
const char* wasm_msp_get_fc_variant(); // Convenience function
```

---

## Common Issues & Solutions

### Issue: serialWriteByte not found
**Cause:** CMake not including serial_wasm.c
**Fix:** Add to CMakeLists.txt or sitl.cmake

### Issue: No MSP responses
**Cause:** wasmMspProcess() not called from main loop
**Fix:** Add call in scheduler/main loop

### Issue: Responses delayed
**Cause:** Polling interval too long
**Fix:** Adjust setTimeout() delay in _pollSerialResponse()

### Issue: Buffer overflow
**Cause:** TX buffer too small or not reading fast enough
**Fix:** Increase WASM_SERIAL_TX_BUFFER_SIZE or poll more frequently

### Issue: MSP packet corruption
**Cause:** Race condition in ring buffers
**Fix:** Buffers use volatile, should be safe. Check timing.

---

## Important Notes

1. **Don't duplicate MSP code!**
   - The whole point is to reuse existing infrastructure
   - If you're parsing MSP in JavaScript, you're doing it wrong

2. **Mode 2 is recommended**
   - Mode 1 (direct commands) works but bypasses serial layer
   - Mode 2 (serial bytes) is more realistic and consistent

3. **Ring buffer sizes**
   - RX: 512 bytes (enough for max MSP packet + overhead)
   - TX: 2048 bytes (can buffer multiple responses)
   - Can adjust if needed, but should be sufficient

4. **Polling vs Events**
   - Current implementation uses polling (setTimeout)
   - Could use Emscripten asyncify for true async, but adds complexity
   - Polling is simpler and good enough for MSP (low bandwidth)

5. **Approach 1 vs 2 in connectionWasm.js**
   - Both preserved in comments
   - Easy to switch by commenting/uncommenting
   - Keep both for flexibility

---

## Next Session Action Plan

1. **Build Integration** (30 min)
   - Add serial_wasm.c to CMake
   - Build WASM binaries
   - Verify exports

2. **Main Loop Integration** (15 min)
   - Add wasmMspProcess() call
   - Rebuild and test

3. **Configurator Updates** (30 min)
   - Implement sendImplementation()
   - Implement _pollSerialResponse()
   - Test connection

4. **Testing** (1 hour)
   - Basic connection test
   - MSP command tests
   - Full configurator test
   - Compare with TCP SITL

5. **Cleanup** (30 min)
   - Commit changes
   - Update documentation
   - Email manager

**Total estimated time:** 2.5 - 3 hours

---

## Resources

- **Phase 5 docs:** `inav/src/test/wasm/msp_test_harness.html` - working MSP test
- **Phase 6 plan:** `claude/projects/active/sitl-wasm-configurator/06-configurator-integration/`
- **Task 1 docs:** `claude/projects/active/sitl-wasm-configurator/phase6-task1-completed/`
- **Serial interface:** `inav/src/main/drivers/serial.h` - serialPort_t definition
- **MSP parser:** `inav/src/main/msp/msp_serial.c` - reference implementation
- **TCP connection:** `inav-configurator/js/connection/connectionTcp.js` - similar pattern

---

## Contact Points for Questions

If the next session has questions:

1. **Architecture:** Read IMPLEMENTATION.md in this directory
2. **MSP Protocol:** Check `inav/src/main/msp/msp_serial.c`
3. **Serial Port Interface:** Check `inav/src/main/drivers/serial.h`
4. **Connection Pattern:** Compare with `connectionTcp.js`
5. **Build Issues:** Use `inav-builder` agent

---

**Status Summary:**
- Firmware code: ✅ Complete (needs build integration)
- Configurator code: 🟡 Skeleton (needs sendImplementation)
- Testing: ❌ Not started
- Documentation: ✅ Complete

**Ready to proceed with build integration and testing!**
