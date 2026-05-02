# Project: Remove Non-DroneCAN Functions from ITCM

**Status:** ⏸️ BACKBURNER
**Priority:** LOW
**Type:** Maintenance
**Created:** 2026-05-02
**Estimated Effort:** 2-4 hours

## Overview

Three functions currently attributed to ITCM have no genuine latency requirement and should be relocated to flash, recovering space in ITCM for future genuinely time-critical code.

## Problem

During the `investigate-itcm-dronecan-isr` audit, three ITCM residents were identified as speculative or historical placements with no current timing justification:

- `taskSendSbus2Telemetry`
- `calculateThrottleStatus`
- `applySensorAlignment`

These consume ITCM headroom that should be reserved for functions with real hard-deadline constraints (e.g. the 8 kHz gyro pipeline).

## Solution

Remove the `FAST_CODE` (or equivalent) attribute from each function, verify the firmware still compiles and behaves correctly, and confirm ITCM utilisation decreases on MATEKF765SE.

## Note: Needs Discussion Before Starting

User flagged that they don't understand these functions well enough to test thoroughly. Discussion required before assigning to developer to agree on:
- What correct behaviour looks like for each function
- How to verify no regression (bench test, flight test, telemetry check, etc.)

## Implementation

1. Confirm each function's current ITCM attribution (FAST_CODE / section attribute)
2. Remove FAST_CODE from `taskSendSbus2Telemetry` — verify SBUS2 telemetry still transmits correctly
3. Remove FAST_CODE from `calculateThrottleStatus` — verify throttle status flags are unaffected
4. Remove FAST_CODE from `applySensorAlignment` — verify IMU alignment is applied correctly
5. Build for MATEKF765SE and confirm ITCM utilisation decreases
6. Run any available unit tests

## Success Criteria

- [ ] All three functions relocated from ITCM to flash
- [ ] MATEKF765SE ITCM utilisation decreases by expected amount
- [ ] Firmware builds cleanly for F7 targets
- [ ] No functional regressions (per agreed test plan)
- [ ] PR created targeting `maintenance-10.x`

## Related

- **Source investigation:** `completed/investigate-itcm-dronecan-isr/`
- **Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
