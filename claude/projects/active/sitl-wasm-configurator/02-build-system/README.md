# Component: Build System (Phase 1)

**Status:** ✅ Complete
**Time Investment:** 6 hours
**Key Deliverable:** SITL.wasm (4.5 MB) + SITL.elf (173 KB) successfully compiled

---

## Overview

This component covers the WASM compilation infrastructure that enables INAV SITL firmware to be compiled to WebAssembly using the Emscripten toolchain.

## What This Solves

The core challenge was adapting INAV's build system, which relies heavily on GNU linker scripts and native toolchains, to compile to WebAssembly using Emscripten's wasm-ld linker.

## Key Achievements

### 1. Emscripten Toolchain Integration
- **Toolchain Version:** v4.0.20
- **CMake Configuration:** Added WASM as a valid TOOLCHAIN option
- **Build Command:** `cmake -DTOOLCHAIN=wasm -DSITL=ON .. && cmake --build . --target SITL`

### 2. Parameter Group (PG) Registry Solution ⭐

**The Blocker:** INAV's PG system uses GNU LD linker script features (`PROVIDE_HIDDEN`, custom sections `.pg_registry`) not supported by wasm-ld.

**The Solution:** Script-Generated Manual Registry
- **Script:** `generate_wasm_pg_registry.sh` scans source for `PG_REGISTER*` macros
- **Generated Code:** `wasm_pg_registry.c` manually lists all 66 PG registries
- **Header Changes:** Different declarations for WASM (pointers vs arrays)
- **Build Integration:** Conditional compilation via `#ifdef __EMSCRIPTEN__`

**Time to Solution:** 1.5 hours (after evaluating 3 approaches)

### 3. Conditional Feature Compilation
- Reduced from 74 to 66 PG registries by filtering non-SITL sources
- Excluded: LED strips, ESC sensors, pinout box, OSD joystick, SmartPort master telemetry

### 4. Missing Symbol Stubs
- Created `wasm_stubs.c` with 9 stub implementations for TCP, config streamer, and WebSocket functions
- Allows compilation to succeed while deferring actual implementation

## Files Created/Modified

### New Files
```
cmake/wasm.cmake                                    # Emscripten toolchain file
src/utils/generate_wasm_pg_registry.sh              # PG registry auto-generator
src/main/target/SITL/wasm_pg_registry.c             # Manual PG registry (auto-generated)
src/main/target/SITL/wasm_stubs.c                   # WASM-specific function stubs
```

### Modified Files
```
CMakeLists.txt                                      # Added wasm to TOOLCHAIN_OPTIONS
cmake/sitl.cmake                                    # WASM build configuration
cmake/settings.cmake                                # WASM toolchain support
src/main/config/parameter_group.h                   # WASM-specific symbol declarations
src/main/target/SITL/target.c                       # Wrapped simulator with SKIP_SIMULATOR
```

## Documentation

- **Technical Details:** See `01-investigation/wasm_pg_registry.md` for PG registry solution analysis
- **Feasibility Assessment:** See `01-investigation/03-feasibility-assessment.md`
- **Completion Report:** `email-archive/2025-12-02-wasm-phase1-complete.md`

## Build Output

```
build_wasm/bin/
├── SITL.wasm          # 4.5 MB WebAssembly binary
└── SITL.elf           # 173 KB JavaScript glue code (Emscripten runtime)
```

## Test Infrastructure (Phase 2a)

While technically Phase 2a, the browser test infrastructure is documented here as it's part of the build/test workflow:

- **Test Harness:** `build_wasm/test_harness.html` - Visual WASM loading verification
- **HTTP Server:** `build_wasm/serve.py` - Serves WASM with COOP/COEP headers for pthread support
- **Documentation:** `build_wasm/README.md` - Quick start guide

**Time Investment:** 2 hours

## Success Metrics

✅ WASM binary compiles successfully
✅ All 66 parameter groups registered correctly
✅ No linker errors
✅ WASM loads in browser
✅ Under budget (30-40% of 15-20 hour estimate)

## Next Component

→ **03-runtime-system/** - Runtime lazy allocation and browser integration
