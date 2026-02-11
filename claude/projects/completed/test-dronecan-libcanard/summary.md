# Project: Generate Test Code for DroneCAN/Libcanard Implementation

**Status:** ✅ COMPLETED
**Priority:** HIGH
**Type:** Testing / Test Development
**Created:** 2026-02-10
**Completed:** 2026-02-10
**Actual Effort:** ~3 hours

## Overview

Create comprehensive unit tests and integration tests for the DroneCAN/UAVCAN implementation (libcanard) added in PR #11313. The add-libcanard branch introduces 26,383+ lines of code including CAN drivers, protocol message handling, GPS support, and battery sensor integration.

## Problem

The add-libcanard branch is a major feature addition that requires thorough test coverage to ensure:
- CAN driver functionality is correct (STM32F7 and STM32H7)
- DroneCAN message encoding/decoding works properly
- GPS over DroneCAN integration functions correctly
- Battery sensor over DroneCAN reports accurate data
- Protocol compliance with DroneCAN/UAVCAN specifications
- No regressions in existing INAV functionality

## Scope

### In Scope

**Unit Tests:**
- CAN driver initialization and configuration (STM32F7, STM32H7)
- Message encoding/decoding for key DSDL types
- Libcanard API usage (transmission, reception, filtering)
- GPS DroneCAN message parsing
- Battery sensor DroneCAN message parsing
- Error handling and edge cases

**Integration Tests:**
- End-to-end DroneCAN communication with SITL
- GPS position updates via DroneCAN
- Battery voltage/current reporting via DroneCAN
- Multi-node scenarios
- Protocol timing and sequencing

### Out of Scope

- Hardware testing with physical CAN devices (user/maintainer responsibility)
- Performance benchmarking
- All 300 DSDL message types (focus on actively used messages)
- CAN bus electrical/physical layer testing

## Key Files to Test

**CAN Drivers:**
- `src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c` (454 lines)
- `src/main/drivers/dronecan/libcanard/canard_stm32h7xx_driver.c` (396 lines)
- `src/main/drivers/dronecan/dronecan.c` (506 lines)

**GPS Integration:**
- `src/main/io/gps_dronecan.c` (163 lines)

**Battery Sensor:**
- `src/main/sensors/battery_sensor_dronecan.c` (55 lines)

**Core Library:**
- `src/main/drivers/dronecan/libcanard/canard.c` (1960 lines)
- `src/main/drivers/dronecan/libcanard/canard.h` (741 lines)

**Key DSDL Messages:**
- `uavcan.equipment.gnss.Fix2` (GPS data)
- `uavcan.equipment.power.BatteryInfo` (battery data)
- `uavcan.protocol.NodeStatus` (node health)
- `uavcan.protocol.GetNodeInfo` (node discovery)

## Implementation Plan

### Phase 1: Unit Tests (8-10 hours)

1. **CAN Driver Tests**
   - Initialization with valid/invalid parameters
   - Frame transmission (standard/extended ID, data/remote)
   - Frame reception and filtering
   - Error state handling
   - Buffer overflow scenarios

2. **Message Encoding/Decoding Tests**
   - GPS Fix2 message serialization/deserialization
   - BatteryInfo message serialization/deserialization
   - NodeStatus message serialization/deserialization
   - Timestamp handling
   - Field boundary conditions

3. **Libcanard API Tests**
   - Memory pool management
   - Transfer transmission
   - Transfer reception
   - Transfer ID management
   - CRC validation

### Phase 2: Integration Tests with SITL (7-10 hours)

1. **GPS DroneCAN Tests**
   - Simulate DroneCAN GPS device sending Fix2 messages
   - Verify INAV receives and processes position updates
   - Test GPS status reporting in configurator
   - Validate coordinate transformations

2. **Battery Sensor DroneCAN Tests**
   - Simulate DroneCAN battery sensor sending BatteryInfo
   - Verify voltage/current readings in INAV
   - Test battery capacity tracking
   - Validate low battery warnings

3. **Multi-Node Tests**
   - Multiple DroneCAN devices on same bus
   - Node discovery and enumeration
   - Message prioritization
   - Bus bandwidth management

4. **Error Recovery Tests**
   - Node timeout handling
   - Message loss scenarios
   - Bus-off recovery
   - Malformed message handling

## Test Tools and Framework

- **Unit Tests:** Standard C testing framework (possibly Unity, or custom test harness)
- **Integration Tests:** SITL with synthetic DroneCAN message injection
- **Test Infrastructure:** Python scripts using mspapi2 to control SITL and verify behavior
- **Message Generation:** Python scripts to generate DroneCAN messages for test scenarios

## Success Criteria

- [ ] Unit tests cover core CAN driver functionality (>80% coverage)
- [ ] Unit tests cover critical message types (GPS, Battery, NodeStatus)
- [ ] Integration tests verify GPS over DroneCAN end-to-end
- [ ] Integration tests verify battery sensor over DroneCAN end-to-end
- [ ] All tests pass with SITL
- [ ] Test documentation explains how to run tests
- [ ] Tests can be integrated into CI pipeline (optional, document requirements)

## Related

- **PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313)
- **Branch:** `add-libcanard` (origin)
- **Base Branch:** TBD (likely `master` or `maintenance-9.x`)
- **Files Changed:** 300 files, 26,383 insertions, 20 deletions
- **Key Commits:**
  - c3ad505a9 - CAN battery voltage meter tested
  - 6e5558390 - DroneCAN battery sensor
  - 569f9532a - SITL 64-bit support

## Notes

- DroneCAN is the successor to UAVCAN v0
- Libcanard is a lightweight, portable CAN stack
- Implementation supports STM32F7 (bxCAN) and STM32H7 (FDCAN)
- MATEKF765 and MATEKH743 targets have CAN hardware support
- This is a high-impact feature requiring thorough validation

## Estimated Timeline

- Unit Tests: 8-10 hours
- Integration Tests: 7-10 hours
- **Total: 15-20 hours**

## Priority Justification

**HIGH priority** because:
1. Large feature addition (26K+ lines) requires comprehensive testing
2. Safety-critical functionality (GPS, battery monitoring)
3. New communication protocol needs validation
4. PR is likely awaiting review - tests will facilitate merge
5. Without tests, regressions may go undetected
