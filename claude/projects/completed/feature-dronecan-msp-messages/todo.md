# Todo: Add DroneCAN MSP Messages

## Phase 1: Node Table Infrastructure

- [x] Define `dronecanNodeInfo_t` struct in `dronecan.h`
- [x] Add `nodeTable[DRONECAN_MAX_NODES]` and `activeNodeCount` in `dronecan.c`
- [x] Update `handle_NodeStatus()` to upsert into node table
- [x] Add `dronecanGetNodeCount()` accessor
- [x] Add `dronecanGetNode(uint8_t index)` accessor
- [x] Build cleanly for MATEKF765SE

## Phase 2: MSP Commands

- [x] Define `MSP2_INAV_DRONECAN_NODES` (0x2042) in `msp_protocol_v2_inav.h`
- [x] Define `MSP2_INAV_DRONECAN_NODE_INFO` (0x2043) in `msp_protocol_v2_inav.h`
- [x] Implement `MSP2_INAV_DRONECAN_NODES` handler in `fc_msp.c`
- [x] Implement `MSP2_INAV_DRONECAN_NODE_INFO` handler in `fc_msp.c`
- [x] Build cleanly with zero errors/warnings

## Phase 3: Qodo Review Fixes (2026-05-01)

- [x] Fix buffer overflow: reduce per-node record to 7 bytes
- [x] Fix return convention: use `*ret` out-parameter in NODE_INFO handler
- [x] Hardware re-test after fixes (MATEKF765SE, node ID 73)

## Phase 4: Hardware Validation

- [x] Flash MATEKF765SE with new firmware
- [x] Verify DroneCAN battery monitor node appears in `MSP2_INAV_DRONECAN_NODES` response
- [x] Verify `MSP2_INAV_DRONECAN_NODE_INFO` returns correct node name and health

## Completion

- [x] All success criteria met
- [x] PR opened against `maintenance-10.x` (#11527)
- [x] Send completion report to manager
- [ ] PR merged upstream — awaiting maintainer review
