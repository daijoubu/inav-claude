# Task Completed: Investigate DroneCAN Battery SOC

**Date:** 2026-02-14 21:06 | **From:** Developer | **To:** Manager | **Status:** COMPLETED

## Summary

Investigation complete. **DroneCAN BatteryInfo already contains SOC data that INAV ignores.**

## Key Findings

1. **BatteryInfo message has rich SOC data:**
   - `state_of_charge_pct` - Direct SOC percentage (0-100%)
   - `remaining_capacity_wh` - Remaining energy in Wh
   - `full_charge_capacity_wh` - Full capacity in Wh
   - `state_of_health_pct` - Battery health %

2. **Current implementation only extracts voltage/current** - All SOC fields ignored

3. **Implementation is straightforward:**
   - Add new setting `battery_capacity_source` (ADC/CAN)
   - Extract SOC fields in battery_sensor_dronecan.c
   - Modify battery.c to use DroneCAN SOC when configured
   - **Estimated effort: 3-5 hours**

## Recommendation

Create implementation task following the pattern of existing `vbat_meter_type` and `current_meter_type` settings.

## Deliverables

- **FINDINGS.md** - Full technical analysis and implementation plan

## Project Directory

`claude/projects/active/investigate-dronecan-battery-soc/`

---
**Developer**
