# Project: Add DroneCAN Tab to INAV Configurator

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Feature
**Created:** 2026-04-25
**Estimated Effort:** 4-6 hours

## Overview

Add a DroneCAN tab to inav-configurator that displays detected DroneCAN nodes, their health status, mode, uptime, and reported sensor data. Provides a software-visible view of the CAN bus without requiring hardware debugger access.

## Problem

Even after `feature-dronecan-msp-messages` exposes node data via MSP, users have no UI to view it. Configuring and validating DroneCAN peripherals (battery monitors, GPS, ESCs) currently requires CLI commands or external tools. A dedicated tab would make DroneCAN setup and diagnosis accessible to all users.

## Solution

Add a "DroneCAN" tab to inav-configurator that:
1. Queries `MSP2_INAV_DRONECAN_NODES` on page load and periodically
2. Displays a node table: ID, name, health, mode, uptime, last seen
3. Shows per-node sensor data (voltage/current for battery monitors, etc.) on row expand or selection
4. Uses health status colour coding (green/yellow/red)

## Implementation

### Phase 1: MSP Integration

- Add `MSP2_INAV_DRONECAN_NODES` (0x2042) and `MSP2_INAV_DRONECAN_NODE_INFO` (0x2043) to the configurator's MSP command list
- Implement JS functions to request and parse responses

### Phase 2: UI Tab

- Add tab entry in navigation (follow existing tab pattern, e.g. `tabs/esc_motors.js`)
- Create `tabs/dronecan.js` and `tabs/dronecan.html`
- Node table columns: Node ID | Name | Health | Mode | Uptime | Last Seen
- Health indicator: colour-coded badge (OK=green, WARNING=amber, ERROR/CRITICAL=red)
- Auto-refresh every 2 seconds while tab is active

### Phase 3: Per-Node Detail

- Click/expand row to query `MSP2_INAV_DRONECAN_NODE_INFO` for that node
- Show: software version, hardware version, vendor status code
- For known node types (battery monitor): show voltage and current

## Success Criteria

- [ ] MSP2_INAV_DRONECAN_NODES and NODE_INFO integrated into configurator MSP layer
- [ ] DroneCAN tab appears in navigation when CAN is enabled
- [ ] Node table populates correctly from live MSP data
- [ ] Health status colour coding works correctly
- [ ] Auto-refresh functional (2s interval, stops when tab not active)
- [ ] Tested against MATEKF765SE with DroneCAN battery monitor attached
- [ ] PR opened against `maintenance-10.x`

## Dependencies

**Blocked until `feature-dronecan-msp-messages` is complete** — the MSP commands must exist in firmware before the configurator tab can be built and tested.

## Related

- **Prerequisite:** `feature-dronecan-msp-messages` (firmware MSP commands)
- **Suggestion email:** `manager/email/inbox/2026-04-21-1000-suggestion-dronecan-configurator.md`
- **Reference tabs:** `tabs/esc_motors.js`, `tabs/gps.js` (follow existing patterns)
- **Repository:** inav-configurator | **Branch:** `maintenance-10.x`
