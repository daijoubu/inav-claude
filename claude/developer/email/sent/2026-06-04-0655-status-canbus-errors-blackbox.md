# Status Update: CAN Bus Error Stats Blackbox Logging

**Date:** 2026-06-04 06:55
**From:** Developer
**To:** Manager
**Re:** feature-canbus-errors-blackbox

## Current Status

BLOCKED — Unable to start implementation. Project is awaiting upstream dependency merge.

## Blocker Details

PR #11560 (DroneCAN ISR-driven TX for F7) must merge into `maintenance-10.x` before this project can proceed. This PR adds critical infrastructure:

- Extended `canardProtocolStatus_t` struct with `tec`, `rec`, `lec`, and `tx_dropped` fields
- New `dronecan` CLI command exposing live CAN bus error data
- Foundation for all subsequent CAN error logging work

## Implementation Plan Status

Complete and documented in `claude/projects/active/feature-canbus-errors-blackbox/PLAN.md`. Ready to execute immediately once #11560 merges.

## Known Deferral

H7 driver population of `tec`/`rec`/`lec` fields is deferred within PR #11560 itself. Once #11560 merges, we can implement logging against it. H7 platforms will report zeros for these fields until a follow-on driver fix arrives. This does not block F7 implementation.

## Next Steps

1. Monitor PR #11560 merge status
2. Once merged to `maintenance-10.x`, rebase feature branch and begin implementation
3. INDEX.md entry for #11560 will automatically trigger both h7-dronecan-driver rebase and canbus-errors-blackbox branch creation

## Estimated Unblock Date

Dependent on PR #11560 merge timeline

---
**Developer**
