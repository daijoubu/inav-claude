# Todo List: DroneCAN Bus Error Statistics to Blackbox

## Phase 1: Branch Setup

- [ ] Create `feature/canbus-errors-blackbox` off `fix/h7-dronecan-driver` (PR #11607's branch)

## Phase 2: Blackbox Integration (`blackbox.c` only — see PLAN.md for exact code)

- [ ] Extend `blackboxSlowState_t` with 6 `#ifdef USE_DRONECAN` fields
- [ ] Add matching field defs to `blackboxSlowFields[]`
- [ ] Populate fields in `loadSlowState()` via `canardSTM32GetProtocolStatus()`, `dronecanGetState()`, `dronecanGetBusOffCount()`, `canardSTM32GetAndClearRxDropCount()`
- [ ] Write fields in `writeSlowFrame()` — same order as struct/field-defs
- [ ] Confirm blackbox is the sole caller of `canardSTM32GetAndClearRxDropCount()` (destructive read — don't double-consume with the CLI command)

## Phase 3: Validation

- [ ] Full build matrix: F4, F7, H7, AT32 (IFLIGHT_BLITZ_ATF435), SITL
- [ ] Bench/flight test on F7 with DroneCAN node attached; verify log header + S-frame values
- [ ] Verify `droneCANBusOffCount` increments on a real bus-off event (disconnect CAN bus briefly)
- [ ] Cross-check TEC/REC/LEC values against live `dronecan` CLI output

## Completion

- [ ] Draft PR opened against `maintenance-10.x`
- [ ] PR description notes rebase-pending-on-#11607 and TX-drop-counting is out of scope
- [ ] Send completion report to manager
