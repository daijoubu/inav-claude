# Task Assignment: MSP/Mavlink vs DroneCAN NodeStatus Field Equivalents Investigation

**Date:** 2026-02-16 07:39 | **From:** Manager | **To:** Developer | **Priority:** MEDIUM

## Task
Research and document the relationship between DroneCAN NodeStatus message fields and their equivalents (if any) in MSP and Mavlink protocols. Create a comprehensive comparison matrix and provide recommendations for improvements.

## Background
This investigation will inform decisions about telemetry capabilities and future protocol enhancements. It relates to ongoing projects exploring DroneCAN node statistics and CAN bus error tracking in INAV.

The goal is to understand what node status information is available across these protocols, how INAV populates them, and compare with Ardupilot's approach to identify best practices and gaps.

## Detailed Subtasks

1. **Research DroneCAN NodeStatus** - Study the DroneCAN specification and NodeStatus message structure with all fields documented
2. **Map MSP Equivalents** - Search INAV source code for MSP messages that contain status/health related information
3. **Map Mavlink Equivalents** - Identify relevant Mavlink messages (SYS_STATUS, HEARTBEAT, etc.) and their field mappings
4. **Analyze INAV Implementation** - Locate and review source code showing how these fields are populated
5. **Study Ardupilot Approach** - Research Ardupilot's implementation for comparison and best practices
6. **Create Comparison Matrix** - Document all fields across protocols with field names, data types, and semantics
7. **Gap Analysis** - Identify missing information and capabilities across protocols
8. **Recommendations** - Provide specific suggestions for improvements or enhancements

## Key Resources
- INAV firmware: `src/main/drivers/dronecan.c`, `dronecan.h`
- MSP protocol definitions in INAV codebase
- Mavlink specification and INAV integration
- DroneCAN specification (protocol documentation)
- Ardupilot GitHub repository for comparison
- Project directory: `claude/projects/active/investigate-msp-mavlink-dronecan-equivalents/`

## Success Criteria
- [ ] Comprehensive comparison matrix created (DroneCAN ↔ MSP ↔ Mavlink fields)
- [ ] INAV source code locations identified for each field
- [ ] Documentation of how each field is computed/populated
- [ ] Ardupilot implementation comparison completed
- [ ] Gap analysis documented with specific examples
- [ ] Recommendations provided for improvements or enhancements
- [ ] Deliverables committed to project directory with clear documentation

## Estimated Effort
6-8 hours

---
**Manager**
