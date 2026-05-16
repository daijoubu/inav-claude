# Todo: STM32F7 CAN TX ISR Migration

## Phase 0: Prerequisites (LOG_DEBUG Cleanup) ✅

- [x] Remove or replace `LOG_DEBUG` from `canardSTM32Transmit()` line 166
- [x] Reduce verbose `LOG_DEBUG` in `canardSTM32ComputeTimings()`
- [x] Gate or reduce per-frame `LOG_DEBUG` calls in `dronecan.c` transfer handler
  - Committed: `3b33ce1` fix: remove LOG_DEBUG calls unsafe in ISR context

## Phase 1: Investigation ✅

- [x] Locate STM32F7 CAN driver source file(s)
- [x] Understand current TX implementation (polling, mailbox management)
- [x] Identify how F4/H7 CAN TX ISR is done (for reference pattern)
- [x] Confirm whether TX queue exists or needs adding

## Phase 2: Implementation ✅

- [x] Implement TX ISR handler for CAN TX mailbox empty interrupts
- [x] Add/extend TX frame queue if needed
- [x] Enable TX interrupts in CAN peripheral init
- [x] Remove or gate blocking TX polling code
  - Committed: `5e73786` drivers: migrate STM32F7 CAN TX to ISR-driven transmission

## Phase 3: Validation 🚧

- [ ] Firmware builds cleanly for F7 targets
- [ ] DroneCAN GPS operates correctly — **odd behaviour observed under long-running tests**
- [ ] Multi-frame transfers verified in order
- [ ] No regressions on existing CAN functionality
- [ ] Debug approach needed: MSP node status messages (from `feature/msp-dronecan-support` branch) or serial CAN peripheral diagnostics

## Completion

- [ ] Code compiles
- [ ] Tested on hardware (or SITL if available)
- [ ] PR created targeting `maintenance-10.x`
- [ ] Completion report sent to manager
