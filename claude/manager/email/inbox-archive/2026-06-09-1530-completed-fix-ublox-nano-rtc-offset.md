# Task Completed: Fix uBlox nano Field RTC Offset

**Date:** 2026-06-09 15:30
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Fixed the uBlox nano field sign bug that caused the RTC to be set ~64 seconds fast on first GPS lock. The nano field (int32_t) can legitimately be negative near second boundaries; clamping it to zero before the millis conversion prevents uint16_t wraparound.

## Branch and Commits

**Branch:** `fix/ublox-nano-rtc-offset` (based on `release/9.1`)
**PR:** #11642 — https://github.com/iNavFlight/inav/pull/11642
**Commits:**
- `6c6df28b8` — fix(gps): clamp negative uBlox nano field before millis conversion

## Changes Made

**Files modified:**
- `src/main/io/gps_ublox.c` — Clamped nano to zero before millis division on both MSG_TIMEUTC (line 638) and MSG_PVT (line 677) handlers

## Testing

- [x] SITL build: PASS
- [x] F4 (MATEKF405): PASS
- [x] F7 (MATEKF765SE): PASS
- [x] H7 (KAKUTEH7WING): PASS
- [x] AT32 (IFLIGHT_BLITZ_ATF435): PASS
- [ ] Hardware test with actual negative nano capture: not performed (requires GPS lock at second boundary)

## Notes

Per your instruction, only one PR was opened (release/9.1). maintenance-10.x will receive the fix when release/9.1 merges into it.

---
**Developer**
