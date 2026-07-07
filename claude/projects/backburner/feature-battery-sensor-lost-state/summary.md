# Project: Battery Sensor Lost State

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature / Bug Fix
**Created:** 2026-06-10
**Estimated Time:** 3-5 hours

## Overview

Add a `BATTERY_SENSOR_LOST` state to INAV's battery state machine and wire CRSF and SmartPort battery drivers to signal it when their sensor goes stale. Extends the per-driver staleness detection already present in the DroneCAN battery driver to a shared, battery-layer solution.

## Problem

When an external battery sensor (DroneCAN, CRSF, SmartPort) stops sending data mid-flight, `vbat` decays toward 0 through the LPF, crosses `VBATT_PRESENT_THRESHOLD`, and the state machine transitions to `BATTERY_NOT_PRESENT`. The OSD shows nothing unusual and the pilot has no indication that sensor telemetry has been lost.

The DroneCAN battery driver already has a per-driver workaround (staleness timer + freeze + OSD warning). CRSF and SmartPort have no equivalent — they silently transition to `BATTERY_NOT_PRESENT`. CRSF sensors are independent peripherals (not just receiver telemetry), so the same failure mode applies.

The right fix is one shared mechanism in `battery.c` that any driver can signal, rather than duplicating staleness logic in each driver.

## Objectives

1. Add `BATTERY_SENSOR_LOST` state to the battery state machine in `battery.c`
2. Add staleness detection to the CRSF battery driver — signal `BATTERY_SENSOR_LOST` on timeout
3. Add staleness detection to the SmartPort battery driver — signal `BATTERY_SENSOR_LOST` on timeout
4. OSD: show a distinct warning (e.g. `BAT SENSOR LOST`) when in `BATTERY_SENSOR_LOST` state
5. Optionally refactor the DroneCAN driver to use the shared state rather than its own OSD path

## Scope

**In Scope:**
- `src/main/sensors/battery.c` / `battery.h` — new state, state transition logic
- CRSF battery sensor driver — staleness timer, signal new state
- SmartPort battery sensor driver — staleness timer, signal new state
- OSD — distinct message for `BATTERY_SENSOR_LOST`
- Targeting `maintenance-10.x`

**Out of Scope:**
- Voltage threshold preservation after sensor loss (frozen voltage can't trigger new alarms anyway — the OSD warning is the actionable signal)
- ADC battery sources (hardwired, no staleness scenario)

## Success Criteria

- [ ] `BATTERY_SENSOR_LOST` state added to battery state machine
- [ ] CRSF battery driver detects staleness and signals new state
- [ ] SmartPort battery driver detects staleness and signals new state
- [ ] OSD displays distinct warning in `BATTERY_SENSOR_LOST` state
- [ ] `BATTERY_NOT_PRESENT` transition no longer triggered by sensor loss
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] PR opened against `maintenance-10.x`
- [ ] Completion report sent to manager

## Estimated Time

3-5 hours

## Priority Justification

Safety issue: mid-flight sensor loss is silent under current behaviour. OSD warning gives the pilot actionable information to land conservatively. CRSF sensors are independent peripherals with the same failure mode as DroneCAN.
