# Todo: Add DroneCAN MSP Messages

## Phase 1: Node Table Infrastructure

- [ ] Define `dronecanNodeInfo_t` struct in `dronecan.h`
- [ ] Add `nodeTable[DRONECAN_MAX_NODES]` and `activeNodeCount` in `dronecan.c`
- [ ] Update `handle_NodeStatus()` to upsert into node table
- [ ] Add `dronecanGetNodeCount()` accessor
- [ ] Add `dronecanGetNode(uint8_t index)` accessor
- [ ] Build cleanly for MATEKF765SE

## Phase 2: MSP Commands

- [ ] Define `MSP2_INAV_DRONECAN_NODES` (0x2042) in `msp_protocol_v2_inav.h`
- [ ] Define `MSP2_INAV_DRONECAN_NODE_INFO` (0x2043) in `msp_protocol_v2_inav.h`
- [ ] Implement `MSP2_INAV_DRONECAN_NODES` handler in `fc_msp.c`
- [ ] Implement `MSP2_INAV_DRONECAN_NODE_INFO` handler in `fc_msp.c`
- [ ] Build cleanly with zero errors/warnings

## Phase 3: Hardware Validation

- [ ] Flash MATEKF765SE with new firmware
- [ ] Verify DroneCAN battery monitor node appears in `MSP2_INAV_DRONECAN_NODES` response
- [ ] Verify `MSP2_INAV_DRONECAN_NODE_INFO` returns correct node name and health

## Completion

- [ ] All success criteria met
- [ ] PR opened against `maintenance-10.x`
- [ ] Send completion report to manager
