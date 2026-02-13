# Todo: DroneCAN SITL Implementation (Phase 2)

**Assigned to:** Developer
**Started:** TBD
**Completed:** TBD

---

## Phase 2.1: Stub Driver Foundation (4 hours)

- [ ] Create `src/main/drivers/dronecan/libcanard/canard_sitl_driver.c` with stub implementation
- [ ] Modify `src/main/drivers/dronecan/dronecan.c`: Change `!defined(SITL_BUILD)` to allow SITL builds
- [ ] Add SITL guards in `src/main/drivers/dronecan/libcanard/canard_stm32_driver.h` around STM32-specific code
- [ ] Update `cmake/sitl.cmake` to include new `canard_sitl_driver.c` source file
- [ ] Add `USE_DRONECAN` definition to `src/main/target/SITL/target.h`
- [ ] Build SITL with `USE_DRONECAN` enabled and verify compilation succeeds
- [ ] Run SITL and verify DroneCAN task initializes without crash
- [ ] Document findings in workspace notes

---

## Phase 2.2: SocketCAN Integration (8 hours)

- [ ] Implement SocketCAN socket creation in `canard_sitl_driver.c`
- [ ] Implement non-blocking socket I/O using select() or poll()
- [ ] Implement TX function: Convert libcanard frames to CAN frames and send via socket
- [ ] Implement RX function: Receive CAN frames from socket and convert to libcanard format
- [ ] Add interface name configuration: `DRONECAN_SITL_INTERFACE` setting (default: "vcan0")
- [ ] Add graceful fallback logic: Fall back to stub if socket creation/binding fails
- [ ] Add socket error handling and logging for debugging
- [ ] Test SocketCAN implementation with vcan0
- [ ] Verify NodeStatus messages visible on vcan0 using candump
- [ ] Test RX: Inject frames with cansend and verify reception
- [ ] Test multi-node: Run two SITL instances on same vcan and verify communication

---

## Phase 2.3: Testing & Documentation (4 hours)

- [ ] Create `scripts/test_dronecan_sitl.sh` test script
  - [ ] vcan0 setup (modprobe vcan, ip link add/set up)
  - [ ] Start SITL in background
  - [ ] Monitor for NodeStatus with candump
  - [ ] Inject test frames with cansend
  - [ ] Verify multi-node communication
  - [ ] Cleanup and report results
- [ ] Run test script and verify all checks pass
- [ ] Test on Linux (primary platform)
- [ ] Verify fallback behavior on non-Linux (macOS/Windows if available)
- [ ] Update INAV wiki with vcan0 setup instructions
- [ ] Update INAV wiki with DroneCAN SITL testing procedure
- [ ] Document all testing scenarios and results

---

## Code Quality & Integration

- [ ] Code compiles without warnings (all platforms)
- [ ] No whitespace/style issues (match surrounding code)
- [ ] Error handling is comprehensive and logged appropriately
- [ ] Memory is properly managed (no leaks, matching hardware driver patterns)
- [ ] Code follows INAV conventions (similar to other SITL drivers)

---

## Completion

- [ ] All phases 2.1, 2.2, 2.3 complete
- [ ] Code passes compilation and runs without crash
- [ ] Test script validates all success criteria
- [ ] Wiki documentation updated with setup and usage
- [ ] Create pull request with all changes
- [ ] All CI checks pass (or document expected failures like vcan not available)
- [ ] Send completion report to manager

---

## Notes

**Phase 2.1 Output:** SITL builds with USE_DRONECAN, DroneCAN task runs (but no actual CAN communication)

**Phase 2.2 Output:** Real CAN frames flow on vcan0, multi-node testing possible, non-Linux fallback works

**Phase 2.3 Output:** Complete documentation and verified test suite

**Effort Distribution:** 4h foundation + 8h SocketCAN + 4h testing = 16h total

**Dependency:** Requires completion of Phase 1 (investigate-dronecan-sitl) ✅ Completed 2026-02-12

