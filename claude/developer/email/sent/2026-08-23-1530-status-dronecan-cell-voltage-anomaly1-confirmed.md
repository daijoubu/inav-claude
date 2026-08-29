# Status Update: DroneCAN Cell Voltage Anomaly #1 Confirmed on Real Hardware

**Date:** 2026-08-23 15:30
**From:** Developer
**To:** Manager
**Type:** Status Update
**Project:** fix-dronecan-cell-voltage-calculation
**Re:** Bench test confirmation of idle/connect-time cell-count miscount

## Current Status

Anomaly #1 (cell-count auto-detection miscount at connect time) is now empirically confirmed on real NEMESIS hardware with a live flight battery connected. The root cause theory from 2026-08-22 (`VBATT_STABLE_DELAY` timing bug) is strengthened by this result.

## What Was Tested

Connected a real flight battery (3S, nominal 12.6V) to NEMESIS aircraft with rapid MSP polling to capture the exact moment of battery connection. The FC auto-detected the cell count as **2 cells** instead of the correct **3 cells**, despite the battery settling to a normal resting voltage of 12.40V (4.13V/cell — well above the 4.25V threshold that would trigger this behavior).

By working backward through the auto-detect formula, the actual sampled voltage at the moment of latching had to have been in the 4.25–8.49V range — well below the settled value — indicating the cell count was latched during the rising-edge transient as the sense line charged up after connection, not at a stable value. Once latched, the count never changed over 23+ seconds of steady 12.40V operation.

**Configuration confirmed via CLI dump:**
- `vbat_meter_type = CAN` ✓
- `current_meter_type = CAN` ✓
- `bat_cells = 0` (auto-detect active) ✓
- `vbat_cell_detect_voltage = 425` (default) ✓
- Aircraft name: `NEMESIS` (verified via `diff battery`)

This behavior is consistent with the ~40-microsecond stabilization window hypothesis from the 2026-08-22 analysis: with no real settling time (the 2025-01-17 refactor switched `VBATT_STABLE_DELAY` from a blocking 40ms delay to a non-blocking 40µs check without unit conversion), transient values get latched during connect ramps. The flight footage's apparent cell overcount and today's confirmed undercount appear to be two manifestations of the same root cause — direction depends on which side of the true voltage the sampled transient happens to land.

## Anomaly #2 Status

Anomaly #2 (cell voltage not tracking pack voltage sag under load) remains **unconfirmed**. No load event was applied during this session; the battery was connected and left at static conditions.

## Incidental Findings

FC also reported:
- `HARDWARE FAILURE FLAGGED` in MSP_STATUS_EX
- `Arming disabled flags: NAV HWFAIL RX CLI`
- 50 I2C errors (stable count, not climbing; likely historical from missing SD card rather than active fault)

Not part of this project's scope — flagged for awareness only.

## Next Steps

Detailed trace data and full technical analysis are captured in `claude/developer/workspace/fix-dronecan-cell-voltage-calculation/notes.md` for your review.

---
**Developer**
