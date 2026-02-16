# Todo: Investigate DroneCAN NodeStatus Content

## Phase 1: Current Implementation

- [x] Find NodeStatus broadcast in dronecan.c
- [x] Document current health, mode, sub_mode, vendor_status values
- [x] Check broadcast frequency

## Phase 2: INAV State Analysis

- [x] List INAV states relevant to "health" (sensor status, failsafe, etc.)
- [x] List INAV states relevant to "mode" (armed, CLI, bootloader, etc.)
- [x] Identify candidates for vendor_specific_status_code

## Phase 3: Recommendations

- [x] Propose health mapping (what triggers WARNING, ERROR, CRITICAL)
- [x] Propose mode mapping (when to use each mode value)
- [x] Propose vendor_status encoding (if useful)
- [x] Note any concerns or trade-offs

## Completion

- [x] FINDINGS.md created with recommendations
- [ ] Report sent to manager
