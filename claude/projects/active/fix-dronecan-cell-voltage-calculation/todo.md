# Todo: DroneCAN Average Cell Voltage Not Tracking Pack Voltage

## Phase 1: Reproduce

- [ ] Bench-test with a DroneCAN battery monitor reporting a known 3S
      resting voltage (or send synthetic `uavcan.equipment.power.BatteryInfo`
      messages). Record `battery_cells` and `vbat_cell_detect_voltage` CLI
      values and the resulting `getBatteryCellCount()`.
- [ ] Confirm whether idle cell voltage reproduces the ~25% low reading
      (consistent with cellCount detected as 4 instead of 3) seen in the
      2026-08-16 `NEMESIS` flight footage.
- [ ] Apply/simulate a current draw sufficient to sag pack voltage (target:
      ~15-20% sag, matching the 12.3→10.1V observed) and confirm whether
      displayed average cell voltage tracks proportionally as
      `pack ÷ cellCount` predicts, or diverges like it did in the footage.

## Phase 2: Root Cause

- [ ] Determine why cell count was 4 instead of 3: `battery_cells`
      misconfigured, or `vbat / vbat_cell_detect_voltage + 1` auto-detect
      formula (`battery.c:432`) producing the wrong result for this pack's
      resting per-cell voltage relative to the default/configured
      `vbat_cell_detect_voltage` (425 = 4.25V).
- [ ] Determine why average cell voltage didn't track pack voltage sag
      under load — confirmed NOT a stale/lagging display, so trace whether
      `vbat` and `batteryCellCount` are actually consistent at the moment
      the OSD/telemetry getters are called, or whether something else
      (race, separate cached value, DroneCAN-source-specific path) is
      involved.
- [ ] Confirm whether both anomalies share one root cause or are separate
      bugs.

## Phase 3: Implementation

- [ ] Fix identified root cause(s) in `src/main/sensors/battery.c` and/or
      `src/main/sensors/battery_sensor_dronecan.c`.

## Phase 4: Verify

- [ ] Reproduction cases from Phase 1 no longer show the bug
- [ ] Unit test added: DroneCAN-source cell count detection at a
      representative 3S resting voltage
- [ ] Unit test added: average cell voltage tracks pack voltage
      proportionally under a simulated voltage sag
- [ ] Existing battery/OSD unit tests still pass
- [ ] Full pre-PR build matrix clean (F4/F7/H7/AT32, SITL)

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created
- [ ] Completion report sent to manager
