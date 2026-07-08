# Task Assignment: HITL Tests for add-libcanard on MATEKH743

**Date:** 2026-02-16
**Project:** hitl-tests-add-libcanard-matekh743
**Priority:** HIGH
**Estimated Effort:** 8-12 hours
**Branch:** From maintenance-9.x
**Hardware Target:** MATEKH743

## Task

Execute comprehensive HITL (Hardware-In-The-Loop) tests for the add-libcanard branch running on the MATEKH743 flight controller. This testing is critical before the branch can be merged - we need to validate DroneCAN functionality, performance, and stability with the new libcanard integration.

## Background

The add-libcanard branch integrates a new DroneCAN library implementation. Before this can be merged into maintenance-9.x, we need comprehensive hardware testing to verify:
- All flight functionality works correctly
- DroneCAN node communication is reliable
- No regressions compared to the current implementation
- Performance metrics are acceptable
- The system remains stable under sustained operation

Review these reference projects to understand the context:
- code-review-maintenance-10-vs-libcanard
- hitl-extended-testing (for test execution patterns)

## What to Do

### Phase 1: Build and Environment Setup
1. Checkout add-libcanard branch
2. Build firmware for MATEKH743 target
3. Prepare test environment and hardware

### Phase 2: Basic Functionality (Flight, GPS, Battery, ESC)
1. Test basic flight functionality
2. Verify GPS integration and telemetry
3. Test battery monitoring
4. Verify ESC communication

### Phase 3: DroneCAN Features (NodeStatus, Stats, Errors, Multi-node)
1. Test DroneCAN node discovery and messaging
2. Verify NodeStatus messages
3. Test transport statistics collection
4. Test error condition handling
5. Test multi-node scenarios

### Phase 4: Performance and Stability (60-min run, Metrics Collection)
1. Capture CPU usage metrics
2. Monitor memory usage
3. Track DroneCAN throughput
4. Execute 60-minute stability run
5. Collect and document all performance data

### Phase 5: Documentation and Reporting
1. Document all test results
2. Note any issues found or observations
3. Create TEST-RESULTS.md in project directory
4. Send completion report to manager

## Success Criteria

- [ ] All HITL tests pass without hardfaults
- [ ] DroneCAN functionality verified working correctly
- [ ] 60-minute stability run completes successfully
- [ ] Performance metrics (CPU, memory, throughput) captured and acceptable
- [ ] No regressions compared to current implementation
- [ ] All issues/observations documented in TEST-RESULTS.md
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/hitl-tests-add-libcanard-matekh743/`

---
**Manager**
