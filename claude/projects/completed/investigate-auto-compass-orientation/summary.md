# Project: Auto Compass Orientation Detection — Feasibility Investigation

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-06-08
**Estimated Time:** 2-4 hours

## Overview

Determine whether INAV can implement automatic compass orientation detection during calibration, based on the variance-minimisation algorithm used by ArduPilot. No implementation — investigation and recommendation only.

## Problem

Compass misorientation is one of the most common configuration mistakes. Users mounting a GPS/compass module in a non-standard orientation must manually select the correct rotation from a long list. Getting it wrong silently causes navigation failures. Auto-detection during calibration would catch this without requiring the user to understand rotation matrices.

## Background

ArduPilot's algorithm (`libraries/AP_Compass/CompassCalibrator.cpp`):
- During calibration, each magnetometer sample is stored with the vehicle's attitude at that moment (roll/pitch/yaw from AHRS DCM, packed as int8_t triplets)
- After 300 samples and ellipsoid fit, every candidate orientation is tried (~ROTATION_MAX minus duplicates)
- For each candidate, samples are rotated into earth frame using the candidate orientation + recorded AHRS attitude; variance of the implied earth field is computed
- Lowest-variance candidate wins; confidence = second_best / best (>4.0 = very confident, >2.0 = acceptable)
- For external compasses with fix_orientation=true, offsets are corrected and fit re-run; internal mismatches flagged as BAD_ORIENTATION

INAV already has ellipsoid/sphere fitting in `src/main/sensors/compass.c`, AHRS attitude available during calibration, and a rotation enum system.

## Objectives

Answer the four feasibility questions before any implementation decision:

1. **Memory**: Is INAV's calibration architecture compatible with recording per-sample attitude snapshots? (300 samples × ~9 bytes = ~2.7 KB RAM — acceptable on F4?)
2. **Rotation coverage**: Does INAV's rotation enum cover the same set of orientations as ArduPilot's, or is a mapping needed?
3. **Configurator UI**: What changes would be required to surface orientation confidence and auto-correction to the user?
4. **Worth it?**: Given flash/RAM constraints on F4 targets, is the feature viable and valuable enough to implement?

## Scope

**In Scope:**
- Read and map INAV's compass calibration code (`src/main/sensors/compass.c`)
- Read and map INAV's rotation enum (`src/main/common/axis.h` or equivalent)
- Estimate RAM and flash cost of the ArduPilot approach
- Identify required Configurator UI changes
- Produce a written recommendation: implement / defer / not viable

**Out of Scope:**
- Any implementation code
- Changes to existing calibration logic

## Success Criteria

- [ ] Memory cost estimate produced (RAM bytes on F4)
- [ ] Rotation enum parity assessment completed
- [ ] Configurator UI change list produced
- [ ] Go/no-go recommendation written with rationale
- [ ] Findings documented in project directory
- [ ] Completion report sent to manager

## Estimated Time

2-4 hours

## Priority Justification

No user impact until investigated. Developer has already completed ArduPilot research which cuts investigation time. Medium priority — do after RC-cycle fix work.
