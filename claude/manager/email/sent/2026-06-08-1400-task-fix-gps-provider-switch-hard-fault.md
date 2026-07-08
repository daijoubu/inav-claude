# Task Assignment: Fix GPS Provider Switch Hard Fault

**Date:** 2026-06-08 14:00
**From:** Manager
**To:** Developer
**Project:** fix-gps-provider-switch-hard-fault
**Priority:** HIGH
**Estimated Effort:** 1-2 hours

## Task

Fix a reproducible hard fault in release/9.1 that occurs when switching GPS provider via CLI (e.g. `set gps_provider = UBLOX` after booting with `gps_provider = MSP` or `FAKE`) without a reboot.

## Background

Driver-based providers (MSP, FAKE) never open a serial port during `gpsInit()` — `gpsState.gpsPort` stays NULL. Because `gpsState.gpsConfig` is a pointer to live PG data, the CLI change takes effect immediately. On the next scheduler tick, `gpsUpdate()` dispatches to `gpsHandleUBLOX()`, which calls `serialRxBytesWaiting(NULL)` → hard fault. A GitHub issue has been filed against iNavFlight/inav.

We are in the RC cycle for release/9.1. This is a blocker.

## What to Do

1. Add a field to `gpsState` (in `gps_private.h`) to record the provider that was active when `gpsInit()` ran
2. At the top of `gpsUpdate()`, compare `gpsConfig()->provider` against the stored value
3. On mismatch: close existing serial port (if open), call `gpsInit()`, return early
4. Build full matrix: F4, F7, H7, AT32, SITL

## Branch

**Base branch: `release/9.1`** (NOT maintenance-10.x, NOT master)
This is a release-branch fix — PR must target `release/9.1`.

## Success Criteria

- [ ] CLI `set gps_provider = UBLOX` after booting with MSP/FAKE no longer hard faults
- [ ] Normal GPS init (provider unchanged) still works correctly
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] PR opened against `release/9.1`, GitHub issue referenced in PR description
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/fix-gps-provider-switch-hard-fault/`

---
**Manager**
