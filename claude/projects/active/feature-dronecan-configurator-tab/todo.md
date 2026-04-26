# Todo: Add DroneCAN Tab to INAV Configurator

## Prerequisite

- [ ] Confirm `feature-dronecan-msp-messages` is complete and firmware PR merged (or branch available for testing)

## Phase 1: MSP Integration

- [ ] Add MSP2_INAV_DRONECAN_NODES (0x2042) to configurator MSP command definitions
- [ ] Add MSP2_INAV_DRONECAN_NODE_INFO (0x2043) to configurator MSP command definitions
- [ ] Implement JS parse functions for both command responses

## Phase 2: UI Tab

- [ ] Add DroneCAN tab entry to navigation
- [ ] Create `tabs/dronecan.html` with node table layout
- [ ] Create `tabs/dronecan.js` with MSP query and table population logic
- [ ] Implement health status colour coding (green/amber/red)
- [ ] Implement 2-second auto-refresh while tab is active

## Phase 3: Per-Node Detail

- [ ] Implement row expand/click to query NODE_INFO
- [ ] Display software version, hardware version, vendor status
- [ ] Display voltage/current for known battery monitor nodes

## Phase 4: Hardware Testing

- [ ] Test against MATEKF765SE with DroneCAN battery monitor attached
- [ ] Verify node table populates and refreshes correctly
- [ ] Verify health colour coding reflects actual node status

## Completion

- [ ] All success criteria met
- [ ] PR opened against `maintenance-10.x`
- [ ] Send completion report to manager
