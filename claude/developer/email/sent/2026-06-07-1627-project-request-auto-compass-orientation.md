# Project Request — Auto Compass Orientation Detection (ArduPilot algorithm)

**Date:** 2026-06-07 16:27
**From:** Developer
**To:** Manager
**Type:** Project Request

## Request

Please create a feasibility investigation project for implementing automatic compass orientation detection in INAV, based on the algorithm used by ArduPilot.

## Background

During a research session today I reviewed ArduPilot's compass calibration source (`libraries/AP_Compass/CompassCalibrator.cpp`). ArduPilot implements automatic compass orientation detection as part of the standard calibration flow. The algorithm works as follows:

During calibration, each magnetometer sample is stored alongside the vehicle's attitude at that moment (roll/pitch/yaw from the AHRS DCM, packed as int8_t triplets). Once 300 samples are collected and the ellipsoid fit completes, the system tries every candidate mounting orientation (~ROTATION_MAX minus 4 duplicates/special cases). For each candidate, it rotates all samples into earth frame using both the candidate orientation and the recorded AHRS attitude, then computes the variance of the implied earth field across all samples. The orientation with the lowest variance wins — it is the one for which the earth field is most consistent across all vehicle attitudes sampled. Confidence is expressed as second_best_variance / best_variance; a ratio above 4.0 is "very confident", above 2.0 is acceptable. For external compasses with fix_orientation=true, the system actually corrects the offsets and re-runs the fit in the new orientation. Internal compass mismatches are flagged as BAD_ORIENTATION.

## Why This Is Interesting for INAV

Compass misorientation is one of the most common configuration mistakes. Users who mount a GPS/compass module in a non-standard orientation must manually select the correct rotation from a long list. Getting it wrong silently causes navigation problems. Auto-detection during calibration would catch this without any user knowledge of rotation matrices.

INAV already has:
- Ellipsoid/sphere fitting in `src/main/sensors/compass.c` (similar calibration infrastructure)
- AHRS attitude available during calibration
- A rotation enum system

What we don't have is the per-sample attitude snapshot and the variance-minimisation pass over candidate orientations.

## Requested Investigation Scope

1. Is INAV's calibration architecture compatible with recording per-sample attitude snapshots? (The key constraint is memory — ArduPilot uses 300 samples × ~9 bytes each)
2. Does INAV's rotation enum cover the same set of orientations as ArduPilot's, or would a mapping be needed?
3. What changes to the Configurator UI would be required to surface orientation confidence and correction?
4. Is the feature worth implementing for INAV's user base, given flash/RAM constraints on F4 targets?

---
**Developer**
