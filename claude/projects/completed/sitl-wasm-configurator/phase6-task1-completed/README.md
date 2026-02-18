# Phase 6 Task 1 - WASM Module Loader (COMPLETED)

**Completed:** 2026-01-31
**Status:** ✅ Fully tested and working
**Time:** ~4 hours

---

## Summary

Successfully implemented and tested the WASM module loader for INAV Configurator. The loader can load WASM SITL binaries, initialize the Emscripten runtime, and execute MSP commands.

## Deliverables

### 1. WASM Module Loader
**File:** `inav-configurator/js/wasm_sitl_loader.js` (268 lines)

**Class:** `WasmSitlLoader`

**Key Methods:**
- `static isWasmSupported()` - Browser capability detection
- `async load()` - Load and initialize WASM module
- `getModule()` - Get loaded Emscripten Module
- `isLoaded()` / `isLoading()` - State checking
- `processMspCommand(cmdId, cmdData)` - MSP command wrapper

**Features:**
- Automatic Emscripten runtime configuration
- Memory management (malloc/free)
- Error handling with user-friendly messages
- Usage documentation and examples

### 2. Test Harness
**File:** `test_wasm_loader.html` (saved in this directory)

**Tests:**
1. Browser WebAssembly support detection
2. WASM module loading from `resources/sitl/`
3. MSP command execution (MSP_API_VERSION)

**Test Results:** All passed ✅
- API Version 2.5 (protocol 0) received from WASM SITL

### 3. WASM Binaries
**Location:** `inav-configurator/resources/sitl/`
- `SITL.wasm` (4.5 MB) - WebAssembly binary
- `SITL.elf` (173 KB) - Emscripten JavaScript glue code

**Source:** Built from `inav/build_wasm_clean/` using Emscripten toolchain

---

## How to Rebuild WASM Binaries (If Needed)

If build directories are cleaned and you need to regenerate:

```bash
# 1. Ensure you're on the correct firmware branch
cd inav
git checkout feature/wasm-sitl-firmware

# 2. Build with inav-builder agent (recommended)
# Use Task tool with subagent_type="inav-builder"
# Prompt: "Build SITL with WASM toolchain"

# OR manually:
source ~/emsdk/emsdk_env.sh
mkdir -p build_wasm && cd build_wasm
cmake -DTOOLCHAIN=wasm -DSITL=ON ..
cmake --build . --target SITL

# 3. Copy binaries to configurator
cp inav/build_wasm/bin/SITL.wasm inav-configurator/resources/sitl/
cp inav/build_wasm/bin/SITL.elf inav-configurator/resources/sitl/
```

---

## Source Files Merged

The WASM source files were discovered across two branches and merged:

**From `wasm-pg_registry` branch:**
- `cmake/wasm.cmake` - Emscripten toolchain configuration
- `src/main/target/SITL/wasm_pg_runtime.c` - Parameter group runtime
- `src/main/target/SITL/wasm_pg_registry.c` - PG registry (66 groups)
- `src/main/target/SITL/wasm_stubs.c` - Function stubs
- `src/utils/generate_wasm_pg_registry.sh` - Registry generator script

**From `wasm-msp-direct` branch:**
- `src/main/target/SITL/wasm_msp_bridge.c` - MSP interface
- `src/test/wasm/msp_test_harness.html` - Phase 5 test harness
- `cmake/wasm-checks.cmake` - Additional build checks

**Current branch:** `feature/wasm-sitl-firmware` (has both merged)

---

## Key Learnings

### Memory Access in Emscripten
❌ **Don't use:** `Module.HEAPU8[ptr]` or `Module.HEAPU8.subarray()`
✅ **Use:** `Module.getValue(ptr, 'i8') & 0xFF`

The HEAPU8 typed array is not always available or properly initialized. Use `Module.getValue()` for reliable memory access.

### MSP Bridge Function Signature
```c
int wasm_msp_process_command(
    uint16_t cmdId,      // MSP command ID
    uint8_t *cmdData,    // Command payload (or 0 for no data)
    int cmdLen,          // Payload length
    uint8_t *replyData,  // Reply buffer
    int replyMaxLen      // Reply buffer size
)
```

**Returns:**
- `>= 0` - Reply length in bytes
- `-1` - MSP_RESULT_ERROR
- `-2` - Reply buffer too small
- `-3` - Invalid parameters

---

## Testing Instructions

### Using Test Harness
1. Start configurator dev server: `cd inav-configurator && yarn start`
2. Navigate to: `http://localhost:5173/test_wasm_loader.html`
3. Click buttons in order:
   - 1. Check Browser Support
   - 2. Load WASM Module
   - 3. Test MSP Command

### Using Chrome DevTools MCP
If configurator is running with MCP server:
```javascript
navigate_page("http://localhost:5173/test_wasm_loader.html")
click(uid="load_button")
click(uid="test_button")
take_snapshot()
```

---

## Next Steps (Phase 6 Task 2)

**Task 2: Serial Backend Abstraction (4-5 hours)**

Create WASM connection backend that integrates with configurator's connection system:

1. Study existing connection architecture:
   - `js/connection/connection.js` - Abstract base class
   - `js/connection/connectionTcp.js` - Reference implementation
   - `js/connection/connectionFactory.js` - Factory pattern

2. Create WASM backend class:
   - Extend `Connection` base class
   - Implement required abstract methods
   - Add WASM type (4) to `ConnectionType` enum

3. Integrate MSP communication:
   - Parse MSP packets from configurator
   - Extract command ID and payload
   - Call `loader.processMspCommand()`
   - Return responses via callbacks

4. Update connection factory:
   - Add WASM backend creation
   - Handle connection type selection

**Estimated effort:** 4-5 hours
**Dependencies:** Task 1 complete ✅

---

## Files Modified (Configurator)

**New:**
- `js/wasm_sitl_loader.js` - WASM loader class
- `resources/sitl/SITL.wasm` - WASM binary (build artifact)
- `resources/sitl/SITL.elf` - Emscripten glue (build artifact)
- `test_wasm_loader.html` - Test harness

**Modified:**
- None yet (Task 2 will modify connection files)

---

## Branches

**Configurator:** `feature/wasm-sitl-configurator`
**Firmware:** `feature/wasm-sitl-firmware` (merged wasm-pg_registry + wasm-msp-direct)

---

## Resources

- **Project docs:** `claude/projects/active/sitl-wasm-configurator/`
- **Phase 5 docs:** `04-msp-protocol/README.md` (MSP bridge interface)
- **Phase 6 plan:** `06-configurator-integration/README.md`
- **Todo list:** `todo.md`
