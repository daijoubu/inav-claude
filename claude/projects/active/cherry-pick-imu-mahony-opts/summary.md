# Project: Cherry-pick IMU Mahony AHRS Hot-Path Optimizations

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Performance / Cherry-pick
**Created:** 2026-02-18
**Estimated Effort:** 0.5 hours
**Assignee:** Developer

## Overview

Cherry-pick commit `f99ea57b58` to a new branch off `maintenance-9.x` and open a PR to `inavflight/inav`. Request review from `breadoven`.

## Commit

- **Hash:** `f99ea57b58` (full: `f99ea57b`)
- **Message:** `imu: optimize imuMahonyAHRSupdate() hot path (5 micro-opts)`
- **Files:** `src/main/flight/imu.c`, `src/main/flight/imu.h`

**Five optimizations applied to the 1 kHz Mahony AHRS hot path:**
1. Read `rMat[2][0..2]` directly instead of calling `quaternionRotateVector()` (~32 mults + 24 adds saved per cycle)
2. Replace `thetaMagnitudeSq < sqrt(24e-6)` with `thetaMagnitudeSq² < 24e-6` (eliminates a `sqrt()` call)
3. First-order Newton renormalization instead of `quaternionNormalize()` (eliminates `sqrt()` + 4 divides)
4. Precompute `dcm_i_limit` in `imuConfigure()` (called on settings save) instead of recalculating it each PID cycle
5. Snapshot `prevOrientation` every 100 cycles instead of every cycle (used only by near-zero-probability fault recovery)

## Target

- **Repository:** `inavflight/inav` (upstream)
- **Base Branch:** `maintenance-9.x`
- **PR Reviewer:** `breadoven`

## Success Criteria

- [ ] New branch created from `maintenance-9.x`
- [ ] Commit cherry-picked cleanly
- [ ] Clean build
- [ ] PR opened targeting `inavflight/inav` `maintenance-9.x`
- [ ] Review requested from `breadoven`
- [ ] Completion report sent to manager with PR link

## Related

- **Assignment:** `manager/email/sent/2026-02-18-HHMM-task-cherry-pick-imu-mahony-opts.md`
