# Task Assignment: HITL Test Plan for add-libcanard Branch

**Date:** 2026-02-11 11:06
**From:** Manager
**To:** Developer
**Project:** hitl-test-plan-libcanard
**Priority:** HIGH
**Estimated Effort:** 2-4 hours

## Task

Develop a comprehensive list of Hardware-In-The-Loop (HITL) tests to validate the DroneCAN/libcanard implementation on the `add-libcanard` branch of INAV firmware.

## Background

The add-libcanard branch introduces DroneCAN support via the libcanard library. Before merging or deploying to real hardware, we need a structured test plan to validate functionality with actual DroneCAN peripherals.

**Available hardware for testing:**
- DroneCAN GPS module
- DroneCAN Battery monitor

## What to Do

1. Review the add-libcanard branch to understand supported DroneCAN features
2. Identify all DroneCAN message types implemented
3. Create test cases for GPS functionality (discovery, position, velocity, fix quality, failover)
4. Create test cases for battery monitor (discovery, voltage, current, capacity tracking)
5. Create integration tests (multi-device, error handling, hot-plug, stability)
6. Document each test with clear pass/fail criteria
7. Prioritize tests by criticality

## Success Criteria

- [ ] Complete list of HITL tests covering GPS functionality
- [ ] Complete list of HITL tests covering battery monitor functionality
- [ ] Each test has clear pass/fail criteria
- [ ] Tests are prioritized by importance
- [ ] Test plan document ready for execution

## Recommended Workflow

1. Use inav-architecture agent to locate DroneCAN code in the branch
2. Use Grep to find message handlers and supported UAVCAN data types
3. Create test plan document in the project directory

## Project Directory

`claude/projects/active/hitl-test-plan-libcanard/`

## Related References

- PR #11313
- Completed project: collaborate-dronecan-pr11313

---
**Manager**
