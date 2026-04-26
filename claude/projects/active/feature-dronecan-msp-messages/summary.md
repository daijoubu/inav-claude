# Project: Add DroneCAN MSP Messages

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Feature
**Created:** 2026-04-25
**Estimated Effort:** 3-4 hours

## Overview

Add MSP2 commands to expose DroneCAN node status and identity data from the flight controller. Currently INAV receives DroneCAN NodeStatus broadcasts but discards them — this project adds a persistent node table and MSP commands to surface that data to the configurator.

## Problem

During HAL v1.3.3 hardware validation, the only way to verify DroneCAN node detection was via OpenOCD/GDB introspection. No MSP command exists to query which DroneCAN nodes are present, their health status, or their reported sensor data. This blocks software-based DroneCAN validation and is a gap compared to PX4/ArduPilot (which expose UAVCAN node info via MAVLink).

## Solution

1. Add a persistent node table in `dronecan.c` (populated from existing NodeStatus broadcasts)
2. Define `MSP2_INAV_DRONECAN_NODES` (0x2042) — returns node count + per-node status
3. Define `MSP2_INAV_DRONECAN_NODE_INFO` (0x2043) — returns per-node detail by node ID

Follow the `MSP2_INAV_ESC_TELEM` design pattern: count header + repeated fixed-size records.

## Implementation

### Phase 1: Node Table (prerequisite)

Add to `src/main/drivers/dronecan/dronecan.h`:
```c
typedef struct {
    uint8_t  nodeID;
    uint8_t  health;          // 0=OK, 1=WARNING, 2=ERROR, 3=CRITICAL
    uint8_t  mode;            // 0=OPERATIONAL, 1=INIT, 2=MAINTENANCE, 3=SW_UPDATE
    uint32_t uptime_sec;
    uint16_t vendor_status_code;
    uint32_t last_seen_ms;
    uint8_t  name_len;
    char     name[32];
} dronecanNodeInfo_t;
```

Add to `src/main/drivers/dronecan/dronecan.c`:
- `dronecanNodeInfo_t nodeTable[DRONECAN_MAX_NODES]` (max 32 nodes)
- Update `handle_NodeStatus()` to upsert into node table
- Add `dronecanGetNodeCount()` and `dronecanGetNode(uint8_t index)` accessors

### Phase 2: MSP Commands

In `src/main/msp/msp_protocol_v2_inav.h`:
```c
#define MSP2_INAV_DRONECAN_NODES     0x2042
#define MSP2_INAV_DRONECAN_NODE_INFO 0x2043
```

In `src/main/fc/fc_msp.c`, add handlers following the ESC_TELEM pattern.

**MSP2_INAV_DRONECAN_NODES response layout:**
```
[nodeCount: U8] then per node:
  nodeID(1) + health(1) + mode(1) + uptime_sec(4) + vendor_status(2) + last_seen_ms(4) + name_len(1) + name[16]
= 30 bytes per node (name truncated to 16 bytes to keep packets manageable)
```

**MSP2_INAV_DRONECAN_NODE_INFO request/response:**
- Request: nodeID (U8)
- Response: full node detail including name up to 32 bytes

## Success Criteria

- [ ] `dronecanNodeInfo_t` struct defined and node table maintained in dronecan.c
- [ ] `handle_NodeStatus()` populates node table on each broadcast
- [ ] `MSP2_INAV_DRONECAN_NODES` returns correct node list (verified with msp tool)
- [ ] `MSP2_INAV_DRONECAN_NODE_INFO` returns correct per-node detail
- [ ] Builds cleanly for MATEKF765SE with zero errors/warnings
- [ ] Hardware tested: DroneCAN battery monitor node visible in MSP response
- [ ] PR opened against `maintenance-10.x`

## Related

- **Suggestion email:** `manager/email/inbox/2026-04-21-1000-suggestion-dronecan-configurator.md`
- **Prior art:** `MSP2_INAV_ESC_TELEM` (0x2041) in `src/main/fc/fc_msp.c` — follow this pattern
- **DroneCAN driver:** `src/main/drivers/dronecan/dronecan.c`
- **MSP protocol:** `src/main/msp/msp_protocol_v2_inav.h`
- **Downstream:** `feature-dronecan-configurator-tab` (depends on this project)
- **Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
