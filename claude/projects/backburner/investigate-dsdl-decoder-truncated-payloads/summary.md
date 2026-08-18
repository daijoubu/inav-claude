# Project: DSDL-Generated Decoders Silently Accept Truncated/Malformed DroneCAN Payloads

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-08-12
**Estimated Time:** TBD (scope depends on Objective 1 answer)

## Overview

Every scalar-field decode call in the generated DSDL decoders under
`lib/main/Dronecan/dsdlc_generated/` discards the return value of
`canardDecodeScalar()`, so truncated or zero-length DroneCAN payloads decode
as "success" with fields left at whatever the destination struct was
initialized to (typically zero) instead of being rejected.

## Problem

Traced via `uavcan_equipment_gnss_Fix2_decode()`
(`lib/main/Dronecan/dsdlc_generated/src/uavcan.equipment.gnss.Fix2.c:29-44`):
only the two nested `_uavcan_Timestamp_decode()` calls have their result
checked at all, and even that check is defeated —
`_uavcan_Timestamp_decode()` (`uavcan.Timestamp.h:45-54`) unconditionally
`return false` (success) regardless of what `canardDecodeScalar()` reported.
Every other scalar field (longitude, latitude, altitude, velocity,
sats_used, etc.) calls `canardDecodeScalar()` directly and ignores the
return value entirely.

`canardDecodeScalar()` → `descatterTransferPayload()`
(`src/main/drivers/dronecan/libcanard/canard.c:1717-1719`) correctly detects
reads past `transfer->payload_len` and returns 0 — the primitive works. The
failure signal is simply thrown away at every generated call site.

**Net effect:** a completely empty/zero-length DroneCAN payload decodes as a
GNSSFix2 message with `false` (success) and all fields left at zero — a
truncated or corrupted GPS fix from a misbehaving/compromised DroneCAN node
is currently accepted as a "valid" all-zero fix rather than rejected.
Developer spot-checked `uavcan.protocol.NodeStatus.h` and
`uavcan.equipment.power.BatteryInfo.h` and found the identical pattern —
this looks structural to the generator template, not isolated to GNSSFix2.

Found 2026-08-04 by the developer while fixing two weak assertions in
`dronecan_messages_unittest.cc` (`GNSSFix2_ZeroPayload`,
`GNSSFix2_TruncatedBuffer` — both currently `(void)result;`, asserting
nothing) as part of the PR #11607 review-response test audit.

## Objectives

1. **Determine intent first:** is silent truncated-payload acceptance a
   known/accepted limitation (e.g. DroneCAN nodes assumed trusted, or a
   length check happens upstream in `canardHandleRxFrame()`/`on_reception()`
   before decode is even reached), or a genuine gap? This determines
   everything else — do not skip straight to a fix.
2. If a genuine gap: fix belongs in the code generator (or a hand-maintained
   post-processing step) that produces `lib/main/Dronecan/dsdlc_generated/`,
   not a hand-patch to the generated files — it needs to apply to every
   generated message type, not just GNSSFix2.
3. Once intent is settled, fix `GNSSFix2_ZeroPayload` and
   `GNSSFix2_TruncatedBuffer` in `dronecan_messages_unittest.cc` to assert
   the actual (correct) contract instead of `(void)result;`.

## Scope

**In Scope:**
- `lib/main/Dronecan/dsdlc_generated/` decode return-value handling
  (generator or post-processing step, not hand-patched generated files)
- `_uavcan_Timestamp_decode()` and other shared decode helpers
- `dronecan_messages_unittest.cc` assertions once intent is known

**Out of Scope:**
- `canardDecodeScalar()` / `descatterTransferPayload()` themselves —
  confirmed already correct
- Re-auditing every generated message type exhaustively (developer
  spot-checked 3; a fix at the generator/helper level should cover all)

## Related Work

- Discovered during the same test-suite audit as
  [[fix-fragile-unittest-mirrors]] (same day, same PR #11607 review
  response, unrelated code path).
- Parent context: `fix-dronecan-driver-rework` (PR #11607, currently
  blocked pending re-review/soak test) — this finding doesn't block that
  PR.

## Success Criteria

- [ ] Answered: known limitation vs. genuine gap, with reasoning documented
- [ ] If gap: generator/helper fix implemented, covers all generated
      message types (not just GNSSFix2)
- [ ] `GNSSFix2_ZeroPayload` / `GNSSFix2_TruncatedBuffer` assert the correct
      contract
- [ ] PR opened against the correct base branch (if code change needed)

## Estimated Time

TBD — investigation first (1-2 hours), fix scope depends on answer

## Priority Justification

HIGH: if this is a genuine gap, it means INAV currently accepts a corrupted
or truncated sensor reading (GPS position, battery state, etc.) from any
DroneCAN node as valid data rather than rejecting it — a data-integrity
issue with direct flight-safety relevance, and structural (affects every
generated message type) rather than a one-off. Not CRITICAL because no
field incident has been attributed to this yet and it requires a
misbehaving/corrupted node to trigger.
