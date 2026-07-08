# New Project Request: Investigate IMU/Baro-Based In-Flight Detection for Fixed-Wing

**Date:** 2026-06-08 19:00
**From:** Developer
**To:** Manager
**Type:** New Project Request

## Background

During DroneCAN GPS health guard work (fix/dronecan-gps-health-guard), a structural issue was identified in how fixed-wing in-flight status is determined.

`isProbablyStillFlying()` uses `isGPSHeadingValid()` as the sole in-flight indicator for fixed-wing aircraft. `isGPSHeadingValid()` requires a GPS fix, ≥6 satellites, and ground speed ≥300 cm/s.

This creates a circular dependency: any GPS failure that would warrant an arming block also disables the emergency re-arm bypass (`IN_FLIGHT_EMERG_REARM`) that depends on `isProbablyStillFlying()`. A pilot who loses GPS mid-flight and accidentally disarms cannot re-arm via the emergency path on fixed-wing.

Note: `isGPSHealthy()` returning false from DroneCAN node health does not add new risk here — `isGPSHeadingValid()` would already fail from GPS timeout by that point. The circular dependency predates DroneCAN work.

## Proposed Investigation

Review `src/main/navigation/` to determine whether an IMU-based or barometer-based in-flight confidence signal exists or could be derived independently of GPS, and whether it could be substituted into `isProbablyStillFlying()` for fixed-wing. A dead-reckoning system with positional confidence should also have velocity/altitude information sufficient to confirm airborne status without GPS.

## Why It Matters

This is a prerequisite before any health-gated arming block approach (e.g. blocking arming when a DroneCAN GPS node reports HEALTH_ERROR) can be considered safe for fixed-wing aircraft.

## Suggested Scope

- Investigation only (no implementation)
- Review position estimator in-flight detection signals
- Produce go/no-go recommendation with candidate signal(s) if viable

---
**Developer**
