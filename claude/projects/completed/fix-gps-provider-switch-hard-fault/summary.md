# Project: GPS Provider Switch Hard Fault Fix

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-06-08
**Estimated Time:** 1-2 hours

## Overview

Fix a reproducible hard fault that occurs in INAV release/9.1 when a GPS provider is switched via the CLI (e.g. from MSP or FAKE to UBLOX) without a reboot.

## Problem

Driver-based GPS providers (MSP, FAKE) never open a serial port during `gpsInit()` — `gpsState.gpsPort` stays NULL. Because `gpsState.gpsConfig` is a pointer to live PG data, a CLI `set gps_provider = UBLOX` takes effect immediately without a reboot. On the next scheduler tick, `gpsUpdate()` dispatches to `gpsHandleUBLOX()`, which calls `serialRxBytesWaiting(NULL)` → hard fault. FC becomes non-responsive.

A GitHub issue has been filed against iNavFlight/inav.

## Objectives

1. Detect a runtime GPS provider change in `gpsUpdate()`
2. Close any existing serial port and call `gpsInit()` again for the new provider
3. Ensure no regression in normal GPS init/update paths

## Scope

**In Scope:**
- `src/main/io/gps_private.h` — track provider active at init time
- `src/main/io/gps.c` — detect provider change, reinit cleanly
- Targeting `release/9.1` branch

**Out of Scope:**
- Changes to GPS driver logic beyond the reinit path
- Backport to earlier releases
- Configurator changes

## Implementation Steps

1. Add a field to `gpsState` (in `gps_private.h`) to record the provider that was active when `gpsInit()` ran
2. At the top of `gpsUpdate()`, compare current `gpsConfig()->provider` against the stored value
3. On mismatch: close existing serial port (if open), call `gpsInit()`, return
4. Build and verify against `release/9.1` — F4, F7, H7, AT32, SITL

## Success Criteria

- [ ] CLI `set gps_provider = UBLOX` after boot from MSP/FAKE no longer causes a hard fault
- [ ] Normal GPS init (provider set before boot) still works correctly
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] PR opened against `release/9.1`
- [ ] GitHub issue referenced in PR

## Estimated Time

1-2 hours

## Priority Justification

Reproducible crash in the active RC cycle for release/9.1. Minimal, well-understood fix with low risk of regression.
