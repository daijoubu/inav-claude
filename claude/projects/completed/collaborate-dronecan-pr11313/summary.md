# Project: Collaborate on DroneCAN PR #11313

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM-HIGH
**Type:** Feature (Collaboration)
**Created:** 2026-02-11
**Estimated Effort:** 5-8 hours (revised from 15-25 after scope change)

## Overview

Collaborate with @daijoubu on PR #11313 to help complete the DroneCAN/libcanard implementation for INAV. This PR adds foundational CAN bus support and we will contribute additional features and testing.

## Background

PR #11313 introduces DroneCAN protocol support using the libcanard library:
- Core CAN framework and libcanard integration
- FDCAN driver for STM32H7
- bxCAN driver for STM32F7
- GPS receiver driver (initial implementation)
- Battery voltage sensor
- 44 unit tests

**PR Details:**
- **Author:** @daijoubu
- **Status:** Draft (Open)
- **Base Branch:** `maintenance-10.x`
- **Size:** +27,716 lines, 303 files changed, 46 commits
- **Related Issue:** #11128
- **PR URL:** https://github.com/iNavFlight/inav/pull/11313

## Our Contribution Scope (Revised)

### 1. CAN Current Sensor Driver - COMPLETE
Add current sensing capability to complement the existing battery voltage driver.
- **Commit:** `f54bb4d4e` - Add DroneCAN current sensor support to battery system

### 2. Documentation - COMPLETE
Write user-facing documentation for the DroneCAN feature.
- **Commit:** `7fb2567f0` - Add DroneCAN documentation
- Created `docs/DroneCAN.md`
- Updated `docs/Battery.md` with CAN sensor option

### 3. Parameter Get/Set Protocol - DEFERRED
Implement the DroneCAN parameter protocol for reading and writing configuration parameters.
- **Decision:** Deferred to follow-up PR
- **Reason:** Current functionality (GPS, voltage, current) is sufficient for initial release

### 4. HITL Testing - SKIPPED
Test the implementation using Hardware-in-the-Loop simulation.
- **Status:** Skipped - hardware not available
- **Alternative:** Unit tests (81 passing) and SITL build verification completed

## Out of Scope

- PWM output via CAN (ESC/servo control) - complex, separate effort
- Peripheral board compatibility - requires specific hardware
- Flight testing - requires physical aircraft
- Parameter protocol - deferred to follow-up

## Progress

| Phase | Status | Commit |
|-------|--------|--------|
| Research & Setup | Complete | - |
| CAN Current Sensor | Complete | `f54bb4d4e` |
| Documentation | Complete | `7fb2567f0` |
| HITL Testing | Skipped | N/A |
| Parameter Protocol | Deferred | N/A |

## Success Criteria (Revised)

- [x] CAN current sensor driver implemented and tested
- [ ] ~~Parameter get/set protocol working~~ (DEFERRED)
- [x] ~~HITL testing completed~~ Unit tests pass (81/81)
- [x] Wiki documentation written for DroneCAN feature
- [ ] Changes submitted to PR author for review

## Next Steps

1. Coordinate with @daijoubu on submitting changes
2. Submit as patch or suggestions on PR #11313
3. Close project upon acceptance

## References

- **PR:** https://github.com/iNavFlight/inav/pull/11313
- **Issue:** https://github.com/iNavFlight/inav/issues/11128
- **libcanard:** https://github.com/dronecan/libcanard
- **DroneCAN Spec:** https://dronecan.github.io/
