# Task Completed: Investigate DroneCAN Messages Roadmap

**Date:** 2026-02-15 10:00 | **From:** Developer | **To:** Manager | **Status:** COMPLETED

## Summary

Investigation of the DroneCAN message catalog is complete. Surveyed available message types, identified 7 currently supported by INAV, and produced a prioritized roadmap for future implementation.

## Key Findings

- **Currently Supported:** 7 messages (NodeStatus, GetNodeInfo, GNSS Fix/Fix2/Auxiliary/RTCMStream, BatteryInfo)
- **BatteryInfo Status:** Partially implemented - voltage/current OK, SOC missing
- **Recommended Priorities:**
  1. BatteryInfo SOC (1-2 hours) - Quick win
  2. Dynamic Node Allocation (8-12 hours) - Usability improvement
  3. ESC Status (8-12 hours) - Popular BLHeli_32 feature

## Deliverables

- [x] Survey DroneCAN message specification documentation
- [x] Identify messages already implemented in INAV
- [x] List candidate messages for future implementation
- [x] Prioritize based on: user demand, implementation complexity, feature completeness
- [x] Provide effort estimates
- [x] Document findings in FINDINGS.md

## Project Location

**Directory:** `/home/robs/Projects/inav-claude/claude/projects/active/investigate-dronecan-messages-roadmap/`
**Findings File:** `FINDINGS.md`

## Branch

**Base Branch:** `maintenance-9.x`

## Changes

- Created comprehensive FINDINGS.md documenting:
  - Current INAV DroneCAN implementation (7 messages)
  - Survey of ~80+ available DSDL message types
  - Priority rankings (HIGH/MEDIUM/LOW)
  - Implementation order recommendations
  - Effort estimates for each feature

## Testing

- [x] Code survey complete
- [x] DSDL directory analyzed
- [x] Findings documented

---
**Developer**
