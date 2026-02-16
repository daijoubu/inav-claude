# Project: CAN Bus Error Tracking in Blackbox

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-02-14
**Estimated Effort:** 4-5 hours

## Overview

Add CAN bus error tracking to Blackbox logs, including Tx/Rx error counts and CAN controller state transitions (ERROR_ACTIVE, ERROR_PASSIVE, BUS_OFF).

## Problem

When troubleshooting CAN bus issues, it's valuable to have historical data of CAN bus errors logged in Blackbox. Currently, CAN bus errors are not logged, making it difficult to diagnose intermittent CAN bus problems from Blackbox logs.

## Objectives

1. Track CAN bus error statistics
   - Tx error count
   - Rx error count
   - CAN controller state (ERROR_ACTIVE, ERROR_PASSIVE, BUS_OFF)

2. Add Blackbox logging
   - Log CAN error counts and state changes
   - Ensure logging is efficient (only log changes or at reasonable intervals)

3. Make data accessible
   - Data available for analysis in Blackbox viewer
   - Include state transition events

## Scope

**In Scope:**
- STM32 CAN peripheral error tracking
- Blackbox logging integration
- CAN controller state machine

**Out of Scope:**
- Real-time OSD display of CAN errors
- CLI commands for CAN errors (future enhancement)

## Implementation Steps

1. Research CAN driver
   - Find CAN peripheral driver code
   - Identify error flag registers
   - Understand CAN state machine

2. Add error tracking
   - Create error counters structure
   - Poll or interrupt-based error detection
   - Track state transitions

3. Add Blackbox logging
   - Add field definitions
   - Implement logging in blackbox.c
   - Test logging output

4. Test the implementation

## Success Criteria

- [ ] Tx and Rx error counts tracked
- [ ] CAN controller state tracked (ERROR_ACTIVE, ERROR_PASSIVE, BUS_OFF)
- [ ] State transitions logged in Blackbox
- [ ] Backwards compatible (works without Blackbox)

## Related

- **dronecan-driver-docs:** Related documentation
- **PR #11313:** DroneCAN implementation
