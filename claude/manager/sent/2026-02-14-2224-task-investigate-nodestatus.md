# Task Assignment: Investigate DroneCAN NodeStatus Content

**From:** Manager
**To:** Developer
**Date:** 2026-02-14
**Priority:** MEDIUM
**Type:** Investigation
**Estimated Effort:** 2-3 hours

---

## Task

Investigate what INAV status information should be reported in the DroneCAN NodeStatus message that INAV broadcasts as a CAN node.

## Background

Every DroneCAN node broadcasts NodeStatus messages containing:
- **uptime_sec** (uint32) - Seconds since boot
- **health** (uint2) - OK=0, WARNING=1, ERROR=2, CRITICAL=3
- **mode** (uint3) - OPERATIONAL=0, INITIALIZATION=1, MAINTENANCE=2, SOFTWARE_UPDATE=3, OFFLINE=7
- **sub_mode** (uint3) - Vendor-specific
- **vendor_specific_status_code** (uint16) - Vendor-specific

Currently INAV may be broadcasting static/default values. We need to determine what meaningful status INAV could report.

## Questions to Answer

1. **What does INAV currently broadcast in NodeStatus?**
   - Find the NodeStatus message construction in dronecan.c
   - Document current values for health, mode, sub_mode, vendor_status

2. **What INAV states could map to NodeStatus health?**
   - Sensor failures → WARNING or ERROR?
   - Arming disabled reasons → WARNING?
   - Failsafe active → CRITICAL?
   - GPS fix status?

3. **What INAV states could map to NodeStatus mode?**
   - Pre-arm checks → INITIALIZATION?
   - Armed and flying → OPERATIONAL?
   - CLI mode → MAINTENANCE?
   - DFU/bootloader → SOFTWARE_UPDATE?

4. **What could vendor_specific_status_code contain?**
   - Flight mode encoded?
   - Arming flags summary?
   - Sensor health bitmask?

## Deliverables

- Document current NodeStatus implementation
- List INAV states that could map to NodeStatus fields
- Recommend what INAV should report
- Create FINDINGS.md in project directory
- Send findings report to Manager

## Project Directory

`claude/projects/active/investigate-dronecan-nodestatus-content/`
