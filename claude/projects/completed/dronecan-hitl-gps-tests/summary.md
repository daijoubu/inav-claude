# Project: Complete DroneCAN HITL GPS Tests

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Testing
**Created:** 2026-02-14
**Estimated Effort:** 2-3 hours

## Overview

Execute the previously skipped DroneCAN GPS-related HITL tests now that the tester has a DroneCAN GPS module. These tests were skipped in the previous HITL test session due to lack of hardware.

## Background

Previous HITL test project (`hitl-test-execution-dronecan`) was completed on 2026-02-11 with:
- 13 PASS, 0 FAIL, 16 SKIP
- 16 tests were skipped due to no DroneCAN GPS hardware

Now that a DroneCAN GPS module is available, we can complete the GPS-related tests.

## Tests to Execute

### Phase 1: Basic Validation
- [ ] TEST-GPS-001: GPS Device Discovery
- [ ] TEST-GPS-002: Position Data Reception

### Phase 2: Functional Testing
- [ ] TEST-GPS-003: Velocity Data Reception
- [ ] TEST-GPS-004: Fix Quality Reporting
- [ ] TEST-INT-001: GPS + Battery Simultaneous

### Phase 3: Robustness Testing
- [ ] TEST-GPS-006: GPS Loss and Recovery
- [ ] TEST-INT-004: Hot Plug - GPS

### Phase 4: Stress Testing
- [ ] TEST-GPS-005: GPS Fix2 Message Support
- [x] TEST-GPS-007: GPS Data Update Rate

## Related

- **Previous Test Results:** `completed/hitl-test-execution-dronecan/TEST-RESULTS.md`
- **Test Plan:** `completed/hitl-test-plan-libcanard/HITL-TEST-PLAN.md`
- **PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313)

## Success Criteria

- [x] All GPS device discovery tests pass
- [x] All position/velocity data reception tests pass
- [x] All fix quality tests pass
- [x] GPS + Battery simultaneous operation works
- [x] GPS loss and recovery works
- [x] Hot-plug GPS works
- [x] GPS update rate meets requirements
- [x] Update TEST-RESULTS.md with new results
- [x] No new issues found (or documented if found)
