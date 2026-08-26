# Complex Enhancements

Larger feature work requiring significant development effort.

---

## Issues

### #11128 - DroneCAN/CANBus support

**Created:** 2024-11-25
**Labels:** enhancement
**URL:** https://github.com/iNavFlight/inav/issues/11128

**Problem:**
Request for DroneCAN/CANBus protocol support.

**Scope:**
- Major protocol implementation
- Hardware abstraction needed
- Multiple sensor types

**Notes:**
Major feature requiring significant architecture work.

---

### #11184 - Add support for SRXL2 as ESC protocol

**Created:** 2024-12-15
**Labels:** enhancement
**URL:** https://github.com/iNavFlight/inav/issues/11184

**Problem:**
Request for SRXL2 as an ESC telemetry protocol.

**Scope:**
- Protocol implementation
- ESC driver integration

**Notes:**
Protocol implementation work.

---

### inav #11735 - Adding HoTTv4 telemetry to ESC telemetry sensors

**Created:** 2026-07-19
**URL:** https://github.com/iNavFlight/inav/issues/11735

**Problem:** Request to add HoTTv4 as an ESC telemetry protocol source.

**Scope:** New telemetry protocol parser/integration into the ESC telemetry sensor framework.

**Assigned:** `active/investigate-hottv4-esc-telemetry/`

---

### inav #11651 - URML (open robot intent language): a declared, validated mission intent above INAV (RFC)

**Created:** 2026-06-14
**URL:** https://github.com/iNavFlight/inav/issues/11651

**Problem:** Proposal for a new declared/validated mission-intent language layered above INAV's existing mission system. Has 8 comments — active discussion.

**Scope:** Major architectural proposal; needs core-developer design discussion before any implementation work, not a straightforward feature add.

**Assigned:** `active/investigate-urml-mission-intent-rfc/` (read + respond, not a code project — priority LOW)

---

### inav #11645 - RFC: Automatic compass orientation detection during calibration

**Created:** 2026-06-11
**URL:** https://github.com/iNavFlight/inav/issues/11645

**Problem:** RFC proposing automatic compass orientation detection during calibration, instead of manual `align_mag` configuration.

**Scope:** Algorithm/sensor-fusion work. This is already being implemented — see `active/investigate-ardupilot-orientation-technique/` (adapts ArduPilot's `calculate_orientation()` technique, draft PR #11708). Link this issue to that project rather than treating it as separate scope.

As-shipped in PR #11708, `compass_orientation.c` buffers up to 128 `(rawMag, attitude-quaternion)` sample pairs (`int16_t rawMag[3]` + Q15-fixed-point `int16_t q[4]` = 14 bytes/sample → 1,792 bytes / 1.75KB static RAM for `sampleBuffer`), then runs Welford's algorithm over all 16 candidate mounting rotations against that buffered data. Smaller than ArduPilot's ~2.7KB float-based 300-sample buffer, but larger than the original planning doc's ~256-byte online-only design — buffering raw samples was needed so all 16 candidates can be evaluated against the same data rather than requiring 16 parallel accumulators live.

**2026-08-11:** Ray commented directly on #11645 linking to draft PR #11708 — reporter now knows this is already in progress. No further manager/developer action needed beyond what `active/investigate-ardupilot-orientation-technique/` is already doing.

---

### inav #11644 - [RFC] Fixed-wing in-flight detection fails during dead reckoning: replace GPS heading dependency with estimator-fused equivalent

**Created:** 2026-06-11
**URL:** https://github.com/iNavFlight/inav/issues/11644

**Problem:** RFC: in-flight detection for fixed-wing relies on GPS heading, which fails during dead reckoning (GPS-denied); proposes using the estimator-fused heading instead.

**Scope:** Navigation/estimator architecture change — touches flight-safety-relevant in-flight detection logic, needs careful design review.

**Assigned:** `active/investigate-fw-inflight-detection-dead-reckoning/` (priority MEDIUM-HIGH — blocks emergency rearm during dead reckoning)

---

### inav #11563 - Update STM32H7xx HAL from V1.11.4 to V1.13.0

**Created:** 2026-05-15
**URL:** https://github.com/iNavFlight/inav/issues/11563

**Problem:** Request to update the STM32H7xx HAL, citing DMA IRQHandler bug fixes, SPI overflow fixes, and FDCAN fixes upstream between V1.11.4 and V1.13.0.

**Scope:** Large-surface-area HAL version bump affecting all H7 targets — needs full regression testing across H7 boards, not a small change despite being "just" a dependency update. Possibly relevant to the cache-coherency concerns raised in #11562.

**Assigned:** `active/update-stm32h7xx-hal/`

---

### #10848 - Wind Speed Estimator for Multicopters

**Created:** 2024-10-20
**Labels:** enhancement
**URL:** https://github.com/iNavFlight/inav/issues/10848

**Problem:**
Feature request for wind speed estimation on multicopters.

**Scope:**
- Algorithm development
- Sensor fusion work
- May require research

**Notes:**
Algorithm-heavy feature requiring research and testing.
