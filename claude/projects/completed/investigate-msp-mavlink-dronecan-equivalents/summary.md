# Project: MSP/Mavlink vs DroneCAN NodeStatus Field Equivalents

**Status:** ✅ COMPLETED
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-02-16
**Completed:** 2026-02-16
**Actual Effort:** 8 hours
**Estimated Effort:** 6-8 hours

## Overview

Investigate whether MSP (MultiWii Serial Protocol) and Mavlink have equivalent fields to the DroneCAN NodeStatus message. Identify which INAV endpoints populate these fields and compare implementation approaches with Ardupilot.

## Key Finding

✅ **All three protocols (DroneCAN, MSP, Mavlink) can fully represent node status information.** INAV provides comprehensive status data equivalent or superior to Ardupilot, with lossless bi-directional translation possible between all protocols.

**Deliverables:**
- 37 pages of detailed analysis across 4 comprehensive phase reports
- Complete field mapping showing DroneCAN ↔ MSP ↔ Mavlink equivalents
- 5 prioritized recommendations for implementation (total effort: 12-22 hours)
- Protocol efficiency analysis and gap documentation

**Completion Report:** `2026-02-16-1430-completed-investigate-msp-mavlink-dronecan-equivalents.md`

## Problem

To improve telemetry and monitoring capabilities, we need to understand:
1. What node status information is available across different protocols (MSP, Mavlink, DroneCAN)
2. How INAV currently exposes node status information via MSP and Mavlink
3. What gaps exist compared to DroneCAN's comprehensive NodeStatus message
4. How Ardupilot handles equivalent functionality for reference/comparison

## Research Questions

1. **DroneCAN NodeStatus:** What fields does the standard DroneCAN NodeStatus message contain?
2. **MSP Equivalents:** Are there MSP messages that carry node health/status data? Which ones?
3. **Mavlink Equivalents:** What Mavlink messages correspond to DroneCAN NodeStatus?
4. **INAV Population:** How does INAV populate these fields? (CPU usage, memory, error counts, etc.)
5. **Ardupilot Comparison:** How does Ardupilot handle the same information?
6. **Gaps:** What DroneCAN NodeStatus fields are NOT exposed via MSP/Mavlink in INAV?

## Scope

**In Scope:**
- DroneCAN NodeStatus message specification
- MSP message definitions related to node/system status
- Mavlink message definitions for equivalent information
- INAV source code: how these fields are populated
- Ardupilot implementation for reference
- Comparison analysis and gap identification

**Out of Scope:**
- Implementation of new features (this is research only)
- Modifying INAV code
- Modifying Ardupilot code

## Implementation

### Phase 1: Understanding DroneCAN NodeStatus
- [ ] Locate DroneCAN NodeStatus specification
- [ ] Document all fields in NodeStatus message
- [ ] Understand purpose of each field
- [ ] Note which are mandatory vs optional

### Phase 2: MSP Protocol Research
- [ ] Find MSP message specifications/definitions
- [ ] Identify messages related to system health/status
- [ ] Map MSP messages to DroneCAN NodeStatus fields
- [ ] Check INAV source for MSP handlers

### Phase 3: Mavlink Protocol Research
- [ ] Find Mavlink message specifications
- [ ] Identify messages for node/system status
- [ ] Map Mavlink messages to DroneCAN NodeStatus fields
- [ ] Check INAV source for Mavlink population

### Phase 4: INAV Implementation Analysis
- [ ] Locate relevant INAV source code
- [ ] Identify how each field is computed/populated
- [ ] Document data sources (CPU timing, memory, errors, etc.)
- [ ] Note any limitations or approximations

### Phase 5: Ardupilot Comparison
- [ ] Research Ardupilot's approach to node status
- [ ] Compare field coverage vs INAV
- [ ] Document differences in computation/aggregation
- [ ] Identify best practices

### Phase 6: Synthesis and Report
- [ ] Create comparison matrix (DroneCAN ↔ MSP ↔ Mavlink)
- [ ] Document gaps and recommendations
- [ ] Write comprehensive investigation report
- [ ] Provide suggestions for future enhancements

## Success Criteria

- [ ] Complete comparison matrix showing DroneCAN/MSP/Mavlink field equivalents
- [ ] INAV source code locations identified for each field
- [ ] Documentation of how each field is populated in INAV
- [ ] Ardupilot comparison completed
- [ ] Gap analysis identifying missing fields/features
- [ ] Comprehensive investigation report written
- [ ] Recommendations for future improvements documented

## Research Resources

**Key Files to Investigate:**
- INAV firmware: `src/main/drivers/dronecan.c`, `src/main/drivers/dronecan.h`
- INAV firmware: MSP protocol handlers
- INAV firmware: Mavlink integration
- DroneCAN specification documents
- Ardupilot equivalent implementations

**External Resources:**
- DroneCAN specification: http://uavcan.org/
- Mavlink protocol specification: https://mavlink.io/
- MSP protocol documentation (in INAV codebase)
- Ardupilot GitHub repository

## Notes

- Focus on understanding current capabilities, not implementing changes
- Document findings clearly for future development decisions
- Consider scalability and extensibility in analysis
- Note any protocol limitations or constraints discovered

## Related

- **Directory:** `active/investigate-msp-mavlink-dronecan-equivalents/`
- **Related Projects:** feature-dronecan-node-stats, feature-canbus-errors-blackbox
