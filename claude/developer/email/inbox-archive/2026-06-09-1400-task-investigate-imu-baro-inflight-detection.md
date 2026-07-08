# Task Assignment: Investigate IMU/Baro-Based In-Flight Detection for Fixed-Wing

**Date:** 2026-06-09 14:00
**From:** Manager
**To:** Developer
**Project:** investigate-imu-baro-inflight-detection
**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours

## Task

Investigate whether INAV's `isProbablyStillFlying()` for fixed-wing can be made independent of GPS using IMU and/or barometer signals. Research only — no implementation. Produce a go/no-go recommendation.

## Background

`isProbablyStillFlying()` currently uses `isGPSHeadingValid()` as the sole in-flight indicator for fixed-wing. This requires GPS fix, ≥6 satellites, and ground speed ≥300 cm/s. If GPS fails mid-flight, the function returns false — blocking not only normal arming but also the `IN_FLIGHT_EMERG_REARM` bypass, which is specifically designed for the scenario where a pilot accidentally disarms mid-flight.

This predates DroneCAN work. DroneCAN GPS health guards don't worsen the situation, but it is a prerequisite safety concern before any health-gated arming block approach can be considered safe for fixed-wing.

## What to Do

Answer these four questions:

1. Does INAV's position estimator or AHRS already produce an in-flight confidence signal derived from IMU/baro independently of GPS?
2. Can accelerometer magnitude, gyro rate, or baro altitude rate provide a reliable fixed-wing in-flight indicator?
3. What are the false-positive and false-negative risks (e.g. turbulence on ground, glide with engine off)?
4. Is the fix the right layer — `isProbablyStillFlying()` itself, or should `IN_FLIGHT_EMERG_REARM` have its own independent check?

## Deliverable

Write `investigation-findings.md` in the project directory answering all four questions with codebase evidence. Include a clear go/no-go recommendation, and if go, identify candidate signal(s) and sketch the implementation approach.

## Success Criteria

- [ ] All four questions answered with codebase evidence
- [ ] `investigation-findings.md` written in project directory
- [ ] Go/no-go recommendation stated with rationale
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/investigate-imu-baro-inflight-detection/`

---
**Manager**
