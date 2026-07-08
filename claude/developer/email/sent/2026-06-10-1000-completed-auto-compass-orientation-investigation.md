# Investigation Complete: Auto Compass Orientation Detection — GO recommendation

**Date:** 2026-06-10 10:00
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: INVESTIGATION COMPLETED

Investigation complete. Findings written to `claude/projects/active/investigate-auto-compass-orientation/investigation-findings.md`.

## Recommendation: GO — ~2 days estimated effort

Compass misorientation is a common silent failure that only reveals itself in the air. The algorithm is well-validated in ArduPilot and self-contained. All four feasibility questions answered:

## Q1: Memory — Compatible with F4?

Current calibration discards all samples into a running accumulator (`sensorCalibrationState_t` = 80 bytes). No attitude is ever captured. Needs a new static sample buffer.

ArduPilot's `CompassSample` = 9 bytes (3 × int8_t attitude + 3 × int16_t mag). 100 samples × 9 bytes = **900 bytes** (reduced from ArduPilot's 300 for F4 compatibility — sufficient for 8-candidate discrimination). Gate behind `USE_AUTO_MAG_ORIENTATION` so it can be excluded from the most constrained targets. Static allocation is required given INAV's task-loop architecture.

**Verdict: Feasible on F4 with the define guard.**

## Q2: Rotation coverage — Mapping needed?

No mapping needed. INAV has 8 standard orientations in `sensor_align_e` (CW0/90/180/270 + FLIP variants) covering all practical compass mounting cases. The ArduPilot variance algorithm is orientation-agnostic — it iterates over whatever candidate list you give it. Run it over INAV's 8 values instead of ArduPilot's 49. Confidence ratio (second_best / best variance) remains valid.

Limitation: arbitrary-angle external alignment (rollDeciDegrees path) is not detectable — too many candidates. Detection skips/reports "indeterminate" when external alignment is active.

## Q3: Configurator UI changes

After calibration completes:
- Firmware returns detected orientation + confidence ratio via MSP (new fields)
- Magnetometer tab displays: "Detected: CW90_DEG_FLIP (confidence 6.2×)"
- "Apply detected orientation" button sets `align_mag` and saves
- Threshold guidance: ≥3× reliable, <2× ambiguous

Scope: ~50–100 lines JS/HTML in the magnetometer tab. Moderate.

## Q4: Worth it?

Yes. The only significant cost is the 900-byte static buffer. Benefits: catches the most common compass setup mistake at calibration time, before the user's first GPS flight. Algorithm is proven, implementation risk is low.

## Suggested implementation phases

1. **Phase 1 — Firmware (~1 day):** Add sample buffer + attitude capture in `compassUpdate()`; add variance-minimisation pass over 8 orientations after solve; expose result via MSP.
2. **Phase 2 — Configurator (~0.5 day):** Display detected orientation + confidence; "Apply" button in magnetometer tab.
3. **Phase 3 — Testing (~0.5 day):** Physical compass in wrong orientation; correct orientation; F4 RAM fit check.

**Total: ~2 days. Recommend targeting maintenance-10.x.**

Note: this investigation was triggered partly by the DroneCAN magnetometer task (also in inbox). The two features are independent but the compass orientation detection would benefit DroneCAN mag users too once that driver exists.

---
**Developer**
