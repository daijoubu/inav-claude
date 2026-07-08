# Task Assignment: Execute DroneCAN HITL GPS Tests

**Date:** 2026-02-14 16:35 | **From:** Manager | **To:** Developer | **Priority:** HIGH

## Task

Execute the previously skipped DroneCAN GPS-related HITL tests now that you have a DroneCAN GPS module available.

## Background

Previous test session had 16 tests skipped due to no DroneCAN GPS hardware available. Previous results: 13 PASS, 0 FAIL, 16 SKIP. Now we can complete the GPS-related tests.

## Tests to Execute

From `claude/projects/active/dronecan-hitl-gps-tests/todo.md`:

### Phase 1: Basic Validation
1. **TEST-GPS-001:** GPS Device Discovery
   - Power on DroneCAN GPS module
   - Verify GPS is discovered on CAN bus
   - Verify GPS node appears in INAV configurator

2. **TEST-GPS-002:** Position Data Reception
   - Wait for GPS fix
   - Verify latitude/longitude data received
   - Verify altitude data received

### Phase 2: Functional Testing
3. **TEST-GPS-003:** Velocity Data Reception
   - Move vehicle or simulate movement
   - Verify velocity data (ground speed) is received
   - Verify heading data is received

4. **TEST-GPS-004:** Fix Quality Reporting
   - Verify satellites count is displayed
   - Verify HDOP/VDOP values are reasonable
   - Verify fix type (2D/3D) is correctly reported

5. **TEST-INT-001:** GPS + Battery Simultaneous
   - Verify GPS and battery both operational
   - Verify no CAN bus errors with both devices
   - Verify data refresh rates are maintained

### Phase 3: Robustness Testing
6. **TEST-GPS-006:** GPS Loss and Recovery
   - Disconnect GPS module
   - Verify GPS loss is detected
   - Reconnect GPS module
   - Verify GPS recovery and data resume

7. **TEST-INT-004:** Hot Plug - GPS
   - Power on FC without GPS
   - Connect GPS module
   - Verify GPS is discovered
   - Verify data starts flowing

### Phase 4: Stress Testing
8. **TEST-GPS-005:** GPS Fix2 Message Support
   - Verify Fix2 message is being used
   - Verify all Fix2 fields are parsed correctly

9. **TEST-GPS-007:** GPS Data Update Rate
   - Measure actual update rate
   - Verify meets requirements (typically 5-10Hz)
   - Verify no dropped frames

## Project Directory

`claude/projects/active/dronecan-hitl-gps-tests/`

## Base Branch

`maintenance-9.x`

## Success Criteria

- [ ] All GPS device discovery tests pass
- [ ] All position/velocity data reception tests pass
- [ ] All fix quality tests pass
- [ ] GPS + Battery simultaneous operation works
- [ ] GPS loss and recovery works
- [ ] Hot-plug GPS works
- [ ] GPS update rate meets requirements
- [ ] Update TEST-RESULTS.md with new results

## Instructions

1. Guide the user through each test step by step
2. Help them execute tests using the appropriate test infrastructure
3. Document results in TEST-RESULTS.md
4. Report completion back to Manager

---

**Manager**
