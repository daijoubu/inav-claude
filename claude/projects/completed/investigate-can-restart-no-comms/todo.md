# Todo: Investigate CAN Network No-Comms After INAV Restart

## Phase 1: Code Audit

- [ ] Read `canard_stm32f7xx_driver.c` — review init and start sequence
- [ ] Check whether `HAL_CAN_Start()` issues a proper bus reset
- [ ] Review DroneCAN node allocation table reset on firmware init
- [ ] Check ERROR_PASSIVE / BUS_OFF recovery logic

## Phase 2: Bench Reproduction

- [ ] Connect MATEKF765SE + DroneCAN battery monitor
- [ ] Confirm normal operation on fresh power-on
- [ ] Reboot FC (without power-cycling DroneCAN device)
- [ ] Confirm no-comms failure is reproduced
- [ ] If CAN analyser available: capture bus state after reboot

## Phase 3: Fix

- [ ] Implement fix (bus reset, node re-allocation, or error recovery)
- [ ] Verify FC reboot restores CAN comms without power cycle
- [ ] Verify normal power-on behaviour unchanged

## Completion

- [ ] Root cause documented in summary.md
- [ ] Code compiles, zero warnings
- [ ] Fix verified on hardware
- [ ] PR opened against `maintenance-10.x`
- [ ] Completion report sent to manager
