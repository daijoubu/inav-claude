# Investigation: IMU/Baro In-Flight Detection for Fixed-Wing

**Date:** 2026-06-10
**Branch:** n/a (research only)

---

## Q1: Does INAV already produce a GPS-independent in-flight confidence signal?

**No — not for fixed-wing.**

The fixed-wing path in `isProbablyStillFlying()` (`navigation.c:3598`) delegates entirely to `isFixedWingFlying()` (`navigation_fixedwing.c:754`), which requires `isGPSHeadingValid()` as a hard precondition:

```c
// navigation.c:3603-3604
} else {
    inFlightSanityCheck = isGPSHeadingValid();
}
```

```c
// navigation_fixedwing.c:767
return (isGPSHeadingValid() && throttleCondition && velCondition && altCondition) || launchCondition;
```

`isGPSHeadingValid()` requires GPS fix, ≥6 satellites, and ground speed ≥300 cm/s (`gps.c:672`). If GPS fails, this returns false unconditionally.

Multicopter has a GPS-independent path — `averageAbsGyroRates() > 4.0f` (`navigation.c:3602`) — but no equivalent exists for fixed-wing.

**Key find:** The position estimator's Z estimate (`posControl.actualState.abs.pos.z`) IS baro-fused and GPS-independent. It is computed even without GPS (`navigation_pos_estimator.c:510–640` fuses baro into `posEstimator.est.pos.z`). The `altCondition` in `isFixedWingFlying()` uses this value, but it is AND'd with `isGPSHeadingValid()` so it never fires without GPS.

---

## Q2: Can IMU/baro signals reliably indicate fixed-wing in-flight?

### Candidate signals

| Signal | Source | Available without GPS? | Notes |
|---|---|---|---|
| `posControl.actualState.abs.pos.z - getTakeoffAltitude()` | Baro/IMU fused | Yes | Already computed in `isFixedWingFlying()` |
| `posControl.actualState.velXY` | GPS-fused estimator | Degrades without GPS | Already used in `isFixedWingFlying()` |
| `getEstimatedActualVelocity(Z)` | Baro/IMU fused | Yes | Used in MC emerg rearm check (`fc_core.c:534`) |
| `averageAbsGyroRates()` | Gyro only | Yes | Used for MC in `isProbablyStillFlying()` |
| `rcCommand[THROTTLE]` | RC | Yes | Used in `isFixedWingFlying()` |
| Airspeed (`getAirspeedEstimate()`) | Pitot | Yes (if pitot fitted) | Already in `isFixedWingFlying()` |

### Most reliable: altitude above takeoff (baro-derived)

`fabsf(posControl.actualState.abs.pos.z - getTakeoffAltitude()) > 500.0f` (5 m) is:
- Already computed in `isFixedWingFlying()` — zero new signal derivation needed
- GPS-independent (baro-fused Z)
- Meaningful for emergency rearm: a plane that accidentally disarmed in the air will be >5 m above its takeoff altitude

### Vertical velocity — not suitable as primary FW signal

`fabsf(getEstimatedActualVelocity(Z)) > 100.0f` is already used for the MC emergency rearm path (`fc_core.c:534`). For FW this has a critical weakness: a fixed-wing in level cruise has ~0 m/s vertical velocity — it would give false negatives in the most common flight scenario.

### Gyro rates — not suitable for FW primary check

MC uses `averageAbsGyroRates() > 4.0f`. A stable fixed-wing in cruise has low gyro rates. Too many false negatives.

---

## Q3: False positive / negative risks

### Baro altitude check (recommended signal)

| Scenario | Risk | Severity |
|---|---|---|
| Baro drift puts altitude >5m above recorded takeoff | False positive | Low — `landingDetectorIsActive` gate means it only fires after a real arming cycle |
| FW disarmed on ground after taxi/bounced landing | False positive | Low — unlikely to be >5m off takeoff altitude |
| FW disarmed while airborne at <5m AGL (very low pass) | False negative | Low — pilot unlikely to attempt rearm at <5m AGL |
| Takeoff altitude not set (no baro calibration) | False negative | Medium — same failure mode as current GPS check |

---

## Q4: Right layer — `isProbablyStillFlying()` or `IN_FLIGHT_EMERG_REARM`?

**Neither is the root fix. The root fix is architectural.**

`isGPSHeadingValid()` is a GPS protocol function — it answers "does the GPS receiver have a good heading fix?" not "is the aircraft flying?" It is being used as a flight proxy in multiple places across the codebase. This is the underlying problem.

### Call sites using `isGPSHeadingValid()` as a flight proxy

Nine call sites in total. Three are flight-detection uses where the GPS dependency is wrong:

| File | Use | Problem |
|---|---|---|
| `navigation.c:3604` | `isProbablyStillFlying()` FW path | Returns false on GPS failure mid-flight |
| `navigation_fixedwing.c:767` | `isFixedWingFlying()` — landing detector | GPS gate overrides estimator velXY/alt signals already present |
| `servos.c:643` | Enable mixer flying mode | Even marked `// TODO: proper flying detection` |
| `navigation.c:4686` | Gate launch mode activation | If GPS fails mid-flight, launch mode could activate while airborne |

The remaining five (`imu.c`, `navigation_pos_estimator.c`, `wind_estimator.c`, `rth_trackback.c`, `navigation_fw_launch.c`) are correctly GPS-dependent — they need GPS data specifically, not just a flight indication.

### The launch mode check is also wrong

`navigation.c:4686`:
```c
canActivateLaunchMode = isNavLaunchEnabled() &&
    (!sensors(SENSOR_GPS) || (sensors(SENSOR_GPS) && !isGPSHeadingValid()));
```

Intent: don't allow switching to launch mode if already flying. But it uses `isGPSHeadingValid()` as the "flying" signal. GPS failure mid-flight makes this return false (not flying), allowing launch mode to activate while actually airborne. The condition also simplifies to just `!isGPSHeadingValid()` — the sensor presence check is redundant.

---

## Recommendation: GO — but implement the architectural fix, not a narrow patch

### Proposed: `isEstimatedFlyingConfident()` in the navigation/estimator layer

Add a new function that uses the position estimator's fused state rather than querying GPS directly:

```c
// navigation.c or navigation_fixedwing.c
bool isEstimatedFlyingConfident(void)
{
    if (STATE(MULTIROTOR)) {
        return posControl.actualState.velXY > MC_LAND_CHECK_VEL_XY_MOVING ||
               averageAbsGyroRates() > 4.0f;
    } else {
        bool altCheck = fabsf(posControl.actualState.abs.pos.z - getTakeoffAltitude()) > 500.0f;
        bool velCheck = posControl.actualState.velXY > 350.0f;  // estimator output, not raw GPS
#ifdef USE_PITOT
        bool airspeedCheck = sensors(SENSOR_PITOT) && pitotIsHealthy() &&
                             getAirspeedEstimate() > 350.0f;
#else
        bool airspeedCheck = false;
#endif
        return isGPSHeadingValid() || altCheck || (velCheck && airspeedCheck);
    }
}
```

Key properties:
- For MC: identical to current behaviour (MC was already correct)
- For FW: GPS heading valid is still the primary signal; baro altitude and airspeed are fallbacks when GPS fails
- Uses `posControl.actualState.velXY` (estimator output) not raw GPS — already degraded gracefully by the estimator

### Call site changes

| File | Current | Proposed |
|---|---|---|
| `navigation.c:3604` | `isGPSHeadingValid()` | `isEstimatedFlyingConfident()` (replace `isProbablyStillFlying()` body entirely) |
| `navigation_fixedwing.c:767` | `isGPSHeadingValid() && ... velXY && altCondition` | `isEstimatedFlyingConfident() && throttleCondition` |
| `servos.c:643` | `isGPSHeadingValid()` | `isEstimatedFlyingConfident()` |
| `navigation.c:4686` | `!isGPSHeadingValid()` | `!isEstimatedFlyingConfident()` |

`isProbablyStillFlying()` becomes a thin wrapper (or is replaced inline) around `isEstimatedFlyingConfident()` with the `landingDetectorIsActive` gate preserved.

`isProbablyStillFlying()` becomes a thin wrapper (or is replaced inline) around `isEstimatedFlyingConfident()` with the `landingDetectorIsActive` gate preserved.

---

## Additional Finding: Geozone fence preview bypasses estimator for horizontal motion

**File:** `navigation_geozone.c:840–841`, function `calcPreviewPoint()`

```c
calculateFarAwayTarget(target, DECIDEGREES_TO_CENTIDEGREES(gpsSol.groundCourse), distance);
target->z = getEstimatedActualPosition(Z)
          + calcTime(geoZoneConfig()->fenceDetectionDistance, gpsSol.groundSpeed)
          * getEstimatedActualVelocity(Z);
```

This projects a future position for geozone fence intersection detection. The Z components correctly use the position estimator (`getEstimatedActualPosition(Z)`, `getEstimatedActualVelocity(Z)`), but the horizontal inputs come directly from GPS:

- `gpsSol.groundCourse` — raw GPS course over ground
- `gpsSol.groundSpeed` — raw GPS ground speed, used in `calcTime()` as the divisor (time = fence_distance / speed)

**Problem:** If GPS fails, `gpsSol.groundSpeed` goes stale or zeroes. `calcTime()` divides by speed — a zero or stale value produces an infinite or wildly wrong time-to-fence estimate. The geozone preview breaks silently while the Z path continues working correctly.

**Fix:** Use estimator outputs for consistency and GPS-failure resilience:
- Replace `gpsSol.groundSpeed` with `posControl.actualState.velXY`
- Replace `gpsSol.groundCourse` with the estimator's course-over-ground (`posEstimator.est.cog`, already exposed via `navigation_pos_estimator.c`)

This is a separate, narrower issue from the flight-inference problem — not a flight detection bug, but the same pattern of bypassing the estimator unnecessarily. Scope: one function, two variable substitutions.

---

## What the main fix does NOT address
- The emergency rearm time window — if GPS fails and the plane has been flying for longer than `EMERGENCY_INFLIGHT_REARM_TIME_WINDOW_MS`, rearm is still blocked. That is separate policy.
- Scenarios where baro is also unavailable — the estimator would have no Z reference, but that is an extreme failure mode.
- The geozone issue above — separate fix, separate PR.
