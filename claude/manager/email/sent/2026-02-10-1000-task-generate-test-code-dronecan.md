# Task Assignment: Generate Test Code for DroneCAN/Libcanard Implementation

**Date:** 2026-02-10 10:00
**From:** Manager
**To:** Developer
**Project:** test-dronecan-libcanard
**Priority:** HIGH
**Estimated Effort:** 15-20 hours

## Task

Create comprehensive unit tests and integration tests for the DroneCAN/UAVCAN implementation added in the add-libcanard branch (PR #11313).

## Background

The add-libcanard branch introduces a major feature - DroneCAN/UAVCAN support for INAV. This includes:
- 26,383+ lines of code added/changed across 300 files
- CAN bus drivers for STM32F7 (bxCAN) and STM32H7 (FDCAN)
- 300 generated DSDL protocol message files
- GPS over DroneCAN support
- Battery sensor over DroneCAN support
- Targets: MATEKF765, MATEKH743

This is safety-critical functionality (GPS navigation, battery monitoring) that requires thorough test coverage before merge.

## What to Do

### Phase 1: Unit Tests (8-10 hours)

Create unit tests for:

1. **CAN Driver Functionality**
   - Initialization (STM32F7 and STM32H7)
   - Frame transmission (standard/extended ID)
   - Frame reception and filtering
   - Error handling (bus-off, buffer overflow)
   - Files: `canard_stm32f7xx_driver.c`, `canard_stm32h7xx_driver.c`

2. **Message Encoding/Decoding**
   - GPS Fix2 message (GNSS position data)
   - BatteryInfo message (voltage, current, capacity)
   - NodeStatus message (health monitoring)
   - GetNodeInfo request/response (node discovery)
   - Test boundary conditions and error cases

3. **Libcanard API**
   - Memory pool management
   - Transfer transmission/reception
   - Transfer ID management
   - CRC validation

### Phase 2: Integration Tests with SITL (7-10 hours)

Create integration tests for:

1. **GPS over DroneCAN**
   - Inject synthetic DroneCAN GPS messages into SITL
   - Verify INAV receives and processes position updates
   - Test timeout and error recovery
   - File: `src/main/io/gps_dronecan.c`

2. **Battery Sensor over DroneCAN**
   - Inject synthetic battery sensor messages
   - Verify voltage/current readings in INAV
   - Test low battery warnings
   - File: `src/main/sensors/battery_sensor_dronecan.c`

3. **Multi-Node Scenarios**
   - Multiple DroneCAN devices (GPS + battery)
   - Node discovery and enumeration
   - Message prioritization

4. **Error Recovery**
   - Node timeout handling
   - Message loss scenarios
   - Malformed message handling

## Files to Focus On

**Core Implementation:**
- `src/main/drivers/dronecan/dronecan.c` (506 lines)
- `src/main/drivers/dronecan/libcanard/canard.c` (1960 lines)
- `src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c` (454 lines)
- `src/main/drivers/dronecan/libcanard/canard_stm32h7xx_driver.c` (396 lines)

**Application Integration:**
- `src/main/io/gps_dronecan.c` (163 lines)
- `src/main/sensors/battery_sensor_dronecan.c` (55 lines)

**Key DSDL Messages:**
- `uavcan.equipment.gnss.Fix2`
- `uavcan.equipment.power.BatteryInfo`
- `uavcan.protocol.NodeStatus`
- `uavcan.protocol.GetNodeInfo`

## Test Infrastructure

- Use Python scripts with mspapi2 for SITL control and verification
- Create synthetic DroneCAN message generators
- Document test setup and execution procedures
- Consider CI integration requirements

## Success Criteria

- [ ] Unit tests cover CAN driver core functionality (>80% coverage)
- [ ] Unit tests cover critical message types (GPS, Battery, NodeStatus)
- [ ] Integration tests verify GPS over DroneCAN end-to-end
- [ ] Integration tests verify battery sensor over DroneCAN end-to-end
- [ ] All tests pass with SITL
- [ ] Test documentation explains setup and execution
- [ ] Tests can be integrated into CI pipeline (document requirements)

## Recommended Workflow

1. **Checkout and build:** Get add-libcanard branch building on your system
2. **Review PR #11313:** Understand the implementation approach
3. **Plan test structure:** Decide on test framework and directory layout
4. **Unit tests first:** Easier to write and debug, build foundation
5. **Integration tests:** Build on unit tests, verify end-to-end
6. **Document everything:** Tests are useless if no one can run them

## Recommended Agents

- **inav-builder** - Build add-libcanard branch
- **inav-architecture** - Understand DroneCAN subsystem organization
- **test-engineer** - Run and validate tests

## Branch Information

- **Repository:** iNavFlight/inav (upstream)
- **Branch:** `add-libcanard` (origin/add-libcanard)
- **PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313)
- **Base Branch:** TBD (check PR target - likely master or maintenance-9.x)

## Project Directory

`claude/projects/active/test-dronecan-libcanard/`

Contains:
- `summary.md` - Complete project specification
- `todo.md` - Detailed task breakdown with 8 phases

## Timeline

- Unit Tests: 8-10 hours
- Integration Tests: 7-10 hours
- Documentation: 1-2 hours
- **Total: 15-20 hours**

## Notes

- This is HIGH priority - large feature needs validation before merge
- Safety-critical functionality (GPS, battery) requires thorough testing
- DroneCAN is the successor to UAVCAN v0
- Libcanard is a lightweight, portable CAN stack
- Implementation supports STM32F7 (bxCAN) and STM32H7 (FDCAN)

When complete, send a completion report with:
- Test coverage summary
- How to run the tests
- Any issues or bugs found
- Recommendations for PR reviewers

---
**Manager**
