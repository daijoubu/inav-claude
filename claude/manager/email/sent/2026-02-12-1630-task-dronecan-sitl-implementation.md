# Task Assignment: DroneCAN SITL Implementation - Phases 2.2 & 2.3

**Date:** 2026-02-12 16:30
**From:** Manager
**To:** Developer
**Project:** dronecan-sitl-implementation
**Priority:** MEDIUM
**Estimated Effort:** 12 hours (8h + 4h)

## Task

Complete the DroneCAN SITL implementation by implementing the SocketCAN driver (Phase 2.2) and comprehensive testing/documentation (Phase 2.3).

Phase 2.1 (Stub Driver Foundation) is already complete - great work! Now we need real CAN communication via SocketCAN.

## Background

The SITL build now compiles with USE_DRONECAN and the stub driver is in place. The next step is to make the driver actually communicate using Linux SocketCAN, enabling:
- Real CAN frame transmission/reception on vcan0
- Multi-node DroneCAN testing (multiple SITL instances)
- External tooling support (candump, cansend)
- Foundation for future HITL testing

## What to Do

### Phase 2.2: SocketCAN Integration (8 hours)

1. **Implement SocketCAN in `canard_sitl_driver.c`:**
   - Socket creation with `socket(PF_CAN, SOCK_RAW, CAN_RAW)`
   - Interface binding to "vcan0" (or configured interface)
   - Non-blocking I/O using `select()` or `poll()`

2. **Implement frame conversion:**
   - TX: Convert libcanard CanardCANFrame to `struct can_frame`
   - RX: Convert `struct can_frame` to libcanard CanardCANFrame
   - Handle Extended Frame format (EFF) for DroneCAN

3. **Add configuration:**
   - Add `DRONECAN_SITL_INTERFACE` setting (default: "vcan0")
   - Add to `src/main/target/SITL/target.h` or as a CLI setting

4. **Error handling:**
   - Graceful fallback to stub if socket creation fails
   - Proper logging for debugging
   - Socket cleanup on driver shutdown

### Phase 2.3: Testing & Documentation (4 hours)

1. **Create `scripts/test_dronecan_sitl.sh`:**
   - Set up vcan0 (modprobe, ip link add/up)
   - Start SITL in background
   - Use `candump` to verify NodeStatus messages (1Hz)
   - Use `cansend` to inject test frames
   - Run two SITL instances, verify they see each other
   - Cleanup and report pass/fail

2. **Documentation:**
   - Update INAV wiki with vcan setup instructions
   - Document the multi-node testing procedure

## Success Criteria

- [ ] NodeStatus messages visible on vcan0 via candump (1Hz)
- [ ] Can inject RX messages via cansend and see them processed
- [ ] Two SITL instances can communicate on same vcan
- [ ] Gracefully falls back to stub on non-Linux platforms
- [ ] Test script validates all scenarios automatically
- [ ] Wiki documentation updated with setup instructions
- [ ] Code compiles cleanly with no warnings
- [ ] All tests pass on CI/CD

## Project Directory

`claude/projects/active/dronecan-sitl-implementation/`

## Key Files

- `src/main/drivers/dronecan/libcanard/canard_sitl_driver.c` - Modify existing stub
- `src/main/target/SITL/target.h` - Add interface configuration
- `scripts/test_dronecan_sitl.sh` - Create new test script

## Recommended Workflow

1. **inav-builder agent:** Build SITL after each change to verify compilation
2. **sitl-operator agent:** Run SITL for testing with vcan0
3. **test-engineer agent:** Create and run the test script

## Branch Information

**Base Branch:** `maintenance-9.x` (from inavflight/inav)
**PR Target:** inavflight/inav (upstream)

---
**Manager**
