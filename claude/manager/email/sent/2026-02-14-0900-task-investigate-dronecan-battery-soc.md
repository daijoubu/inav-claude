# Task Assignment: Investigate DroneCAN Battery State of Charge Integration

**Date:** 2026-02-14 09:00
**From:** Manager
**To:** Developer
**Project:** investigate-dronecan-battery-soc
**Priority:** MEDIUM
**Estimated Effort:** 2-3 weeks

## Task

Investigate adding support for using battery State of Charge (SOC) and energy consumption measurements reported by DroneCAN battery devices instead of calculating from current sensor. Currently INAV calculates battery remaining by integrating current over time, but many DroneCAN battery monitors report their own SOC values from fuel gauge ICs or BMS.

The user wants a user-configurable option to choose which method to use.

## Background

Many modern battery monitors (e.g., WiseFing, CUAV, JTT) have built-in fuel gauge ICs or Battery Management Systems (BMS) that calculate SOC internally with much higher accuracy than current integration. These devices report SOC via DroneCAN messages. This investigation will determine how to integrate this data into INAV.

## What to Do

### Phase 1: Research DroneCAN Battery Messages
- Identify battery-related messages in DSDL (BatteryInfo, etc.)
- Check for SOC/remaining_capacity fields
- Look for energy consumption fields (Wh consumed)
- Document which devices support SOC reporting

### Phase 2: Analyze Current Battery Implementation
- Review battery_sensor_dronecan.c
- Review battery.c - how current integration works
- Understand how mAh consumption is calculated

### Phase 3: Determine Implementation Requirements
- How to integrate SOC from DroneCAN
- Design user configuration (Current Sensor / DroneCAN Reported / Primary + Fallback)
- What new settings needed

### Phase 4: Create Implementation Plan
- Architecture design
- File changes needed
- Settings configuration

### Phase 5: Document Findings
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

`maintenance-9.x` (INAV firmware)

---
**Manager**
