# Task Assignment: Battery Sensor Lost State

**Date:** 2026-06-10 15:00
**From:** Manager
**To:** Developer
**Project:** feature-battery-sensor-lost-state
**Priority:** MEDIUM
**Estimated Effort:** 3-5 hours

## Task

Add a `BATTERY_SENSOR_LOST` state to the battery state machine and wire CRSF and SmartPort battery drivers to signal it when their sensor goes stale. This extends the per-driver staleness pattern from the DroneCAN battery fix to a shared, battery-layer solution covering all external sensor types.

## Background

When a CRSF or SmartPort battery sensor goes stale mid-flight, vbat decays through the LPF, crosses `VBATT_PRESENT_THRESHOLD`, and the state machine silently transitions to `BATTERY_NOT_PRESENT`. The pilot gets no indication that telemetry has been lost. CRSF sensors are independent peripherals (not just receiver telemetry), so the same failure mode exists as with DroneCAN.

The DroneCAN battery driver already has a per-driver workaround. The right fix is one shared mechanism in `battery.c` rather than duplicating staleness logic in each driver.

The primary value is the **OSD warning** — giving the pilot actionable information to land conservatively. Voltage threshold preservation is a secondary concern (frozen voltage can't trigger new alarms it hasn't already crossed).

## What to Do

1. Add `BATTERY_SENSOR_LOST` state to battery state enum (`battery.h`) and an API for drivers to signal it (e.g. `batterySetSensorLost()`)
2. Ensure `BATTERY_NOT_PRESENT` transition is suppressed when in `BATTERY_SENSOR_LOST` state; freeze last-known vbat/amperage
3. Wire CRSF battery driver: add staleness timer, call new API on timeout
4. Wire SmartPort battery driver: add staleness timer, call new API on timeout
5. OSD: add distinct warning for `BATTERY_SENSOR_LOST` state
6. Optionally refactor DroneCAN driver to use shared state instead of its own OSD path
7. Build full matrix: F4, F7, H7, AT32, SITL

## Reference

Use `fix/dronecan-battery-health` as the reference pattern for staleness detection and OSD warning.

## Branch

**Base branch: `maintenance-10.x`**

## Success Criteria

- [ ] `BATTERY_SENSOR_LOST` state added to battery state machine
- [ ] CRSF battery driver detects staleness and signals new state
- [ ] SmartPort battery driver detects staleness and signals new state
- [ ] OSD displays distinct warning in `BATTERY_SENSOR_LOST` state
- [ ] `BATTERY_NOT_PRESENT` no longer triggered by sensor loss
- [ ] Full build matrix passes
- [ ] PR opened against `maintenance-10.x`
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/feature-battery-sensor-lost-state/`

---
**Manager**
