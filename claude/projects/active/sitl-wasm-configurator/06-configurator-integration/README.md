# Component: Configurator Integration (Phase 6 - NOT STARTED)

**Status:** 📋 TODO
**Estimated Effort:** 12-16 hours
**Goal:** Full WASM SITL integration with INAV Configurator UI

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

### Connection Flow

```
User clicks "Connect to SITL (Browser)"
    ↓
Configurator UI
    ↓
WASM Loader (sitl_loader.js)
    ↓ Loads SITL.wasm + SITL.elf
WASM Module Initialized
    ↓
WASM Backend Class (extends SerialBackend)
    ↓ Implements send() using Module._wasm_msp_process_command()
MSP Communication
    ↓
All Configurator tabs work normally
```

### Interface Specification

**WASM Backend Must Implement:**
```javascript
class WasmBackend extends SerialBackend {
    async connect(connectionInfo) {
        // Load WASM module
        // Initialize SITL
        // Return connection success
    }

    async send(data, callback) {
        // Convert data to MSP command
        // Call Module._wasm_msp_process_command()
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

### Task 2: Serial Backend Abstraction (4-5 hours)

**Modify:** `inav-configurator/src/js/serial_backend.js`

**Current Architecture:**
- Serial backend is tightly coupled to chrome.serial API
- Assumes external SITL binary connection

**Required Changes:**
1. Abstract serial backend to support multiple connection types
2. Create WASM backend class implementing serial interface
3. Replace WebSocket calls with direct `Module._wasm_msp_process_command()`
4. Ensure API compatibility with existing Configurator code

**Deliverables:**
```javascript
// Factory pattern
function createSerialBackend(type) {
    switch (type) {
        case 'native':
            return new NativeSerialBackend();  // Existing chrome.serial
        case 'wasm':
            return new WasmSerialBackend();    // NEW
        default:
            throw new Error('Unknown backend type');
    }
}
```

**API Contract (must match existing serial.js expectations):**
```javascript
interface SerialBackend {
    connect(connectionInfo): Promise<boolean>
    send(data, callback): void
    receive(callback): void
    disconnect(): Promise<void>
    isConnected(): boolean
}
```

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
