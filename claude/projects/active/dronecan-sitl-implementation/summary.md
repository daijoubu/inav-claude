# Project: DroneCAN SITL Implementation (Phase 2)

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature / Driver Implementation
**Created:** 2026-02-12
**Estimated Effort:** 16 hours

## Overview

Implement DroneCAN support in INAV SITL using a hybrid approach: Linux SocketCAN for full CAN simulation (primary) with graceful stub fallback for non-Linux platforms. This enables developers to test DroneCAN module functionality in the Software-In-The-Loop simulator without physical hardware.

## Problem

DroneCAN module is currently excluded from SITL builds via `#if defined(USE_DRONECAN) && !defined(SITL_BUILD)` in dronecan.c. This prevents:
- Unit testing of DroneCAN-dependent code
- Multi-node DroneCAN testing (node discovery, message routing)
- Integration testing before hardware deployment
- HITL testing with real DroneCAN nodes

## Solution

**Hybrid Approach: SocketCAN + Stub Fallback**

1. **Primary (Linux):** Real CAN protocol simulation via Linux SocketCAN/vcan
   - Actual CAN frames through kernel stack
   - Multi-node capability for node discovery testing
   - External tooling support (candump, cansend, can-utils)
   - Hardware bridging for HITL testing

2. **Fallback (macOS/Windows):** Stub driver for basic testing
   - Graceful degradation on non-Linux platforms
   - Allows unit testing without vcan setup
   - Foundation for future platform-specific implementations

## Implementation

### Phase 2.1: Stub Driver Foundation (4 hours)
Create minimal working SITL DroneCAN support with stub in-process driver.

**Files to Create:**
- `src/main/drivers/dronecan/libcanard/canard_sitl_driver.c` - New SITL-specific CAN driver

**Files to Modify:**
- `src/main/drivers/dronecan/dronecan.c` - Remove `!defined(SITL_BUILD)` guard
- `src/main/drivers/dronecan/libcanard/canard_stm32_driver.h` - Add SITL conditional
- `cmake/sitl.cmake` - Include new driver source file
- `src/main/target/SITL/target.h` - Add `USE_DRONECAN` definition

**Tasks:**
- Create stub `canard_sitl_driver.c` with no-op init/TX/RX functions
- Modify conditional compilation guards
- Update CMake build configuration
- Verify SITL compiles with USE_DRONECAN enabled
- Verify DroneCAN task initializes without crash

### Phase 2.2: SocketCAN Integration (8 hours)
Implement real CAN communication via Linux SocketCAN API.

**Files to Modify:**
- `src/main/drivers/dronecan/libcanard/canard_sitl_driver.c` - Add SocketCAN implementation
- `src/main/target/SITL/target.h` - Add interface name configuration

**Tasks:**
- Implement SocketCAN socket creation and management
- Add non-blocking I/O using select()/poll()
- Implement TX function to send frames via socket
- Implement RX function to receive frames from socket
- Add interface name configuration (`DRONECAN_SITL_INTERFACE`, default: "vcan0")
- Add graceful fallback to stub on socket errors
- Handle socket lifecycle (init, cleanup, error recovery)

### Phase 2.3: Testing & Documentation (4 hours)
Verify functionality and document usage.

**Tasks:**
- Create test script (`scripts/test_dronecan_sitl.sh`)
- Test single SITL instance with vcan0
- Test multi-node scenario (2 SITL instances on same vcan)
- Test TX with candump verification
- Test RX with cansend injection
- Update wiki with vcan setup instructions
- Document testing procedure in project notes

## Success Criteria

- [x] Investigation phase completed (Phase 1)
- [ ] SITL compiles with `USE_DRONECAN` enabled (Phase 2.1)
- [ ] DroneCAN task initializes and runs in SITL (Phase 2.1)
- [ ] NodeStatus messages visible on vcan0 via candump (Phase 2.2)
- [ ] Can inject RX messages via cansend (Phase 2.2)
- [ ] Two SITL instances can communicate on same vcan (Phase 2.2)
- [ ] Gracefully falls back to stub on non-Linux platforms (Phase 2.2)
- [ ] Test script validates all scenarios (Phase 2.3)
- [ ] Wiki documentation updated (Phase 2.3)
- [ ] Code compiles cleanly with no warnings
- [ ] All tests pass on CI/CD (where vcan available)

## Related

- **Investigation:** [investigate-dronecan-sitl](../completed/investigate-dronecan-sitl/) - Phase 1 research completed 2026-02-12
- **Research Files:** `claude/developer/workspace/investigate-dronecan-sitl/`
  - `RESEARCH-FINDINGS.md` - Architecture analysis
  - `SOLUTION-OPTIONS.md` - Three options evaluation
  - `RECOMMENDATION.md` - Implementation plan
- **PR:** TBD (when created)
- **Assignment:** `manager/email/sent/dronecan-sitl-implementation-assign.md`

## Technical Notes

- **SocketCAN Kernel Module:** Requires `CONFIG_CAN=y` and `CONFIG_CAN_RAW=y` (built into most modern Linux distros)
- **Virtual CAN Setup:** `modprobe vcan && ip link add dev vcan0 type vcan && ip link set up vcan0`
- **UAVCAN Node IDs:** 1-125 for regular nodes, 0 for anonymous
- **DroneCAN Message Period:** NodeStatus typically 1Hz, payload varies by message type
- **libcanard Design:** Core library is platform-independent; only driver layer needs SITL implementation

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| vcan not available in CI | Medium | Fall back to stub, log warning |
| Socket permission issues | Low | Document sudo setup, test locally first |
| Non-blocking I/O complexity | Low | Use select() with proper timeout handling |
| Memory differences from hardware | Low | Use same pool sizes as STM32 implementation |

