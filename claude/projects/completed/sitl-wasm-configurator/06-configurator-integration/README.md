# Component: Configurator Integration (Phase 6 - IN PROGRESS)

**Status:** 🚧 IN PROGRESS (Tasks 1-2 Complete, Tasks 3-5 Remaining)
**Estimated Effort:** 12-16 hours
**Goal:** Full WASM SITL integration with INAV Configurator UI

---

## ⚠️ IMPORTANT: Architecture Changed to Mode 2

**This document was originally written for Mode 1 (direct command interface).**

**ACTUAL IMPLEMENTATION uses Mode 2 (byte-level serial transport).**

**Key Changes:**
- ✅ Task 1: WASM Module Loader - COMPLETE
- ✅ Task 2: Serial Backend Abstraction - COMPLETE (using Mode 2, not Mode 1)
- 📋 Task 3: Build System Integration - TODO
- 📋 Task 4: UI Integration - TODO
- 📋 Task 5: Testing & Validation - TODO

**For Architecture Details:**
- See: `ARCHITECTURE-DECISION-BYTE-LEVEL-SERIAL.md` - Why Mode 2 was chosen
- See: `THREADING-AND-EXECUTION-MODEL.md` - How WASM and JS cooperate
- See: `phase6-task2-serial-backend/` - Implementation details

---

## Overview

This is the **remaining work** to complete the SITL WASM project. All core WASM functionality is complete (Phases 1-5). This phase integrates it with the user-facing Configurator application.

## Current State

**What's Complete (Phases 1-5):**
- ✅ WASM compilation (Phase 1)
- ✅ Browser test harness (Phase 2a)
- ✅ Parameter group runtime (Phase 3)
- ✅ Scheduler integration (Phase 4)
- ✅ MSP direct calls (Phase 5)

**What's Missing:**
- ❌ Configurator doesn't know about WASM backend
- ❌ No "Connect to SITL (Browser)" button
- ❌ WASM binaries not bundled with Configurator
- ❌ Serial backend doesn't support WASM mode

## Architecture Plan

### Connection Flow (Updated for Mode 2)

```
User clicks "Connect to SITL (Browser)"
    ↓
Configurator UI
    ↓
WASM Loader (wasm_sitl_loader.js)
    ↓ Loads SITL.wasm + SITL.elf
WASM Module Initialized
    ↓
ConnectionWasm (extends Connection base class)
    ↓ Implements send() using Module._serialWriteByte() byte-by-byte
    ↓ Polls Module._serialAvailable() / _serialReadByte() for responses
MSP Communication (via standard firmware serial interface)
    ↓
All Configurator tabs work normally
```

**Note:** This uses byte-level serial transport (Mode 2), NOT direct command interface (Mode 1).

### Interface Specification (Mode 2 - Byte-Level Serial)

**WASM Backend Implements (ACTUAL IMPLEMENTATION):**
```javascript
class ConnectionWasm extends Connection {
    async connect(connectionInfo) {
        // Load WASM module via WasmSitlLoader
        // Initialize SITL firmware
        // Return connection success
    }

    async send(data, callback) {
        // Send MSP packet bytes via Module._serialWriteByte() (byte-by-byte)
        // Poll Module._serialAvailable() for response
        // Read response bytes via Module._serialReadByte()
        // Return response via callback
    }

    async disconnect() {
        // Cleanup WASM module
    }

    isConnected() {
        // Return WASM module state
    }
}
```

**Exported WASM Functions (Mode 2):**
```c
void _serialWriteByte(uint8_t data);  // JS → Firmware RX buffer
int _serialReadByte(void);             // Firmware TX buffer → JS
int _serialAvailable(void);            // Check response ready
```

**Deprecated Functions (Mode 1 - Preserved for Phase 5 test harness):**
```c
int _wasm_msp_process_command(...);  // Direct command interface (not recommended)
uint32_t _wasm_msp_get_api_version(); // Convenience (deprecated)
const char* _wasm_msp_get_fc_variant(); // Convenience (deprecated)
```

## Task Breakdown

### Task 1: WASM Module Loader (3-4 hours)

**Create:** `inav-configurator/src/js/sitl_loader.js`

**Responsibilities:**
- Load WASM binary from resources
- Initialize Emscripten runtime
- Export MSP interface functions
- Handle loading errors with user-friendly messages

**Deliverables:**
```javascript
class SITLLoader {
    async load() {
        // Load SITL.wasm and SITL.elf
        // Initialize Emscripten Module
        // Return initialized module
    }

    getModule() {
        // Return loaded Module object
    }

    isLoaded() {
        // Return loading state
    }
}
```

---

### Task 2: Serial Backend Abstraction (4-5 hours) - ✅ COMPLETE

**Status:** COMPLETE (2026-02-01)
**Architecture:** Mode 2 - Byte-Level Serial Transport

**IMPORTANT:** This task was completed using **Mode 2** (byte-level serial), NOT Mode 1 (direct command interface).

**Files Created/Modified:**
- `inav-configurator/js/connection/connectionWasm.js` (NEW - byte-level interface)
- `inav-configurator/js/connection/connection.js` (MODIFIED - added WASM type)
- `inav-configurator/js/connection/connectionFactory.js` (MODIFIED - added WASM case)
- `inav/src/main/target/SITL/serial_wasm.c` (NEW - 283 lines ring buffer management)
- `inav/src/main/target/SITL/serial_wasm.h` (NEW - interface declarations)
- `inav/src/main/target/SITL/wasm_msp_bridge.c` (MODIFIED - simplified for Mode 2)
- `inav/cmake/sitl.cmake` (MODIFIED - exported byte-level functions)
- `inav/src/main/main.c` (MODIFIED - added `wasmMspProcess()` to main loop)

**Architecture Implemented (Mode 2):**
```
JavaScript MSP Packet (byte array)
      ↓
  _serialWriteByte() (byte-by-byte)
      ↓
  RX Ring Buffer (512B)    ← serial_wasm.c (NEW)
      ↓
  MSP Parser               ← msp_serial.c (REUSED)
      ↓
  MSP Handler              ← fc_msp.c (REUSED)
      ↓
  MSP Encoder              ← msp_serial.c (REUSED)
      ↓
  TX Ring Buffer (2048B)   ← serial_wasm.c (NEW)
      ↓
  _serialReadByte() / _serialAvailable()
      ↓
JavaScript Response (byte array)
```

**Exported Functions (Mode 2):**
```javascript
Module._serialWriteByte(byte);  // Write byte to firmware RX buffer
Module._serialReadByte();       // Read byte from firmware TX buffer
Module._serialAvailable();      // Check bytes available in TX buffer
```

**Key Achievement:** 92% code reuse (5,600 lines reused, 470 new), zero MSP duplication

**See:**
- `ARCHITECTURE-DECISION-BYTE-LEVEL-SERIAL.md` - Why Mode 2 was chosen
- `phase6-task2-serial-backend/` - Implementation details

---

### Task 3: Build System Integration (2-3 hours)

**Modify:** `inav-configurator/package.json`

**Requirements:**
1. Copy WASM binaries to Configurator resources during build
2. Ensure WASM files are packaged with Electron app
3. Update build scripts for development and production

**Changes Needed:**

**Directory Structure:**
```
inav-configurator/
├── resources/
│   └── sitl/
│       ├── SITL.wasm       # Copied from inav/build_wasm/bin/
│       └── SITL.elf        # Copied from inav/build_wasm/bin/
```

**package.json additions:**
```json
{
  "scripts": {
    "prebuild": "npm run copy-wasm",
    "copy-wasm": "node scripts/copy-wasm-binaries.js"
  }
}
```

**Copy script:** `scripts/copy-wasm-binaries.js`
```javascript
// Copy SITL.wasm and SITL.elf from ../inav/build_wasm/bin/
// to resources/sitl/
```

---

### Task 4: UI Integration (2-3 hours)

**Modify:** `inav-configurator/main.html` and related UI files

**Requirements:**
1. Add "SITL (Browser)" connection option
2. Show WASM loading status
3. Display WASM-specific errors
4. Handle module lifecycle (load/unload)

**UI Changes:**

**Connection Dialog:**
```html
<select id="connection-type">
    <option value="serial">Serial Port</option>
    <option value="tcp">TCP (Native SITL)</option>
    <option value="wasm">SITL (Browser)</option>  <!-- NEW -->
</select>
```

**Status Indicator:**
```html
<div id="wasm-status" class="hidden">
    <span id="wasm-loading">Loading WASM...</span>
    <span id="wasm-ready" class="hidden">✓ Ready</span>
    <span id="wasm-error" class="hidden">⚠ Error</span>
</div>
```

**Error Handling:**
- WASM not supported (old browser)
- WASM load failure (network error, missing file)
- WASM initialization failure (crash, out of memory)

---

### Task 5: Testing & Validation (2-3 hours)

**Test Matrix:**

| Test Case | Expected Result |
|-----------|----------------|
| Connect to WASM SITL | Connection succeeds |
| Setup tab | Shows firmware version, board info |
| Configuration tab | Load/save settings work |
| Calibration tab | Accelerometer/compass data shown |
| Modes tab | Mode switches configurable |
| Adjustments tab | PID tuning works |
| GPS tab | GPS position displays |
| CLI tab | Commands execute, save/load work |

**Performance Validation:**
- Connection time < 5 seconds
- Tab switching responsive
- Settings save/load < 1 second
- No browser "unresponsive script" warnings

**Cross-Browser Testing:**
- Chrome/Edge (Chromium)
- Firefox
- Safari (if WASM support sufficient)

---

## Critical Files for Implementation

### Configurator Files to Modify

1. **`inav-configurator/src/js/serial_backend.js`**
   - Add WASM backend implementation
   - Modify connection logic to support backend selection

2. **`inav-configurator/src/js/serial.js`**
   - Add WASM connection mode
   - Update connection flow

3. **`inav-configurator/main.html`**
   - Add "Connect to SITL (Browser)" UI
   - Add WASM status indicators

4. **`inav-configurator/package.json`**
   - Add WASM build/copy steps
   - Update dependencies if needed

### Reference Files (Already Implemented)

5. **`inav/src/main/target/SITL/wasm_msp_bridge.c`**
   - MSP bridge implementation (Phase 5)

6. **`inav/src/test/wasm/msp_test_harness.html`**
   - Example of MSP direct calls
   - Reference for JavaScript integration

### WASM Binaries to Bundle

7. **`inav/build_wasm/bin/SITL.wasm`** (4.5 MB)
8. **`inav/build_wasm/bin/SITL.elf`** (173 KB)

---

## Success Criteria

- [ ] Configurator has "SITL (Browser)" connection option
- [ ] Clicking it loads WASM and connects
- [ ] All Configurator tabs work with WASM backend
- [ ] Settings save/load functions correctly
- [ ] CLI commands execute
- [ ] Performance is acceptable (< 5s connect, responsive UI)
- [ ] Works in Chrome, Firefox, Edge
- [ ] Error messages are user-friendly
- [ ] WASM binaries automatically packaged with Configurator builds

---

## Estimated Effort Breakdown

| Task | Estimated Hours |
|------|----------------|
| WASM Module Loader | 3-4h |
| Serial Backend Abstraction | 4-5h |
| Build System Integration | 2-3h |
| UI Integration | 2-3h |
| Testing & Validation | 2-3h |
| **TOTAL** | **13-18h** |

**Conservative Estimate:** 12-16 hours
**Optimistic Estimate:** 10-12 hours

---

## Risks & Mitigations

### Risk 1: Serial API Compatibility
**Risk:** Existing Configurator code assumes serial API semantics
**Mitigation:** Careful interface design, extensive testing

### Risk 2: WASM Binary Size
**Risk:** 4.5 MB WASM file increases package size
**Mitigation:** Acceptable for Electron app, can compress with gzip

### Risk 3: Browser Compatibility
**Risk:** Older browsers may not support WASM features
**Mitigation:** Feature detection, clear error messages

---

## Next Steps

1. **Architecture Review:** Verify serial backend abstraction design
2. **Prototype:** Create minimal WASM loader + backend class
3. **Incremental Testing:** Test each Configurator tab individually
4. **Integration:** Full end-to-end testing
5. **Documentation:** Update Configurator README with WASM instructions

---

## Related Documentation

- **Phase 5 MSP Bridge:** `../04-msp-protocol/wasm-sitl-phase5-msp-integration.md`
- **Test Harness Example:** `inav/src/test/wasm/msp_test_harness.html`
- **Build Infrastructure:** `../02-build-system/README.md`
