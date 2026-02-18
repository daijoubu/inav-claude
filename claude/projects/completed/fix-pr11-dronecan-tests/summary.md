# Project: Fix PR #11 DroneCAN Unit Tests

**Status:** ✅ COMPLETED
**Priority:** MEDIUM
**Type:** Bug Fix / Tests
**Created:** 2026-02-18
**Completed:** 2026-02-18
**Estimated Effort:** 1 hour (actual)

## Overview

Fixed 2 failing unit tests in PR #11 that used values exceeding DSDL field sizes.

## Problem

PR #11 adds 9 new unit tests for DroneCAN message decoders. Two tests fail:
- `DroneCANMessageTest.BatteryInfo_StateOfChargePercentBoundaries`
- `DroneCANMessageTest.GNSSFix2_MaxSatellites`

**Root Cause:** Tests used uint8 max values (255) for fields with smaller bit widths defined by DSDL:
- `state_of_charge_pct`: 7-bit field (max 127), test used 255
- `sats_used`: 6-bit field (max 63), test used 255

When encoded, values are truncated to field width, then decoded values don't match expected.

## Solution

Corrected test boundary values to match DSDL spec:
- `BatteryInfo_StateOfChargePercentBoundaries`: Changed `{0,1,50,100,127,255}` to `{0,1,50,100,127}`
- `GNSSFix2_MaxSatellites`: Changed 255 to 63

## Files Modified

- `src/test/unit/dronecan_messages_unittest.cc` - Fixed boundary test values

## Success Criteria

- [x] All 90 unit tests pass
- [x] CI builds succeed (21/21 checks pass)
- [x] PR #11 merged

## PR

- **PR:** [#11](https://github.com/daijoubu/inav/pull/11) - MERGED
- **Repository:** daijoubu/inav
- **Commit:** `447cb3183`

## Related

- PR #10 (interrupt fix) - MERGED
