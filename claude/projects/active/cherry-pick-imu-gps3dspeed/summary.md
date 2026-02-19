# Project: Cherry-pick imu GPS 3D Speed Fix

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Bug Fix / Cherry-pick
**Created:** 2026-02-18
**Estimated Effort:** 0.5 hours
**Assignee:** Developer

## Overview

Cherry-pick commit `bb02220fc3399c73d4bb2284d77add5b66576f5b` from the current branch to a new branch off `maintenance-9.x`, and open a PR targeting upstream `inavflight/inav` `maintenance-9.x`. Request review from `breadoven`.

## Commit

- **Hash:** `bb02220fc3399c73d4bb2284d77add5b66576f5b`
- **Message:** `imu: compute GPS 3D speed only on new GPS data`
- **File:** `src/main/flight/imu.c`
- **Change:** Moves GPS 3D speed filter computation inside a `gpsHeartbeat` check so it only runs when new GPS data arrives, rather than every IMU cycle. Also converts the filter/state variables from module-level statics to function-local statics.

## Target

- **Repository:** `inavflight/inav` (upstream)
- **Base Branch:** `maintenance-9.x`
- **PR Reviewer:** `breadoven`

## Success Criteria

- [ ] New branch created from `maintenance-9.x`
- [ ] Commit cherry-picked cleanly (no conflicts)
- [ ] PR opened targeting `inavflight/inav` `maintenance-9.x`
- [ ] Review requested from `breadoven`
- [ ] Completion report sent to manager

## Related

- **Assignment:** `manager/email/sent/2026-02-18-HHMM-task-cherry-pick-imu-gps3dspeed.md`
