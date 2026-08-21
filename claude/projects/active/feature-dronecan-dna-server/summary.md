# Project: feature-dronecan-dna-server

**Status:** 🚫 BLOCKED — was stale at 📋 TODO; code/tests/hardware complete, PRs #11688 (fw) + #2672 (configurator) open in draft, stacked on unmerged #11607/#11683, no dev work pending until those merge. Reclassified from IN PROGRESS 2026-07-07.
**Priority:** Medium
**Type:** Feature
**Created:** 2026-06-03
**Estimated Time:** 6-10 hours
**Depends On:** feature-canbus-errors-blackbox (assign after that completes)

**2026-08-19: PG_DRONECAN_CONFIG version reconciliation needed on resume.** This project's `dronecanUseDNAServer` field was added to `dronecanConfig_t`/`PG_DRONECAN_CONFIG` (PR #11688) without a version bump — struct is still registered at version 0. Meanwhile `feature-dronecan-actuator-control` has since added its own field (`servoOutputBitmask`) to the same struct and bumped the registered version 0→1. When this project resumes (after PR #11607 merges and #11688 rebases), reconcile `PG_DRONECAN_CONFIG`'s version so it correctly accounts for **both** fields as a single version bump — not two independent/conflicting ones. Also check whether `EEPROM_CONF_VERSION` (`src/main/config/config_eeprom.h:24`, currently 126) needs bumping, since the struct's on-flash layout has now changed twice. Flagged by developer, see archived email `claude/manager/email/inbox-archive/2026-08-19-1030-flag-pg-dronecan-config-version-coordination.md`.

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
