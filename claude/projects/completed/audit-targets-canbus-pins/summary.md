# Project: Audit AP H7/F7 Targets — Add CAN Bus Pins to INAV Targets

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Feature / Maintenance
**Created:** 2026-06-06
**Estimated Time:** 4-8 hours

## Overview

Audit ArduPilot H7 and F7 hardware definitions to extract CAN bus pin assignments, then add those pins to the corresponding INAV targets. CAN sections should be commented out by default (enabling custom builds) except for boards the user has hardware to test.

## Problem

Many INAV H7 and F7 targets support hardware that has CAN bus pins on the MCU, but those pins are not defined in the INAV target configuration. People who want to use DroneCAN on those boards currently have no reference for which pins to use. ArduPilot already has this mapping for many boards and is a reliable reference source.

## Objectives

1. Enumerate all INAV H7 and F7 targets
2. Find corresponding ArduPilot board definitions for each
3. Extract CAN RX/TX pin assignments from AP definitions
4. Add CAN pin definitions to INAV target.h files, commented out by default
5. Leave KAKUTEH7WING uncommented (user has hardware to test)

## Scope

**In Scope:**
- All STM32H7 and STM32F7 INAV targets in `src/main/target/`
- ArduPilot board definitions in `ArduPilot/` directory as reference
- CAN bus pin definitions only (RX/TX pins, not full DroneCAN feature enablement)
- Commented-out blocks with a note explaining how to enable

**Out of Scope:**
- F4 targets (no hardware CAN on most F4 MCUs)
- AT32 targets (separate architecture)
- Enabling full DroneCAN features — pins only
- Targets with no AP equivalent (skip with a note)

## Commented-Out Convention

Add to each target's `target.h`:
```c
// CAN bus pins — sourced from ArduPilot board definition
// Uncomment to enable DroneCAN support (requires custom build)
// #define USE_CAN
// #define CAN1_RX_PIN Pxx
// #define CAN1_TX_PIN Pxx
// #define CAN2_RX_PIN Pxx  // if available
// #define CAN2_TX_PIN Pxx  // if available
```

**Exception:** KAKUTEH7WING — leave uncommented (tested hardware).

## Success Criteria

- [ ] All H7 and F7 INAV targets audited against AP
- [ ] CAN pin definitions added (commented) to all targets where AP mapping exists
- [ ] KAKUTEH7WING CAN pins left active (not commented)
- [ ] Targets with no AP equivalent documented (skipped with note)
- [ ] Full build matrix passes — commented pins must not break any builds
- [ ] PR to `maintenance-10.x`

## Priority Justification

Low-effort, high-value community contribution. Enables DroneCAN on a wide range of existing hardware without requiring users to reverse-engineer pin assignments.
