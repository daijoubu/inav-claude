# Task Assignment: Investigate DroneCAN Average Cell Voltage Calculation

**Date:** 2026-08-21 14:30
**From:** Manager
**To:** Developer
**Project:** fix-dronecan-cell-voltage-calculation
**Priority:** HIGH
**Estimated Effort:** 2-4 hours

## Task

Investigate and fix whether average cell voltage is calculated correctly
in `src/main/sensors/battery.c` when the battery voltage source is
DroneCAN (`src/main/sensors/battery_sensor_dronecan.c`).

## Background

Manager reviewed HD FPV goggle-recorder footage from a 2026-08-16 flight
on `NEMESIS` (KAKUTEH7WING, DroneCAN battery monitor, confirmed 3S pack) —
`0007_record_2026-08-16_16-17-59.RECOVERED.mp4`, first ~90s before a crash.
OSD shows the 4 stock battery elements (raw/sag-comp pack voltage,
raw/sag-comp average cell voltage).

Observed:
- Idle (disarmed): pack 12.3V, cell voltage ~2.9-3.03V. True cell voltage
  for a resting 3S pack at 12.3V should be ~4.1V. The ~3.0V reading is
  close to 12.3V ÷ 4, not ÷ 3 — signature of cell count being detected as
  4 instead of 3.
- Under ~44A load (RTH abort, pre-crash): pack sagged 12.3→10.1V (-18%)
  but cell voltage barely moved (3.03→3.06V). User confirmed this is NOT
  a stale/lagging OSD display — it's updating live. Neither ÷3 nor ÷4 of
  the live 10.1V pack value matches the displayed 3.06V, so this doesn't
  fit a simple fixed-wrong-cell-count explanation on its own — needs
  actual investigation, not just a config check.

Manager did read-only code review (no changes made) — relevant code:
- `battery.c:519-570` — `getBatteryVoltage()`, `getBatteryRawVoltage()`,
  `getBatterySagCompensatedVoltage()`, `getBatteryCellCount()`,
  `getBatteryAverageCellVoltage()`, `getBatteryRawAverageCellVoltage()`,
  `getBatterySagCompensatedAverageCellVoltage()`
- `battery.c:400-459` — `batteryUpdate()`, cell-count determination
  (fixed profile value vs. auto-detect via `vbat / vbat_cell_detect_voltage
  + 1`), runs once per battery-connect event
- `battery.c` voltage-source switch — `vbat = dronecanBattSensorGetVBat();`
  for DroneCAN source
- `battery_sensor_dronecan.c` — `dronecanBatterySensorReceiveInfo()` sets
  `dronecanVbat` directly from `uavcan.equipment.power.BatteryInfo.voltage`
  on every CAN message
- `osd.c:1838-1846, 3515-3521` — OSD elements call the getters directly;
  no caching found in `osdDisplayBattVoltDJI()`/`osdDisplayBatteryVoltage()`

Since raw pack voltage and raw average cell voltage both read the same
`vbat` static (cell voltage just divides it by `batteryCellCount`), they
should always be exactly proportional — the loaded-frame numbers say they
weren't at that instant. That inconsistency needs to be reproduced and
traced on the bench, not just reasoned about from source.

## What to Do

See full details in `claude/projects/active/fix-dronecan-cell-voltage-calculation/summary.md`
and `todo.md`. Summary:

1. Reproduce cell-count misdetection on the bench with a DroneCAN battery
   monitor (or synthetic `BatteryInfo` messages) at a known 3S resting
   voltage. Check `battery_cells`/`vbat_cell_detect_voltage` CLI settings
   and resulting `getBatteryCellCount()`.
2. Root-cause the idle miscount (config vs. auto-detect formula vs.
   DroneCAN-source-specific bug).
3. Reproduce the load-sag anomaly by driving current up while watching
   `vbat`/`batteryCellCount`/computed cell voltage together.
4. Fix whatever is found; add unit test coverage for DroneCAN-source cell
   count detection and average cell voltage calculation.

## Success Criteria

- [ ] Root cause identified for both anomalies (or confirmed as one cause)
- [ ] `getBatteryCellCount()` correct for a DroneCAN battery source across
      the pack's normal voltage range, including under load/sag
- [ ] Average cell voltage tracks pack voltage proportionally at all times
- [ ] Unit test added
- [ ] Full build matrix passes (F4/F7/H7/AT32/SITL)

## Project Directory

`claude/projects/active/fix-dronecan-cell-voltage-calculation/`

---
**Manager**
