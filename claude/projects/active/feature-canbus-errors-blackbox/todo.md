# Todo List: DroneCAN Bus Error Statistics to Blackbox

**Scope revised 2026-07-14** — cut from 6 fields to 1 (`droneCANBusOffCount` only)
after design review. See `PLAN.md` "Fields Considered And Dropped" for why
TEC/REC/LEC/state were dropped and RxDropCount was deferred.

## Phase 1: Branch Setup

- [x] Create `feature/canbus-errors-blackbox` off `fix/h7-dronecan-driver` (PR #11607's branch) — done 2026-07-14, sitting clean at tip `37ec2baf3`, no commits ahead

## Phase 2: Blackbox Integration (`blackbox.c` only — see PLAN.md for exact code)

- [ ] Extend `blackboxSlowState_t` with `droneCANBusOffCount` (uint32_t, `#ifdef USE_DRONECAN`)
- [ ] Add matching field def to `blackboxSlowFields[]`
- [ ] Populate the field in `loadSlowState()` via `dronecanGetBusOffCount()`
- [ ] Write the field in `writeSlowFrame()`

## Phase 3: Validation

- [ ] Full build matrix: F4, F7, H7, AT32 (IFLIGHT_BLITZ_ATF435), SITL
- [ ] Bench/flight test on F7 with DroneCAN node attached; verify log header + S-frame values
- [ ] Verify `droneCANBusOffCount` increments on a real bus-off event (disconnect CAN bus briefly)
- [ ] Cross-check count against live `dronecan` CLI output

## Completion

- [ ] Draft PR opened against `maintenance-10.x`
- [ ] PR description notes rebase-pending-on-#11607 and the scope-cut rationale (see PLAN.md PR Notes)
- [ ] Send completion report to manager
