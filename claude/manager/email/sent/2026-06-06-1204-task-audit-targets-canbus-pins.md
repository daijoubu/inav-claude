# Task Assignment: Audit AP H7/F7 Targets — Add CAN Bus Pins to INAV Targets

**Date:** 2026-06-06 12:04
**From:** Manager
**To:** Developer
**Project:** audit-targets-canbus-pins
**Priority:** MEDIUM
**Estimated Effort:** 4-8 hours

## Task

Audit ArduPilot H7 and F7 board definitions to extract CAN bus pin assignments, then add those pins to the corresponding INAV targets. CAN sections should be commented out by default so they don't affect normal builds, but allow anyone with the hardware to enable them via a custom build.

## Background

Many INAV H7 and F7 targets have CAN-capable MCU pins that are never defined in target.h. ArduPilot already has this mapping for most boards. Adding the pins (commented out) is a low-effort, high-value contribution — it gives the community a reference without requiring anyone to reverse-engineer the hardware.

## What to Do

1. List all H7 and F7 INAV targets in `src/main/target/`
2. For each, find the corresponding ArduPilot board definition in the `ArduPilot/` directory
3. Extract CAN1 and CAN2 RX/TX pin assignments from the AP definitions
4. Add a commented-out CAN block to each INAV `target.h` using this convention:

```c
// CAN bus pins — sourced from ArduPilot board definition
// Uncomment to enable DroneCAN support (requires custom build)
// #define USE_CAN
// #define CAN1_RX_PIN Pxx
// #define CAN1_TX_PIN Pxx
// #define CAN2_RX_PIN Pxx  // if second CAN bus available
// #define CAN2_TX_PIN Pxx
```

5. **Exception: KAKUTEH7WING** — add the pins but leave them **uncommented** (we have hardware to test this one)
6. Skip targets with no AP equivalent — note them in the completion report
7. Verify no commented blocks break the build matrix

## Success Criteria

- [ ] All H7 and F7 INAV targets audited against ArduPilot
- [ ] CAN pin definitions added (commented) to all targets where an AP mapping exists
- [ ] KAKUTEH7WING pins left active/uncommented
- [ ] Full build matrix passes (F4/F7/H7/AT32/SITL)
- [ ] PR to `maintenance-10.x`

## Project Directory

`claude/projects/active/audit-targets-canbus-pins/`

## Notes

- The ArduPilot board definitions are in the `ArduPilot/` directory in this repo
- If a target already has CAN pins defined in INAV, skip it and note it in the report
- Include your mapping table (INAV target → AP board → pins) in the completion report — useful for future reference

---
**Manager**
