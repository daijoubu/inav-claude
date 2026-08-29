# Status Update: Qodo Finding 2 - Truncated MSP Writes Implemented and Verified

**Date:** 2026-08-22 15:00
**From:** Developer
**To:** Manager
**Type:** Status Update
**Project:** feature-dronecan-param-getset
**Re:** PR #11683 — Address Qodo bot findings

## Summary

Finding 2 (truncated MSP PARAM_GETSET writes being accepted) has been fully implemented, tested with comprehensive unit coverage, and verified through both isolated unit tests and real SITL build validation. The implementation revealed and fixed a real build-time bug that unit tests alone would not have caught.

## Finding 2: Truncated MSP Writes Accepted - IMPLEMENTED

**Status: COMPLETED**

The fix extracted the truncated-payload-vulnerable parsing logic from `fc_msp.c`'s massive inline switch statement into a pair of dedicated files following the existing `fc_msp_box.c` precedent (a small `.c`/`.h` pair already cleanly separated from the main file for self-contained MSP logic).

**Implementation approach:**
- **New files:** `src/main/fc/fc_msp_dronecan.h` and `src/main/fc/fc_msp_dronecan.c`
- **New function:** `bool mspParseDronecanParamGetSetRequest(sbuf_t *src, dronecanParamRequest_t *req)`
  - Returns `false` immediately on **any** truncation: index/is_write read, value_type read, each type's value bytes, name field
  - Rejects nonsensical `value_type == DRONECAN_PARAM_TYPE_EMPTY` on a write
  - Replaces the old behavior of silently skipping truncated reads and dispatching UAVCAN requests with zeroed/garbage values
- **Integration:** `fc_msp.c` now replaces the ~45-line inline block with a 4-line call to the new function; returns `MSP_RESULT_ERROR` and breaks on failure
- **CMake registration:** Main source list (`src/main/CMakeLists.txt`) and new unit test target (`src/test/unit/CMakeLists.txt`)

## New Test Coverage: 13 Unit Tests, All Passing

**Test file:** `src/test/unit/fc_msp_dronecan_unittest.cc` (new)

**Test coverage:**
- Underflow before index/is_write read → rejection
- Read-request (is_write=0) pass-through → accepted regardless of trailing bytes (read requests intentionally don't validate)
- Complete INT write (8 bytes) → accepted, value decoded correctly
- Truncated INT writes (0-7 bytes) → all rejected
- Complete FLOAT write (4 bytes) → accepted
- Truncated FLOAT writes (0-3 bytes) → all rejected
- Complete BOOL write (1 byte) → accepted
- Truncated BOOL write (0 bytes) → rejected
- Complete STRING write (length byte + string data) → accepted, correctly clamps oversized lengths
- Truncated STRING writes (declared length > remaining bytes) → all rejected
- EMPTY type on a write → rejected
- Truncated trailing name field → rejected
- Complete name field → accepted

**Test result:** `fc_msp_dronecan_unittest` **13/13 PASS**

## Real Bug Caught and Fixed During Verification

**The bug:** `fc_msp_dronecan.c` and `fc_msp_dronecan.h` originally wrapped their own `#include "platform.h"` *inside* their `#ifdef USE_DRONECAN` guard. In a real firmware or SITL build, `USE_DRONECAN` is defined **by** `platform.h` itself (transitively via `target.h`) — so the guard was always false when checked. The entire file silently compiled to an empty translation unit. This caused a real **SITL link failure**: `undefined reference to mspParseDronecanParamGetSetRequest`.

**Why the unit test alone didn't catch this:** The unit test CMake target defines `USE_DRONECAN` directly via compiler flag (e.g., `-DUSE_DRONECAN`), completely bypassing the platform.h ordering issue.

**The fix:** Moved `#include "platform.h"` (and `<string.h>`) above the `#ifdef USE_DRONECAN` guard in both files, matching the pattern already established in `drivers/dronecan/dronecan.c`.

**Key insight for future work:** This is a great example of why testing in the real build target (not just an isolated unit test environment) matters. Build-time issues like header ordering and include-guard interactions can remain hidden in synthetic unit test defines. Always verify new code in its actual deployment context (SITL in this case, hardware targets for release validation).

## Full Verification After the Include-Order Fix

All verification completed and passing:

**SITL Build:**
- `build_sitl` links cleanly with zero warnings or errors
- Preprocessor verification under real SITL build flags (not the unit test's synthetic `-DUSE_DRONECAN`) confirms `mspParseDronecanParamGetSetRequest`'s definition survives preprocessing — root cause genuinely fixed, not a coincidental symptom

**Unit Test Suite:**
All 4 relevant binaries pass:
- `fc_msp_dronecan_unittest`: **13/13 PASS** (new)
- `dronecan_application_unittest`: **30/30 PASS** (unchanged, regression check)
- `dronecan_getnodeinfo_unittest`: **13/13 PASS** (unchanged)
- `dronecan_messages_unittest`: **23/23 PASS** (unchanged)

## Commit

**Branch:** `feature/dronecan-param-getset`

**Commit:** `7c775c2b1 fix(dronecan): reject truncated MSP PARAM_GETSET write payloads`

Stacked on top of the earlier Finding 1 fix commit `0a1556d96`.

**Not yet pushed to origin** — same as Finding 1's commit. Branch has an open PR (#11683).

## Status: Both Qodo Findings Ready for Merge

**Finding 1** (commit `0a1556d96`): Reordered timeout check, new regression test rewritten and verified
**Finding 2** (commit `7c775c2b1`): Refactored into dedicated module, 13 unit tests passing, verified in SITL build

**Decision needed:** Does the manager want these commits pushed to the open PR #11683 now?

**Important caveat:** Full pre-PR build matrix (F4/F7/H7/AT32 hardware targets) has **NOT** been run yet — only SITL and unit test suite. Per project convention, new code should be validated across hardware families before being considered PR-ready. Recommend running hardware target builds before pushing.

---
**Developer**
