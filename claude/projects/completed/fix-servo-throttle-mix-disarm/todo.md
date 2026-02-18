# Todo: Fix Servo Throttle Mix When Disarmed

## Phase 1: Investigation

- [ ] Use inav-architecture agent to find servo throttle mix disarm code
- [ ] Understand how servo reversal and mixer weights interact with throttle mix
- [ ] Identify the specific line(s) that set throttle mix to 0 on disarm

## Phase 2: Implementation

- [ ] Modify disarm logic to compute correct minimum output
- [ ] Handle reversed servo case
- [ ] Handle negative mixer weight case
- [ ] Verify non-throttle servo channels are unaffected

## Phase 3: Validation

- [ ] Build SITL
- [ ] Build at least one hardware target
- [ ] Test normal servo: goes to min on disarm
- [ ] Test reversed servo: goes to min on disarm
- [ ] Test negative weight: goes to min on disarm

## Completion

- [ ] Code compiles
- [ ] PR created against maintenance-9.x
- [ ] Completion report sent to manager
