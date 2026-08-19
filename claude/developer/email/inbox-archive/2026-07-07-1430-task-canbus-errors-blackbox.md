# Task Assignment: DroneCAN Bus Error Statistics to Blackbox

**Date:** 2026-07-07 14:30
**From:** Manager
**To:** Developer
**Project:** feature-canbus-errors-blackbox
**Priority:** MEDIUM
**Estimated Effort:** 2-3 hours

## Task

Log DroneCAN bus error statistics to the Blackbox slow frame: TEC, REC, LEC, cumulative bus-off count, and cumulative RX drop count. This makes intermittent CAN bus problems diagnosable from flight logs instead of requiring a live `dronecan` CLI session.

## Background

This project was blocked on `fix-dronecan-driver-rework` PR #11607 merging, since its foundation (`canardProtocolStatus_t` tec/rec/lec fields) only exists on that unmerged branch. Unblocked today: branch directly off `fix/h7-dronecan-driver` (PR #11607's branch), same pattern already used for `feature/dronecan-getnodeinfo`, `feature/dronecan-param-getset`, `fix/dronecan-gps-health-guard`, and `feature/dronecan-dna-server`. You'll need to rebase onto `maintenance-10.x` once #11607 merges, like those branches did.

Important: `PLAN.md` for this project was just rewritten (2026-07-07) after being found stale — it was written in Feb 2026 before the driver rework landed. Three corrections vs. the old plan:
1. `dronecanGetBusOffCount()` already exists in `dronecan.c`/`.h` — no firmware changes needed there, only `blackbox.c`.
2. The old plan assumed `canardProtocolStatus_t` has `tx_dropped`/`tx_queue_hwm`/`rx_buffer_hwm` fields — it doesn't. Don't reference those.
3. A real RX-drop-count getter (`canardSTM32GetAndClearRxDropCount()`, F7-only, stubbed to 0 on H7) and a pool-allocator-stats getter (`dronecanGetPoolStats()`) exist and aren't in the old plan — the RX-drop-count getter is now part of the revised scope.

Please read the current `PLAN.md` in full before starting — don't work from memory of the old version.

## What to Do

1. Read `active/feature-canbus-errors-blackbox/PLAN.md` and `todo.md` in full
2. Create branch `feature/canbus-errors-blackbox` off `fix/h7-dronecan-driver`
3. Implement the 6 blackbox slow-frame fields in `blackbox.c` only (struct, field defs, `loadSlowState()`, `writeSlowFrame()` — exact code in PLAN.md)
4. Watch the field-order-must-match constraint across all three locations (PLAN.md explains why)
5. Confirm the CLI command and blackbox logger don't both call `canardSTM32GetAndClearRxDropCount()` in a way that steals each other's counts (it clears on read) — flagged as a real risk in PLAN.md's testing section
6. Full build matrix: F4, F7, H7, AT32, SITL
7. Bench/flight test on F7 with a DroneCAN node attached; verify against live `dronecan` CLI output
8. Open draft PR against `maintenance-10.x` (note in the PR description that it's stacked on unmerged #11607 and will need a rebase)

## Success Criteria

- [ ] All 6 fields wired consistently across struct/field-defs/load/write
- [ ] Full build matrix passes
- [ ] Hardware-verified: log header shows new fields, values match live CLI, bus-off count increments on a real bus-off event
- [ ] Confirmed no double-consumption of the destructive RX-drop-count read
- [ ] Draft PR opened

## Project Directory

`claude/projects/active/feature-canbus-errors-blackbox/`

---
**Manager**
