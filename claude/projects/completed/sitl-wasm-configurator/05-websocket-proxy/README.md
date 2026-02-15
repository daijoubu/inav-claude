# Component: WebSocket Proxy Architecture (Phase 2b - DEFERRED)

**Status:** ⏸️ Deferred / Superseded by Phase 5
**Reason:** Direct MSP function calls (Phase 5) eliminated the need for proxy architecture

---

## Overview

This component documents the WebSocket proxy architecture that was originally planned for Phase 2b to enable Configurator ↔ WASM SITL communication. However, Phase 5's direct function call approach proved simpler and more efficient.

## Historical Context

### The Problem (Discovered in Phase 2)

**Native SITL Architecture:**
- SITL acts as WebSocket **SERVER**
- Uses POSIX APIs: `socket()`, `bind()`, `listen()`, `accept()`
- Listens on port 5771
- Configurator connects **TO** SITL

**Browser/WASM Limitation:**
- ❌ Browsers **cannot create socket servers**
- ❌ POSIX socket APIs don't exist in WebAssembly
- ❌ Cannot listen for incoming connections

### Proposed Solutions (Phase 2b Planning)

Three architectures were evaluated:

#### Solution 1: Proxy Server (RECOMMENDED at the time)
```
INAV Configurator (Browser)
    ↓ WebSocket Client
Proxy Server (Node.js/Python, localhost:5771)
    ↓ Emscripten WebSocket POSIX shim
WASM SITL (Browser)
```

**Pros:**
- Minimal SITL code changes
- Existing WebSocket code works
- Bidirectional communication

**Cons:**
- Requires separate proxy process
- Added complexity
- User must run proxy server

#### Solution 2: Direct MSP via postMessage()
**Status:** Explored in Phase 5, became the winning solution!

#### Solution 3: Rewrite WebSocket Code
**Status:** Rejected (too invasive)

## Why This Was Deferred

**Phase 5 Discovery:** Direct WASM function calls work perfectly for MSP communication.

**Comparison:**

| Aspect | Proxy (Phase 2b) | Direct Calls (Phase 5) |
|--------|------------------|------------------------|
| **Complexity** | High (proxy server, WebSocket shims) | Low (single C function) |
| **User Setup** | Must run proxy server | None (pure browser) |
| **Performance** | WebSocket overhead + serialization | Zero overhead |
| **Code Changes** | Minimal SITL changes | One new file (wasm_msp_bridge.c) |
| **Deployment** | Multi-process | Single page load |

**Decision:** Phase 5's approach is superior in every way for MSP communication.

## When Proxy Might Still Be Needed

The proxy architecture may still be relevant for:

1. **Full Simulator Integration**
   - If SITL's X-Plane UDP socket code needs to work in browser
   - Flight dynamics simulation with external tools

2. **Hardware-in-the-Loop (HITL)**
   - Connecting browser WASM to real hardware via USB/serial
   - Would require browser Serial API or WebUSB instead of proxy

3. **Legacy Compatibility**
   - Running old Configurator versions against WASM SITL
   - Supporting tools that expect WebSocket server

## Current Status

**For MSP Communication:** ✅ **SOLVED** by Phase 5 direct calls

**For Future Enhancements:** ⏸️ **DEFERRED** until specific use case emerges

## Documentation

- **Phase 2 Partial Report:** `email-archive/2025-12-02-wasm-phase2-partial.md`
  - Contains detailed proxy architecture analysis
  - Emscripten WebSocket POSIX API documentation
  - Implementation effort estimates

## Related Components

- **04-msp-protocol/** - The solution that replaced this approach
- **06-configurator-integration/** - Configurator integration without proxy

## Recommendation

**For Phase 6:** Use direct MSP calls (Phase 5 approach). Only revisit proxy architecture if a specific requirement emerges that cannot be solved with direct function calls.
