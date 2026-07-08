# Project Request: DroneCAN GetNodeInfo Firmware Implementation

**Date:** 2026-05-31 00:00
**From:** Developer
**To:** Manager
**Type:** Project Request

## Request

Please create a project for implementing DroneCAN GetNodeInfo service requests in the firmware so node names can be populated in the configurator DroneCAN tab.

## Background

The DroneCAN tab currently shows node names as blank. The FC only responds to incoming GetNodeInfo requests but never sends them to other nodes. Node names are only available via the GetNodeInfo service response.

## Work Required (firmware - dronecan.c)

1. When a new node is discovered (in the NodeStatus handler), send a GetNodeInfo service request to that node via `canardRequestOrRespond`
2. Add `handle_GetNodeInfoResponse()` to decode the response and store `name`/`name_len` in the node table
3. Register `UAVCAN_PROTOCOL_GETNODEINFO_SIGNATURE` in `shouldAcceptTransfer` for responses
4. Wire the handler into the empty `CanardTransferTypeResponse` switch in `onTransferReceived`

## Files

- `src/main/drivers/dronecan/dronecan.c`
- `src/main/drivers/dronecan/dronecan.h` (possibly, if struct needs updating)

## Branch

Should target `fix/h7-dronecan-driver` or a new branch off it.

---
**Developer**
