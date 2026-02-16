# Project: DroneCAN Node Transport Statistics

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-02-14
**Estimated Effort:** 4-6 hours

## Overview

Implement DroneCAN transport statistics collection by requesting uavcan.protocol.GetTransportStats from other nodes on the CAN bus, allowing INAV to monitor transfer counts, errors, and communication health of connected DroneCAN devices.

## Problem

When diagnosing CAN bus issues with DroneCAN peripherals (GPS, airspeed sensors, ESCs), there's no visibility into transport-level statistics. The GetTransportStats service provides valuable diagnostic data including transfer counts and error rates that would help identify communication problems.

## Objectives

1. Request transport statistics from nodes
   - Implement uavcan.protocol.GetTransportStats service client
   - Periodically poll known nodes for their statistics
   - Store and track statistics per node ID

2. Make statistics accessible
   - Expose via CLI for debugging (`can_stats` or similar)
   - Track tx_transfers, rx_transfers, transfer_errors per node
   - Calculate error rates

3. Optional: Integration with Blackbox
   - Log transport statistics periodically
   - Correlate with CAN bus errors (feature-canbus-errors-blackbox)

## Scope

**In Scope:**
- GetTransportStats service client implementation
- Node statistics storage structure
- CLI commands to view transport stats
- Periodic polling of known nodes

**Out of Scope:**
- NodeStatus message handling (separate feature)
- Real-time OSD display
- Writing stats to external devices

## Technical Details

**GetTransportStats Service:**
- Service ID: uavcan.protocol.GetTransportStats (data type ID 4)
- Request: Empty
- Response:
  - `transfers_tx` (uint48) - Total transmitted transfers
  - `transfers_rx` (uint48) - Total received transfers
  - `transfer_errors` (uint48) - Total transfer errors
  - `can_iface_stats[]` - Per-interface statistics (optional)

## Implementation Steps

1. Research DroneCAN service mechanism
   - Understand service request/response flow
   - Check existing service implementations in dronecan.c

2. Add GetTransportStats service client
   - Register service response handler
   - Implement request sending function
   - Parse response into storage

3. Add node statistics tracking
   - Structure to hold per-node stats
   - Periodic polling timer (e.g., every 10 seconds)

4. Add CLI support
   - Command to list node transport stats
   - Show error rates and transfer counts

5. Test implementation

## Success Criteria

- [ ] GetTransportStats requests sent to discovered nodes
- [ ] Transport statistics received and stored per node
- [ ] Statistics accessible via CLI command
- [ ] Works with existing DroneCAN devices

## Related

- **feature-canbus-errors-blackbox:** CAN error tracking (complementary)
- **dronecan-driver-docs:** Related documentation
- **PR #11313:** DroneCAN implementation
