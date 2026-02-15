# Adopting Scavanger's WASM Implementation as Base

This document provides recommendations for using Scavanger's WASM SITL implementation as the foundation, with specific guidance on what to add from our implementation.

---

## Executive Summary

Scavanger's implementation is more mature in core firmware areas (PG registry, threading, simulator support). Our implementation excels in configurator integration. A hybrid approach would combine the best of both.

---

## Additions from Our Implementation

### 1. Configurator Integration Files

**Files needed:**
- `js/connection/connectionWasm.js`
- `js/wasm_sitl_loader.js`
- Modifications to `js/connection/connectionFactory.js`
- Modifications to `js/connection/connection.js`

**Why Important:** ⭐⭐⭐ CRITICAL

Scavanger's implementation is standalone with a custom HTML debugger. It has no integration with INAV Configurator. Without these files, users cannot:
- Connect to WASM SITL from the configurator UI
- Use the standard connection workflow
- Access any configurator features (setup, PID tuning, OSD, etc.)

The entire point of browser-based SITL is to work with the configurator.

**Effort:** Medium - need to adapt `connectionWasm.js` to use `serial_ex` API instead of our `serial_wasm` API.

---

### 2. Callback-Based Serial Notification

**Our code:**
```c
// serial_wasm.c
EM_JS(void, notifySerialDataAvailable, (), {
    if (Module.wasmSerialDataCallback) {
        Module.wasmSerialDataCallback();
    }
});

static void wasmSerialEndWrite(serialPort_t *instance) {
    notifySerialDataAvailable();  // Notify JS when response complete
}
```

**Scavanger's approach:** JavaScript polls with `requestAnimationFrame`:
```javascript
function pollFrame() {
    if (pollingActive && wasmRunning) {
        pollSerialMessages();
        requestAnimationFrame(pollFrame);  // 60Hz polling
    }
}
```

**Why Important:** ⭐⭐ RECOMMENDED

| Aspect | Polling (Scavanger) | Callback (Ours) |
|--------|---------------------|-----------------|
| CPU usage when idle | Continuous | Zero |
| Response latency | Up to 16ms (60Hz) | Immediate |
| Battery impact | Higher | Lower |
| Code complexity | Simple | Slightly more |

**Verdict:** Callback approach is more efficient but not strictly necessary. Polling works fine - it's just wasteful. For a desktop Electron app, the difference is minor. For a web app on mobile, callbacks would matter more.

**Effort:** Low - add `EM_JS` notification to `serial_ex.c` write path.

---

### 3. EEPROM Injection Before main()

**Our code:**
```javascript
Module = {
    noInitialRun: true,  // Don't auto-call main()
    onRuntimeInitialized: () => {
        // Load from IndexedDB
        const storedEeprom = await this._loadStoredEeprom();

        // Inject BEFORE main() runs
        if (storedEeprom) {
            Module.HEAPU8.set(storedEeprom, ptr);
        }

        // NOW start firmware - it will read our injected data
        Module.callMain();
    }
};
```

**Scavanger's approach:** Uses OPFS filesystem, firmware reads file during normal init.

**Why Important:** ⭐⭐ SITUATIONAL

This is critical **if** the persistence mechanism doesn't load data before `init()` reads EEPROM.

With Scavanger's OPFS approach:
- Filesystem is initialized in `wasmInitFilesystem()` before `systemInit()`
- Config is loaded via standard `config_streamer_file.c`
- Should work without special timing

**However**, need to verify:
1. OPFS mount completes synchronously
2. File read happens before `readEEPROM()` in `init()`

If OPFS has async timing issues, our injection approach would be needed as a fix.

**Effort:** Low if not needed; Medium if OPFS has timing issues.

---

### 4. Electron IPC Reboot Handling

**Our code:**
```javascript
// In wasm_sitl_loader.js
wasmRequestReboot: () => {
    if (window.electronAPI && window.electronAPI.reloadPage) {
        window.electronAPI.reloadPage();
    }
}
```

```c
// In systemReset() - uses ASYNCIFY to cleanly unwind
EM_ASM({ Module.wasmRequestReboot(); });
emscripten_force_exit(0);
```

**Scavanger's approach:** Uses `execvp()` to restart process (works for native, not browser):
```c
void systemReset(void) {
    execvp(c_argv[0], c_argv);  // Won't work in browser!
}
```

**Why Important:** ⭐⭐⭐ CRITICAL for Configurator

When firmware reboots (after saving settings, firmware update simulation, etc.):
- Scavanger: Tries `execvp()` which fails in browser
- Ours: Cleanly reloads the Electron page

Without this fix, the configurator would freeze after any reboot command.

**Note:** Scavanger does have `wasmExit()` which calls `emscripten_force_exit()`, but it's not wired up to `systemReset()`.

**Effort:** Low - wire up the IPC call.

---

### 5. Source Map Generation

**Our cmake:**
```cmake
-gsource-map  # Generate .wasm.map for browser debugging
```

**Scavanger's cmake:** Not present.

**Why Important:** ⭐⭐ RECOMMENDED for Development

Source maps allow:
- Setting breakpoints in C code from browser DevTools
- Seeing C source in stack traces
- Stepping through firmware code

Without source maps, debugging is limited to disassembly view.

**Impact:** ~10-20% larger build output, but invaluable for debugging.

**Effort:** Trivial - add one linker flag.

---

### 6. Dropped Byte Counters

**Our code:**
```c
static uint32_t wasmSerialTxDroppedBytes = 0;
static uint32_t wasmSerialRxDroppedBytes = 0;

EMSCRIPTEN_KEEPALIVE
uint32_t serialGetRxDroppedBytes(void) {
    return wasmSerialRxDroppedBytes;
}
```

**Scavanger's approach:** Logs overflow to stderr but no counter:
```c
fprintf(stderr, "[SERIAL_EX] Message queue overflow...");
```

**Why Important:** ⭐ NICE TO HAVE

Counters allow:
- JavaScript to detect buffer issues programmatically
- Automated testing to verify no data loss
- Debug logging with statistics

Scavanger's stderr logging is adequate for manual debugging.

**Effort:** Trivial.

---

### 7. Single-Threaded Build Option (ASYNCIFY)

**Our approach:** Single-threaded with ASYNCIFY:
```cmake
-sASYNCIFY=1
# No -pthread
```

**Scavanger's approach:** Multi-threaded with pthreads:
```cmake
-pthread
-sPROXY_TO_PTHREAD
-sPTHREAD_POOL_SIZE=10
```

**Why Important:** ⭐⭐ SITUATIONAL

| Aspect | pthreads | Single-thread |
|--------|----------|---------------|
| Scheduler accuracy | ~1kHz | Frame rate |
| Browser requirements | SharedArrayBuffer + COOP/COEP headers | None |
| Server config needed | Yes | No |
| Debugging | Harder (workers) | Easier |
| Simulator support | Better | Adequate |

**Trade-off:**
- pthreads needed for accurate real-time simulation
- Single-thread works for configuration-only use
- pthreads requires server to send specific HTTP headers

**Recommendation:** Make it a build option. Default to single-thread for easier deployment.

**Effort:** Medium - need to conditionalize threading code.

---

### 8. IndexedDB Fallback

**Our approach:** IndexedDB with EEPROM bridge
**Scavanger's approach:** OPFS only

**Why Important:** ⭐ LOW PRIORITY

OPFS browser support:
- Chrome 86+ (Oct 2020)
- Firefox 111+ (Mar 2023)
- Safari 15.2+ (Dec 2021)

IndexedDB is universal but requires custom bridge code.

**Recommendation:** OPFS is fine for modern browsers. IndexedDB fallback only needed if supporting very old browsers.

**Effort:** High (if needed) - would require our bridge code.

---

## Modifications to Scavanger's Code

### 1. Fix systemReset() for Browser

**Current:**
```c
void systemReset(void) {
    // ... cleanup ...
    execvp(c_argv[0], c_argv);  // Doesn't work in browser
}
```

**Needed:**
```c
void systemReset(void) {
#ifdef WASM_BUILD
    EM_ASM({
        if (Module.wasmRequestReboot) {
            Module.wasmRequestReboot();
        }
    });
    emscripten_force_exit(0);
#else
    // existing code
#endif
}
```

---

### 2. Add Source Maps

**In `cmake/wasm.cmake`:**
```cmake
set(WASM_LINK_OPTIONS ${WASM_LINK_OPTIONS}
    -gsource-map
)
```

---

### 3. Export Additional Runtime Methods

**Current:**
```cmake
-sEXPORTED_RUNTIME_METHODS=['cwrap','ccall','callMain','addFunction','HEAP8','HEAPU8','HEAPU16','wasmMemory','FS']
```

**Add for configurator integration:**
```cmake
-sEXPORTED_RUNTIME_METHODS=['cwrap','ccall','callMain','addFunction','HEAP8','HEAPU8','HEAPU16','wasmMemory','FS','getValue','setValue','UTF8ToString','stringToUTF8','lengthBytesUTF8']
```

---

## Integration Checklist

### Phase 1: Core Integration
- [ ] Copy Scavanger's PG registry changes to our `parameter_group.h/.c`
- [ ] Remove our `wasm_pg_registry.c` and `wasm_pg_runtime.c`
- [ ] Test PG initialization works correctly

### Phase 2: Configurator Integration
- [ ] Adapt `connectionWasm.js` for `serial_ex` API
- [ ] Adapt `wasm_sitl_loader.js` for Scavanger's module structure
- [ ] Add reboot handling IPC
- [ ] Test connect/disconnect cycle

### Phase 3: Polish
- [ ] Add source map generation
- [ ] Add callback notification (optional)
- [ ] Add dropped byte counters (optional)
- [ ] Test settings persistence across reload

### Phase 4: Optional Enhancements
- [ ] Add single-threaded build option
- [ ] Add IndexedDB fallback (if needed)
- [ ] Integrate simulator support into configurator

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OPFS timing issues | Low | High | Test early; have injection fallback ready |
| pthread header requirements | Medium | Medium | Document; provide single-thread option |
| serial_ex API mismatch | Low | Medium | Adapter layer in JS |
| PG registry count overflow | Very Low | High | Increase MAX_ENTRIES; add runtime check |

---

## Conclusion

Scavanger's implementation provides a better foundation for the firmware side, particularly:
- Automatic PG registry (huge maintenance win)
- OPFS persistence (simpler than our bridge)
- pthread support (better real-time if needed)

Our implementation provides essential configurator integration that Scavanger lacks entirely.

**Recommended path forward:**
1. Adopt Scavanger's firmware changes (PG registry, OPFS)
2. Port our configurator integration layer
3. Fix `systemReset()` for browser environment
4. Add source maps for debugging
5. Test thoroughly before merging
