# WASM SITL Implementation Comparison: Scavanger vs Our Implementation

This document compares two independent WASM SITL implementations:
- **Scavanger's implementation**: `/scavanger_wasm/inav/` branch `WebAssembly`
- **Our implementation**: `inav/` + `inav-configurator/` branch `feature/wasm-sitl-configurator`

---

## 1. Overall Architecture Philosophy

| Aspect | Scavanger | Our Implementation |
|--------|-----------|-------------------|
| **Target Use Case** | Standalone debugger + Configurator (planned) | Configurator integration only |
| **Threading Model** | Multi-threaded (pthreads/web workers) | Single-threaded (Phase 1 MVP) |
| **Simulator Support** | Full (RealFlight, X-Plane via socket proxy) | None (configurator-only) |
| **HTML UI** | Custom debugger HTML (1088 lines) | Integrated into Electron configurator |
| **Socket Proxy** | Required for TCP/simulator connections | Not used |

---

## 2. Build System

### Scavanger (`cmake/wasm.cmake`)
```cmake
-sWASM=1
-sINVOKE_RUN=0              # Don't auto-run main
-sWASMFS=1                  # WebAssembly filesystem
-pthread                     # Enable pthreads
-lwebsocket.js              # WebSocket library
-sPROXY_POSIX_SOCKETS       # Proxy sockets via WebSocket
-sPROXY_TO_PTHREAD          # Main loop in worker thread
-sPTHREAD_POOL_SIZE=10      # Thread pool for workers
-sALLOW_TABLE_GROWTH=1      # Dynamic function tables
```

### Our Implementation (`cmake/sitl.cmake`)
```cmake
-sALLOW_MEMORY_GROWTH=1     # Dynamic memory
-sASYNCIFY=1                # For EM_ASM callbacks to unwind stack
-sWEBSOCKET_URL="..."       # Direct WebSocket (not proxy)
-sFORCE_FILESYSTEM=1        # For potential file ops
-lidbfs.js                  # IndexedDB filesystem (unused currently)
# No pthreads (Phase 1 MVP simplification)
```

**Key Difference**: Scavanger uses pthreads for a true multi-threaded scheduler; we use single-threaded with ASYNCIFY for simpler browser integration.

---

## 3. Serial Communication

### Scavanger: `serial_ex.c` (Message Queue)

**Architecture**: Message-based queue with fragmentation support

```c
// Port-based API with connect/disconnect
bool inavSerialExConnect(int portIndex);
bool inavSerialExDisconnect(int portIndex);
bool inavSerialExSend(int portIndex, const uint8_t* buffer, int recvSize);

// JavaScript polls for outgoing messages
bool serialExHasMessages(void);
bool serialExGetMessage(uint8_t* outPortIndex, uint8_t* outData, uint16_t* outLength);
```

**Features**:
- Multiple port support (SERIAL_PORT_COUNT ports)
- Message queue (256 entries, 256 bytes each)
- Automatic fragmentation of large messages
- Queue overflow protection with error logging
- Thread-safe design for multi-threaded operation

### Our Implementation: `serial_wasm.c` (Ring Buffer)

**Architecture**: Byte-level ring buffers with callback notification

```c
// Byte-level API (no port abstraction)
void serialWriteByte(uint8_t data);    // JS → WASM
int serialReadByte(void);               // WASM → JS
int serialAvailable(void);              // Check bytes ready

// Debug
uint32_t serialGetRxDroppedBytes(void);
uint32_t serialGetTxDroppedBytes(void);
```

**Features**:
- Single virtual port (sufficient for configurator)
- Simple ring buffers (512B RX, 2048B TX)
- Callback notification via EM_JS (`notifySerialDataAvailable`)
- Overflow counters for debugging
- No fragmentation (MSP max is ~256B, fits in buffer)

### Comparison

| Feature | Scavanger | Ours |
|---------|-----------|------|
| Port count | Multiple | Single |
| Data model | Message chunks | Byte stream |
| Notification | JS polls queue | Callback (interrupt-style) |
| Thread safety | Yes (queue locks) | N/A (single-threaded) |
| Large message handling | Fragmentation | Direct (buffer large enough) |

---

## 4. Config/EEPROM Persistence

### Scavanger: File-based with OPFS

```c
// Uses WASMFS with OPFS (Origin-Private File System) backend
void wasmInitFilesystem(void) {
    const backend_t backend = wasmfs_create_opfs_backend();
    wasmfs_create_directory(MOUNT_POINT, 0777, backend);
}
// Mounts to /inav_data/ - standard file I/O works
```

**Uses**: `config_streamer_file.c` with `MOUNT_POINT` prefix

### Our Implementation: RAM + IndexedDB

```c
// RAM-based EEPROM in firmware
uint8_t eepromData[EEPROM_SIZE];

// JavaScript bridge for persistence
uint8_t* wasmGetEepromPtr(void);     // Get buffer address
uint32_t wasmGetEepromSize(void);     // Get size
bool wasmReloadConfig(void);          // Reload after injection
void wasmNotifyEepromSaved(void);     // Notify JS to persist
```

**JavaScript**: IndexedDB via `wasm_sitl_loader.js`
- Loads EEPROM from IndexedDB before `main()`
- Injects into WASM memory via `HEAPU8.set()`
- Saves to IndexedDB when firmware writes config

### Comparison

| Feature | Scavanger | Ours |
|---------|-----------|------|
| Storage backend | OPFS (browser filesystem) | IndexedDB |
| Firmware changes | Minimal (file path only) | Custom RAM streamer + bridge |
| Complexity | Lower (uses existing file I/O) | Higher (custom bridge layer) |
| Browser support | Newer browsers (OPFS) | Wider (IndexedDB is universal) |

---

## 5. JavaScript Integration

### Scavanger: Standalone HTML Debugger

**File**: `inav_WASM.html` (1088 lines)

**Features**:
- MSP protocol implementation in JavaScript
- MSP frame builder and parser
- Message reassembly for fragmented packets
- Memory usage visualization
- Command-line argument support (localStorage)
- Start/Stop/Clear controls
- Full MSP test buttons (API_VERSION, FC_VARIANT, BOARD_INFO)

**Module loading**:
```javascript
wasmScriptTag = document.createElement('script');
wasmScriptTag.src = 'inav_WASM.js?t=' + Date.now();  // Cache-bust
Module.callMain(argv);
```

### Our Implementation: Electron Integration

**Files**:
- `wasm_sitl_loader.js` (567 lines) - Module loading + EEPROM persistence
- `connectionWasm.js` (287 lines) - Connection interface

**Features**:
- Integrates with existing ConnectionFactory pattern
- Uses configurator's MSP implementation (no duplication!)
- IndexedDB EEPROM persistence
- Reboot handling via Electron IPC
- Callback-based data notification

**Module loading**:
```javascript
// noInitialRun: true to inject EEPROM first
Module.HEAPU8.set(storedEeprom, ptr);
Module.callMain();
```

### Comparison

| Feature | Scavanger | Ours |
|---------|-----------|------|
| MSP in JavaScript | Full implementation | None (reuses firmware) |
| UI | Custom debugger | Existing configurator |
| Module cleanup | Script tag removal + wasmExit() | dispose() + page reload |
| Error handling | Console logging | GUI.log() integration |
| Reboot handling | N/A | Page reload via Electron IPC |

---

## 6. Simulator Integration

### Scavanger: Full Simulator Support

**Features**:
- WebSocket-to-POSIX socket proxy for TCP
- RealFlight and X-Plane integration
- Motor/servo channel mapping
- IMU data from simulator (optional)
- Command-line arguments for configuration

**Architecture**:
```
Browser → WebSocket → Proxy (port 8081) → TCP → Simulator
```

### Our Implementation: No Simulator

**Rationale**: Phase 1 MVP focuses on configurator integration only. Simulators require:
1. External proxy server
2. Complex socket bridging
3. COOP/COEP headers for pthreads

---

## 7. Parameter Group (PG) Registry

### Scavanger: GCC Constructor-Based Auto-Registration

**Elegant solution using `__attribute__((constructor))`**

**Modified files**: `config/parameter_group.h` and `config/parameter_group.c`

**How it works** (`parameter_group.h:149-163`):
```c
#if defined(WASM_BUILD)
    #define PG_REGISTER_INIT(_name)                                     \
        __attribute__((constructor(200)))                               \
        static void _name ## _register_init(void) {                     \
            pgRegistryAdd(&_name ## _Registry);                         \
        }
#else
    #define PG_REGISTER_INIT(_name) /* nothing */
#endif
```

**Runtime registry** (`parameter_group.c:27-51`):
```c
#if defined(WASM_BUILD)
    #define PG_REGISTRY_MAX_ENTRIES 256

    static pgRegistry_t __pg_registry_data[PG_REGISTRY_MAX_ENTRIES];
    static size_t __pg_registry_count = 0;

    const pgRegistry_t* __pg_registry_start = __pg_registry_data;
    const pgRegistry_t* __pg_registry_end = __pg_registry_data;

    void pgRegistryAdd(const pgRegistry_t *reg)
    {
        if (__pg_registry_count >= PG_REGISTRY_MAX_ENTRIES) {
            return;  // Error: too many registries
        }
        __pg_registry_data[__pg_registry_count++] = *reg;
        __pg_registry_end = &__pg_registry_data[__pg_registry_count];
    }
#endif
```

**Key insight**: Uses `struct` instead of `union` for reset data in WASM builds to avoid type-punning issues:
```c
#if defined(WASM_BUILD)
    struct {  // NOT union - avoid type-punning
#else
    union {
#endif
        void *ptr;
        pgResetFunc *fn;
    } reset;
```

### Our Implementation: Manual Registry

**Files**:
- `wasm_pg_registry.c` - Hand-coded registry (~74 PGs)
- `wasm_pg_runtime.c` - Lazy allocation for PG memory

**Why Needed**: WASM linker (wasm-ld) doesn't support GNU LD custom sections used by INAV's PG system.

### Comparison

| Feature | Scavanger | Ours |
|---------|-----------|------|
| Registration | Automatic (constructor attr) | Manual (script-generated) |
| Maintenance | Zero (code-driven) | High (update with new PGs) |
| Core INAV changes | Yes (parameter_group.h/.c) | No (separate files) |
| Reset data handling | Struct (avoids union issues) | Pointer-only approach |
| Max registries | 256 (configurable) | Hardcoded list |

**Verdict**: Scavanger's approach is significantly better - automatic registration with no maintenance burden. We should consider adopting it.

---

## 8. Exported Functions

### Scavanger
```cmake
_main, _wasmExit, _malloc, _free, _fcScheduler,
_inavSerialExSend, _inavSerialExConnect, _inavSerialExDisconnect,
_serialExHasMessages, _serialExGetMessage
```

### Our Implementation
```cmake
_main, _serialWriteByte, _serialReadByte, _serialAvailable,
_serialGetRxDroppedBytes, _serialGetTxDroppedBytes,
_wasmGetEepromPtr, _wasmGetEepromSize, _wasmReloadConfig,
_wasmIsEepromValid, _malloc, _free
```

**Difference**: Scavanger exports scheduler (`_fcScheduler`) for worker thread; we export EEPROM bridge functions.

---

## 9. Threading and Main Loop

### Scavanger: Web Worker Thread

```c
void wasmStart(wasmMainThreadType thread) {
    wasmMainThreadWorker = thread;
    wasmInitFilesystem();
    emscripten_set_main_loop(wasmMainLoop, 0, false);
}

void wasmMainLoop(void) {
    if (!wasmMainWorkerThreadStarted && wasmMainThreadWorker != NULL) {
        pthread_create(&wasmMainThread, NULL, wasmMainThreadWorker, NULL);
        wasmMainWorkerThreadStarted = true;
    }
}
```

**Scheduler**: Runs in pthread (web worker) at ~1kHz

### Our Implementation: Single Thread with ASYNCIFY

```cmake
-sASYNCIFY=1  # Allows EM_ASM to unwind call stack
```

**Main loop**: Uses standard SITL scheduler in main thread. ASYNCIFY enables `emscripten_force_exit()` to work correctly during reboot.

---

## 10. Error Handling and Debugging

### Scavanger
- `fprintf(stderr, ...)` for all logging
- Console captures stderr with styling
- Memory bar visualization
- Detailed queue overflow messages

### Our Implementation
- `console.log/error()` via `EM_ASM`
- Overflow counters (`serialGetRxDroppedBytes()`)
- Error callback integration with GUI
- Source maps for browser debugging (`-gsource-map`)

---

## 11. Summary: When to Use Which

| Use Case | Recommended |
|----------|-------------|
| Standalone WASM testing | Scavanger |
| Configurator integration | Our implementation |
| Simulator (X-Plane/RealFlight) | Scavanger |
| Simple MSP testing | Either |
| Settings persistence | Both (different backends) |
| Multi-port serial | Scavanger |
| Single-port MSP | Our implementation (simpler) |

---

## 12. File Inventory

### Scavanger Implementation
| File | Purpose |
|------|---------|
| `cmake/wasm.cmake` | WASM build configuration |
| `drivers/serial_ex.c/h` | Message queue serial |
| `target/SITL/target.c` | WASM init, threading, proxy |
| `target/SITL/wasm/inav_WASM.html` | Debugger UI |
| `config/config_streamer_file.c` | OPFS-based persistence |

### Our Implementation
| File | Purpose |
|------|---------|
| `cmake/sitl.cmake` | WASM build config (integrated) |
| `target/SITL/serial_wasm.c/h` | Ring buffer serial |
| `target/SITL/wasm_eeprom_bridge.c/h` | EEPROM JavaScript bridge |
| `target/SITL/wasm_pg_registry.c` | Manual PG registry |
| `target/SITL/wasm_pg_runtime.c/h` | Lazy PG allocation |
| `target/SITL/wasm_stubs.c` | API stubs |
| `config/config_streamer_ram.c` | RAM-based EEPROM |
| `js/wasm_sitl_loader.js` | Module loader + IndexedDB |
| `js/connection/connectionWasm.js` | Connection interface |
