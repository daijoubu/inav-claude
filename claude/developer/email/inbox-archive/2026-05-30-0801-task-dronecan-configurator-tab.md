# Task Assignment: Add DroneCAN Tab to INAV Configurator

**Date:** 2026-05-30 08:01
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-configurator-tab
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 4-6 hours

## Task

Add a DroneCAN tab to inav-configurator that displays detected DroneCAN nodes, their health status, mode, uptime, and sensor data. The firmware MSP commands (`MSP2_INAV_DRONECAN_NODES` 0x2042 and `MSP2_INAV_DRONECAN_NODE_INFO` 0x2043) are now merged (PR #11527) and available as of maintenance-10.x.

## Background

Users currently have no UI to view DroneCAN node status. Configuring and diagnosing DroneCAN peripherals (battery monitors, GPS, ESCs) requires CLI commands. This tab makes it accessible to all users.

## What to Do

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

## Key References

- Firmware MSP commands: PR #11527 (merged) — `MSP2_INAV_DRONECAN_NODES` (0x2042), `MSP2_INAV_DRONECAN_NODE_INFO` (0x2043)
- Reference tabs: `tabs/esc_motors.js`, `tabs/gps.js`
- Repository: inav-configurator | Branch: `maintenance-10.x`

## Project Directory

`claude/projects/active/feature-dronecan-configurator-tab/`

---
**Manager**
