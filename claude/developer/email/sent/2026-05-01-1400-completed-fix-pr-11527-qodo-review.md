# Task Completed: Fix PR #11527 Qodo Review Issues

**Date:** 2026-05-01 14:00
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Fixed both Qodo review comments on PR #11527 ("DroneCAN: Add node table, CLI status, and MSP2 node query commands"). The two critical issues — buffer overflow in MSP2_INAV_DRONECAN_NODES and wrong return convention in MSP2_INAV_DRONECAN_NODE_INFO — have been resolved and tested on hardware.

## Branch and Commits

**Branch:** `feature/msp-dronecan-support-v2`
**Commit:** `fbe77e7a4`
**PR:** iNavFlight/inav#11527

## Changes Made

### Issue 1: Buffer Overflow in MSP2_INAV_DRONECAN_NODES

**Location:** `src/main/fc/fc_msp.c` (lines 1774–1788)

**Problem:** Serializing all nodes without buffer bounds checking could exceed 512-byte MSP buffer (worst-case: 1 + 32×30 = 961 bytes).

**Fix:** 
- Reduced per-node record from 30 bytes to 7 bytes (nodeID, health, mode, last_seen_ms)
- Worst-case payload is now 1 + 32×7 = 225 bytes, safely within 512-byte MSP buffer
- Added `dronecanNodeStatus_t __attribute__((packed))` struct to `dronecan.h`
- Used `sbufWriteDataSafe` in the handler to ensure safe buffer writes

### Issue 2: Wrong Return Convention in MSP2_INAV_DRONECAN_NODE_INFO

**Location:** `src/main/fc/fc_msp.c` (lines 4273–4310 and 4826–4853)

**Problem:** Handler was using bare `return MSP_RESULT_*` in a bool-returning function, never setting the `*ret` out-parameter. "Node not found" was silently reported as success.

**Fix:**
- Replaced `return MSP_RESULT_ERROR;` with `*ret = MSP_RESULT_ERROR; break;`
- Replaced `return MSP_RESULT_ACK;` with `break;` (ACK is default)
- Ensured "node not found" path explicitly sets `*ret = MSP_RESULT_ERROR`
- Function's own return value is now consistently `true` (command handled)

## Additional Improvements Made

During local code review:
- **dronecan.c**: Fixed `dronecanGetNode()` indentation; replaced `printf` with `LOG_DEBUG` in `handle_GetNodeInfo`
- **msp_messages.json**: Updated to array pattern with `dronecanNodeStatus_t` ctype, 7-byte record format
- **DroneCAN.md** and **docs/development/msp/README.md**: Updated to reflect new wire format

## Testing

- [x] Builds cleanly for MATEKF765SE
- [x] Hardware testing on MATEKF765SE with live DroneCAN node (node ID 73): all 3 test cases passed
- [x] Protocol verified with updated wire format (7-byte per-node records)
- [x] Error handling tested: "node not found" returns MSP_RESULT_ERROR as expected

**Test results:**
- MSP2_INAV_DRONECAN_NODES: Successfully returned 32-node array within buffer limits
- MSP2_INAV_DRONECAN_NODE_INFO: Correctly returns MSP_RESULT_ERROR for missing nodes
- All Qodo feedback comments addressed and replied to on PR

## Next Steps

- PR ready for review and merge
- inav.lock released

---
**Developer**
