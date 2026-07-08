# Task Assignment: Fix PR #11 DroneCAN Unit Tests

**Date:** 2026-02-17 10:30
**From:** Manager
**To:** Developer
**Project:** fix-pr11-dronecan-tests
**Priority:** MEDIUM
**Estimated Effort:** 1-2 hours

## Task

Fix 2 failing unit tests in PR #11 (daijoubu/inav):
- `BatteryInfo_StateOfChargePercentBoundaries`
- `GNSSFix2_MaxSatellites`

## Background

PR #11 implements DroneCAN support using libcanard. Two unit tests are failing due to incorrect test assertions. The tests use `EXPECT_FALSE(decode(...))` but successful decode returns false (no error). The tests should verify the result correctly.

## What to Do

1. Fetch PR #11 branch locally:
   ```bash
   cd inav
   git fetch origin pull/11/head:pr11-dronecan
   git checkout pr11-dronecan
   ```
   
2. Locate and examine the failing tests in `src/test/unit/dronecan_messages_unittest.cc`

3. Fix the test assertions - change `EXPECT_FALSE(decode(...))` to `EXPECT_TRUE(decode(...))` for successful decode scenarios

4. Run tests locally:
   ```bash
   cmake --build build --target check
   ```

5. Push fix to PR branch

6. Verify CI passes

## Success Criteria

- [ ] All 90+ unit tests pass
- [ ] CI builds succeed
- [ ] PR #11 ready for merge

## Project Directory

`claude/projects/active/fix-pr11-dronecan-tests/`

## Files to Check

- `src/test/unit/dronecan_messages_unittest.cc` (lines for both failing tests)

## Base Branch

`feature/finalize-libcanard-dronecan` (targeting `add-libcanard`)

**Repository:** `daijoubu/inav` (fork)

---
**Manager**
