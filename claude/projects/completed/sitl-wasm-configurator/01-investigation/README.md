# Component: Investigation & Feasibility (Initial Research)

**Status:** ✅ Complete
**Time Investment:** Research phase before Phase 1 implementation
**Key Deliverable:** GO decision for WASM compilation feasibility

---

## Overview

This component contains the initial research and feasibility assessment that determined whether INAV SITL could be compiled to WebAssembly for browser execution.

## What This Answered

**Primary Question:** Can INAV SITL firmware be compiled to WebAssembly and run in a browser?

**Answer:** ✅ **Conditional GO** - Feasible with parameter group registry workaround

## Key Documents

### 1. `summary.md`
- Complete project overview
- Problem statement and motivation
- Research findings summary

### 2. `02-emscripten-research.md`
- Emscripten toolchain evaluation
- WASM compilation requirements
- Browser API limitations

### 3. `03-feasibility-assessment.md`
- Technical blockers identified
- Solution approaches evaluated
- GO/NO-GO decision matrix

### 4. `04-final-recommendation.md`
- Conditional GO decision
- Implementation roadmap
- Risk assessment

### 5. `wasm_pg_registry.md`
- Deep dive into parameter group linker script challenge
- Analysis of 3 solution approaches
- Recommended approach (script-generated registry)

## Key Findings

### Blockers Identified

1. **Parameter Group Registry** (CRITICAL)
   - INAV uses GNU LD `PROVIDE_HIDDEN()` and custom sections
   - wasm-ld doesn't support these features
   - **Solution:** Script-generated manual registry

2. **WebSocket Server Architecture** (MAJOR)
   - SITL normally acts as WebSocket server
   - Browsers cannot create socket servers
   - **Solution:** Proxy architecture or direct MSP calls (Phase 5 proved direct calls work!)

3. **Threading & SharedArrayBuffer** (MODERATE)
   - SITL uses pthreads
   - Requires COOP/COEP headers and SharedArrayBuffer
   - **Solution:** HTTP server with correct headers

4. **Filesystem Access** (MODERATE)
   - EEPROM simulation needs persistent storage
   - **Solution:** IndexedDB via Emscripten FS API

### Decision Rationale

**GO Decision Based On:**
- Parameter group registry has viable workaround (script generation)
- Emscripten toolchain is mature and well-documented
- pthread support available via SharedArrayBuffer
- IndexedDB provides persistence
- WebSocket proxy is implementable (though deferred to Phase 6)

**Risk Mitigation:**
- Start with minimal POC (Phase 1: just compilation)
- Incremental phases to validate each component
- Early testing in browser environment

## Research Impact on Implementation

This investigation led to the phased approach:
- **Phase 1:** Build system (validate compilation)
- **Phase 2a:** Test infrastructure (validate browser loading)
- **Phase 3:** Runtime PG system (validate memory management)
- **Phase 4:** Scheduler integration (validate event loop)
- **Phase 5:** MSP protocol (validate communication)
- **Phase 6:** Configurator integration (full user-facing feature)

## Outcome

Research successfully de-risked the project and provided a clear implementation path. The conditional GO proved correct - all identified blockers had workable solutions.

## Next Component

→ **02-build-system/** - Implementation of WASM compilation infrastructure
