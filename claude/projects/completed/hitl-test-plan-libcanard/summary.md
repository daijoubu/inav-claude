# Project: HITL Test Plan for add-libcanard Branch

**Status:** ✅ COMPLETED
**Priority:** HIGH
**Type:** Investigation / Test Planning
**Created:** 2026-02-11
**Completed:** 2026-02-11
**Estimated Effort:** 2-4 hours

## Overview

Develop a comprehensive list of Hardware-In-The-Loop (HITL) tests to validate the DroneCAN/libcanard implementation on the `add-libcanard` branch of INAV firmware.

## Problem

The add-libcanard branch introduces DroneCAN support via the libcanard library. Before merging or deploying to real hardware, we need a structured test plan to validate functionality with actual DroneCAN peripherals.

## Available Hardware

- DroneCAN GPS module
- DroneCAN Battery monitor

## Solution

Create a detailed HITL test plan covering:
1. Device enumeration and discovery
2. GPS data reception and parsing
3. Battery monitor telemetry
4. Error handling and recovery
5. Performance under load

## Scope

**In Scope:**
- Review add-libcanard branch changes
- Identify all DroneCAN message types supported
- Create test cases for available hardware (GPS, battery monitor)
- Define pass/fail criteria for each test
- Document test procedures

**Out of Scope:**
- Actually running the tests (separate project)
- Testing hardware we don't have (ESCs, airspeed sensors, etc.)
- SITL-only testing (this is specifically HITL)

## Implementation

1. Review the add-libcanard branch to understand supported features
2. Identify DroneCAN message types implemented
3. Map available hardware to testable functionality
4. Write test cases with:
   - Preconditions
   - Steps
   - Expected results
   - Pass/fail criteria
5. Organize tests by priority/criticality

## Success Criteria

- [ ] Complete list of HITL tests covering GPS functionality
- [ ] Complete list of HITL tests covering battery monitor functionality
- [ ] Each test has clear pass/fail criteria
- [ ] Tests are prioritized by importance
- [ ] Test plan document ready for execution

## Related

- **Branch:** `add-libcanard` (inav firmware)
- **Related Project:** collaborate-dronecan-pr11313 (completed)
- **PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313)
- **Assignment:** `manager/email/sent/2026-02-11-1106-task-hitl-test-plan-libcanard.md`

**Assignee:** Developer | **Assignment Status:** ✉️ Assigned
