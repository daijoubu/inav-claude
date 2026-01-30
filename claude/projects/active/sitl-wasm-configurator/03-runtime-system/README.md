# Component: Runtime System (Phases 3-4)

**Status:** ✅ Complete
**Time Investment:** ~16 hours (Phase 3: 10h, Phase 4: 6h)
**Key Deliverable:** Flight controller firmware running in browser with responsive UI

---

## Overview

This component covers the runtime adaptations needed to make INAV firmware execute in a browser WebAssembly environment, including parameter group memory management and scheduler integration with the JavaScript event loop.

## What This Solves

Two fundamental architectural differences between native and WASM execution:
1. **Memory Management:** Native builds use linker-allocated sections (`.pg_registry`, `.bss`) that don't exist in WASM
2. **Event Loop:** Native SITL runs an infinite loop, but browsers require cooperative yielding to the JavaScript event loop

---

## Phase 3: Parameter Group Runtime (10 hours)

### Problem

Native builds rely on linker sections to pre-allocate memory for 66 parameter groups. WASM doesn't have these sections.

### Solution: Lazy Allocation with Hybrid Accessors

**Core Implementation:** `wasmPgEnsureAllocated()`
- Runtime memory allocation via `malloc()` on first access
- Handles both single instances and profile arrays
- Initializes from reset templates
- Updates registry pointers dynamically

### Technical Details

**Lazy Allocator Logic:**
```c
void* wasmPgEnsureAllocated(const pgRegistry_t *reg) {
    // 1. Check if already allocated
    if (pgInitialized[trackingIndex]) {
        return existing pointer;
    }

    // 2. Allocate memory
    if (isProfile) {
        storage = calloc(regSize * MAX_PROFILE_COUNT);
        copyStorage = calloc(regSize * MAX_PROFILE_COUNT);
    } else {
        memory = calloc(regSize);
        copyMemory = calloc(regSize);
    }

    // 3. Update registry pointers
    reg->address = memory;
    reg->copy = copyMemory;

    // 4. Load reset template
    memcpy(memory, reg->reset.ptr, regSize);

    return memory;
}
```

**WASM Accessor Macros:**
- `PG_DECLARE(_type, _name)` - Inline accessor calling lazy allocator
- Registry structure as common primitive for all accessor types
- CLI helper macros for "backdoor" access to copy storage

### Files Created/Modified

**New Files:**
- `src/main/target/SITL/wasm_pg_runtime.c` - Lazy allocator (154 lines)

**Modified Files:**
- `src/main/config/parameter_group.h` - WASM-specific PG_DECLARE macros
- `src/main/fc/config.c` - WASM readEEPROM() with minimal initialization
- `src/main/fc/cli.c` - CLI helper macros (CLI_COPY_PTR, CLI_COPY_ARRAY, CLI_COPY_STRUCT)
- `src/main/flight/mixer_profile.h` - Conditional accessor definition
- `cmake/sitl.cmake` - Added wasm_pg_runtime.c to build

### Success Metrics

✅ All 66 parameter groups allocate successfully
✅ Read/write accessors work correctly
✅ CLI can dump/save settings
✅ No memory leaks or initialization issues

---

## Phase 4: Scheduler & Browser Integration (6 hours)

### Problem 1: Divide-by-Zero Crash

**Root Cause:** Tasks not properly initialized before scheduler runs
- Scheduler calculates `taskAgeCycles = timeDelta / task->desiredPeriod`
- When `task->desiredPeriod == 0` → crash at 0xbdfd

**Solution:** WASM-Specific `init()` Function

Created minimal initialization in `fc_init.c`:
```c
void init(void) {
    systemState = SYSTEM_STATE_INITIALISING;

    readEEPROM();              // PG system (Phase 3)
    systemState |= SYSTEM_STATE_CONFIG_LOADED;

    latchActiveFeatures();
    fcTasksInit();             // CRITICAL: Initialize task periods

    // Disable hardware-dependent tasks for MVP
    setTaskEnabled(TASK_PID, false);
    setTaskEnabled(TASK_GYRO, false);
    setTaskEnabled(TASK_AUX, false);
    setTaskEnabled(TASK_RX, false);
    setTaskEnabled(TASK_BATTERY, false);
    setTaskEnabled(TASK_TEMPERATURE, false);

    // Keep SERIAL for MSP communication
    setTaskEnabled(TASK_SERIAL, true);
    setTaskEnabled(TASK_SYSTEM, true);

    systemState |= SYSTEM_STATE_MOTORS_READY | SYSTEM_STATE_READY;
}
```

### Problem 2: Infinite Loop Blocks Browser

**Challenge:** Native SITL main loop runs forever, blocking JavaScript event loop

**Solution:** Cooperative Event Loop via Emscripten

Used `emscripten_set_main_loop()` in `main.c`:
```c
#ifdef __EMSCRIPTEN__
    // Pass scheduler to Emscripten for cooperative execution
    emscripten_set_main_loop(scheduler, 0, 1);
#else
    // Native infinite loop
    while (true) {
        scheduler();
    }
#endif
```

**Benefits:**
- Browser UI remains responsive
- JavaScript can execute between scheduler cycles
- No browser "unresponsive script" warnings

### Problem 3: Timing System

**Challenge:** Native SITL uses SysTick timer; WASM needs browser timing

**Solution:** Browser `performance.now()` via Emscripten API

Replaced in `time.c`:
```c
#ifdef __EMSCRIPTEN__
timeMs_t millis(void) {
    return (timeMs_t)emscripten_get_now();
}

timeUs_t micros(void) {
    return (timeUs_t)(emscripten_get_now() * 1000.0);
}
#endif
```

**Precision:** Sub-millisecond (typically 5μs resolution in modern browsers)

### Files Modified

```
src/main/fc/fc_init.c          # WASM-specific init() function
src/main/main.c                # Cooperative event loop
src/main/drivers/time.c        # Browser timing integration
```

### Success Metrics

✅ Scheduler runs in browser without crashing
✅ UI remains responsive (cooperative yielding works)
✅ Timing system provides microsecond precision
✅ MSP tasks execute correctly

---

## Combined Achievement

**What Works:**
- INAV firmware loads and initializes in browser
- Parameter group system functional with runtime allocation
- Scheduler executes with proper task timing
- Browser event loop integration maintains UI responsiveness
- Ready for MSP communication layer (Phase 5)

**Performance:**
- Scheduler runs at native speeds (no significant overhead)
- Memory allocation is lazy (only used PGs consume memory)
- Timing precision sufficient for flight control logic

## Documentation

- **Phase 3 Report:** `email-archive/2025-12-02-wasm-phase3-complete.md`
- **Phase 3 Analysis:** `email-archive/2025-12-02-wasm-phase3-pg-accessor-analysis.md`
- **Phase 4 Report:** `email-archive/2025-12-02-wasm-phase4-complete.md`

## Next Component

→ **04-msp-protocol/** - Direct JavaScript ↔ WASM MSP communication
