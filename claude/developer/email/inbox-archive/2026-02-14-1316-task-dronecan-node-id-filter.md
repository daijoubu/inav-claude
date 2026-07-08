# Task Assignment: DroneCAN Node ID Filter for Sensors

**Date:** 2026-02-14 13:16
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-node-filter
**Priority:** MEDIUM
**Estimated Effort:** 8-12 hours

## Task

Add the ability for INAV to filter DroneCAN sensor messages by source Node ID, allowing users to select which specific sensor node to use when multiple instances of the same sensor type exist on the DroneCAN network (e.g., two batteries).

## Background

When multiple identical sensors (e.g., two batteries with Battery.smart.ai) are connected to the same DroneCAN bus, INAV currently has no way to specify which specific node should be used. This feature adds Node ID filtering capability to ensure users can select the correct sensor.

## What to Do

1. **Review battery_sensor_dronecan.c driver** - Identify message callback structure and how sensor data is processed

2. **Add settings** - Create new settings like:
   - `dronecan_battery_node_id` - Filter for battery sensor messages
   - `dronecan_gps_node_id` - Filter for GPS sensor messages
   - Consider other sensors (baro, etc.)

3. **Implement filtering logic** - In the message callbacks:
   - Check if a specific Node ID is configured
   - Only process messages from that node when configured
   - Setting of 0 or "auto" means use any available node (current behavior, backwards compatible)

4. **Test compilation** - Ensure the code compiles without errors

## Success Criteria

- [ ] User can configure specific Node ID for battery sensor
- [ ] User can configure specific Node ID for other sensors (GPS, baro)
- [ ] Setting 0 uses any available node (backwards compatible)
- [ ] Filtered messages are ignored when Node ID is configured
- [ ] Code compiles successfully

## Project Directory

`claude/projects/active/feature-dronecan-node-filter/`

## Branch

Use `maintenance-9.x` as base branch for INAV firmware

---
**Manager**
