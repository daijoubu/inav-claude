# Task Assignment: DroneCAN DNA Server

**Date:** 2026-06-04 15:51
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-dna-server
**Priority:** MEDIUM
**Estimated Effort:** 6-10 hours

## Task

Implement a DroneCAN DNA (Dynamic Node Allocation) server in INAV so that peripherals configured with node_id=0 are automatically assigned a node ID at runtime, enabling plug-and-play DroneCAN setup.

## Background

Many DroneCAN peripherals ship with node_id=0, expecting an allocator to assign them an ID. Currently users must manually configure each peripheral's node ID via CLI. A DNA server eliminates this friction entirely. INAV should implement non-redundant (single) mode — the spec explicitly states this is valid and appropriate for flight controllers.

Reference issue: daijoubu/inav #4

## What to Do

1. Create `src/main/drivers/dronecan/dronecan_dna_server.h` and `.c` with data structures and allocation logic
2. Implement the 3-part UID accumulation and node ID assignment handler
3. Integrate the handler into `src/main/drivers/dronecan/dronecan.c`
4. Add settings to `src/main/fc/settings.yaml`:
   - `dronecan_dna_server` (ON/OFF)
   - `dronecan_dna_max_nodes` (default 8, max 16)
5. Build matrix: F4, F7, H7, SITL
6. Open PR to `maintenance-10.x`

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

#define DNA_MAX_NODES 8
```

## Reference Implementation

ArduPilot: `libraries/AP_DroneCAN/AP_DroneCAN_DNA_Server.cpp`

## Success Criteria

- [ ] Peripheral with node_id=0 receives an allocated ID automatically on power-up
- [ ] Same peripheral retains the same ID on subsequent power cycles
- [ ] `dronecan_dna_server` setting enables/disables the feature
- [ ] Full build matrix passes (F4/F7/H7/SITL)
- [ ] PR opened to `maintenance-10.x`

## Project Directory

`claude/projects/active/feature-dronecan-dna-server/`

---
**Manager**
