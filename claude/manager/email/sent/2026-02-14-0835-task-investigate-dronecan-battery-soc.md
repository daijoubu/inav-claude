# Task Assignment: Investigate DroneCAN Battery SOC Integration

**Date:** 2026-02-14 08:35
**From:** Manager
**To:** Developer
**Project:** investigate-dronecan-battery-soc
**Priority:** MEDIUM
**Estimated Effort:** 8-12 hours

## Task

Investigate adding support for using energy consumption and battery State of Charge (SOC) measurements reported by DroneCAN battery devices instead of calculating from current sensor. Users should configure which method to use.

## Background

Users with DroneCAN battery devices want to use the SOC/energy data reported directly from the battery management system rather than calculating consumption from current sensor readings. This can provide more accurate fuel gauge functionality.

## What to Do

1. **Phase 1: Research DroneCAN Battery Messages**
   - Identify battery-related DroneCAN messages in DSDL
   - Check for SOC/remaining_capacity fields
   - Look for energy consumption fields (Wh consumed)
   - Document which devices support SOC reporting

2. **Phase 2: Analyze Current Battery Implementation**
   - Review battery_sensor_dronecan.c
   - Review battery.c - general battery handling
   - Understand how current integration works
   - How mAh consumption is calculated

3. **Phase 3: Determine Implementation Requirements**
   - How to integrate SOC from DroneCAN
   - Design user configuration (Current Sensor / DroneCAN / Fallback)
   - What settings needed
   - Edge cases (unavailable data, out of range)

4. **Phase 4: Create Implementation Plan**
   - Architecture design
   - Step-by-step implementation approach
   - Timeline estimate

5. **Phase 5: Document Findings**
   - Write investigation report with executive summary, technical analysis, implementation plan, risk assessment

## Success Criteria

- [ ] Identify DroneCAN messages with SOC/energy data
- [ ] Understand current battery calculation in INAV
- [ ] Determine integration approach (user-configurable)
- [ ] Create implementation plan with specific steps
- [ ] Estimate effort and timeline
- [ ] Identify potential issues

## Project Directory

`claude/projects/active/investigate-dronecan-battery-soc/`

## Base Branch

`maintenance-9.x`

---
**Manager**
