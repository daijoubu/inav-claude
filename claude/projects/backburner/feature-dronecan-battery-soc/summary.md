# Project: DroneCAN Battery SOC Support

**Status:** ⏸️ BACKBURNER
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-07-07
**Estimated Time:** 3-5 hours

## Overview

Extract and use the state-of-charge (SOC) fields already present in the DroneCAN `BatteryInfo` message, so smart batteries/BMS nodes can report actual remaining capacity instead of INAV relying solely on current-integration estimates.

## Problem

`battery_sensor_dronecan.c` only extracts `voltage` and `current` from `uavcan.equipment.power.BatteryInfo`; the rest of the message — `remaining_capacity_wh`, `full_charge_capacity_wh`, `state_of_charge_pct`, `state_of_charge_pct_stdev`, `state_of_health_pct`, `battery_id` — is ignored. `status_flags` warnings and the `int16_t` charging-current fix were addressed separately (`review-dronecan-battery-monitor`, `feature-battery-charging-current`), but SOC itself was explicitly scoped out of both as "a separate future project." This is that project.

Reference: [daijoubu/inav#3](https://github.com/daijoubu/inav/issues/3)

## Objectives

1. Add a `battery_capacity_source` setting (`ADC` default / `CAN`) per the issue's proposed enum
2. Extract SOC-related fields from `BatteryInfo` in the DroneCAN driver
3. Wire a hybrid capacity calculation: prefer Wh-based (`remaining_capacity_wh`/`full_charge_capacity_wh`), fall back to `state_of_charge_pct`, fall back to current-integration

## Scope

**In Scope:**
- `battery_sensor_dronecan.c` / `.h` — extract and expose SOC fields via getters
- `battery.c` / `.h` — `battery_capacity_source` setting + hybrid capacity logic
- `settings.yaml` — new setting

**Out of Scope:**
- `battery_id` multi-battery disambiguation (separate concern from `feature-battery-sensor-lost-state`'s node-ID filter pattern)
- OSD display changes beyond what already consumes `batteryRemainingCapacity`

## Success Criteria

- [ ] `battery_capacity_source = ADC` (default) — behaviour identical to today
- [ ] `battery_capacity_source = CAN` — capacity derived from BMS-reported SOC per the hybrid rule
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] Draft PR opened against `maintenance-10.x`

## Priority Justification

Not urgent — current-integration estimation works today. Genuinely useful for smart-battery/BMS users where reported SOC is more accurate than integration drift over long flights.

## Dependencies

None blocking — can be assigned independently, though touches the same files as `feature-battery-charging-current` (sequence to avoid simultaneous edits).
