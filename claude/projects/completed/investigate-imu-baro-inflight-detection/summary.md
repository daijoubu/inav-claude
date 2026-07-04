# Project: Investigate IMU/Baro-Based In-Flight Detection for Fixed-Wing

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-06-09
**Estimated Time:** 2-4 hours

## Overview

Investigate whether INAV's `isProbablyStillFlying()` for fixed-wing can be made independent of GPS by using IMU and/or barometer signals. No implementation — produce a go/no-go recommendation.

## Problem

`isProbablyStillFlying()` uses `isGPSHeadingValid()` as the sole in-flight indicator for fixed-wing aircraft. This requires GPS fix, ≥6 satellites, and ground speed ≥300 cm/s. If GPS fails mid-flight, the function returns false.

This creates a circular dependency: GPS failure blocks both normal arming AND the emergency re-arm bypass (`IN_FLIGHT_EMERG_REARM`). A pilot who loses GPS mid-flight and accidentally disarms cannot re-arm via the emergency path — the one path specifically designed for this scenario.

Note: This predates DroneCAN work. DroneCAN GPS node health guards do not worsen this — a GPS timeout would already fail `isGPSHeadingValid()` — but it is a prerequisite safety concern before any health-gated arming block approach can be considered safe for fixed-wing.

## Objectives

Determine whether a GPS-independent in-flight confidence signal exists or can be derived. Answer these questions:

1. Does INAV's position estimator or AHRS already produce an in-flight confidence signal derived from IMU/baro independently of GPS?
2. Can accelerometer magnitude, gyro magnitude, or baro altitude rate provide a reliable in-flight indicator for fixed-wing at cruise speeds?
3. What are the false-positive and false-negative risks (e.g. turbulence on the ground, glide with engine off)?
4. Is the fix the right layer — `isProbablyStillFlying()` itself, or should `IN_FLIGHT_EMERG_REARM` have its own independent check?

## Scope

**In Scope:**
- `isProbablyStillFlying()` implementation and callers
- Position estimator in-flight detection signals
- IMU/baro signal availability during GPS outage
- Go/no-go recommendation with candidate signal(s) if viable

**Out of Scope:**
- Any implementation code
- Multirotor (different in-flight detection requirements)

## Success Criteria

- [ ] All four questions answered with codebase evidence
- [ ] `investigation-findings.md` written in project directory
- [ ] Go/no-go recommendation stated with rationale
- [ ] If go: candidate signal(s) identified and implementation approach sketched
- [ ] Completion report sent to manager

## Estimated Time

2-4 hours

## Priority Justification

Safety concern for fixed-wing users. Emergency re-arm path blocked by GPS dependency defeats its purpose. Low implementation cost to investigate; high safety value if a viable signal exists.
