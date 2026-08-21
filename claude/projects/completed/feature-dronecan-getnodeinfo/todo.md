# Todo: DroneCAN GetNodeInfo Firmware Implementation

## Branch

Base on `fix/h7-dronecan-driver`. Rebase onto `maintenance-10.x` once that branch merges.

## Phase 1: Extend Node Table Struct

- [ ] Add version fields to `dronecanNodeInfo_t` in `dronecan.h`:
  - `uint8_t sw_major`
  - `uint8_t sw_minor`
  - `uint8_t sw_optional_field_flags`
  - `uint32_t sw_vcs_commit`
  - `uint8_t hw_major`
  - `uint8_t hw_minor`
  - `uint8_t hw_unique_id[16]`
- [ ] Zero-initialise all new fields in the "new node" block of `handle_NodeStatus`

## Phase 2: Request Side

- [ ] In `handle_NodeStatus`, after adding a new node, send a GetNodeInfo request:
  - Call `canardRequestOrRespond` with `CanardTransferTypeRequest`
  - Use `UAVCAN_PROTOCOL_GETNODEINFO_SIGNATURE` and `UAVCAN_PROTOCOL_GETNODEINFO_ID`
  - Transfer priority: `CANARD_TRANSFER_PRIORITY_LOW`
  - Zero-length payload (GetNodeInfo request is empty)

## Phase 3: Accept Filter

- [ ] In `shouldAcceptTransfer`, add `CanardTransferTypeResponse` handling for
  `UAVCAN_PROTOCOL_GETNODEINFO_ID` so response packets are accepted

## Phase 4: Response Handler

- [ ] Add `handle_GetNodeInfoResponse(CanardInstance *ins, CanardRxTransfer *transfer)`:
  - Decode with `uavcan_protocol_GetNodeInfoResponse_decode`
  - Find node in table by `transfer->source_node_id`
  - Store `name` / `name_len` (cap at 32)
  - Store `sw_major`, `sw_minor`, `sw_optional_field_flags`, `sw_vcs_commit`
  - Store `hw_major`, `hw_minor`, `hw_unique_id[16]`
- [ ] Dispatch from `CanardTransferTypeResponse` switch in `onTransferReceived`

## Phase 5: Extend MSP Message

- [ ] In `fc_msp.c`, `MSP2_INAV_DRONECAN_NODE_INFO` handler — append after existing 46 bytes:
  - `sbufWriteU8(dst, node->sw_major)`
  - `sbufWriteU8(dst, node->sw_minor)`
  - `sbufWriteU8(dst, node->sw_optional_field_flags)`
  - `sbufWriteU32(dst, node->sw_vcs_commit)`
  - `sbufWriteU8(dst, node->hw_major)`
  - `sbufWriteU8(dst, node->hw_minor)`
  - `sbufWriteData(dst, node->hw_unique_id, 16)`
  - Update size guard from `< 46` to `< 71`
  - New total: 71 bytes

## Phase 6: Update Configurator

- [ ] In `MSPHelper.js`, extend `MSP2_INAV_DRONECAN_NODE_INFO` decoder to parse bytes 46–70:
  - `sw_major`, `sw_minor`, `sw_optional_field_flags`, `sw_vcs_commit`
  - `hw_major`, `hw_minor`, `hw_unique_id[16]`
  - Guard on `data.byteLength >= 71`
- [ ] In `dronecan.js` `showDetail()`, add rows for:
  - Software Version: `sw_major.sw_minor` (+ vcs commit if `optional_field_flags & 0x01`)
  - Hardware Version: `hw_major.hw_minor`
  - Unique ID: hex string of `hw_unique_id`
- [ ] Add i18n keys for new detail rows

## Phase 7: Build & Test

- [ ] Build on F7 target
- [ ] Build on H7 target (KAKUTEH7WING)
- [ ] Test against real DroneCAN node — verify name and version appear in configurator detail panel
- [ ] Confirm no regression in NodeStatus update path

## Completion

- [ ] All success criteria met
- [ ] Send completion report to manager

## Future Optimization (post-ship)

The version fields in `dronecanNodeInfo_t` (25 bytes × 32 nodes = 800 bytes) plus the
name cache (33 bytes × 32 = 1056 bytes) are statically allocated RAM that is only
consumed during configuration, never during flight. Acceptable on H7/F7 targets, but
worth revisiting in an optimization pass. Candidate approach: drop version fields from
the per-node struct and replace with a single-slot detail cache (one GetNodeInfo
response for the last-queried node, ~40 bytes total). MSP handler returns cached data
if fresh and node ID matches, otherwise returns zeroes and triggers a new CAN request;
configurator polls after ~200ms. See discussion in session 2026-06-01.
