# Project: Review DroneCAN Battery Monitor — Node Health, Device Associations & Field Coverage

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Review / Feature Enhancement
**Created:** 2026-06-06
**Estimated Time:** 3-5 hours

## Overview

Review the existing DroneCAN battery monitor implementation for correct node health monitoring and device association usage. Additionally assess what fields from the uavcan.equipment.power.BatteryInfo message are not currently tracked, and whether charging current should be displayed.

## Problem

The DroneCAN battery monitor may not correctly handle node health or device associations. Additionally, the BatteryInfo message contains richer data than we currently expose. Issue #3 (daijoubu/inav) identified that the existing driver only extracts `voltage` and `current`, ignoring all other fields including SOC, capacity, temperature, and status flags.

## Known Field Coverage Gap (from issue #3)

Current driver (`sensors/battery_sensor_dronecan.c`) only uses:
- `voltage` ✅
- `current` ✅

Ignored fields worth evaluating:
- `state_of_charge_pct` — SOC % (0-100) from smart BMS
- `remaining_capacity_wh` — Remaining energy in Wh
- `full_charge_capacity_wh` — Full pack capacity in Wh
- `temperature` — Battery temperature (Kelvin)
- `status_flags` — Pack status/fault flags
- `state_of_health_pct` — Battery health %
- `hours_to_full_charge` — Time to full (charging)
- `average_power_10sec` — Short-term average power draw

Issue #3 proposes a `battery_capacity_source` setting (ADC = current integration, CAN = BMS-reported) using Wh-based SOC with percentage fallback. See daijoubu/inav #3 for full implementation notes.

## Objectives

1. Audit node health monitoring in the DroneCAN battery monitor
2. Audit device association usage
3. Identify unused BatteryInfo fields worth tracking (capacity, state of charge, status flags, etc.)
4. Evaluate whether charging current should be displayed (OSD, telemetry, or both)
5. Implement fixes and any agreed enhancements

## Scope

**In Scope:**
- DroneCAN battery monitor driver (firmware)
- Node health monitoring and device association correctness
- BatteryInfo field coverage audit
- Charging current display consideration (OSD and/or MSP telemetry)
- Consistency with other DroneCAN sensor drivers

**Out of Scope:**
- Non-DroneCAN battery monitoring
- Hardware-specific battery fuel gauge integration

## Success Criteria

- [ ] Node health monitored; battery data invalidated if node goes offline or enters ERROR state
- [ ] Device associations used correctly
- [ ] All BatteryInfo fields assessed; decision made on which to add
- [ ] Charging current display decision made and implemented if agreed
- [ ] Fixes and enhancements build cleanly across full target matrix (F4/F7/H7/AT32/SITL)

## Priority Justification

Battery monitoring is safety-relevant. Stale data from a failed node could mask a real battery problem. Additional field coverage improves situational awareness.
