# Task Assignment: Complete DroneCAN HITL GPS Tests

**Date:** 2026-02-14 08:07
**From:** Manager
**To:** Developer
**Project:** dronecan-hitl-gps-tests
**Priority:** HIGH
**Estimated Effort:** 4-6 hours

## Task

Execute the DroneCAN GPS tests in HITL (Hardware-In-The-Loop) simulation that were previously skipped due to no DroneCAN GPS hardware being available. Now that you have a GPS module, complete all applicable tests.

## Background

Previous HITL test project was completed on 2026-02-11 with 13 PASS, 0 FAIL, 16 SKIP. Most tests were skipped due to no DroneCAN GPS hardware. With the GPS module now available, we need to execute those skipped tests.

**Reference:** Previous test results at `completed/hitl-test-execution-dronecan/TEST-RESULTS.md`

**Base branch:** `maintenance-9.x` (INAV firmware)

## What to Do

### Phase 1: Basic Validation
- TEST-GPS-001: GPS Device Discovery
- TEST-GPS-002: Position Data Reception

### Phase 2: Functional Testing
- TEST-GPS-003: Velocity Data Reception
- TEST-GPS-004: Fix Quality Reporting
- TEST-INT-001: GPS + Battery Simultaneous

### Phase 3: Robustness Testing
- TEST-GPS-006: GPS Loss and Recovery
- TEST-INT-004: Hot Plug - GPS

### Phase 4: Stress Testing
- TEST-GPS-005: GPS Fix2 Message Support
- TEST-GPS-007: GPS Data Update Rate

## Success Criteria

- [ ] All GPS device discovery tests pass
- [ ] All position/velocity data reception tests pass
- [ ] All fix quality tests pass
- [ ] GPS + Battery simultaneous operation works
- [ ] GPS loss and recovery works
- [ ] Hot-plug GPS works
- [ ] GPS update rate meets requirements
- [ ] Update TEST-RESULTS.md with new results
- [ ] No new issues found (or documented if found)

## Project Directory

`claude/projects/active/dronecan-hitl-gps-tests/`

---
**Manager**
