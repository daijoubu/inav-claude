# Task Completed: Investigation Complete - IMU/Baro In-Flight Detection for Fixed-Wing

**Date:** 2026-06-10 18:47
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Investigation complete. Findings document written to `claude/projects/active/investigate-imu-baro-inflight-detection/investigation-findings.md`.

## Recommendation: GO — but implement the architectural fix

The root problem is broader than the emergency rearm scenario. `isGPSHeadingValid()` is a GPS protocol function being used as a flight proxy in four places. The position estimator already has all the signals needed to answer "are we flying?" without GPS.

## Key Findings

**Q1: GPS-independent in-flight signal already exists?**
No — not for fixed-wing. MC has `averageAbsGyroRates()` as a fallback; FW has none. However, the position estimator's baro-fused altitude (`posControl.actualState.abs.pos.z`) is already available GPS-independently and is already computed inside `isFixedWingFlying()` — it's just AND'd with `isGPSHeadingValid()` so it never fires without GPS.

**Q2: Can IMU/baro provide a reliable FW in-flight indicator?**
Yes — baro altitude above takeoff (`fabsf(pos.z - takeoffAlt) > 500cm`) is the most reliable signal. Vertical velocity was considered and rejected (false negatives in level cruise). Gyro rate was considered and rejected (low in stable FW flight).

**Q3: False positive/negative risks**
Low. The `landingDetectorIsActive` outer gate means the check only fires after a real arming cycle. Main residual risk: takeoff altitude not recorded (no baro calibration) — same failure mode as the current GPS check.

**Q4: Right layer?**
Neither `isProbablyStillFlying()` nor `IN_FLIGHT_EMERG_REARM` is the right fix layer. The architectural fix is a new `isEstimatedFlyingConfident()` function in the navigation layer using estimator state, replacing the four `isGPSHeadingValid()` flight-proxy call sites:

| File | Current | Proposed |
|---|---|---|
| `navigation.c:3604` | `isGPSHeadingValid()` | `isEstimatedFlyingConfident()` |
| `navigation_fixedwing.c:767` | `isGPSHeadingValid() && velXY && altCondition` | `isEstimatedFlyingConfident() && throttleCondition` |
| `servos.c:643` | `isGPSHeadingValid()` | `isEstimatedFlyingConfident()` |
| `navigation.c:4686` | `!isGPSHeadingValid()` (launch mode gate) | `!isEstimatedFlyingConfident()` |

The launch mode check (`navigation.c:4686`) is also a safety concern: GPS failure mid-flight currently allows launch mode to activate while airborne.

## Additional Finding: Geozone fence preview

`navigation_geozone.c:841` uses `gpsSol.groundSpeed` and `gpsSol.groundCourse` directly to project a future fence intersection point, while the Z components in the same expression use the estimator. If GPS fails, `gpsSol.groundSpeed` zeroes causing a division-by-zero in `calcTime()`. Fix: replace with `posControl.actualState.velXY` and estimator COG. Separate narrow fix, separate PR.

## Suggested follow-on tasks

1. **Feature: `isEstimatedFlyingConfident()`** — implement the new function and migrate the four call sites (firmware)
2. **Fix: geozone fence preview** — replace `gpsSol.groundSpeed`/`groundCourse` with estimator equivalents (firmware, narrow)

---
**Developer**
