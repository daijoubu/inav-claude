# Guidance: feature-auto-compass-orientation — run calculation on PC, not FC

**Date:** 2026-06-10 16:20
**From:** Manager
**To:** Developer
**Type:** Architecture Correction
**Re:** feature-auto-compass-orientation (supersedes 2026-06-10-1610 flash guidance)

## Revised architecture: stream samples to configurator

Two problems with the on-FC approach:

1. **F405 RAM**: 128KB total. A 900-byte static calibration buffer is permanent — it sits allocated even when the FC is flying, for a task that runs once at a bench. Larger sample counts (ArduPilot uses 300) would make this worse.
2. **F722 flash**: As flagged in the earlier email, F722 has only 448KB usable flash and already compiles at -Os. Adding algorithm code pushes it closer to the limit.

Since compass calibration is a **one-time bench task**, the right place for the computation is the PC:

- FC streams raw (mag + attitude) samples via MSP during calibration — no buffer needed on the FC
- Configurator receives the stream, accumulates samples, and runs the variance-minimisation pass locally
- PC has unlimited memory and compute — can use ArduPilot's full 300-sample, 49-orientation algorithm if desired
- FC firmware change is minimal: one MSP message to emit a sample each calibration tick
- No `USE_AUTO_MAG_ORIENTATION` guard, no per-target exclusions, no flash or RAM concern on any target

## Implementation sketch

**Firmware (small):**
- During compass calibration (while `compassIsCalibrationComplete()` is false), emit a new MSP message each tick containing current attitude quaternion/Euler + raw mag vector
- No sample buffer on the FC — just emit and forget

**Configurator (most of the work):**
- During calibration, subscribe to the new MSP sample stream
- After calibration completes, run variance-minimisation over received samples across INAV's 8 `sensor_align_e` orientations
- Display: "Detected orientation: CW90_DEG_FLIP (confidence 6.2×)"
- "Apply" button sets `align_mag` and saves

## Deliverable change

Update `summary.md` and `todo.md` in `claude/projects/active/feature-auto-compass-orientation/` to reflect this architecture before starting implementation.

---

**Manager**
