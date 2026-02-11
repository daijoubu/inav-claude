# Todo: HITL Test Plan for add-libcanard Branch

## Phase 1: Branch Analysis

- [x] Review add-libcanard branch changes
- [x] Identify all DroneCAN message types supported
- [x] Document CAN peripheral types implemented
- [x] Note any configuration settings relevant to testing

## Phase 2: GPS Test Cases

- [x] Device discovery/enumeration test
- [x] Position data reception test
- [x] Velocity data reception test
- [x] Satellite count/fix quality test
- [x] Hot/warm/cold start tests (covered in loss/recovery)
- [x] GPS failover/recovery test

## Phase 3: Battery Monitor Test Cases

- [x] Device discovery/enumeration test
- [x] Voltage reading accuracy test
- [x] Current reading accuracy test
- [x] Capacity/consumption tracking test (via low voltage alarm)
- [x] Multi-cell voltage test (implicit in voltage test)
- [x] Low voltage alert test

## Phase 4: Integration Tests

- [x] Multiple CAN devices simultaneously
- [x] CAN bus error handling
- [x] Device hot-plug behavior
- [x] Performance under CPU load
- [x] Long-duration stability test

## Phase 5: Documentation

- [x] Compile test cases into structured document
- [x] Add test environment requirements
- [x] Define pass/fail criteria for each test
- [x] Prioritize tests by criticality

## Completion

- [x] Test plan document complete
- [x] All test cases have clear procedures
- [x] Pass/fail criteria defined
- [x] Send completion report to manager
