# Task Assignment: DroneCAN Node Parameter Get/Set

**Date:** 2026-06-02 12:00
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-param-getset
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 4-6 hours

## Task

Implement DroneCAN node parameter read/write support using `uavcan.protocol.param.GetSet`. This allows the configurator to read and change configuration parameters on any DroneCAN node directly from the INAV UI.

## Background

DroneCAN nodes expose their configuration via the `uavcan.protocol.param.GetSet` service — a standard request/response service where an empty value = read, a non-empty value = write, and the response always echoes the current value. Currently INAV has no way to access these parameters; users need external tools.

The key design constraint is that DroneCAN service responses are asynchronous but MSP is synchronous. We solve this with a **single in-flight pending slot** (~100 bytes) — no per-node parameter cache needed.

## Design: Single Pending Slot (Option A)

1. MSP REQUEST command — configurator sends `{node_id, param_index, value_or_empty}`. FC sends the DroneCAN GetSet request and returns immediately with state=PENDING.
2. MSP RESULT command — configurator polls (every ~75ms). FC returns state (PENDING/READY/ERROR) plus decoded parameter data when ready.
3. A new REQUEST while PENDING returns busy. Firmware-side 2-second timeout resets slot to ERROR. RESULT read consumes the slot (resets to IDLE).

## What to Do

Full task breakdown is in the project directory. High-level phases:

1. **dronecan.h** — Add `dronecanParamState_e` enum and `dronecanParamPending_t` struct
2. **dronecan.c** — Add static pending slot, `dronecanParamRequest()` sender, 2-second timeout check in scheduler task
3. **dronecan.c** — Register `UAVCAN_PROTOCOL_PARAM_GETSET_ID` in `shouldAcceptTransfer` for `CanardTransferTypeResponse`
4. **dronecan.c** — Add `handle_ParamGetSetResponse()` decoder, dispatch from `onTransferReceived`
5. **fc_msp.c** — Two new MSP2 commands: `MSP2_INAV_DRONECAN_PARAM_REQUEST` and `MSP2_INAV_DRONECAN_PARAM_RESULT`
6. **MSPHelper.js** — Encoder for REQUEST, decoder for RESULT, `dronecanParamPoll()` helper
7. **dronecan.js** — Parameter list/edit UI in the node detail panel
8. Build and test on F4, F7, H7 — read and write a real parameter on a real node

## Relationship to feature-dronecan-getnodeinfo

Follow-on to getnodeinfo — both touch `dronecan.c`, `fc_msp.c`, and the configurator DroneCAN tab. You may combine them into a single PR at your discretion. If combined, the GetNodeInfo and GetSet response handlers share the same `CanardTransferTypeResponse` dispatch block.

## Success Criteria

- [ ] Reading a parameter by index returns correct name, type, and value from a real node
- [ ] Writing a parameter updates the node (confirmed by re-reading after write)
- [ ] REQUEST while PENDING returns busy (not silent corruption)
- [ ] Slot resets to IDLE after RESULT is read, or after 2-second timeout → ERROR
- [ ] Builds cleanly on F4, F7, and H7 targets
- [ ] No regression in NodeStatus or GetNodeInfo handling

## Project Directory

`claude/projects/active/feature-dronecan-param-getset/`

## Branch

Base on `fix/h7-dronecan-driver` alongside `feature-dronecan-getnodeinfo`. PR target: `maintenance-10.x`.

---
**Manager**
