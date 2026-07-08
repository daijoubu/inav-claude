# Project Request: DroneCAN HITL Hybrid Simulation

**Date:** 2026-06-09 07:23
**From:** Developer
**To:** Manager
**Type:** Project Request

## Summary

Hybrid HITL simulation mode that combines MSP_SIMULATOR (for gyro/accel only) with live DroneCAN traffic over SLCAN (for GPS, baro, mag, airspeed, battery) — exercising real CAN sensor drivers under flight dynamics rather than bypassing them.

## Problem

INAV currently has two test methods:
1. MSP_SIMULATOR (in X-Plane HITL) — tests flight dynamics but bypasses all CAN sensor drivers
2. Bench testing CAN nodes — tests sensor parsing but at zero airspeed, disarmed

Neither catches failures in CAN sensor infrastructure (health timeouts, stale node recovery, failover) that occur mid-flight.

## Proposed Solution

Two deliverables:

1. **Firmware (inav)**: New MSP_SIMULATOR flag `HITL_CAN_SENSORS` (or similar) that tells `readMspSimulatorValues()` to skip GPS, baro, mag, and airspeed fields — letting real DroneCAN drivers handle them. IMU (gyro/accel) still comes from MSP.

2. **Python tool** (standalone, lives in claude/developer/scripts/): Reads X-Plane datarefs (via UDP/XPLM) and emits DroneCAN frames over SLCAN for GPS (GnssFix), compass (MagneticFieldStrength), baro (RawAirData), and battery (BatteryInfo). Runs alongside the HITL plugin without modifying it.

## Required changes

- `inav/src/main/fc/fc_msp.c` — `readMspSimulatorValues()`: conditional skip of GPS/baro/mag/airspeed based on new flag
- `inav/src/main/fc/runtime_config.h` — new `HITL_CAN_SENSORS` flag constant
- New Python tool: `claude/developer/scripts/hitl/dronecan_hitl_bridge.py`

## Value

Closes the gap between bench CAN testing and MSP-only HITL. Catches node health/timeout/failover bugs before they're found in real aircraft.

---

Let me know if you want more detail before creating the project.

---
**Developer**
