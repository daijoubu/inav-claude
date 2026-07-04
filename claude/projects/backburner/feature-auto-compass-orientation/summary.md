# Project: Automatic Compass Orientation Detection

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-06-10
**Estimated Time:** 2 days

## Overview

During compass calibration, detect the physical mounting orientation automatically using a variance-minimisation algorithm. The **calculation runs in the configurator (PC), not on the FC** — the FC streams raw samples via MSP during calibration and the configurator does the math. This avoids any RAM or flash cost on the FC.

## Architecture

**Firmware (small change):**
- While calibration is in progress, emit a new MSP message each calibration tick: current attitude (Euler or quaternion) + raw mag vector
- No sample buffer on the FC — emit and forget

**Configurator (most of the work):**
- Subscribe to the sample stream during calibration
- After calibration completes, run variance-minimisation over received samples across INAV's 8 `sensor_align_e` orientations
- Display result: "Detected orientation: CW90_DEG_FLIP (confidence 6.2×)"
- "Apply" button sets `align_mag` and saves
- Confidence threshold guidance: ≥3× reliable, <2× ambiguous

## Why Not On-FC

The on-FC approach (static sample buffer + algorithm) was rejected:
- **F405 RAM**: 128KB total; a permanent static buffer for a one-time bench task wastes scarce in-flight RAM
- **F722 flash**: 448KB usable, compiles at -Os; algorithm code adds unnecessary pressure
- Calibration is a bench-only task — the PC has unlimited memory and compute

## Feasibility Findings (from investigation)

- INAV has 8 standard `sensor_align_e` orientations — sufficient for all practical mounting cases; no ArduPilot mapping needed
- Arbitrary-angle external alignment (rollDeciDegrees path) is out of scope; detection reports "indeterminate" when active
- Algorithm is orientation-agnostic: iterate over whatever candidate list is provided
- Configurator scope: moderate (~50–150 lines JS/HTML in magnetometer tab plus sample accumulation logic)

## Success Criteria

- [ ] New MSP message emits attitude + raw mag sample each calibration tick
- [ ] Configurator accumulates samples during calibration stream
- [ ] Variance-minimisation correctly identifies orientation in bench test
- [ ] Configurator displays result and confidence; "Apply" button works
- [ ] No static RAM buffer added to firmware
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL) — firmware change should be tiny
- [ ] PR opened against `maintenance-10.x` (firmware + configurator)
- [ ] Completion report sent to manager

## Estimated Time

2 days (mostly configurator work)
