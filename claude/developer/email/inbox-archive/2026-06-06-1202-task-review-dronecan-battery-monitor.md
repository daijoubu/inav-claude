# Task Assignment: Review DroneCAN Battery Monitor — Node Health, Device Associations & Field Coverage

**Date:** 2026-06-06 12:02
**From:** Manager
**To:** Developer
**Project:** review-dronecan-battery-monitor
**Priority:** MEDIUM
**Estimated Effort:** 3-5 hours

## Task

Review the existing DroneCAN battery monitor for correct node health monitoring and device association usage. Additionally audit what fields from the uavcan.equipment.power.BatteryInfo message we are not currently tracking, and evaluate whether charging current should be displayed.

## Background

Battery monitoring is safety-relevant — stale data from a failed node could mask a real battery problem. Beyond the correctness issues, the BatteryInfo message is richer than what we likely expose today (capacity, state of charge, status flags, charging current, etc.) and it's worth assessing what would be useful to pilots.

## What to Do

1. Locate the DroneCAN battery monitor driver source
2. Check node health monitoring — is battery data invalidated when a node goes OFFLINE or ERROR?
3. Check device association usage — is data correctly tied to the originating node ID?
4. Audit all fields in uavcan.equipment.power.BatteryInfo — list what we use vs what we ignore
5. Evaluate charging current specifically: is it available from the message? Should it be shown on OSD, sent via MSP telemetry, or both?
6. Make a recommendation on which additional fields are worth adding
7. Implement agreed fixes and enhancements
8. Verify full build matrix (F4/F7/H7/AT32/SITL)

## Success Criteria

- [ ] Node health monitored; battery data invalidated if node goes offline or enters ERROR state
- [ ] Device associations used correctly
- [ ] All BatteryInfo fields assessed; recommendation made on which to add
- [ ] Charging current decision made and implemented if agreed
- [ ] Full build matrix passes

## Project Directory

`claude/projects/active/review-dronecan-battery-monitor/`

## Notes

For the field coverage question, focus on what's practically useful — don't add fields just because they exist. State of charge percentage and charging current are the most likely candidates worth discussing. If fixes require a new branch, use `maintenance-10.x` as the base.

---
**Manager**
