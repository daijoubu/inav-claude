# Project: DroneCAN Average Cell Voltage Not Tracking Pack Voltage

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-08-21
**Estimated Time:** 2-4 hours

## Overview

Investigate whether INAV's average-cell-voltage calculation
(`getBatteryAverageCellVoltage()` / `getBatteryRawAverageCellVoltage()` /
`getBatterySagCompensatedAverageCellVoltage()` in `src/main/sensors/battery.c`)
is correct when the configured battery voltage source is DroneCAN
(`VOLTAGE_SENSOR_TYPE_DRONECAN`, fed by
`src/main/sensors/battery_sensor_dronecan.c`).

## Problem

Manager reviewed HD FPV goggle-recorder footage from a 2026-08-16 flight on
`NEMESIS` (KAKUTEH7WING, DroneCAN battery monitor, confirmed **3S** pack) —
file `0007_record_2026-08-16_16-17-59.RECOVERED.mp4`, first ~90s before a
crash. OSD shows 4 stock battery elements: raw pack voltage, sag-compensated
pack voltage, raw average cell voltage, sag-compensated average cell voltage.

Observed:

| Time | State | Pack voltage (raw/sag-comp) | Cell voltage (raw/sag-comp) |
|---|---|---|---|
| t=5s | idle, disarmed | 12.3 / 12.3 V | 2.91 / 2.9 V |
| t=35s | idle, disarmed | 12.3 / 12.3 V | 2.99 / 2.9 V |
| t=50s | idle, disarmed | 12.3 / 12.3 V | 3.03 / 3.0 V |
| t=65s | ~44A load (RTH abort, pre-crash) | 10.1 / 10.0 V | 3.06 / 3.0 V |

Two anomalies, confirmed by developer's own review of the footage as **not**
a stale/lagging-display artifact — the OSD is updating live each frame:

1. **At idle, cell voltage is wrong by a factor consistent with counting
   one too many cells.** For a resting 3S pack at 12.3V, true average cell
   voltage should be ~4.10V. Displayed value is ~2.9-3.03V — close to
   12.3V ÷ 4 (3.075V), not ÷ 3. This is the signature of
   `batteryCellCount` (`battery.c`) being determined as 4 instead of 3,
   either via a misconfigured `battery_cells` setting or via the
   `vbat / vbat_cell_detect_voltage + 1` auto-detect formula
   (`battery.c:432`) picking the wrong threshold for this pack's resting
   per-cell voltage.

2. **Under the ~44A load event, pack voltage sagged 12.3→10.1V (-18%) but
   displayed cell voltage barely moved (3.03→3.06V, if anything slightly
   up).** This does not fit a simple fixed-wrong-cellCount explanation
   either — dividing the live sagged pack voltage by any constant integer
   (3 or 4) does not reproduce the displayed cell value (10.1/4 = 2.53V,
   10.1/3 = 3.37V; neither matches 3.06V). Confirmed not a display-refresh
   staleness issue, so the calculation itself appears to be reading from
   something other than the live pack voltage at that moment, or
   `batteryCellCount` is not what's assumed. Root cause not yet
   identified — needs investigation, not just a config check.

Code path confirmed by manager (read-only, no code changed):
- `src/main/sensors/battery.c:519-570` — `getBatteryVoltage()`,
  `getBatteryRawVoltage()`, `getBatterySagCompensatedVoltage()`,
  `getBatteryCellCount()`, `getBatteryAverageCellVoltage()`,
  `getBatteryRawAverageCellVoltage()`,
  `getBatterySagCompensatedAverageCellVoltage()`
- `src/main/sensors/battery.c:400-459` — `batteryUpdate()`, cell-count
  determination (fixed profile value vs. auto-detect) — runs once per
  battery-connect event, independent of voltage source
- `src/main/sensors/battery.c:280-341` (`updateBatteryVoltage()` /
  voltage-source switch, approx.) — `vbat = dronecanBattSensorGetVBat();`
  for the DroneCAN source
- `src/main/sensors/battery_sensor_dronecan.c` —
  `dronecanBatterySensorReceiveInfo()` sets `dronecanVbat` directly from
  `uavcan.equipment.power.BatteryInfo.voltage` on every CAN message
- `src/main/io/osd.c:1838-1846, 3515-3521` — OSD elements call the
  getters above directly, no OSD-level caching found in
  `osdDisplayBattVoltDJI()`/`osdDisplayBatteryVoltage()`

Since `getBatteryRawVoltage()` returns the same `vbat` static that
`getBatteryRawAverageCellVoltage()` divides by `batteryCellCount`, the two
values should always be exactly proportional (same numerator, fixed
integer divisor) — the loaded-frame numbers say they weren't at that
instant, which is the part that needs a developer to actually instrument
and reproduce on hardware, not just read the source.

## Objectives

1. Reproduce on the bench: connect a DroneCAN battery monitor reporting a
   known 3S voltage, observe `battery_cells`/`vbat_cell_detect_voltage`
   CLI settings and actual detected `batteryCellCount`.
2. Confirm whether cell count is being mis-detected (config issue,
   auto-detect formula issue, or a DroneCAN-source-specific bug) for a
   pack whose resting per-cell voltage is close to `vbat_cell_detect_voltage`.
3. Reproduce the load-sag anomaly: apply a current draw (or simulate one)
   and confirm whether displayed/computed average cell voltage tracks
   `vbat` proportionally as the code implies it should. If it doesn't,
   find why — e.g. a race between `vbat` update and `batteryCellCount`
   use, a separate/duplicate cell-count variable, or something specific
   to how `dronecanBattSensorGetVBat()`/`updateBatteryVoltage()` interacts
   with the OSD render cycle.
4. Fix root cause(s) found.

## Scope

**In Scope:**
- `src/main/sensors/battery.c` (cell count detection, average cell
  voltage calculation)
- `src/main/sensors/battery_sensor_dronecan.c` (DroneCAN voltage feed)
- Any OSD/telemetry consumer only if the bug turns out to be in how they
  read these getters, not in the getters themselves

**Out of Scope:**
- Non-DroneCAN battery sources (ADC, ESC telemetry, ibus/crsf/smartport
  sensors) — unless investigation shows the bug is generic, not
  DroneCAN-specific
- OSD layout/configuration itself

## Implementation Steps

1. Reproduce cell-count misdetection with a bench DroneCAN battery
   monitor (or simulate `dronecanBatterySensorReceiveInfo()` calls) at a
   known 3S resting voltage; capture `battery_cells`/
   `vbat_cell_detect_voltage` CLI diff and confirm `getBatteryCellCount()`.
2. Root-cause the idle miscount (config vs. auto-detect formula vs.
   DroneCAN-source-specific bug).
3. Reproduce the load-sag anomaly by driving current up while watching
   `vbat`/`batteryCellCount`/computed cell voltage together (e.g. via
   debug logging or SITL if reproducible there).
4. Fix whatever is found; add/extend unit test coverage in
   `src/test/unit/` for cell-count detection and average-cell-voltage
   calculation under a DroneCAN voltage source.

## Success Criteria

- [ ] Root cause identified for both anomalies (or confirmed to be the
      same root cause)
- [ ] `getBatteryCellCount()` returns the correct value for a DroneCAN
      battery source across the pack's normal voltage range, including
      under load/sag
- [ ] Average cell voltage (raw and sag-compensated) tracks pack voltage
      proportionally at all times, matching `pack ÷ cellCount`
- [ ] Unit test added covering DroneCAN-source cell count detection and
      average cell voltage calculation
- [ ] Full build matrix passes (F4/F7/H7/AT32/SITL)

## Estimated Time

2-4 hours (may grow if the load-sag anomaly requires hardware
reproduction/instrumentation)

## Priority Justification

HIGH — cell voltage is a primary in-flight battery health indicator;
displaying it substantially wrong (here, ~25% low at idle, and not
tracking load sag at all) could mask a genuinely critical low-cell
condition during flight. Flagged by manager while reviewing footage from
a crash, though the crash cause itself is not yet established as related.
