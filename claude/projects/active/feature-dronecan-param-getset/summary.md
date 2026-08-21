# Project: DroneCAN Node Parameter Get/Set

**Status:** 🚫 BLOCKED — was stale at 📋 TODO; code complete, zero CRITICAL/HIGH findings, PR #11683 open in draft, stacked on unmerged #11607, no dev work pending until it merges (user reviewing before dropping draft). Reclassified from IN PROGRESS 2026-07-07.
**Priority:** MEDIUM-HIGH
**Type:** Feature
**Created:** 2026-06-02
**Estimated Time:** 4-6 hours

## Overview

Implement DroneCAN node parameter read/write support in firmware and configurator, using the `uavcan.protocol.param.GetSet` service. Allows the user to read and change configuration parameters on any DroneCAN node (e.g. node ID, bitrate, sensor tuning) directly from the INAV configurator without external tooling.

## Problem

DroneCAN nodes (GPS receivers, ESCs, airspeed sensors, etc.) expose their configuration via the `uavcan.protocol.param.GetSet` service. Currently INAV has no mechanism to read or write these parameters — users must use a separate tool (e.g. DroneCAN GUI Tool or PX4) to configure DroneCAN nodes, even when the FC is the only host on the bus.

## Design: Single Pending Slot (Option A)

DroneCAN service requests are asynchronous — the FC sends a request and the node replies in a later CAN frame. MSP is synchronous and cannot block the scheduler waiting for a CAN reply.

Solution: the FC maintains a **single in-flight parameter slot** (one small struct, ~100 bytes). MSP commands follow a request/poll pattern:

1. **REQUEST** — configurator sends `{node_id, param_index, value_or_empty}`. FC sends the DroneCAN GetSet service request and returns immediately with state=PENDING.
2. **RESULT** — configurator polls with `{node_id}`. FC returns state (PENDING/READY/ERROR) plus the parameter data when ready. Configurator retries every 50–100ms; typical node response is <20ms.

Write and read both use the same flow — DroneCAN GetSet with a non-empty value is a write, with an empty value is a read; the response always echoes the current value.

Only one parameter operation can be in flight at a time. A new REQUEST from a different node or index while PENDING will return an error; configurator must wait for RESULT or timeout.

## Objectives

1. Add `dronecanParamPending_t` pending slot to firmware state
2. Implement MSP REQUEST command: trigger CAN service request, park state
3. Implement MSP RESULT command: return pending state and decoded param
4. Register GetSet response in `shouldAcceptTransfer` and route it to the response handler
5. Add configurator UI for parameter browsing and editing on the DroneCAN tab

## Scope

**In Scope:**
- Firmware: pending slot struct, request sender, response decoder
- Firmware: two new MSP2 message IDs (REQUEST and RESULT)
- Configurator: parameter list/edit UI on the DroneCAN tab detail panel
- Supports param types: integer (int64), float, boolean, string

**Out of Scope:**
- Enumerating all parameters on a node (the configurator drives index iteration)
- Saving/restoring node configs to a file
- Multi-node simultaneous parameter operations

## Relationship to feature-dronecan-getnodeinfo

Follow-on to `feature-dronecan-getnodeinfo`. May be combined into the same PR at developer discretion — both touch `dronecan.c`, `fc_msp.c`, and the configurator DroneCAN tab. If combined, the getnodeinfo GetNodeInfo response handler and the GetSet response handler share the same `CanardTransferTypeResponse` dispatch block.

## Files

**Firmware:**
- `src/main/drivers/dronecan/dronecan.c` — pending slot, request sender, response handler
- `src/main/drivers/dronecan/dronecan.h` — `dronecanParamPending_t` struct, state enum
- `src/main/msp/fc_msp.c` — two new MSP2 command handlers

**Configurator:**
- `src/js/msp/MSPHelper.js` — encode REQUEST, decode RESULT
- `src/js/tabs/dronecan.js` — parameter list/edit UI in detail panel

## Branch

Base off `fix/h7-dronecan-driver` alongside `feature-dronecan-getnodeinfo`, or off `maintenance-10.x` after that branch merges. PR target: `maintenance-10.x`.

## Success Criteria

- [ ] Reading a parameter by index returns correct name, type, and value from a real node
- [ ] Writing a parameter updates the node (confirmed by re-reading after write)
- [ ] A new REQUEST while PENDING returns an error (not silent corruption)
- [ ] Slot resets to IDLE after RESULT is read or after a 2-second timeout
- [ ] Builds cleanly on F4, F7, and H7 targets
- [ ] No regression in NodeStatus or GetNodeInfo handling

## Estimated Time

4-6 hours

## Priority Justification

Closes the last gap in DroneCAN node management from the configurator. Without it, nodes cannot be configured without external tools, limiting the DroneCAN tab's practical utility to read-only monitoring.
