# Task Request: Open GitHub Issue — Battery Sensor Lost vs Battery Absent

**Date:** 2026-06-10 12:00
**From:** Developer
**To:** Manager
**Type:** Task Request
**Re:** DroneCAN Battery Health PR (fix/dronecan-battery-health)

## Summary

During the DroneCAN battery monitor PR (fix/dronecan-battery-health) we identified a deeper architectural issue in battery.c that affects all wireless battery sensors (DroneCAN, CRSF, SmartPort).

## The Problem

The battery state machine currently conflates two distinct failure modes:
1. **Battery sensor lost mid-flight** (wireless comms failure)
2. **Battery not present** (hardware not connected)

**What happens today:**
- When a wireless sensor goes stale, `vbat` drops to 0 through the LPF
- Voltage crosses `VBATT_PRESENT_THRESHOLD`
- System sets `BATTERY_NOT_PRESENT` state
- **This clears all voltage thresholds and silences per-cell alarms for the rest of the flight**

This is dangerous because a mid-flight sensor loss should still trigger warnings based on the last known battery state, not treat it as a normal "no battery" scenario.

## Current Workaround

We've implemented a workaround in the DroneCAN PR:
- Freeze the last known cell voltage values when `IsHealthy()` returns false
- Add OSD warning to indicate sensor is offline

However, this is incomplete and doesn't solve the architectural issue.

## Proposed Solution

Add a new battery state: `BATTERY_SENSOR_LOST` (or similar) that:
- Keeps existing voltage thresholds active (e.g., low battery warnings still trigger)
- Keeps per-cell alarms firing based on last known voltage
- Clearly signals a sensor fault (vs battery absence) to the state machine and OSD
- Allows OSD to differentiate "Bat Sensor Lost" from "No Battery"

## What I'm Asking

Please open a GitHub issue on iNavFlight/inav requesting community input on this architectural change. Suggest tagging it as a discussion/RFC to get input on:
- Naming convention for the new state
- Scope (does it apply to all wireless sensors: DroneCAN, CRSF, SmartPort? Or just CAN?)
- Implementation approach
- OSD messaging

## Out of Scope

This is out of scope for the current PR (fix/dronecan-battery-health) but important to track for future battery monitoring improvements.

## Reference

Related PR: fix/dronecan-battery-health
Related files: src/main/sensors/battery.c, src/main/common/state.h

---
**Developer**
