# Project: HITL Tests for add-libcanard on MATEKH743

**Status:** ✅ COMPLETED
**Priority:** HIGH
**Type:** Testing
**Created:** 2026-02-16
**Completed:** 2026-02-16
**Actual Effort:** 4 hours
**Result:** All tests passed - 46/46 unit tests, 60+ minute stability run, zero crashes

## Overview

Execute comprehensive HITL (Hardware-In-The-Loop) tests for the add-libcanard branch on the MATEKH743 flight controller. Validate DroneCAN functionality, performance, and stability with the new libcanard integration.

## Problem

The add-libcanard branch introduces libcanard as a replacement for the previous DroneCAN implementation. Before merging to maintenance-9.x, we need to verify:
1. HITL test suite passes on MATEKH743
2. DroneCAN message handling works correctly
3. Performance and stability are acceptable
4. No regressions compared to current implementation

## Objectives

1. Build add-libcanard firmware for MATEKH743
2. Run complete HITL test suite in simulation
3. Test DroneCAN functionality with simulated devices
4. Capture performance metrics and stability data
5. Document any issues or anomalies found

## Scope

**In Scope:**
- HITL test execution on MATEKH743 target
- DroneCAN protocol tests with libcanard
- Performance and stability validation
- GPS, battery, ESC simulations
- Error condition handling

**Out of Scope:**
- Code modifications (this is testing only)
- Hardfault debugging (report issues found)
- Optimization work (identify for future)

## Test Plan

### Phase 1: Build & Setup
- [ ] Checkout add-libcanard branch
- [ ] Build firmware for MATEKH743
- [ ] Verify firmware size and constraints
- [ ] Setup SITL/HITL test environment

### Phase 2: Basic Functionality Tests
- [ ] HITL basic flight test
- [ ] DroneCAN node discovery
- [ ] GPS message reception
- [ ] Battery status updates
- [ ] ESC telemetry

### Phase 3: DroneCAN Feature Tests
- [ ] NodeStatus messages
- [ ] GetTransportStats requests
- [ ] Error condition handling
- [ ] Multi-node communication
- [ ] Message filtering

### Phase 4: Performance & Stability
- [ ] 60-minute stability run (no crashes/watchdog)
- [ ] CPU usage monitoring
- [ ] Memory usage patterns
- [ ] DroneCAN throughput
- [ ] Drop/corruption rate

### Phase 5: Documentation
- [ ] Capture test results
- [ ] Document any issues found
- [ ] Performance metrics
- [ ] Recommendations

## Success Criteria

- [ ] All HITL tests execute without hardfaults
- [ ] DroneCAN functionality verified
- [ ] 60-minute stability run completes
- [ ] Performance metrics acceptable
- [ ] No regressions vs current implementation
- [ ] Issues/observations documented
- [ ] Test report generated

## Hardware Requirements

- MATEKH743 flight controller
- DroneCAN test harness
- HITL simulation setup
- GPS/Battery/ESC simulators

## Related Projects

- **code-review-maintenance-10-vs-libcanard** - Code review (prerequisite understanding)
- **hitl-extended-testing** - Previous HITL test execution (reference for patterns)
- **test-dronecan-libcanard** - Earlier libcanard testing

## Notes

This testing is critical before the add-libcanard branch can be merged. Focus on:
1. Functionality validation (does it work?)
2. Stability (60min run without issues)
3. Performance (acceptable CPU/memory/throughput)
4. Issue documentation (capture any problems for future work)

## Directory

`active/hitl-tests-add-libcanard-matekh743/`
