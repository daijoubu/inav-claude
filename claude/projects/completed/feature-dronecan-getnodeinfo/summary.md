# Project: DroneCAN GetNodeInfo Firmware Implementation

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Feature
**Created:** 2026-05-31
**Estimated Time:** 2-4 hours

## Overview

Implement DroneCAN GetNodeInfo service requests in the INAV firmware so that node names are fetched from discovered nodes and stored in the node table. This makes node names visible in the configurator DroneCAN tab (currently blank).

## Problem

The DroneCAN tab in the configurator shows node names as blank because the FC only responds to incoming GetNodeInfo requests — it never sends them. Node names are only available via a GetNodeInfo service response, which requires the FC to actively request them from each discovered node.

## Objectives

1. Send a GetNodeInfo request when a new node is first discovered (in the NodeStatus handler)
2. Decode the GetNodeInfo response and store the node name in the node table
3. Register the GetNodeInfo response signature in `shouldAcceptTransfer`
4. Wire the response handler into the `CanardTransferTypeResponse` switch in `onTransferReceived`

## Scope

**In Scope:**
- Firmware-side GetNodeInfo request/response handling in `dronecan.c`
- Storing `name` / `name_len` in the existing node table struct
- Updating `dronecan.h` if the struct needs a name field added

**Out of Scope:**
- Configurator UI changes (already handled in `feature-dronecan-configurator-tab`)
- GetTransportStats or other node services

## Implementation Steps

1. In the NodeStatus handler, when a new node is added to the table, call `canardRequestOrRespond` to send a GetNodeInfo request to that node's ID
2. Add `handle_GetNodeInfoResponse()` function to decode the response payload and store `name`/`name_len` in the node table entry
3. Register `UAVCAN_PROTOCOL_GETNODEINFO_SIGNATURE` in `shouldAcceptTransfer` for `CanardTransferTypeResponse`
4. In the `CanardTransferTypeResponse` switch in `onTransferReceived`, dispatch to `handle_GetNodeInfoResponse()`
5. Build and test against at least one hardware target (F7 or H7)

## Files

- `src/main/drivers/dronecan/dronecan.c` — primary implementation
- `src/main/drivers/dronecan/dronecan.h` — possibly, if node table struct needs `name` field

## Branch

`fix/h7-dronecan-driver` (or a new branch based off it)

## Success Criteria

- [ ] `handle_GetNodeInfoResponse()` decodes and stores node name
- [ ] GetNodeInfo request is sent automatically when a new node is discovered
- [ ] Node names appear in the configurator DroneCAN tab (Phase 3 row expansion shows name)
- [ ] Builds cleanly on F7 and H7 targets
- [ ] No regression in existing NodeStatus handling

## Estimated Time

2-4 hours

## Priority Justification

Directly unblocks Phase 3 of `feature-dronecan-configurator-tab` (per-node detail view). Without node names, the tab shows blank entries which reduces its value to users.
