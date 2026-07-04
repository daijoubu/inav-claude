# Project: Fix Fixed-Wing In-Flight Detection GPS Dependency

**Status:** ⏸️ BACKBURNER
**Priority:** MEDIUM-HIGH
**Type:** Bug Fix
**Created:** 2026-06-10
**Estimated Time:** 2-4 hours

## Overview

Replace `isGPSHeadingValid()` with a GPS-independent equivalent at four call sites where it is used as a flight proxy rather than a GPS protocol check. Fixes the dead reckoning scenario where a pilot who accidentally disarms cannot use `IN_FLIGHT_EMERG_REARM` because `isProbablyStillFlying()` returns false during GPS loss.

## Problem

`isProbablyStillFlying()` for fixed-wing depends on `isGPSHeadingValid()`, which returns false unconditionally when GPS is absent. During dead reckoning, GPS is already absent — so the function always returns false, blocking `IN_FLIGHT_EMERG_REARM`.

Additionally, `navigation.c:4686` uses `!isGPSHeadingValid()` to gate launch mode activation. GPS failure mid-flight makes this return true (not flying), allowing launch mode to activate while actually airborne.

## RFC

Issue #11644: https://github.com/iNavFlight/inav/issues/11644

Two implementation options under community discussion:
- **Option A:** `isPosEstimatorHeadingValid()` — surgical drop-in replacement (~5 lines + 4 substitutions)
- **Option B:** `isEstimatedFlyingConfident()` — new flight-detection concept using baro altitude above takeoff (~20 lines + 4 substitutions)

## Backburner Condition

Waiting for community feedback on RFC #11644 before choosing Option A or B and implementing.

## Affected Call Sites

| File | Current | Problem |
|---|---|---|
| `navigation.c:3604` | `isGPSHeadingValid()` | Returns false during dead reckoning |
| `navigation_fixedwing.c:767` | `isGPSHeadingValid() && ...` | GPS gate overrides estimator signals |
| `servos.c:643` | `isGPSHeadingValid()` | Marked TODO: proper flying detection |
| `navigation.c:4686` | `!isGPSHeadingValid()` | Launch mode can activate while airborne |

## Success Criteria

- [ ] Chosen approach (A or B) implemented
- [ ] `isProbablyStillFlying()` returns true during dead reckoning when aircraft is flying
- [ ] `IN_FLIGHT_EMERG_REARM` unblocked during GPS loss
- [ ] Launch mode gate corrected
- [ ] No behavioural change when GPS is healthy
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] PR opened against `maintenance-10.x`

## Estimated Time

2-4 hours (after approach is decided)
