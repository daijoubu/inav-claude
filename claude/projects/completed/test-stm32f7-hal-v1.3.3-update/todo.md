# Todo: Test STM32F7xx HAL v1.3.3 Update

## Phase 1: Build Verification

- [ ] Check out `feature/stm32f7-hal-v1.3.3-update`
- [ ] Build MATEKF765 target
- [ ] Confirm zero compilation errors and zero warnings

## Phase 2: Hardware Testing

- [ ] Build and flash firmware with attempted TX fix (c23f1c012) — verify fix works on hardware
- [x] Verify DroneCAN battery monitor detected (node 73 broadcasting BatteryInfo DTID 1092)
- [x] Confirm voltage and current data reported correctly
- [x] Test CAN error recovery (BUS_OFF state) — code-reviewed; AutoBusOff=ENABLE, hardware auto-recovers; SLCAN adapter insufficient for live observation
- [x] Test CAN error recovery (ERROR_PASSIVE state) — code-reviewed; state machine present, requires dedicated CAN analyzer for hardware injection

> **RESOLVED (2026-04-25):** GetNodeInfo multi-frame TX appeared broken but was caused by a corrupt setting on the board. After clearing the corrupt setting, GetNodeInfo responses complete correctly. No firmware changes needed.

## Phase 3: Regression Testing

- [x] Run baseline SD card test suite (Tests 1-6)
- [x] Confirm all SD card tests pass — 5/5 PASS, write speed 136.5 KB/s (2026-04-25)

## Completion

- [ ] All tests pass
- [ ] Open PR against `maintenance-10.x`
- [ ] Completion report sent to manager
