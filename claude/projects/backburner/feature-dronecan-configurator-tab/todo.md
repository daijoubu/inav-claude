# Todo: Add DroneCAN Tab to INAV Configurator

## Prerequisite

- [x] Confirm `feature-dronecan-msp-messages` is complete and firmware PR merged (PR #11527 merged)

## Phase 1: MSP Integration

- [x] Add MSP2_INAV_DRONECAN_NODES (0x2042) to configurator MSP command definitions (`js/msp/MSPCodes.js`)
- [x] Add MSP2_INAV_DRONECAN_NODE_INFO (0x2043) to configurator MSP command definitions (`js/msp/MSPCodes.js`)
- [x] Add FC.DRONECAN_NODES and FC.DRONECAN_NODE_INFO state slots (`js/fc.js` line 95)
- [x] Implement JS parse functions for both command responses (`js/msp/MSPHelper.js` lines 1560–1588)

## Phase 2: UI Tab

- [x] Add i18n strings to `locale/en/messages.json` (tabDroneCAN + 8 column/label strings)
- [x] Add `tab_dronecan` nav entry to `index.html` (Sensors & Peripherals group, line 350)
- [x] Create `tabs/dronecan.html`
- [x] Create `tabs/dronecan.js` (const dronecanTab pattern, export default)
- [x] Add `'dronecan'` to `defaultAllowedTabsWhenConnected` in `js/gui.js`
- [x] Add `import dronecanTab from './../tabs/dronecan'` to `js/configurator_main.js`
- [x] Fix nav-toggle-all `<a>` caught by tab-switch handler (spurious firmware upgrade warning) — in `js/configurator_main.js`
- [x] Implement health status colour coding in CSS (green/amber/red for .health-ok/.health-warning/.health-error/.health-critical)
  - [x] Create `src/css/tabs/dronecan.css`
  - [x] Add `@import 'tabs/dronecan.css';` at end of `src/css/styles.css`
  - [x] Remove duplicate accordion block from `js/configurator_main.js`

## Phase 3: Per-Node Detail

- [x] Implement row expand/click to query NODE_INFO
- [x] Display vendor status, uptime, mode, health in detail panel
- [ ] Display software version, hardware version — **blocked: firmware MSP handler does not send these fields; depends on `feature-dronecan-getnodeinfo` firmware task**

## Phase 4: Hardware Testing

- [x] Test against KAKUTEH7WING with DroneCAN battery monitor attached
- [x] Verify node table populates and refreshes correctly
- [x] Verify health colour coding reflects actual node status (aligned with Mission Planner/QGC: green/amber/red)

## Phase 5: Bus Configuration Settings

Promote from backlog — include in this PR.

### Design decisions (2026-06-01)

**Where:** DroneCAN tab, not Ports tab.
- CAN baud rate is bus-wide (not per-port like UART). The Ports tab is UART-centric; CAN doesn't fit that model.
- Node ID is DroneCAN-specific. Belongs with DroneCAN content.
- Precedent: ArduPilot/Mission Planner keeps CAN settings in a dedicated CAN section.

**Layout:** Bus Configuration section above the node table.

```
┌─ Bus Configuration ──────────────────────┐
│  CAN Baud Rate: [1 Mbps ▼]               │
│  FC Node ID:    [1      ]                │
│                           [Save] [Reboot]│
└──────────────────────────────────────────┘

┌─ Detected Nodes ─────────────────────────┐
│  Node ID │ Name │ Health │ Mode │ Uptime │
└──────────────────────────────────────────┘
```

**MSP:** No dedicated message needed. Use the generic settings API:
- Read: `MSP2_COMMON_SETTING` (0x1003) — send setting name as string, returns typed value
- Write: `MSP2_COMMON_SET_SETTING` (0x1004) — send name + value, then save/reboot

**Firmware setting names** (confirmed in `inav/src/main/fc/settings.yaml`):
- `dronecan_node_id` — int, default 1, valid 1–127 (126–127 reserved for diagnostics)
- `dronecan_bitrate_kbps` — enum, default 1000, valid values: 125 / 250 / 500 / 1000

**Controls:**
- `dronecan_bitrate_kbps` → `<select>` dropdown with the 4 valid values
- `dronecan_node_id` → `<input type="number">` min=1 max=125 with a warning if user enters 126–127
- Save button calls `MSP2_COMMON_SET_SETTING` for both settings, then triggers save + reboot

### Implementation checklist

- [x] On tab load, call `MSP2_COMMON_SETTING` for `dronecan_bitrate_kbps` and `dronecan_node_id` to populate controls
- [x] Add Bus Configuration HTML block to `tabs/dronecan.html` (above node table)
- [x] Add Save handler in `tabs/dronecan.js` — write both settings via `MSP2_COMMON_SET_SETTING`, then `MSP_EEPROM_WRITE` + reboot
- [x] Add i18n strings for Bus Configuration labels
- [x] Validate node ID input: warn (don't hard-block) if value is 126 or 127
- Note: getSetting calls must be chained (not concurrent) — two simultaneous MSPV2_SETTING requests cause response race condition

## Completion

- [ ] All success criteria met
- [ ] Wait for PR 2645 (`fix/accordion-duplicate-handlers`) to merge to `maintenance-10.x`
- [ ] Rebase this branch onto updated `maintenance-10.x` — accordion removal commit becomes no-op; drop it with `git rebase -i` before pushing so the DroneCAN PR stays clean
- [ ] PR opened against `maintenance-10.x`
- [ ] Send completion report to manager
