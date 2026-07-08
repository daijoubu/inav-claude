# Task Assignment: Add DroneCAN MSP Messages

**Date:** 2026-04-25 12:00
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-msp-messages
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 3-4 hours

## Task

Add two MSP2 commands to expose DroneCAN node data from the flight controller:
- `MSP2_INAV_DRONECAN_NODES` (0x2042) — returns count + per-node status for all detected nodes
- `MSP2_INAV_DRONECAN_NODE_INFO` (0x2043) — returns detail for a specific node by ID

## Background

During HAL v1.3.3 hardware validation (PR #11514), the only way to verify DroneCAN node detection was via OpenOCD/GDB. No MSP command exists today for this. This project adds that capability, following the same pattern as `MSP2_INAV_ESC_TELEM` (0x2041).

Research already completed:
- No prior art exists in INAV or Betaflight MSP for CAN node enumeration
- PX4/ArduPilot use MAVLink UAVCAN_NODE_STATUS/UAVCAN_NODE_INFO — same concept, different protocol
- INAV already receives NodeStatus broadcasts in handle_NodeStatus() but discards them — the node table infrastructure needs to be added

## What to Do

### Phase 1: Node Table Infrastructure
1. Define `dronecanNodeInfo_t` struct in `src/main/drivers/dronecan/dronecan.h`:
   - Fields: nodeID (U8), health (U8), mode (U8), uptime_sec (U32), vendor_status_code (U16), last_seen_ms (U32), name_len (U8), name[32]
2. Add `nodeTable[DRONECAN_MAX_NODES]` (max 32) and `activeNodeCount` in `dronecan.c`
3. Update `handle_NodeStatus()` to upsert into the node table on each broadcast
4. Add `dronecanGetNodeCount()` and `dronecanGetNode(uint8_t index)` accessors

### Phase 2: MSP Commands
5. Define the two command IDs in `src/main/msp/msp_protocol_v2_inav.h`
6. Add handlers in `src/main/fc/fc_msp.c` following the ESC_TELEM pattern (count header + repeated fixed records)

**MSP2_INAV_DRONECAN_NODES response layout:**
```
[nodeCount: U8] then per node:
nodeID(1) + health(1) + mode(1) + uptime_sec(4) + vendor_status(2) + last_seen_ms(4) + name_len(1) + name[16]
= 30 bytes per node (name truncated to 16 bytes)
```

**MSP2_INAV_DRONECAN_NODE_INFO:**
- Request: nodeID (U8)
- Response: full node fields including name up to 32 bytes

### Phase 3: Hardware Validation
7. Build MATEKF765SE target — zero errors/warnings
8. Flash and verify DroneCAN battery monitor node appears in MSP2_INAV_DRONECAN_NODES response

## Key Files

- `src/main/drivers/dronecan/dronecan.c` — add node table, update handle_NodeStatus()
- `src/main/drivers/dronecan/dronecan.h` — add dronecanNodeInfo_t struct
- `src/main/msp/msp_protocol_v2_inav.h` — define command IDs
- `src/main/fc/fc_msp.c` — add MSP handlers (follow MSP2_INAV_ESC_TELEM at ~line 1749)

## Success Criteria

- [ ] dronecanNodeInfo_t struct defined and node table maintained
- [ ] handle_NodeStatus() populates node table
- [ ] MSP2_INAV_DRONECAN_NODES returns correct node list
- [ ] MSP2_INAV_DRONECAN_NODE_INFO returns correct per-node detail
- [ ] MATEKF765SE build: zero errors, zero warnings
- [ ] Hardware tested: DroneCAN battery monitor visible in MSP response
- [ ] PR opened against maintenance-10.x

## Notes

- Branch from `maintenance-10.x` (this pairs with the HAL v1.3.3 work on that branch)
- The configurator tab project (feature-dronecan-configurator-tab) is waiting on this — complete and PR before starting that one
- msp-expert agent can help with MSP message numbering and conventions

## Project Directory

`claude/projects/active/feature-dronecan-msp-messages/`

---
**Manager**
