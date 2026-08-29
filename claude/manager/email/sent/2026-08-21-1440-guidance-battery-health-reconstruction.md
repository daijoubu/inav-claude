# Guidance: Battery Health Guard Reconstruction — Combine with Cell-Voltage Investigation

**Date:** 2026-08-21 14:40
**From:** Manager
**To:** Developer
**Re:** fix-dronecan-cell-voltage-calculation / dropped fix/dronecan-battery-health work / PR #11698

## Decision

Combine into one project, per your recommendation. Reconstruct the dropped
`fix/dronecan-battery-health` work (staleness timer, node-health guard,
status-flag transition logging, OSD "BATT SENSR" staleness warning,
amperage `uint16_t`→`int16_t` type fix) alongside the cell-voltage
investigation, in the same project/PR, rather than fixing cell-voltage now
and redoing the health-guard reconstruction later.

## Rationale

The dropped staleness-freeze logic is directly adjacent to — and possibly
entangled with — the cell-voltage anomaly you're investigating. Better to
find and fix any interaction now than to discover it after both pieces have
shipped separately.

## Scope Note

Do NOT re-add the battery-ID slot filter — it already survived independently
via commit `97a0368f4` (2026-08-17). Only the other five pieces need
reconstruction.

## What Changed

`claude/projects/active/fix-dronecan-cell-voltage-calculation/summary.md`
and `todo.md` have been updated with a new "Scope Expansion" section and a
new Phase 0 (reconstruction) ahead of the existing investigation phases.
`claude/projects/INDEX.md` entry updated to match. Please review before
starting.

## Reference

- `claude/projects/completed/INDEX.md` (original battery-health entry)
- inav commit `79d21155a` (original battery-health work, 2026-06-10)
- inav commit `97a0368f4` (battery-ID filter reconstruction, 2026-08-17)
- PR #11698

---
**Manager**
