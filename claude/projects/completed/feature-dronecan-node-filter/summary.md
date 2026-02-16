# Project: DroneCAN Node ID Filter for Sensors

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-02-14
**Estimated Effort:** 4-6 hours

## Overview

Add the ability for INAV to filter DroneCAN sensor messages by source Node ID, allowing users to select which specific sensor node to use when multiple instances of the same sensor type exist on the DroneCAN network.

## Problem

When multiple identical sensors (e.g., two batteries with Battery.smart.ai) are connected to the same DroneCAN bus, INAV currently has no way to specify which specific node should be used. This leads to:
- Ambiguous sensor data selection
- Inability to use a specific battery sensor when multiple are present
- Users cannot configure which node provides the primary data

## Objectives

1. Add Node ID filtering capability to DroneCAN sensor drivers
   - Battery sensor (Battery.smart.ai)
   - GPS sensor
   - Barometer sensor
   - Other sensor types as applicable

2. Add configuration settings for Node ID filtering
   - Allow users to specify which Node ID to use for each sensor type
   - Setting of 0 or "auto" means use any available node (current behavior)

3. Implement filtering logic in sensor drivers
   - Filter incoming messages by source Node ID when configured

## Scope

**In Scope:**
- Modify DroneCAN sensor drivers to support Node ID filtering
- Add CLI settings for Node ID configuration
- Battery sensor driver (primary use case)
- GPS and barometer if applicable

**Out of Scope:**
- UAVCAN/DroneCAN protocol specification changes
- GUI configurator changes (CLI only)
- Multiple node selection (single node only)

## Implementation Steps

1. Research current DroneCAN sensor driver architecture
   - battery_sensor_dronecan.c
   - Other sensor drivers

2. Design configuration approach
   - Add settings like `dronecan_battery_node_id`, `dronecan_gps_node_id`

3. Implement Node ID filtering
   - Add nodeId field check in message handlers
   - Only process messages from specified node when configured

4. Test the implementation

## Success Criteria

- [ ] User can configure specific Node ID for battery sensor
- [ ] User can configure specific Node ID for other sensors
- [ ] Setting 0 or "auto" uses any available node (backwards compatible)
- [ ] Filtered messages are ignored when Node ID is configured

## Related

- **investigate-dronecan-dna:** Related investigation project
- **PR #11313:** DroneCAN implementation
