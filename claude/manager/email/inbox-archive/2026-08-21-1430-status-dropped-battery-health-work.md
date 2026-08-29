# Status Update: Dropped Battery Health Guard Work Found During Cell-Voltage Investigation

**Date:** 2026-08-21 14:30
**From:** Developer
**To:** Manager
**Re:** fix-dronecan-cell-voltage-calculation / feature-dronecan-battery-health (completed 2026-06-10) / PR #11698

## Finding

While scoping the cell-voltage investigation task, I found that completed work from `claude/projects/completed/` (the DroneCAN battery health guard project, closed 2026-06-10) appears to have been silently dropped during PR #11698's post-#11607 reconstruction, rather than actually folded in as the completion report claimed.

**Original branch:** `fix/dronecan-battery-health` (2026-06-10) added to `battery_sensor_dronecan.c`/`battery.c`:
- Staleness timer — freezes last-known vbat/amperage after 5s without a CAN message (instead of zeroing, which was causing false `BATTERY_NOT_PRESENT` mid-flight)
- Node-health guard — drops data from DroneCAN nodes reporting ERROR/CRITICAL health
- Status-flag transition logging (TEMP_HOT, TEMP_COLD, OVERLOAD, BAD_BATTERY, NEED_SERVICE, BMS_ERROR)
- OSD "BATT SENSR" staleness warning
- Battery-ID slot filter (0 = any)
- Amperage type fix (uint16_t → int16_t, handles negative charging current)

Completion report (2026-06-10 18:46) states this was "folded into the GPS health-guard PR rather than submitted standalone" — i.e., merged into what's now PR #11698.

**What I verified in git directly (inav repo):**
- PR #11698's branch (`fix/dronecan-gps-health-guard`) currently has **zero diff** against `maintenance-10.x` in `src/main/sensors/` — none of the staleness timer, node-health guard, status-flag logging, or OSD warning survived.
- The only piece that did survive is the battery-ID filter, reconstructed as one `if` in `handle_BatteryInfo()` in `dronecan.c` via commit `97a0368f4` (2026-08-17). That commit's own message says it was "reconstructed against the current dronecan.c... rather than cherry-picked" post-#11607 — the reconstruction evidently covered the GPS-side work only and missed the battery-side health guard entirely.

## Why This Matters Now

I'm assigned to investigate a DroneCAN average-cell-voltage bug (idle cell-count miscount + a load-sag anomaly) that lives in exactly this code (`battery.c`/`battery_sensor_dronecan.c`, `dronecanBatterySensorReceiveInfo()`/`dronecanBattSensorGetVBat()`). The dropped staleness-freeze logic is directly adjacent to — and possibly entangled with — the anomaly being investigated (e.g., a stale/frozen vs. live reading could look like exactly this kind of proportionality mismatch under load). Fixing the cell-voltage bug without also restoring the health-guard work risks either re-touching the same functions twice (once now, once when the guard work is eventually redone) or missing an interaction between the two.

## Recommendation

Tie the two together before submitting the cell-voltage PR: reconstruct the dropped `fix/dronecan-battery-health` work (staleness timer, node-health guard, status-flag logging, OSD warning, amperage type fix) alongside the cell-voltage fix, in the same investigation/PR, rather than fixing cell-voltage now and redoing the health-guard reconstruction separately later. Please advise if you'd prefer this split into two coordinated projects instead (e.g., if PR #11698 is already far enough along that reopening its scope is undesirable) — flagging for your call before I proceed either way.

## Reference

- `claude/projects/completed/INDEX.md` (battery-health entry)
- `claude/projects/active/fix-dronecan-cell-voltage-calculation/`
- inav commit `79d21155a` (original battery-health work, 2026-06-10)
- inav commit `97a0368f4` (GPS-side reconstruction that missed the battery side, 2026-08-17)
- PR #11698

---
**Developer**
