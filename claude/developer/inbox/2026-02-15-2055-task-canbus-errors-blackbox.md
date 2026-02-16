# Task Assignment: CAN Bus Error Tracking in Blackbox

**Date:** 2026-02-15 20:55 | **From:** Manager | **To:** Developer | **Priority:** MEDIUM-HIGH
**Project:** feature-canbus-errors-blackbox
**Estimated Effort:** 4-5 hours

## Task

Implement CAN bus error tracking in Blackbox logs, including Tx/Rx error counts and CAN controller state transitions (ERROR_ACTIVE, ERROR_PASSIVE, BUS_OFF).

## Background

When troubleshooting CAN bus issues, it's valuable to have historical data of CAN bus errors logged in Blackbox. Currently, CAN bus errors are not logged, making it difficult to diagnose intermittent CAN bus problems from Blackbox logs.

## What to Do

**Phase 1: Research CAN Driver (0.5 hours)**
1. Find CAN peripheral driver code in firmware
2. Identify error flag registers and CAN state machine
3. Understand how errors are currently tracked

**Phase 2: Add Error Tracking (1.5 hours)**
1. Create error counters structure for Tx/Rx errors
2. Implement error detection (poll or interrupt-based)
3. Track state transitions (ERROR_ACTIVE → ERROR_PASSIVE → BUS_OFF)
4. Ensure efficient error counting without performance impact

**Phase 3: Add Blackbox Logging (1.5 hours)**
1. Add field definitions to Blackbox schema
2. Implement logging in blackbox.c (log changes or at intervals)
3. Test logging output with different error scenarios
4. Verify backwards compatibility (works without Blackbox)

**Phase 4: Testing (0.5 hours)**
1. Test error counting with simulated CAN errors
2. Verify state transitions are logged correctly
3. Check Blackbox file format compatibility
4. Test with and without Blackbox enabled

## Success Criteria

- [ ] Tx and Rx error counts tracked correctly
- [ ] CAN controller state tracked (ERROR_ACTIVE, ERROR_PASSIVE, BUS_OFF)
- [ ] State transitions logged in Blackbox
- [ ] Backwards compatible (works without Blackbox)
- [ ] Efficient implementation (minimal performance impact)
- [ ] Tested with various CAN error scenarios

## Project Directory

`claude/projects/active/feature-canbus-errors-blackbox/`

**Files:**
- `summary.md` - Project overview, scope, methodology
- `todo.md` - Detailed task breakdown by phase

## References

**Related Projects:**
- **dronecan-driver-docs:** Related documentation
- **PR #11313:** DroneCAN implementation

**Code Locations:**
- CAN driver code (to be identified in Phase 1)
- Blackbox logging implementation (blackbox.c)

## Implementation Notes

- Use existing CAN driver infrastructure where possible
- Log errors efficiently to avoid performance impact
- Ensure state transitions are clearly logged for analysis
- Maintain backwards compatibility for users without Blackbox

---

**Manager**