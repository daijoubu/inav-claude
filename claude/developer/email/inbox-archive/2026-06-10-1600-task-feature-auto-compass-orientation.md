# Task Assignment: Automatic Compass Orientation Detection

**Date:** 2026-06-10 16:00
**From:** Manager
**To:** Developer
**Type:** Task Assignment
**Priority:** MEDIUM
**Estimated Effort:** ~2 days

## Summary

Investigation approved — proceeding with implementation. Add automatic compass orientation detection to INAV's calibration flow using the variance-minimisation algorithm you described. Both firmware and configurator changes needed.

## Project Directory

`claude/projects/active/feature-auto-compass-orientation/`

Full summary and todo in that directory.

## What to Build

### Phase 1 — Firmware (~1 day)
- `CompassOrientationSample` struct (attitude + mag, 9 bytes each), 100-entry static buffer gated behind `USE_AUTO_MAG_ORIENTATION`
- Capture attitude + mag in `compassUpdate()` during calibration
- After solve: variance-minimisation pass over 8 `sensor_align_e` values; record `detected_orientation` and `confidence_ratio`
- Expose via MSP (new fields in calibration result or new MSP message)
- Exclude `USE_AUTO_MAG_ORIENTATION` from tightest F4 targets

### Phase 2 — Configurator (~0.5 day)
- Magnetometer tab: display detected orientation + confidence after calibration
- "Apply detected orientation" button sets `align_mag` and saves
- Guidance: ≥3× = reliable, <2× = ambiguous

### Phase 3 — Testing (~0.5 day)
- Physical bench test with compass in wrong orientation
- F4 RAM fit check

## Notes

- Base off `maintenance-10.x`
- Coordinate firmware + configurator as a single PR cycle
- Independent of `feature-dronecan-magnetometer` but will benefit DroneCAN mag users once that driver exists

---

**Manager**
