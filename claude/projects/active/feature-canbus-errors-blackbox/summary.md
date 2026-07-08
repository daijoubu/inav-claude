# Project: DroneCAN Bus Error Statistics to Blackbox

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-02-14
**Started:** 2026-07-07
**Estimated Time:** 2-3 hours (reduced from original estimate — bus-off counter already exists, no `dronecan.c`/`.h` changes needed)

## Overview

Log CAN bus error statistics (TEC, REC, LEC, bus-off count, RX drop count) to the INAV blackbox slow frame so intermittent CAN bus problems are diagnosable from flight logs rather than requiring live debugging via the `dronecan` CLI command.

## Problem

DroneCAN bus health data (error counters, bus-off events, RX drops) is only visible live via the `dronecan` CLI command. When a CAN bus problem occurs in flight and isn't actively being watched, there's no record of it afterward — the user has no way to correlate flight log timing/behavior with bus health.

## Decision Log

- **2026-07-07:** Unblocked from waiting on PR #11607 to merge. Branching directly off `fix/h7-dronecan-driver` (#11607's branch) instead — same pattern already used by 4 other stacked DroneCAN branches. Will rebase onto `maintenance-10.x` once #11607 merges.
- **2026-07-07:** Considered basing on `feature/dronecan-param-getset` instead (has configurator DroneCAN tab support) — rejected, since this project's scope is blackbox-log-only with no configurator UI component, so the deeper stack would add unneeded rebase surface with no benefit.
- **2026-07-07:** `PLAN.md` rewritten after finding it stale relative to the current `fix/h7-dronecan-driver` branch — see PLAN.md's own revision note for the three specific discrepancies found (bus-off counter already implemented, `tx_dropped`/`tx_queue_hwm`/`rx_buffer_hwm` fields don't exist, RX-drop-count and pool-allocator-stats getters exist but weren't in the original plan).

## Scope

**In Scope:**
- `blackbox.c` — extend `blackboxSlowState_t`, add field defs, `loadSlowState()`, `writeSlowFrame()`
- 6 new slow-frame fields: `droneCANState`, `droneCANTec`, `droneCANRec`, `droneCANLec`, `droneCANBusOffCount`, `droneCANRxDropCount`

**Out of Scope (see PLAN.md for detail):**
- TX-side drop counting — no backing instrumentation exists today; would be new scope, not just wiring
- High-water-mark tracking for TX queue / RX buffer — only instantaneous fill levels exist
- Pool allocator stats (`peak_usage_blocks`) — flagged as optional in PLAN.md, not committed to scope; discuss before adding

## Implementation

See `PLAN.md` for full field-by-field implementation detail, exact code snippets, and file locations.

## Success Criteria

- [ ] `blackboxSlowState_t`, `blackboxSlowFields[]`, `loadSlowState()`, `writeSlowFrame()` all updated consistently (field order matches across all three)
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] Blackbox log verified on real hardware: header lists new fields, values match live `dronecan` CLI output, bus-off count increments on a real bus-off event
- [ ] Confirmed the CLI command and blackbox logger don't double-consume `canardSTM32GetAndClearRxDropCount()`'s destructive read
- [ ] Draft PR opened against `maintenance-10.x` (will need rebase once #11607 merges)

## Priority Justification

Diagnostic value for troubleshooting intermittent CAN issues without requiring a live debug session. Not urgent, but low-effort now that the foundational counters already exist upstream.

## Dependencies

Branched off `fix/h7-dronecan-driver` (PR #11607, unmerged) — will need a rebase onto `maintenance-10.x` once #11607 lands, same as the other 4 stacked DroneCAN branches.
