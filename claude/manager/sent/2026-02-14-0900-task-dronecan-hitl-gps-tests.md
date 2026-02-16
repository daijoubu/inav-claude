# Task Assignment: Execute DroneCAN HITL GPS Tests

**Date:** 2026-02-14 09:00 | **From:** Manager | **To:** Developer | **Priority:** HIGH

## Task
Execute the previously skipped DroneCAN GPS-related HITL tests now that you have a DroneCAN GPS module available.

## Background
Previous test session on 2026-02-11 had 16 tests skipped due to no GPS hardware. Now you have a DroneCAN GPS module available for testing.

Execute the following tests in order:

**Phase 1: Basic Validation**
- TEST-GPS-001: GPS Device Discovery
- TEST-GPS-002: Position Data Reception

**Phase 2: Functional Testing**
- TEST-GPS-003: Velocity Data Reception
- TEST-GPS-004: Fix Quality Reporting
- TEST-INT-001: GPS + Battery Simultaneous

**Phase 3: Robustness Testing**
- TEST-GPS-006: GPS Loss and Recovery
- TEST-INT-004: Hot Plug - GPS

**Phase 4: Stress Testing**
- TEST-GPS-005: GPS Fix2 Message Support
- TEST-GPS-007: GPS Data Update Rate

## Procedure
1. Use the sitl-operator skill to start SITL
2. Execute each test from the test plan in the project directory
3. Record results in TEST-RESULTS.md
4. Report any issues found

Project directory: `/home/robs/Projects/inav-claude/claude/projects/active/dronecan-hitl-gps-tests/`

Base branch: `maintenance-9.x`

## Success Criteria
- [ ] All GPS device discovery tests pass
- [ ] All position/velocity data reception tests pass
- [ ] All fix quality tests pass
- [ ] GPS + Battery simultaneous operation works
- [ ] GPS loss and recovery works
- [ ] Hot-plug GPS works
- [ ] GPS update rate meets requirements
- [ ] TEST-RESULTS.md updated with results

---
**Manager**
