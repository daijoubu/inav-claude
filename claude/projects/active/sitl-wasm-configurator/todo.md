# Todo List: SITL WASM Configurator Integration

**Last Updated:** 2026-01-24
**Current Phase:** Phase 6 - Configurator Integration
**Status:** 📋 Ready to Start

---

## Project Status Overview

### ✅ Completed Phases (1-5)

- [x] **Investigation** - Feasibility research complete (~4h)
- [x] **Phase 1:** WASM Compilation (6h)
- [x] **Phase 2a:** Test Infrastructure (2h)
- [x] **Phase 3:** Parameter Group Runtime (10h)
- [x] **Phase 4:** Scheduler Integration (6h)
- [x] **Phase 5:** MSP Protocol (8h)
- [x] **Documentation:** Project organization complete

**Subtotal Completed:** ~36 hours invested, core WASM functionality working

---

## 📋 Phase 6: Configurator Integration (NOT STARTED)

**Estimated Total:** 12-16 hours
**Goal:** Full integration with INAV Configurator UI

---

### Task 1: WASM Module Loader (3-4 hours)

**Objective:** Create loader that initializes WASM module in Configurator

**Files to Create:**
- [ ] `inav-configurator/src/js/sitl_loader.js`

**Implementation Checklist:**

- [ ] **Basic Loader Class**
  - [ ] Create `SITLLoader` class
  - [ ] Implement `load()` method to fetch WASM binaries
  - [ ] Implement `getModule()` to return initialized Module
  - [ ] Implement `isLoaded()` state checker

- [ ] **WASM Binary Loading**
  - [ ] Fetch `resources/sitl/SITL.wasm` from package
  - [ ] Fetch `resources/sitl/SITL.elf` (JavaScript glue)
  - [ ] Handle loading errors with user-friendly messages
  - [ ] Show loading progress indicator

- [ ] **Emscripten Runtime Initialization**
  - [ ] Initialize Emscripten Module object
  - [ ] Configure memory settings
  - [ ] Set up exported function wrappers
  - [ ] Handle initialization failures

- [ ] **MSP Interface Export**
  - [ ] Export `Module._wasm_msp_process_command`
  - [ ] Export `Module._malloc` and `Module._free`
  - [ ] Export Emscripten helper functions (getValue, setValue, etc.)
  - [ ] Create convenience wrappers if needed

- [ ] **Error Handling**
  - [ ] Detect WASM support (browser capability check)
  - [ ] Handle network errors (file not found, timeout)
  - [ ] Handle initialization errors (out of memory, crash)
  - [ ] Provide clear error messages to user

**Acceptance Criteria:**
- [ ] `SITLLoader.load()` successfully loads WASM module
- [ ] Errors are caught and reported clearly
- [ ] Module initialization completes within 5 seconds
- [ ] Exported functions are accessible from JavaScript

---

### Task 2: Serial Backend Abstraction (4-5 hours)

**Objective:** Create WASM backend that integrates with Configurator's serial communication system

**Files to Modify:**
- [ ] `inav-configurator/src/js/serial_backend.js`
- [ ] `inav-configurator/src/js/serial.js`

**Implementation Checklist:**

- [ ] **Backend Factory Pattern**
  - [ ] Create `createSerialBackend(type)` factory function
  - [ ] Support `type = 'native'` for existing chrome.serial
  - [ ] Support `type = 'wasm'` for WASM SITL backend
  - [ ] Handle invalid backend types

- [ ] **WASM Backend Class**
  - [ ] Create `WasmSerialBackend` class
  - [ ] Implement `connect(connectionInfo)` method
  - [ ] Implement `send(data, callback)` method
  - [ ] Implement `disconnect()` method
  - [ ] Implement `isConnected()` method

- [ ] **MSP Communication Integration**
  - [ ] Parse MSP packets from Configurator
  - [ ] Extract command ID and payload
  - [ ] Call `Module._wasm_msp_process_command()`
  - [ ] Allocate reply buffer using `Module._malloc()`
  - [ ] Read reply data from WASM memory
  - [ ] Free buffer using `Module._free()`
  - [ ] Return response via callback

- [ ] **API Compatibility**
  - [ ] Match existing serial.js expectations
  - [ ] Handle all MSP message types
  - [ ] Preserve callback semantics
  - [ ] Support connection state transitions

- [ ] **Connection Management**
  - [ ] Load WASM module on connect
  - [ ] Initialize SITL firmware
  - [ ] Handle connection failures
  - [ ] Clean up on disconnect

- [ ] **Testing**
  - [ ] Test with MSP_API_VERSION
  - [ ] Test with MSP_FC_VARIANT
  - [ ] Test with MSP_STATUS
  - [ ] Test with MSP_SET_* commands (write operations)
  - [ ] Verify all Configurator tabs work

**Acceptance Criteria:**
- [ ] WASM backend implements full SerialBackend interface
- [ ] All MSP commands work correctly
- [ ] Read/write operations functional
- [ ] Connection state managed correctly
- [ ] No breaking changes to existing serial backend

---

### Task 3: Build System Integration (2-3 hours)

**Objective:** Bundle WASM binaries with Configurator package

**Files to Create:**
- [ ] `inav-configurator/scripts/copy-wasm-binaries.js`

**Files to Modify:**
- [ ] `inav-configurator/package.json`

**Implementation Checklist:**

- [ ] **Directory Structure**
  - [ ] Create `inav-configurator/resources/sitl/` directory
  - [ ] Document directory purpose in README

- [ ] **Copy Script**
  - [ ] Create `scripts/copy-wasm-binaries.js`
  - [ ] Copy `SITL.wasm` from `../inav/build_wasm/bin/`
  - [ ] Copy `SITL.elf` from `../inav/build_wasm/bin/`
  - [ ] Handle missing source files gracefully
  - [ ] Verify file sizes (SITL.wasm ~4.5MB, SITL.elf ~173KB)
  - [ ] Report copy status

- [ ] **Build Script Integration**
  - [ ] Add `copy-wasm` script to package.json
  - [ ] Add `prebuild` hook to run copy-wasm
  - [ ] Ensure WASM files included in Electron package
  - [ ] Test development build
  - [ ] Test production build

- [ ] **Documentation**
  - [ ] Update README with WASM build requirements
  - [ ] Document path to INAV build_wasm directory
  - [ ] Explain when to rebuild WASM binaries
  - [ ] Add troubleshooting for missing binaries

**Acceptance Criteria:**
- [ ] WASM binaries automatically copied during build
- [ ] Files correctly packaged with Electron app
- [ ] Development and production builds both work
- [ ] Missing source files don't break build (graceful failure)
- [ ] Documentation clear and complete

---

### Task 4: UI Integration (2-3 hours)

**Objective:** Add "SITL (Browser)" connection option to Configurator UI

**Files to Modify:**
- [ ] `inav-configurator/main.html`
- [ ] `inav-configurator/tabs/ports.html` (or relevant connection UI file)

**Implementation Checklist:**

- [ ] **Connection Type Selector**
  - [ ] Add "SITL (Browser)" option to connection type dropdown
  - [ ] Update connection dialog UI
  - [ ] Show/hide relevant options based on selection
  - [ ] Handle connection type persistence (remember last used)

- [ ] **WASM Status Indicators**
  - [ ] Create loading indicator ("Loading WASM...")
  - [ ] Create ready indicator ("✓ SITL Ready")
  - [ ] Create error indicator ("⚠ WASM Error")
  - [ ] Show current status during connection process

- [ ] **Connection Button**
  - [ ] Update "Connect" button behavior for WASM mode
  - [ ] Disable button during WASM loading
  - [ ] Show progress feedback
  - [ ] Handle connection cancellation

- [ ] **Error Display**
  - [ ] Show WASM not supported error (old browser)
  - [ ] Show load failure error (network, missing file)
  - [ ] Show initialization failure error (crash, OOM)
  - [ ] Provide actionable error messages
  - [ ] Link to troubleshooting documentation

- [ ] **Module Lifecycle**
  - [ ] Initialize WASM on first connect
  - [ ] Reuse module on subsequent connects
  - [ ] Clean up on Configurator close
  - [ ] Handle module crashes gracefully

**Acceptance Criteria:**
- [ ] "SITL (Browser)" appears in connection options
- [ ] UI updates clearly indicate connection state
- [ ] Errors are user-friendly and actionable
- [ ] Connection process feels responsive
- [ ] Works with existing connection types (doesn't break serial/TCP)

---

### Task 5: Testing & Validation (2-3 hours)

**Objective:** Comprehensive testing of WASM SITL integration

**Implementation Checklist:**

- [ ] **Functional Testing - All Configurator Tabs**
  - [ ] **Setup Tab**
    - [ ] Firmware version displayed correctly
    - [ ] Board information shown
    - [ ] Features list loads
    - [ ] System stats update
  - [ ] **Configuration Tab**
    - [ ] Settings load correctly
    - [ ] Settings can be modified
    - [ ] Save works (writes to WASM EEPROM)
    - [ ] Reload retrieves saved values
  - [ ] **Calibration Tab**
    - [ ] Accelerometer data displayed
    - [ ] Compass data shown (if applicable)
    - [ ] Calibration commands execute
  - [ ] **Modes Tab**
    - [ ] Flight modes configurable
    - [ ] Mode switches work
    - [ ] Changes persist after save
  - [ ] **Adjustments Tab**
    - [ ] PID values readable
    - [ ] PID tuning functional
    - [ ] Changes save correctly
  - [ ] **GPS Tab**
    - [ ] GPS position displays (simulated data)
    - [ ] Navigation settings accessible
  - [ ] **CLI Tab**
    - [ ] Commands execute
    - [ ] `dump` command works
    - [ ] `save` command works
    - [ ] `diff` command works
    - [ ] Settings changes apply

- [ ] **Performance Validation**
  - [ ] Initial connection < 5 seconds
  - [ ] Tab switching responsive (< 500ms)
  - [ ] Settings save/load < 1 second
  - [ ] No "unresponsive script" warnings
  - [ ] Memory usage acceptable (< 100MB increase)

- [ ] **Cross-Browser Testing**
  - [ ] Chrome (latest)
  - [ ] Edge (latest)
  - [ ] Firefox (latest)
  - [ ] Safari (if WASM support sufficient)
  - [ ] Identify browser-specific issues

- [ ] **Error Scenario Testing**
  - [ ] Connection failure (module doesn't load)
  - [ ] WASM not supported (old browser)
  - [ ] Out of memory
  - [ ] Module crash during operation
  - [ ] Network timeout (slow connection)

- [ ] **Regression Testing**
  - [ ] Native serial connection still works
  - [ ] TCP connection (native SITL) still works
  - [ ] No breaking changes to existing features

**Acceptance Criteria:**
- [ ] All Configurator tabs functional with WASM backend
- [ ] Performance meets targets (< 5s connect, responsive UI)
- [ ] Works in Chrome, Firefox, Edge
- [ ] Error handling graceful and informative
- [ ] No regressions in existing connection types

---

## Completion Checklist

### Code Complete
- [ ] All 5 tasks above completed
- [ ] Code reviewed for quality
- [ ] No console errors or warnings
- [ ] Memory leaks checked

### Documentation
- [ ] Code commented appropriately
- [ ] README updated with WASM instructions
- [ ] User guide created
- [ ] Troubleshooting section added

### Testing
- [ ] All functional tests passing
- [ ] Performance validated
- [ ] Cross-browser compatibility confirmed
- [ ] Error scenarios handled

### Delivery
- [ ] Branch created from appropriate base (TBD: maintenance-9.x or 10.x)
- [ ] Commits clean and well-organized
- [ ] Pull request created
- [ ] Completion report sent to manager

---

## Estimated Timeline

| Task | Hours | Dependencies |
|------|-------|--------------|
| Task 1: WASM Loader | 3-4h | None |
| Task 2: Serial Backend | 4-5h | Task 1 |
| Task 3: Build System | 2-3h | None (parallel with Task 1-2) |
| Task 4: UI Integration | 2-3h | Task 1, Task 2 |
| Task 5: Testing | 2-3h | Tasks 1-4 |
| **Total** | **13-18h** | - |

**Realistic Estimate:** 12-16 hours (with some task overlap)

---

## Success Criteria

### Minimum Viable Product (MVP)
- [ ] "Connect to SITL (Browser)" button works
- [ ] At least 3 Configurator tabs functional (Setup, Configuration, CLI)
- [ ] Settings save/load works
- [ ] Acceptable performance (< 10s connect)

### Full Release Criteria
- [ ] All Configurator tabs functional
- [ ] Performance excellent (< 5s connect)
- [ ] Cross-browser compatibility
- [ ] User documentation complete
- [ ] Zero regressions

---

## Risk Mitigation

| Risk | Mitigation Strategy | Status |
|------|---------------------|--------|
| Serial API incompatibility | Careful interface design, extensive testing | ⏸️ Monitor |
| Performance issues | Profile early, optimize as needed | ⏸️ Monitor |
| Browser compatibility | Feature detection, graceful degradation | ⏸️ Monitor |
| WASM binary size | Acceptable for Electron, can compress | ✅ Validated |

---

## Notes

- **Base Branch:** TBD - Check with manager (likely `maintenance-9.x`)
- **Branch Name:** Consider renaming `websocket-sitl-support` → `wasm-sitl` for clarity
- **PR Target:** `inavflight/inav-configurator` (upstream)

---

## References

- **Architecture:** `06-configurator-integration/README.md`
- **MSP Bridge:** `04-msp-protocol/wasm-sitl-phase5-msp-integration.md`
- **Test Example:** `inav/src/test/wasm/msp_test_harness.html`
- **Build System:** `02-build-system/README.md`
