# Project: Battery Charging Current Tracking

**Status:** ⏸️ BACKBURNER
**Priority:** MEDIUM-HIGH
**Type:** Feature / Bug Fix
**Created:** 2026-06-07
**Estimated Time:** 2-3 hours

## Overview

Allow INAV to track negative (charging) current from DroneCAN BMS nodes and bidirectional ADC current sensors, so mAh/Wh drawn decreases correctly while charging.

## Problem

`battery.c:687` clamps all amperage to ≥ 0:
```c
amperage = MAX(0, amperage);
```
This is correct for unidirectional sensors but discards the sign from DroneCAN BMS nodes (where negative current = charging) and center-biased ADC sensors. Additionally, `battery_sensor_dronecan.c` stores amperage as `uint16_t`, silently truncating the sign bit from the BMS float before it even reaches the clamp.

## Objectives

1. Fix the `uint16_t` type bug in the DroneCAN battery driver
2. Add `current_meter_track_charging` setting to gate the clamp removal
3. Add upper bound on `batteryRemainingCapacity` to handle negative draw

## Scope

**In Scope:**
- `battery_sensor_dronecan.c` / `.h` — `uint16_t → int16_t` for `dronecanAmperage`
- `battery.c:687` — gate `MAX(0, amperage)` on `current_meter_track_charging`
- `battery.c:459` — add `constrain(..., 0, capacityDiffBetweenFullAndEmpty)` upper clamp
- `settings.yaml` — new `current_meter_track_charging` bool setting (default OFF)

**Out of Scope:**
- SOC from BMS (`battery_capacity_source` setting) — separate future project
- OSD changes (downstream consumers already handle signed values correctly)
- MSP / blackbox changes (blackbox `amperage` field is already `int16_t`)

## Implementation Steps

1. Change `dronecanAmperage` type from `uint16_t` to `int16_t` in driver and header
2. Add `current_meter_track_charging` setting to `settings.yaml`
3. In `battery.c:687`: gate the zero-clamp on the new setting
4. In `battery.c:459`: add upper clamp so `batteryRemainingCapacity` can't exceed full capacity when draw goes negative
5. Build matrix (F4, F7, H7, AT32, SITL)
6. Open draft PR to `maintenance-10.x`

## Success Criteria

- [ ] `dronecanAmperage` is `int16_t`; negative current from BMS preserved
- [ ] `current_meter_track_charging = OFF` (default) — behaviour identical to today
- [ ] `current_meter_track_charging = ON` — mAh drawn decreases while charging
- [ ] `batteryRemainingCapacity` clamped to `[0, capacityDiffBetweenFullAndEmpty]`
- [ ] Full build matrix passes
- [ ] Draft PR opened against `maintenance-10.x`

## Priority Justification

Useful for rover use cases with BMS docking stations; the type fix is technically a bug. Deferred until battery health PR (`review-dronecan-battery-monitor`) merges to avoid simultaneous edits to the same files.

## Dependencies

Assign after `review-dronecan-battery-monitor` PR merges (both touch `battery_sensor_dronecan.c`).
