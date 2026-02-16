# Project: Investigate DroneCAN Battery State of Charge Integration

**Status:** ✅ COMPLETED
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-02-14
**Completed:** 2026-02-14
**Estimated Effort:** 2-3 hours
**Actual Effort:** ~30 min

## Overview

Investigate adding support in INAV for using energy consumption and battery State of Charge (SOC) measurements reported by DroneCAN battery devices instead of (or in addition to) calculating these values from current sensor data.

## Background

Currently, INAV calculates battery remaining capacity by integrating current over time. However, many DroneCAN battery monitors (e.g., AFELO, Mauch, etc.) can report their own energy consumption and SOC values based on:
- Battery fuel gauge ICs
- coulomb counters
- battery management system (BMS) data

This feature would allow users to:
- Use more accurate SOC from smart batteries
- Configure which method to use (current sensor integration vs DroneCAN reported)
- Have a fallback option if one method fails

## Investigation Goals

### 1. Understand Available DroneCAN Messages
- What battery-related messages exist in DSDL?
- What fields are available for energy consumption and SOC?
- Which devices support these messages?

### 2. Analyze Current Battery Implementation
- How does INAV currently handle battery remaining calculation?
- What is the battery_sensor_dronecan.c structure?
- How are current/voltage readings processed?

### 3. Determine Implementation Requirements
- How to integrate SOC from DroneCAN
- What new settings/configuration needed
- How to handle the user-selectable method (configurable)
- What UI changes (if any) are needed

### 4. Create Implementation Plan
- Architecture design
- File changes needed
- Settings configuration
- Testing strategy

## Research Areas

- **DroneCAN DSDL:** Battery-related messages (BatteryInfo, etc.)
- **INAV Code:** battery_sensor_dronecan.c, battery.c
- **Existing Sensors:** How current integration works
- **User Settings:** Existing battery configuration

## Integration Options (User Configurable)

Users should be able to configure which method to use:
1. **Current Sensor** - Calculate from current integration (current behavior)
2. **DroneCAN Reported** - Use values directly from DroneCAN device
3. **Primary + Fallback** - Use DroneCAN, fall back to current sensor if unavailable

## Deliverables

A comprehensive investigation report containing:

1. **Executive Summary** - What SOC messages are available and benefits
2. **Technical Analysis** - DSDL messages, fields, device support
3. **Current State** - How battery calculation currently works
4. **Implementation Plan** - Architecture, settings, integration approach
5. **Risk Assessment** - Potential issues and mitigations

## Related

- **PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313)
- **DSDL-GUIDE.md:** `completed/dsdlc-submodule-generation/DSDL-GUIDE.md`
- **Previous Battery Work:** battery_sensor_dronecan.c

## Success Criteria

- [ ] Identify DroneCAN messages with SOC/energy data
- [ ] Understand current battery calculation in INAV
- [ ] Determine integration approach (user-configurable)
- [ ] Create implementation plan with specific steps
- [ ] Estimate effort and timeline
- [ ] Identify potential issues
