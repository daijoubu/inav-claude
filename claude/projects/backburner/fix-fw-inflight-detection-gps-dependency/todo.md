# Todo: Fix Fixed-Wing In-Flight Detection GPS Dependency

## Pre-condition

- [ ] RFC #11644 has received community feedback
- [ ] Option A or Option B chosen (or alternative agreed)

## Phase 1: Implementation

**If Option A (`isPosEstimatorHeadingValid()`):**
- [ ] Add `isPosEstimatorHeadingValid()` to navigation layer
- [ ] Replace `isGPSHeadingValid()` at `navigation.c:3604`
- [ ] Replace `isGPSHeadingValid()` at `navigation_fixedwing.c:767`
- [ ] Replace `isGPSHeadingValid()` at `servos.c:643`
- [ ] Replace `!isGPSHeadingValid()` at `navigation.c:4686`

**If Option B (`isEstimatedFlyingConfident()`):**
- [ ] Add `isEstimatedFlyingConfident()` with baro/velocity/airspeed fallbacks
- [ ] Replace all four call sites as above
- [ ] Confirm threshold values (5 m altitude, 300-350 cm/s velocity)

## Phase 2: Verify

- [ ] Confirm no behavioural change when GPS is healthy
- [ ] Confirm `isProbablyStillFlying()` returns true at estimator velocity >300 cm/s without GPS
- [ ] Confirm launch mode gate (`navigation.c:4686`) no longer allows activation while airborne
- [ ] Full build matrix: F4, F7, H7, AT32, SITL — all clean

## Completion

- [ ] PR opened against `maintenance-10.x`, references RFC #11644
- [ ] Completion report sent to manager
