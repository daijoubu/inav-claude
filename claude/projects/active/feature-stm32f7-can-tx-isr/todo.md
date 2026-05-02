# Todo: STM32F7 CAN TX ISR Migration

## Phase 0: Prerequisites (LOG_DEBUG Cleanup)

- [ ] Remove or replace `LOG_DEBUG` from `canardSTM32Transmit()` line 166
  - **HARD BLOCKER**: calling printf-family from ISR context is undefined behaviour
  - Replace with a counter/flag; log outside interrupt context
- [ ] Reduce verbose `LOG_DEBUG` in `canardSTM32ComputeTimings()` (6 calls → 1 summary line)
  - Acceptable at init but noisy; reduce before upstream submission
- [ ] Gate or reduce per-frame `LOG_DEBUG` calls in `dronecan.c` transfer handler (~10 calls)
  - These fire on every received frame; must be gated before upstream submission

## Phase 1: Investigation

- [ ] Locate STM32F7 CAN driver source file(s)
- [ ] Understand current TX implementation (polling, mailbox management)
- [ ] Identify how F4/H7 CAN TX ISR is done (for reference pattern)
- [ ] Confirm whether TX queue exists or needs adding

## Phase 2: Implementation

- [ ] Implement TX ISR handler for CAN TX mailbox empty interrupts
- [ ] Add/extend TX frame queue if needed
- [ ] Enable TX interrupts in CAN peripheral init
- [ ] Remove or gate blocking TX polling code

## Phase 3: Validation

- [ ] Firmware builds cleanly for F7 targets
- [ ] DroneCAN GPS operates correctly
- [ ] Multi-frame transfers verified in order
- [ ] No regressions on existing CAN functionality

## Completion

- [ ] Code compiles
- [ ] Tested on hardware (or SITL if available)
- [ ] PR created targeting `maintenance-10.x`
- [ ] Completion report sent to manager
