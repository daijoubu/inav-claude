# Investigation: Auto Compass Orientation Detection — Feasibility

**Date:** 2026-06-10
**Branch:** n/a (research only)
**Target branch if go:** maintenance-10.x

---

## Q1: Memory — Is INAV's calibration architecture compatible with per-sample attitude snapshots?

### Current architecture

INAV's `compassUpdate()` (`sensors/compass.c:379`) uses a **running accumulator** — no individual samples are stored:

```c
static sensorCalibrationState_t calState;   // 80 bytes (4 floats XtY + 4×4 floats XtX)
```

`sensorCalibrationPushSampleForOffsetCalculation()` folds each sample into the accumulator and discards it. Attitude is never captured. The calibration is purely "rotate the craft, collect mag readings, solve for sphere centre."

### What the ArduPilot approach needs

ArduPilot's `CompassSample` struct (from `CompassCalibrator.h`):

```cpp
class AttitudeSample {   // 3 × int8_t = 3 bytes (±180° compressed to 1 byte each)
    int8_t roll, pitch, yaw;
};
class CompassSample {    // total: 9 bytes
    AttitudeSample att;  // 3 bytes
    int16_t x, y, z;    // 6 bytes (compressed mag reading)
};
```

300 samples × 9 bytes = **2,700 bytes = 2.7 KB**. ArduPilot uses `calloc()` during calibration and `free()` when done. INAV avoids dynamic allocation.

### F4 RAM budget

F405 linker script: **128 KB RAM + 64 KB CCM**. The calibration state is a `static` in `compassUpdate()`, so the sample buffer would also be static — permanently occupying RAM even when not calibrating.

**Verdict: Feasible but tight.** 2.7 KB as a static array is ~2% of F4 RAM. Acceptable if gated by a compile-time `USE_AUTO_MAG_ORIENTATION` define so it can be excluded from the most constrained targets. 100 samples instead of 300 would reduce to 900 bytes with minimal impact on detection quality for the limited candidate set INAV needs (see Q2).

### Architecture change required

`compassUpdate()` must be modified to:
1. Sample `attitude.values.roll/pitch/yaw` at each `sensorCalibrationPushSampleForOffsetCalculation()` call and store alongside the mag reading
2. After `sensorCalibrationSolveForOffset()` completes, run the orientation variance pass over the stored samples

Attitude values are already available in `compassUpdate()`'s scope (`flight/imu.h`).

---

## Q2: Rotation coverage — Does INAV's enum cover what's needed?

### INAV orientations (`sensor_align_e`, `drivers/sensor.h`)

8 named orientations:

| Value | Name | Description |
|---|---|---|
| 1 | `CW0_DEG` | No rotation |
| 2 | `CW90_DEG` | 90° yaw |
| 3 | `CW180_DEG` | 180° yaw |
| 4 | `CW270_DEG` | 270° yaw |
| 5 | `CW0_DEG_FLIP` | 180° roll (upside down) |
| 6 | `CW90_DEG_FLIP` | 180° roll + 90° yaw |
| 7 | `CW180_DEG_FLIP` | 180° roll + 180° yaw |
| 8 | `CW270_DEG_FLIP` | 180° roll + 270° yaw |

These cover all physically realizable 90°-step orientations for an external compass mounted to a frame with standard connectors. This is the set users actually use.

### ArduPilot orientations

49 enum entries total (`libraries/AP_Math/rotations.h`), including 45° yaw variants, pitch-up/down, arbitrary roll combinations. The orientation check loop uses `ROTATION_MAX-4` candidates. Most of these cover exotic sensor placements that don't exist in practice for compass modules.

### Compatibility

**No mapping needed.** The ArduPilot variance algorithm is orientation-agnostic — it just iterates over a candidate list and picks the lowest-variance one. INAV can run the same algorithm over its 8 `sensor_align_e` values. The confidence ratio (second_best / best variance) remains valid for distinguishing between 8 candidates.

**Limitation:** INAV also supports external alignment via arbitrary `rollDeciDegrees / pitchDeciDegrees / yawDeciDegrees`. The auto-detection only applies to the 8 standard orientations. If the compass is mounted at an odd angle (externally aligned path), orientation detection would return a low confidence score and should be skipped or reported as "indeterminate."

---

## Q3: Configurator UI — What changes are needed?

### Current magnetometer tab

- Orientation dropdown (`align_mag`) for 8 standard values
- Roll/pitch/yaw fields for external alignment (decidegrees)
- "Start calibration" → progress indicator → "Calibration complete"
- No orientation confidence feedback

### Required changes

**Firmware side:**
- After calibration completes, compute and store detected orientation + confidence ratio
- Extend calibration result data returned via MSP (new fields: `detected_orientation`, `orientation_confidence`)

**Configurator side (`tabs/magnetometer.js` and `.html`):**
1. After calibration complete callback, display detected orientation: `"Detected: CW90_DEG_FLIP (confidence 6.2×)"`
2. Threshold guidance: confidence ≥ 3× = reliable; < 2× = ambiguous
3. Button: **"Apply detected orientation"** — sets the `align_mag` dropdown and saves
4. Auto-apply option (optional): if confidence > configurable threshold, apply without asking

**Scope:** Moderate. One new MSP field or piggyback on existing calibration MSP response. ~50–100 lines JS/HTML change in the magnetometer tab.

---

## Q4: Worth it? Flash/RAM viability on F4

### Costs

| Resource | Cost | Notes |
|---|---|---|
| RAM | 900 B (100 samples) – 2.7 KB (300 samples) | Static; gated by `USE_AUTO_MAG_ORIENTATION` |
| Flash | ~1.5–2 KB | Variance loop over 8 orientations × N samples + rotation matrix applies |
| Code complexity | Low–Medium | Algorithm is self-contained; no new dependencies |

### Benefits

Compass misorientation is a **very common user mistake** that causes silent navigation failures. Users rotate the craft, calibration completes successfully, and the compass appears healthy — but heading is wrong. This typically only reveals itself on the first GPS-assisted flight. Auto-detection during calibration catches the mistake at the point where it's easiest to fix.

The algorithm is well-validated in ArduPilot and can be directly adapted — no research risk.

### Mitigation for F4 RAM

- 100 samples instead of 300: sufficient for 8-candidate discrimination, saves 1.8 KB
- `#if defined(USE_AUTO_MAG_ORIENTATION)` gate: excluded from flash-constrained targets by default
- Buffer can be a local array allocated on the stack during the calibration solve phase, not a permanent static — but INAV's compass update is called from a task loop, not a one-shot function, so stack allocation would require refactoring the calibration state machine. A static gated by define is simpler.

---

## Recommendation: GO

The algorithm is straightforward, the codebase changes are self-contained, and the user benefit is high relative to the implementation cost.

### Implementation phases

**Phase 1 — Firmware (~1 day)**
- Add `compassOrientationSample_t` struct (9 bytes: `int8_t roll/pitch/yaw` + `int16_t x/y/z`)
- Add static `compassOrientationSamples[100]` + sample count, gated by `USE_AUTO_MAG_ORIENTATION`
- In `compassUpdate()`, capture attitude snapshot alongside each `pushSampleForOffsetCalculation` call (max 100 stored, circular if more arrive)
- After `sensorCalibrationSolveForOffset()`, iterate over 8 `sensor_align_e` values, rotate each stored sample, compute variance of implied field magnitude, pick lowest
- Store result in new `compassDetectedAlignment` + `compassOrientationConfidence` globals
- Expose via MSP in calibration complete response

**Phase 2 — Configurator (~0.5 day)**
- Read new MSP fields after calibration completes
- Display detected orientation + confidence in magnetometer tab
- "Apply detected orientation" button that sets `align_mag` and saves
- Threshold guidance text (≥3× = reliable)

**Phase 3 — Testing (~0.5 day)**
- Test with physical compass in known wrong orientation, verify detection
- Test with correctly mounted compass, verify correct orientation detected
- Test on F4 target to confirm RAM fits

**Total estimated effort: ~2 days**

### What this does NOT solve
- Arbitrary-angle external alignment detection (roll/pitch/yaw decidegrees path) — too many candidates for variance approach
- Detection after arming (runtime drift) — out of scope; calibration-time detection only
- Targets with extreme flash constraints that must exclude `USE_AUTO_MAG_ORIENTATION`
