# Task Assignment: Investigate NodeStatus Content

**Date:** 2026-02-14 21:00 | **From:** Manager | **To:** Developer | **Priority:** MEDIUM

## Task
Investigate what INAV status should be reported in DroneCAN NodeStatus message. Map INAV states to the NodeStatus fields:
- **health** - Flight controller health status
- **mode** - Current flight mode
- **vendor_specific_status** - Custom vendor-specific status field

## Project
investigate-dronecan-nodestatus-content

## Base Branch
maintenance-9.x

## Background
The DroneCAN protocol defines a NodeStatus message that contains health, mode, and vendor_specific_status fields. We need to determine how INAV's internal state (arming status, flight modes, error conditions, etc.) should map to these fields for proper DroneCAN integration.

## Required Investigation
1. Review DroneCAN NodeStatus specification (uavcan.node.Status)
2. Identify INAV's internal state representations:
   - Flight modes (MANUAL, AUTO, etc.)
   - Arming states (DISARMED, ARMED, ARMING_FAIL)
   - Health/error states (OK, WARNING, CRITICAL, etc.)
3. Create a mapping proposal:
   - Which INAV states map to health values (0=OK, 1=WARNING, 2=ERROR, 3=CRITICAL)
   - Which INAV modes map to DroneCAN mode values
   - What information to encode in vendor_specific_status
4. Document any existing implementation if NodeStatus is already partially implemented

## Success Criteria
- [ ] Document DroneCAN NodeStatus field meanings and valid values
- [ ] List all relevant INAV internal states that should be exposed
- [ ] Propose a mapping table from INAV states to NodeStatus fields
- [ ] Note any edge cases or limitations
- [ ] Identify if any code changes would be needed (no implementation, just investigation)

---
**Manager**
