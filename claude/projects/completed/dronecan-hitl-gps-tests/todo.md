# Todo: Complete DroneCAN HITL GPS Tests

## Phase 1: Basic Validation

- [x] TEST-GPS-001: GPS Device Discovery
  - [x] Power on DroneCAN GPS module
  - [x] Verify GPS is discovered on CAN bus
  - [x] Verify GPS node appears in INAV configurator

- [x] TEST-GPS-002: Position Data Reception
  - [x] Wait for GPS fix
  - [x] Verify latitude/longitude data received
  - [x] Verify altitude data received

## Phase 2: Functional Testing

- [x] TEST-GPS-003: Velocity Data Reception
  - [x] Move vehicle or simulate movement
  - [x] Verify velocity data (ground speed) is received
  - [x] Verify heading data is received

- [x] TEST-GPS-004: Fix Quality Reporting
  - [x] Verify satellites count is displayed
  - [x] Verify HDOP/VDOP values are reasonable
  - [x] Verify fix type (2D/3D) is correctly reported

- [x] TEST-INT-001: GPS + Battery Simultaneous
  - [x] Verify GPS and battery both operational
  - [x] Verify no CAN bus errors with both devices
  - [x] Verify data refresh rates are maintained

## Phase 3: Robustness Testing

- [x] TEST-GPS-006: GPS Loss and Recovery
  - [x] Disconnect GPS module
  - [x] Verify GPS loss is detected
  - [x] Reconnect GPS module
  - [x] Verify GPS recovery and data resume

- [x] TEST-INT-004: Hot Plug - GPS
  - [x] Power on FC without GPS
  - [x] Connect GPS module
  - [x] Verify GPS is discovered
  - [x] Verify data starts flowing

## Phase 4: Stress Testing

- [x] TEST-GPS-005: GPS Fix2 Message Support
  - [x] Verify Fix2 message is being used
  - [x] Verify all Fix2 fields are parsed correctly

- [x] TEST-GPS-007: GPS Data Update Rate
  - [x] Measure actual update rate
  - [x] Verify meets requirements (typically 5-10Hz)
  - [x] Verify no dropped frames

## Completion

- [x] Update TEST-RESULTS.md with results
- [x] Document any issues found
- [ ] Send completion report to manager
