# Task Assignment: DroneCAN GetNodeInfo Firmware Implementation

**Date:** 2026-05-31 15:00
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-getnodeinfo
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 2-4 hours

## Task

Implement DroneCAN GetNodeInfo service requests in the firmware so that the FC actively fetches node names from newly-discovered nodes and stores them in the node table.

## Background

The DroneCAN configurator tab (in progress) shows node names as blank because the FC only responds to incoming GetNodeInfo requests — it never sends them. The `feature-dronecan-msp-messages` firmware work exposed node names via MSP, but the names are always empty because the FC never asks for them. Implementing this request/response cycle will populate names in the configurator's node table.

## What to Do

1. **Check / update the node table struct** in `dronecan.h` — confirm it has a `name` field (e.g. `char name[UAVCAN_PROTOCOL_GETNODEINFO_RESPONSE_MAX_PATH_LENGTH + 1]` and `uint8_t name_len`); add if missing.

2. **Send the request** — in the NodeStatus handler in `dronecan.c`, when a new node is added to the table, call `canardRequestOrRespond` to send a GetNodeInfo service request to that node:
   - Data type ID: `UAVCAN_PROTOCOL_GETNODEINFO_DATA_TYPE_ID`
   - Signature: `UAVCAN_PROTOCOL_GETNODEINFO_SIGNATURE`
   - Transfer type: `CanardTransferTypeRequest`

3. **Accept the response** — in `shouldAcceptTransfer`, add a case for `UAVCAN_PROTOCOL_GETNODEINFO_SIGNATURE` with `CanardTransferTypeResponse`.

4. **Handle the response** — add `handle_GetNodeInfoResponse(CanardRxTransfer *transfer)`:
   - Decode the response payload using libcanard deserialization
   - Find the node in the table by `transfer->source_node_id`
   - Store `name` / `name_len` in the node table entry

5. **Wire the handler** — in the `CanardTransferTypeResponse` switch in `onTransferReceived`, dispatch to `handle_GetNodeInfoResponse()`.

6. **Build and test** on F7 and H7 targets.

## Files

- `src/main/drivers/dronecan/dronecan.c` — primary implementation
- `src/main/drivers/dronecan/dronecan.h` — possibly, if struct needs updating

## Branch

Use `fix/h7-dronecan-driver` or a new branch based off it.
Do NOT target `master` — PR should target `maintenance-10.x`.

## Success Criteria

- [ ] `handle_GetNodeInfoResponse()` decodes and stores node name correctly
- [ ] GetNodeInfo request sent automatically when a new node is discovered
- [ ] Node names appear in the configurator DroneCAN tab
- [ ] Builds cleanly on F7 and H7 targets
- [ ] No regression in NodeStatus handling

## Project Directory

`claude/projects/active/feature-dronecan-getnodeinfo/`

---
**Manager**
