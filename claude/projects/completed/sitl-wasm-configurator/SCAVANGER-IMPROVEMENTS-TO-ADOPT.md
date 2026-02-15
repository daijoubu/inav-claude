# Improvements from Scavanger's WASM Implementation to Consider

This document lists improvements, fixes, and features in Scavanger's WASM implementation that could benefit our implementation.

---

## 0. **CRITICAL: GCC Constructor-Based PG Registry (HIGHEST PRIORITY)**

**Scavanger's approach** (`parameter_group.h:149-163`, `parameter_group.c:27-51`):

Scavanger solves the PG registry problem elegantly using GCC constructor attributes:

```c
// In parameter_group.h - auto-generate registration functions
#if defined(WASM_BUILD)
    #define PG_REGISTER_INIT(_name)                                     \
        __attribute__((constructor(200)))                               \
        static void _name ## _register_init(void) {                     \
            pgRegistryAdd(&_name ## _Registry);                         \
        }

    // Use struct instead of union to avoid type-punning issues
    #define RESET_PRT_NULL ,.ptr = NULL
    #define RESET_FUNC_NULL ,.fn = NULL
#else
    #define PG_REGISTER_INIT(_name) /* nothing */
#endif

// In parameter_group.c - runtime registry array
#if defined(WASM_BUILD)
    #define PG_REGISTRY_MAX_ENTRIES 256

    static pgRegistry_t __pg_registry_data[PG_REGISTRY_MAX_ENTRIES];
    static size_t __pg_registry_count = 0;

    const pgRegistry_t* __pg_registry_start = __pg_registry_data;
    const pgRegistry_t* __pg_registry_end = __pg_registry_data;

    void pgRegistryAdd(const pgRegistry_t *reg)
    {
        if (__pg_registry_count >= PG_REGISTRY_MAX_ENTRIES) return;
        __pg_registry_data[__pg_registry_count++] = *reg;
        __pg_registry_end = &__pg_registry_data[__pg_registry_count];
    }
#endif
```

**Also in the struct definition** (`parameter_group.h:50-58`):
```c
typedef struct pgRegistry_s {
    // ... other fields ...
#if defined(WASM_BUILD)
    struct {  // Use struct, not union - avoids type-punning issues
#else
    union {
#endif
        void *ptr;         // Pointer to init template
        pgResetFunc *fn;   // Pointer to pgResetFunc
    } reset;
} pgRegistry_t;
```

**Benefits over our manual approach**:
1. **Zero maintenance** - new PGs automatically registered via constructor
2. **No manual registry file** - eliminates our 74+ line `wasm_pg_registry.c`
3. **Handles reset data properly** - struct avoids union type-punning issues
4. **Battle-tested** - already working in Scavanger's implementation

**Our current approach problems**:
- Manual `wasm_pg_registry.c` with ~74 `extern` declarations
- Must update when new PGs are added to INAV
- Doesn't properly handle reset template data
- Requires separate `wasm_pg_runtime.c` for allocation

**Trade-off**: Requires modifying core INAV files (`parameter_group.h/.c`), which:
- Adds WASM-specific code to shared files
- May be harder to upstream
- But is much cleaner and more maintainable

**Recommendation**: ✅✅ **HIGH PRIORITY ADOPT** - This is the single most impactful improvement. Our manual registry is a maintenance burden and may be incomplete. Scavanger's solution is elegant and automatic.

**Implementation steps**:
1. Apply Scavanger's changes to `config/parameter_group.h`
2. Apply Scavanger's changes to `config/parameter_group.c`
3. Remove our `wasm_pg_registry.c`
4. Potentially simplify or remove `wasm_pg_runtime.c`
5. Rebuild and test

---

## 1. Module Cleanup: Script Tag Removal + Cache Busting

**Scavanger's approach** (`inav_WASM.html:944-1013`):

```javascript
// Clean up any existing WASM script first
if (wasmScriptTag && wasmScriptTag.parentNode) {
    wasmScriptTag.parentNode.removeChild(wasmScriptTag);
    wasmScriptTag = null;
    // Reset Module for fresh load
    if (typeof Module !== 'undefined') {
        Module = undefined;
    }
    addConsoleLine('Cleaned up previous WASM module', 'debug');
}

// Load with cache-busting timestamp
wasmScriptTag = document.createElement('script');
wasmScriptTag.src = 'inav_WASM.js?t=' + Date.now();  // Cache-bust
```

**Improvement**: Cache-busting prevents stale WASM module issues during development/testing.

**Our current approach**: We use `Date.now()` for script loading but could add more explicit cleanup before reload.

**Recommendation**: ✅ ADOPT - Add cache-busting query parameter to SITL.elf loading:
```javascript
script.src = 'resources/sitl/SITL.elf?t=' + Date.now();
```

---

## 2. Graceful wasmExit() Function

**Scavanger's approach** (`target.c:694-697`):

```c
void wasmExit(void)
{
   emscripten_force_exit(1);
}
```

And in `systemResetToBootloader()`:
```c
void systemResetToBootloader(void)
{
    fprintf(stderr, "[SYSTEM] Reset to bootloader\n");
#if defined(WASM_BUILD)
    wasmExit();
#endif
}
```

**Improvement**: Provides a clean exported function for JavaScript to trigger WASM shutdown.

**Our current approach**: We handle reboot via page reload (`window.electronAPI.reloadPage()`), which works but is less flexible.

**Recommendation**: ✅ CONSIDER - Export `_wasmExit` for more graceful shutdown scenarios. Could be useful for future "stop WASM without full page reload" feature.

---

## 3. Message Fragmentation for Large Responses

**Scavanger's approach** (`serial_ex.c:63-93`):

```c
static void serialExEnqueueMessage(uint8_t portIndex, const uint8_t* data, uint16_t length)
{
    uint16_t remaining = length;
    uint16_t offset = 0;

    // Fragment large messages into smaller chunks
    while (remaining > 0) {
        uint16_t chunkSize = (remaining > SERIAL_EX_MAX_MSG_SIZE) ? SERIAL_EX_MAX_MSG_SIZE : remaining;

        uint32_t nextIdx = (messageQueue.writeIdx + 1) % SERIAL_EX_QUEUE_SIZE;

        // Check if queue is full
        if (nextIdx == messageQueue.readIdx) {
            fprintf(stderr, "[SERIAL_EX] Message queue overflow at offset %u/%u, dropping remaining data\n", offset, length);
            return;
        }

        // Write message chunk to queue
        SerialExMessage *msg = &messageQueue.messages[messageQueue.writeIdx];
        msg->portIndex = portIndex;
        msg->length = chunkSize;
        memcpy(msg->data, data + offset, chunkSize);

        messageQueue.writeIdx = nextIdx;
        remaining -= chunkSize;
        offset += chunkSize;
    }
}
```

**Improvement**: Handles arbitrarily large messages by splitting them into 256-byte chunks.

**Our situation**: MSP messages are typically <256 bytes, and our 2KB TX buffer handles them fine.

**Recommendation**: ⚪ MONITOR - Not critical for our use case, but good to know if we ever need larger transfers.

---

## 4. MSP Message Reassembly in JavaScript

**Scavanger's approach** (`inav_WASM.html:720-776`):

```javascript
let mspReassemblyBuffer = [];  // Buffer for reassembling fragmented MSP messages

function handleSerialData(portId, data) {
    // Add to reassembly buffer
    mspReassemblyBuffer.push(...Array.from(data));

    // Try to parse complete MSP messages from buffer
    processMSPReassemblyBuffer();
}

function processMSPReassemblyBuffer() {
    while (mspReassemblyBuffer.length > 0) {
        // Look for MSP frame start ($M>)
        const startIdx = findMSPFrameStart(mspReassemblyBuffer);

        if (startIdx === -1) {
            // Keep last 2 bytes in case they're the start of $M>
            mspReassemblyBuffer = mspReassemblyBuffer.slice(Math.max(0, mspReassemblyBuffer.length - 2));
            return;
        }

        // ... checksum verification, frame extraction ...
    }
}
```

**Improvement**: Robust handling of fragmented MSP packets that may arrive across multiple reads.

**Our approach**: We rely on the configurator's existing MSP parser which already handles framing.

**Recommendation**: ⚪ NOT NEEDED - Our byte-level serial approach means the configurator's MSP layer handles this automatically.

---

## 5. Detailed Overflow Error Logging

**Scavanger's approach** (`serial_ex.c:75-78`):

```c
if (nextIdx == messageQueue.readIdx) {
    fprintf(stderr, "[SERIAL_EX] Message queue overflow at offset %u/%u, dropping remaining data\n", offset, length);
    return;
}
```

**Improvement**: Logs exact position where overflow occurred, helpful for debugging timing issues.

**Our approach**: We log once and count dropped bytes:
```c
if (!wasmSerialTxOverflowLogged) {
    wasmSerialTxOverflowLogged = true;
    EM_ASM({ console.error('[WASM Serial] TX buffer overflow...'); });
}
```

**Recommendation**: ✅ ADOPT - Add offset/length info to our overflow logging for better debugging:
```c
EM_ASM({
    console.error('[WASM Serial] TX buffer overflow at byte', $0, 'of', $1);
}, offset, total);
```

---

## 6. localStorage for Command-Line Arguments

**Scavanger's approach** (`inav_WASM.html:454-465`):

```javascript
function loadSavedArguments() {
    const saved = localStorage.getItem('wasmArguments');
    if (saved) {
        document.getElementById('argsInput').value = saved;
    }
}

function saveArguments() {
    const args = document.getElementById('argsInput').value;
    localStorage.setItem('wasmArguments', args);
}
```

**Improvement**: Remembers user's preferred startup arguments across sessions.

**Our situation**: We don't use command-line arguments for WASM SITL.

**Recommendation**: ⚪ NOT APPLICABLE - We use IndexedDB for EEPROM persistence instead.

---

## 7. Memory Usage Visualization

**Scavanger's approach** (`inav_WASM.html:967-972`):

```javascript
if (Module.HEAP8) {
    const memBytes = Module.HEAP8.length;
    const memMB = (memBytes / (1024 * 1024)).toFixed(2);
    document.getElementById('memoryText').textContent = `${memMB} MB`;
    addConsoleLine(`Memory allocated: ${memMB} MB`, 'info');
}
```

**Improvement**: Shows users how much memory the WASM module is using.

**Recommendation**: ⚪ NICE TO HAVE - Could add to a WASM SITL status panel in configurator if we ever add one.

---

## 8. Detailed MSP Response Parsing in UI

**Scavanger's approach** (`inav_WASM.html:839-869`):

```javascript
function parseSpecificMSPResponse(command, payload) {
    switch (command) {
        case MSP_API_VERSION:
            const apiVersion = payload[0] + '.' + payload[1] + '.' + payload[2];
            addConsoleLine(`  API Version: ${apiVersion}`, 'debug');
            break;

        case MSP_FC_VARIANT:
            const variant = String.fromCharCode(...payload.slice(0, 4));
            addConsoleLine(`  FC Variant: ${variant}`, 'debug');
            break;

        case MSP_BOARD_INFO:
            const boardName = String.fromCharCode(...payload.slice(0, 8));
            addConsoleLine(`  Board: ${boardName}`, 'debug');
            break;
    }
}
```

**Improvement**: Human-readable display of MSP responses for debugging.

**Our approach**: The configurator already displays this information in its UI.

**Recommendation**: ⚪ NOT NEEDED - Configurator handles this.

---

## 9. OPFS (Origin-Private File System) for Persistence

**Scavanger's approach** (`target.c:675-685`):

```c
void wasmInitFilesystem(void) {
    const char *idbfsMount = MOUNT_POINT;
    const backend_t backend = wasmfs_create_opfs_backend();
    int res = wasmfs_create_directory(idbfsMount, 0777, backend);
    if (res < 0) {
        fprintf(stderr, "[FILESYSTEM] Failed to create IDBFS mount...\n");
        fprintf(stderr, "[FILESYSTEM] Using in-memory filesystem fallback...\n");
    }
}
```

**Improvement**: Uses OPFS which provides file-like API - firmware code needs minimal changes (just path prefix).

**Our approach**: Custom EEPROM bridge with IndexedDB.

**Comparison**:
| Aspect | OPFS (Scavanger) | IndexedDB (Ours) |
|--------|------------------|------------------|
| Firmware changes | Minimal | Custom bridge code |
| Browser support | Chrome 86+, Firefox 111+ | All modern browsers |
| API simplicity | File operations | Key-value store |
| Size limits | Generous | ~50MB typical |

**Recommendation**: ⚪ CONSIDER FOR FUTURE - OPFS is cleaner architecturally but has narrower browser support. Our IndexedDB approach works everywhere.

---

## 10. Socket Proxy for TCP Connectivity

**Scavanger's approach** (`target.c:136-154`):

```c
// Init emscripten socket bridge
char url[64];
snprintf(url, sizeof(url), "ws://localhost:%d", wasmProxyPort);
bridgeSocket = emscripten_init_websocket_to_posix_socket_bridge(url);

uint16_t readyState = 0;
const uint32_t start = millis();
do {
    emscripten_websocket_get_ready_state(bridgeSocket, &readyState);
    emscripten_thread_sleep(100);
} while((readyState != WEBSOCKET_READY_STATE_OPEN && millis() - start < WARM_PROXY_CONNECT_TIMEOUT_MS));
```

**Improvement**: Enables TCP connectivity (needed for X-Plane, RealFlight) via external proxy.

**Our situation**: We're configurator-only (no simulator integration in Phase 1).

**Recommendation**: ⚪ FUTURE FEATURE - If we ever want simulator support, adopt this approach.

---

## 11. Web Worker Thread for Scheduler (pthreads)

**Scavanger's approach** (`target.c:656-673`, `fc_tasks.c:767-776`):

```c
void wasmMainLoop(void) {
    if (!wasmMainWorkerThreadStarted && wasmMainThreadWorker != NULL) {
        int err = pthread_create(&wasmMainThread, NULL, wasmMainThreadWorker, NULL);
        if (err != 0) {
            fprintf(stderr, "[SYSTEM] Failed to start WASM scheduler thread %s\n", strerror(err));
            wasmExit();
        };
        wasmMainWorkerThreadStarted = true;
    }
}

// In fc_tasks.c:
#ifdef WASM_BUILD
void fcScheduler(void) {
    scheduler();  // High-frequency loop in web worker
}
#endif
```

**Improvement**: True multi-threaded operation at ~1kHz scheduler frequency.

**Our approach**: Single-threaded with ASYNCIFY.

**Trade-offs**:
| Aspect | pthreads (Scavanger) | Single-thread (Ours) |
|--------|---------------------|---------------------|
| Scheduler frequency | ~1kHz+ | Browser frame rate |
| Browser requirements | SharedArrayBuffer + COOP/COEP headers | None |
| Complexity | Higher | Lower |
| Real-time accuracy | Better | Adequate for config |

**Recommendation**: ⚪ PHASE 2 - Consider for future if we need better real-time behavior. Requires server-side header changes.

---

## Priority Summary

### Critical Priority (Must Adopt)
1. **GCC Constructor-based PG Registry** - Eliminates our manual 74+ entry registry, zero maintenance, handles reset data properly. This is the most impactful improvement.

### High Priority (Should Adopt)
1. **Cache-busting** for WASM script loading
2. **Better overflow logging** with byte position info

### Medium Priority (Consider)
1. **wasmExit()** export for graceful shutdown
2. **OPFS** for simpler persistence architecture (if browser support is acceptable)

### Low Priority / Future
1. **Socket proxy** for simulator support
2. **pthreads** for better real-time performance
3. **Memory visualization** for debugging

### Not Needed (Our Approach Is Better)
1. MSP parsing in JavaScript - we reuse firmware code
2. Message fragmentation - our buffer is large enough
3. Multi-port support - single port sufficient for configurator
