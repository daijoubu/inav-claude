# Todo: HITL Test Execution - DroneCAN

## Phase 1: Basic Validation

- [ ] TEST-CFG-001 - Node ID Configuration
- [ ] TEST-CFG-002 - Bitrate Configuration
- [ ] TEST-GPS-001 - GPS Device Discovery
- [ ] TEST-GPS-002 - Position Data Reception
- [ ] TEST-BAT-001 - Battery Device Discovery
- [ ] TEST-BAT-002 - Voltage Reading Accuracy

## Phase 2: Functional Testing

- [ ] TEST-GPS-003 - Velocity Data Reception
- [ ] TEST-GPS-004 - Fix Quality Reporting
- [ ] TEST-BAT-003 - Current Reading Accuracy
- [ ] TEST-BAT-006 - Low Voltage Warning Integration
- [ ] TEST-INT-001 - GPS + Battery Simultaneous

## Phase 3: Robustness Testing

- [ ] TEST-CFG-003 - Invalid Configuration Rejection
- [ ] TEST-GPS-006 - GPS Loss and Recovery
- [ ] TEST-BAT-005 - Battery Monitor Loss and Recovery
- [ ] TEST-INT-004 - Hot Plug - GPS
- [ ] TEST-INT-005 - Hot Plug - Battery Monitor
- [ ] TEST-ERR-001 - CAN Bus-Off Recovery

## Phase 4: Stress Testing

- [ ] TEST-GPS-005 - GPS Fix2 Message Support
- [ ] TEST-GPS-007 - GPS Data Update Rate
- [ ] TEST-BAT-004 - Battery Monitor Update Rate
- [ ] TEST-INT-002 - Multiple CAN Devices
- [ ] TEST-INT-003 - CAN Bus With Other Traffic
- [ ] TEST-ERR-002 - Corrupted Message Handling

## Phase 5: Extended (Time Permitting)

- [ ] TEST-PERF-001 - High Message Rate
- [ ] TEST-PERF-002 - Long Duration Stability
- [ ] TEST-PERF-003 - DroneCAN Task Timing
- [ ] TEST-PERF-004 - Memory Pool Stress
- [ ] TEST-ERR-003 - Node ID Conflict Detection
- [ ] TEST-ERR-004 - Invalid Data Values

## Completion

- [ ] All phases executed
- [ ] Results documented in TEST-RESULTS.md
- [ ] Issues filed for any failures
- [ ] Final report to manager
