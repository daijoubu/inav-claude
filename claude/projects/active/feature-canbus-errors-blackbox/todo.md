# Todo: CAN Bus Error Tracking in Blackbox

## Phase 1: Research

- [ ] Find STM32 CAN peripheral driver code
- [ ] Identify CAN error flag registers (TEC, REC, LEC)
- [ ] Understand CAN controller state machine
- [ ] Find Blackbox logging structure

## Phase 2: Implementation

- [ ] Create canError_t structure
- [ ] Add error tracking to CAN driver
- [ ] Track state transitions (ERROR_ACTIVE, ERROR_PASSIVE, BUS_OFF)
- [ ] Add Blackbox field definitions
- [ ] Implement Blackbox logging

## Phase 3: Testing

- [ ] Verify build compiles
- [ ] Test Blackbox output

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created
- [ ] Completion report sent to manager
