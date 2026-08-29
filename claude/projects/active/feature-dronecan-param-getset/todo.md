# Todo: DroneCAN Node Parameter Get/Set

## Branch

Base on `fix/h7-dronecan-driver` alongside `feature-dronecan-getnodeinfo`.
Rebase onto `maintenance-10.x` before opening PR.

---

## Phase 1: Pending Slot Struct (dronecan.h)

- [ ] Add state enum to `dronecan.h`:
  ```c
  typedef enum {
      DRONECAN_PARAM_IDLE = 0,
      DRONECAN_PARAM_PENDING,
      DRONECAN_PARAM_READY,
      DRONECAN_PARAM_ERROR,
  } dronecanParamState_e;
  ```
- [ ] Add `dronecanParamPending_t` struct:
  - `dronecanParamState_e state`
  - `uint8_t node_id`
  - `uint16_t index`
  - `uint8_t type` (EMPTY/INT/FLOAT/BOOL/STRING from libcanard Value union tag)
  - `int64_t value_int`
  - `float value_float`
  - `uint8_t value_bool`
  - `char value_str[64]`
  - `char name[93]` (UAVCAN param name max length)
  - `uint8_t name_len`
  - `uint32_t requested_at_ms` (for 2-second timeout)
- [ ] Declare `extern dronecanParamPending_t dronecanParamPending` in `dronecan.h`

## Phase 2: Request Sender (dronecan.c)

- [ ] Add `dronecanParamPending_t dronecanParamPending` static in `dronecan.c`, zero-initialised
- [ ] Add `dronecanParamRequest(uint8_t node_id, uint16_t index, uavcan_protocol_param_Value *value_or_null)`:
  - If `state == PENDING` and not timed out: return false (busy)
  - Encode `uavcan_protocol_param_GetSet_Request` with `index` and `value` (empty tag if null)
  - Call `canardRequestOrRespond` with `UAVCAN_PROTOCOL_PARAM_GETSET_SIGNATURE` and `UAVCAN_PROTOCOL_PARAM_GETSET_ID`
  - Set `state = PENDING`, record `node_id`, `index`, `requested_at_ms = millis()`
  - Return true
- [ ] In the scheduler task or `processDroneCANTasks`, add timeout check: if `state == PENDING` and `millis() - requested_at_ms > 2000`, set `state = ERROR`

## Phase 3: Accept Filter (dronecan.c)

- [ ] In `shouldAcceptTransfer`, add to `CanardTransferTypeResponse` block:
  ```c
  case UAVCAN_PROTOCOL_PARAM_GETSET_ID:
      *out_data_type_signature = UAVCAN_PROTOCOL_PARAM_GETSET_SIGNATURE;
      return true;
  ```

## Phase 4: Response Handler (dronecan.c)

- [ ] Add `handle_ParamGetSetResponse(CanardInstance *ins, CanardRxTransfer *transfer)`:
  - If `dronecanParamPending.state != PENDING`: return (stale or unsolicited)
  - If `transfer->source_node_id != dronecanParamPending.node_id`: return
  - Decode with `uavcan_protocol_param_GetSet_Response_decode`
  - Copy name, name_len (cap at 92)
  - Inspect value union tag, populate the appropriate typed field in pending slot
  - Set `state = READY`
- [ ] Dispatch from `CanardTransferTypeResponse` switch in `onTransferReceived`

## Phase 5: MSP Commands (fc_msp.c)

Two new MSP2 message IDs — allocate from the INAV MSP2 range.

### MSP2_INAV_DRONECAN_PARAM_REQUEST (write command)

Payload in: `node_id (u8) | param_index (u16) | is_write (u8) | value_type (u8) | value (variable)`

- [ ] Decode node_id, index, is_write flag, value type and value
- [ ] If `is_write`: populate a `uavcan_protocol_param_Value` from the MSP payload
- [ ] Call `dronecanParamRequest(node_id, index, value_or_null)`
- [ ] Return: `status (u8)` — 0=accepted, 1=busy, 2=dronecan_not_ready

### MSP2_INAV_DRONECAN_PARAM_RESULT (read command)

Payload in: none (or optionally node_id for validation)

- [ ] Read `dronecanParamPending` state
- [ ] Return: `state (u8) | node_id (u8) | index (u16) | name_len (u8) | name[name_len] | value_type (u8) | value (variable)`
- [ ] If READY: reset `state = IDLE` after returning (consume the result)

## Phase 6: Configurator — MSP Layer (MSPHelper.js)

- [ ] Add `MSP2_INAV_DRONECAN_PARAM_REQUEST` encoder:
  - Packs node_id, index, is_write, value_type, value bytes
- [ ] Add `MSP2_INAV_DRONECAN_PARAM_RESULT` decoder:
  - Returns `{state, node_id, index, name, value_type, value}`
- [ ] Add helper `dronecanParamPoll(node_id, index, resolve, reject)`:
  - Polls RESULT every 75ms, resolves on READY, rejects on ERROR or after 2.5s

## Phase 7: Configurator — UI (dronecan.js)

- [ ] In the node detail panel, add a "Parameters" section
- [ ] "Load parameters" button — iterates index 0, 1, 2… sending REQUEST (read) and polling RESULT for each, until response name is empty (signals end of list); builds a table
- [ ] Each row: index, name, type, current value, editable input, "Write" button
- [ ] "Write" flow: send REQUEST (write) with new value, poll RESULT, show success/failure badge
- [ ] Disable "Write" while any operation is PENDING
- [ ] Add i18n keys for new UI strings

## Phase 8: Build & Test

- [ ] Build on F4 target (no regression)
- [ ] Build on F7 target
- [ ] Build on H7 target (KAKUTEH7WING)
- [ ] Read a parameter from a real DroneCAN node — verify name, type, value
- [ ] Write a parameter — confirm value persists (re-read after write)
- [ ] Confirm REQUEST while PENDING returns busy (not silent corruption)
- [ ] Confirm 2-second timeout resets slot to ERROR correctly

## Rebase (unblocked 2026-08-21 — PR #11607 merged)

`feature/dronecan-param-getset` is the base of the remaining DroneCAN stack
(`feature/dronecan-dna-server` and `fix/dronecan-gps-health-guard` both
build on top of it — confirmed via `git merge-base` 2026-08-21). Rebase
this one first so the others have a clean branch to rebase onto in turn.

- [x] Rebase `feature/dronecan-param-getset` onto `upstream/maintenance-10.x`
- [x] Force-push, confirm PR #11683 diff is now clean (only this branch's
      own commits vs. `maintenance-10.x`)
- [x] Full build matrix (F4/F7/H7/AT32/SITL) clean post-rebase
- [x] Notify manager once done — `feature-dronecan-dna-server` and
      `review-dronecan-gps-node-health` are both waiting on this rebase
      landing before they can rebase in turn

## Firmware PR #11683 — MERGED 2026-08-28

Merged into `maintenance-10.x` (24 files, +3173/-861). Covers Phases 1-5
(pending slot, request sender, accept filter, response handler, MSP
commands) plus GetNodeInfo/ExecuteOpcode/RestartNode via the async slot.

## Configurator PR #2671 — OPEN, awaiting review/merge

`iNavFlight/inav-configurator#2671`, base `maintenance-10.x`, not draft,
mergeable, all 8 CI checks green, no review decision yet as of 2026-08-28.
Covers Phases 6-7 (MSPHelper.js encode/decode, dronecan.js parameter
list/edit UI). Project stays open until this merges — do not mark
Phase 8 build/test criteria complete until then.

## Completion

- [ ] All success criteria met
- [ ] Send completion report to manager
