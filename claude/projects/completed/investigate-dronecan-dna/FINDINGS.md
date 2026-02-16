# Investigation: DroneCAN DNA Allocator Server in INAV

**Date:** 2026-02-14 (Revised)
**Investigator:** Developer

---

## Executive Summary

Implementing a **DNA allocation server** in INAV is **feasible and recommended**. This would allow INAV to automatically assign node IDs to DroneCAN peripherals that ship configured for dynamic allocation (node_id=0).

**Key Points:**
- Simple single-node allocator is explicitly supported by the DroneCAN spec (no Raft consensus needed)
- DSDL messages already generated in INAV
- Storage requirement: ~170 bytes for 8 nodes (fits easily in EEPROM or RAM)
- Implementation effort: **6-10 hours**
- ArduPilot has a working implementation to reference

**Recommendation:** Implement as a feature for INAV 10.x

---

## Technical Analysis

### 1. Allocator Types

The DroneCAN specification supports two allocator modes:

| Mode | Complexity | Use Case |
|------|------------|----------|
| **Non-redundant (single)** | Simple | Flight controllers, single-master networks |
| **Redundant (Raft)** | Complex | Multi-allocator networks with fault tolerance |

**INAV should implement non-redundant mode** - the spec explicitly states this is valid and requires only maintaining an allocation table and responding to requests.

### 2. How DNA Allocation Works (Server Side)

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Anonymous node (node_id=0) broadcasts Allocation request    │
│     - first_part_of_unique_id = true                            │
│     - unique_id contains first 6 bytes of 16-byte UID           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. Server receives request, echoes back unique_id bytes        │
│     - Allocator broadcasts Allocation with matched bytes        │
│     - Node sends next chunk (first_part_of_unique_id = false)   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. After all 16 bytes matched, server assigns node_id          │
│     - Look up existing allocation or assign new ID              │
│     - Broadcast Allocation with node_id set                     │
│     - Node calls canardSetLocalNodeID() and becomes active      │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Data Structures Needed

```c
// Allocation table entry
typedef struct {
    uint8_t unique_id[16];      // Node's unique identifier
    uint8_t node_id;            // Assigned node ID (1-125)
    uint8_t flags;              // Valid flag, etc.
} dnaAllocationEntry_t;

// Server state
typedef struct {
    dnaAllocationEntry_t entries[DNA_MAX_NODES];  // Allocation table
    uint8_t pendingUniqueId[16];    // UID being accumulated
    uint8_t pendingOffset;          // Bytes received so far
    uint8_t nextAvailableId;        // Next ID to assign (counts down from 125)
    timeMs_t lastRequestTime;       // For timeout handling
} dnaServer_t;

#define DNA_MAX_NODES 8             // Support up to 8 dynamic peripherals
```

**Storage:** 8 entries × 18 bytes = 144 bytes + state ≈ 170 bytes

### 4. Messages to Handle

| Message | Direction | Purpose |
|---------|-----------|---------|
| `Allocation` (ID 1) | Receive | Node requesting ID |
| `Allocation` (ID 1) | Send | Echo UID / assign ID |

**NOT needed for simple allocator:**
- `AppendEntries` - Raft consensus (distributed only)
- `RequestVote` - Raft consensus (distributed only)
- `Discovery` - Raft consensus (distributed only)

### 5. Implementation Plan

#### Phase 1: Data Structures (1 hour)

**New file:** `src/main/drivers/dronecan/dronecan_dna_server.c`

```c
#include "dronecan_dna_server.h"

static dnaServer_t dnaServer;

void dnaServerInit(void) {
    memset(&dnaServer, 0, sizeof(dnaServer));
    dnaServer.nextAvailableId = 125;  // Start high, count down
    // Optionally load from EEPROM
}

uint8_t dnaServerLookupOrAllocate(const uint8_t* uniqueId) {
    // Check existing allocations
    for (int i = 0; i < DNA_MAX_NODES; i++) {
        if (dnaServer.entries[i].flags & DNA_FLAG_VALID) {
            if (memcmp(dnaServer.entries[i].unique_id, uniqueId, 16) == 0) {
                return dnaServer.entries[i].node_id;  // Already allocated
            }
        }
    }
    // Allocate new
    for (int i = 0; i < DNA_MAX_NODES; i++) {
        if (!(dnaServer.entries[i].flags & DNA_FLAG_VALID)) {
            memcpy(dnaServer.entries[i].unique_id, uniqueId, 16);
            dnaServer.entries[i].node_id = dnaServer.nextAvailableId--;
            dnaServer.entries[i].flags = DNA_FLAG_VALID;
            return dnaServer.entries[i].node_id;
        }
    }
    return 0;  // Table full
}
```

#### Phase 2: Request Handler (2-3 hours)

```c
void dnaServerHandleAllocationRequest(CanardRxTransfer* transfer) {
    struct uavcan_protocol_dynamic_node_id_Allocation msg;
    uavcan_protocol_dynamic_node_id_Allocation_decode(transfer, &msg);

    // Anonymous node requesting allocation
    if (transfer->source_node_id == CANARD_BROADCAST_NODE_ID) {
        if (msg.first_part_of_unique_id) {
            // Start new allocation sequence
            memset(dnaServer.pendingUniqueId, 0, 16);
            dnaServer.pendingOffset = 0;
        }

        // Accumulate unique_id bytes
        uint8_t bytesToCopy = MIN(msg.unique_id.len, 16 - dnaServer.pendingOffset);
        memcpy(&dnaServer.pendingUniqueId[dnaServer.pendingOffset],
               msg.unique_id.data, bytesToCopy);
        dnaServer.pendingOffset += bytesToCopy;

        // Respond with echo
        struct uavcan_protocol_dynamic_node_id_Allocation response;
        response.node_id = 0;  // Not assigned yet
        response.first_part_of_unique_id = false;
        response.unique_id.len = dnaServer.pendingOffset;
        memcpy(response.unique_id.data, dnaServer.pendingUniqueId, dnaServer.pendingOffset);

        // If all 16 bytes received, assign node ID
        if (dnaServer.pendingOffset >= 16) {
            response.node_id = dnaServerLookupOrAllocate(dnaServer.pendingUniqueId);
            dnaServer.pendingOffset = 0;  // Reset for next allocation
        }

        dnaServerBroadcastAllocation(&response);
    }
}
```

#### Phase 3: Integration (1-2 hours)

**Modify:** `dronecan.c`

```c
// In shouldAcceptTransfer():
case UAVCAN_PROTOCOL_DYNAMIC_NODE_ID_ALLOCATION_ID:
    *out_data_type_signature = UAVCAN_PROTOCOL_DYNAMIC_NODE_ID_ALLOCATION_SIGNATURE;
    return true;

// In onTransferReceived():
case UAVCAN_PROTOCOL_DYNAMIC_NODE_ID_ALLOCATION_ID:
    dnaServerHandleAllocationRequest(transfer);
    break;

// In dronecanInit():
if (dronecanConfig()->dna_server_enabled) {
    dnaServerInit();
}
```

#### Phase 4: Settings (30 min)

```yaml
- name: dronecan_dna_server
  description: "Enable DNA allocation server for plug-and-play DroneCAN peripherals"
  default_value: OFF
  field: dna_server_enabled
  type: bool
```

#### Phase 5: Persistence (Optional, 2 hours)

Store allocation table in EEPROM for consistent node IDs across reboots:

```c
void dnaServerSave(void) {
    // Write to parameter group or dedicated flash area
}

void dnaServerLoad(void) {
    // Read on init
}
```

#### Phase 6: Testing (2-3 hours)

1. SITL with mock anonymous node
2. Hardware test with real DNA-enabled peripheral
3. Multi-device allocation test
4. Persistence test (reboot and verify same IDs)

---

## Effort Estimate

| Phase | Task | Effort |
|-------|------|--------|
| 1 | Data structures | 1 hour |
| 2 | Request handler | 2-3 hours |
| 3 | Integration into dronecan.c | 1-2 hours |
| 4 | Settings | 30 min |
| 5 | Persistence (optional) | 2 hours |
| 6 | Testing | 2-3 hours |
| **Total** | | **6-10 hours** |

---

## Comparison: Client vs Server

| Aspect | DNA Client (Original) | DNA Server (Revised) |
|--------|----------------------|---------------------|
| **Purpose** | INAV requests ID from allocator | INAV assigns IDs to peripherals |
| **Use case** | Multi-FC networks | Plug-and-play peripherals |
| **Practical value** | Low (INAV is usually master) | **High** (many peripherals ship with DNA) |
| **Requires** | External allocator | Nothing extra |
| **Complexity** | State machine, timeouts | Table lookup, response |
| **Effort** | 10-12 hours | **6-10 hours** |

---

## Reference Implementation

**ArduPilot:** `libraries/AP_DroneCAN/AP_DroneCAN_DNA_Server.cpp`
- Stores allocations in flash (1KB area)
- Supports up to 125 nodes
- Uses FNV-1a hash for fast UID lookup
- Persistence across reboots

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Table overflow (>8 nodes) | Low | Medium | Configurable max, warn user |
| Duplicate allocation | Very Low | Low | UID uniqueness guaranteed by MCU |
| Startup race condition | Low | Low | Delay peripheral power-on |
| Flash wear | Very Low | Low | Only write on new allocation |

---

## Settings Impact

```yaml
# New settings
dronecan_dna_server = OFF        # Enable DNA server
dronecan_dna_max_nodes = 8       # Maximum dynamic allocations

# Existing (unchanged)
dronecan_node_id = 1             # FC's own node ID (static)
```

---

## Success Criteria

- [x] Clear explanation of DroneCAN DNA server
- [x] Analysis of what already exists in INAV
- [x] Implementation plan with specific steps
- [x] Estimated effort and timeline (6-10 hours)
- [x] Potential issues identified

---

## Conclusion

Implementing a DNA **allocation server** in INAV is:
- **Feasible** - All DSDL messages already generated, simple single-node mode supported
- **Valuable** - Enables plug-and-play for DNA-enabled peripherals
- **Reasonable effort** - 6-10 hours for full implementation
- **Low risk** - Simple table lookup, no complex consensus needed

**Recommendation:** Implement for INAV 10.x as an optional feature (`dronecan_dna_server = ON`).
