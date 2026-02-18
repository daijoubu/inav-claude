# Project: Fix NEXUS-X IMU Orientation

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-02-14
**Estimated Effort:** 1 hour

## Overview

The default IMU orientation on the RadioMaster NEXUS-X target is backwards. Users must manually apply YAW-180 to correct it. The alignment constant in `target.h` needs to be fixed.

## Problem

Issue [#11325](https://github.com/iNavFlight/inav/issues/11325): The direction arrow printed on the NEXUS-X board does not match the default IMU orientation in INAV. User (Painless360) had to apply YAW-180 via the alignment tool to correct it. Manager has confirmed this is currently backwards.

## Root Cause

In `inav/src/main/target/NEXUSX/target.h` line 35:
```c
#define IMU_ICM42605_ALIGN     CW180_DEG
```

This alignment is 180 degrees off from the physical board orientation arrow.

## Fix

Change the IMU alignment constant. Since applying YAW-180 in the configurator corrects it, the current `CW180_DEG` likely needs to change to `CW0_DEG` (or the appropriate rotation that matches the board silkscreen).

## Key Files

- `inav/src/main/target/NEXUSX/target.h` — line 35, `IMU_ICM42605_ALIGN`

## Success Criteria

- [ ] IMU orientation matches the direction arrow on the physical board without manual correction
- [ ] Build compiles cleanly
- [ ] PR created against `maintenance-9.x`
- [ ] Reference issue #11325 in PR
