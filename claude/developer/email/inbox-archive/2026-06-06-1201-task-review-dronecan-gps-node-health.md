# Task Assignment: Review DroneCAN GPS — Node Health & Device Associations

**Date:** 2026-06-06
**From:** Manager
**To:** Developer
**Project:** review-dronecan-gps-node-health
**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours

## Task

Review the existing DroneCAN GPS driver to ensure it correctly monitors node health and uses device associations properly. Fix any deficiencies found.

## Background

We want to make sure that if a DroneCAN GPS node goes offline or enters a warning/error health state, the firmware stops using its data. We also want to confirm that in multi-GPS setups, data is correctly tied to the originating node. This is a safety concern — stale GPS data from a failed node could cause navigation issues.

## What to Do

1. Locate the DroneCAN GPS driver source
2. Check whether NodeStatus health is consumed — does GPS data get invalidated when a node goes OFFLINE or into ERROR/WARNING state?
3. Check device association usage — is GPS data correctly tied to a specific node ID, not mixed with other nodes?
4. Compare against other DroneCAN sensor drivers (barometer, airspeed, etc.) for consistency
5. Fix any deficiencies found
6. Verify full build matrix (F4/F7/H7/AT32/SITL)

## Success Criteria

- [ ] Node health monitored; GPS data invalidated if node goes offline or enters ERROR state
- [ ] Device associations used correctly
- [ ] Behaviour consistent with other DroneCAN sensor drivers
- [ ] Full build matrix passes

## Project Directory

`claude/projects/active/review-dronecan-gps-node-health/`

## Notes

Report findings even if no code changes are needed — "no issues found" is a valid outcome. If issues are found, fix them on `maintenance-10.x` base branch.

---
**Manager**
