# Todo: Remove Non-DroneCAN Functions from ITCM

## Phase 0: Pre-Work Discussion

- [ ] Discuss with user: what correct behaviour looks like for each of the three functions
- [ ] Agree on test plan before removing attributes

## Phase 1: Audit and Remove

- [ ] Confirm FAST_CODE / section attribution for each function in source
- [ ] Remove FAST_CODE from `taskSendSbus2Telemetry`
- [ ] Remove FAST_CODE from `calculateThrottleStatus`
- [ ] Remove FAST_CODE from `applySensorAlignment`

## Phase 2: Validation

- [ ] Build for MATEKF765SE — confirm ITCM utilisation decreases
- [ ] Verify SBUS2 telemetry behaves correctly
- [ ] Verify throttle status flags are unaffected
- [ ] Verify sensor alignment applied correctly
- [ ] Run unit tests if available

## Completion

- [ ] Code compiles
- [ ] Tested per agreed plan
- [ ] PR created targeting `maintenance-10.x`
- [ ] Completion report sent to manager
