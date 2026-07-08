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

When multiple identical sensors (e.g., two batteries with Battery.smart.ai) are connected to the same DroneCAN bus, INAV currently has no way to specify which specific node should be used. We need to add Node ID filtering capability.

## What to Do

1. Review battery_sensor_dronecan.c driver and identify message callback structure
2. Add settings like `dronecan_battery_node_id`, `dronecan_gps_node_id`
3. Implement filtering logic - only process messages from specified node when configured
4. Setting of 0 or "auto" means use any available node (current behavior, backwards compatible)
5. Test that it compiles

## Success Criteria

- [ ] User can configure specific Node ID for battery sensor
- [ ] User can configure specific Node ID for other sensors (GPS, baro)
- [ ] Setting 0 uses any available node (backwards compatible)
- [ ] Filtered messages are ignored when Node ID is configured

## Project Directory

`claude/projects/active/feature-dronecan-node-filter/`

## Base Branch

Use `maintenance-9.x` as base branch for INAV firmware

---
**Manager**
