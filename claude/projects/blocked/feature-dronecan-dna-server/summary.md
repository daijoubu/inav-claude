# Project: feature-dronecan-dna-server

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Feature
**Created:** 2026-06-03
**Estimated Time:** 6-10 hours
**Depends On:** feature-canbus-errors-blackbox (assign after that completes)

## Overview

Implement a DroneCAN DNA (Dynamic Node Allocation) server in INAV so that peripherals configured with node_id=0 are automatically assigned a node ID at runtime, enabling plug-and-play DroneCAN setup.

## Problem

Many DroneCAN peripherals ship with node_id=0, expecting an allocator to assign them an ID. Currently users must manually configure each peripheral's node ID via CLI. A DNA server eliminates this friction entirely.

## Objectives

1. Implement non-redundant DNA allocation server per UAVCAN spec
2. Handle multi-part UID accumulation and node ID assignment
3. Persist allocation table across reboots (optional)
4. Expose enable/max-nodes settings

## Scope

**In Scope:**
- `uavcan.protocol.dynamic_node_id.Allocation` message handler
- Allocation table (up to 8 entries, ~170 bytes RAM)
- Settings: `dronecan_dna_server` (ON/OFF), `dronecan_dna_max_nodes`
- Integration into `dronecan.c`

**Out of Scope:**
- Redundant (Raft) allocator mode
- Configurator UI for allocation table

## Implementation Steps

1. Create `src/main/drivers/dronecan/dronecan_dna_server.c/.h` — data structures and allocation logic
2. Implement request handler (3-part UID accumulation, ID assignment)
3. Integrate handler into `dronecan.c`
4. Add settings to `fc/settings.yaml`
5. (Optional) Persist allocation table to config

## Data Structures

```c
typedef struct {
    uint8_t unique_id[16];
    uint8_t node_id;
    uint8_t flags;
} dnaAllocationEntry_t;

typedef struct {
    dnaAllocationEntry_t entries[DNA_MAX_NODES];
    uint8_t pendingUniqueId[16];
    uint8_t pendingOffset;
    uint8_t nextAvailableId;
    timeMs_t lastRequestTime;
} dnaServer_t;
```

## Reference

- ArduPilot: `libraries/AP_DroneCAN/AP_DroneCAN_DNA_Server.cpp`
- Issue: daijoubu/inav #4

## Success Criteria

- [ ] Peripheral with node_id=0 receives an allocated ID automatically on power-up
- [ ] Same peripheral retains the same ID on subsequent power cycles
- [ ] `dronecan_dna_server` setting enables/disables the feature
- [ ] Full build matrix passes (F4/F7/H7/SITL)
- [ ] PR opened to `maintenance-10.x`

## Priority Justification

Medium — significant UX improvement for DroneCAN setup, well-specified, reference implementation available.
