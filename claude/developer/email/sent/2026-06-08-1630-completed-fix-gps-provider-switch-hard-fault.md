# Task Completed: Fix GPS Provider Switch Hard Fault

**Date:** 2026-06-08 16:30
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Fixed a reproducible hard fault in release/9.1 triggered by changing `gps_provider` via CLI from a driver-based provider (MSP/FAKE) to a serial-based provider (e.g. UBLOX) without rebooting. Added null guards in `gpsUpdate()` and `gpsEnablePassthrough()` to prevent NULL serial port dereference.

## Branch and Commits

**Branch:** `fix/gps-provider-null-guard`
**PR:** #11634 (against iNavFlight/inav release/9.1)
**Commits:**
- `d6db20e71` - fix(gps): guard against NULL serial port when GPS provider changed without reboot

## Changes Made

**Files modified:**
- `src/main/io/gps.c` — null guard in gpsUpdate() before state machine dispatch; null guard in gpsEnablePassthrough()
- `src/test/unit/gps_null_port_unittest.cc` — new unit test (4 cases reproducing the bug)
- `src/test/unit/CMakeLists.txt` — test registration

## Testing

- [x] Unit test written that reproduces the crash (confirmed FAIL before fix, PASS after)
- [x] Full build matrix: SITL, F4 (MATEKF405), F7 (MATEKF765), H7 (KAKUTEH7WING), AT32 (IFLIGHT_BLITZ_ATF435) — all clean
- [x] Hardware tested on KAKUTEH7WING: provider switch via CLI no longer causes hard fault
- [x] CI running on PR #11634 — tests and SITL Linux green, hardware matrix in progress

## Next Steps

Monitor CI on PR #11634. No follow-up work anticipated — fix is minimal and targeted.

---
**Developer**
