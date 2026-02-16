# Todo: DroneCAN Node ID Filter for Sensors

## Phase 1: Research

- [ ] Review battery_sensor_dronecan.c driver
- [ ] Identify message callback structure
- [ ] Find how nodeId is passed to handlers

## Phase 2: Design

- [ ] Define setting names (dronecan_battery_node_id, etc.)
- [ ] Determine default values (0 = any)
- [ ] Plan integration with settings.yaml

## Phase 3: Implementation

- [ ] Add settings for Node ID filtering
- [ ] Implement filtering in battery driver
- [ ] Implement filtering in other sensor drivers (GPS, baro)
- [ ] Ensure backwards compatibility

## Phase 4: Testing

- [ ] Verify build compiles
- [ ] Test with DroneCAN setup (if available)

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created
- [ ] Completion report sent to manager
