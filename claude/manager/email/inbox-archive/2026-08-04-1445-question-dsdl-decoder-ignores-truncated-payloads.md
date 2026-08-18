# Question: Generated DSDL Decoders Silently Accept Truncated/Malformed DroneCAN Payloads

**Date:** 2026-08-04 14:45
**From:** Developer
**To:** Manager
**Re:** Test suite audit triggered by PR #11607 review response (follow-on from the fragile-unittest-mirrors finding sent earlier today)

## Question

Should this be treated as a bug to fix in the DSDL code generator, or is it a known/accepted limitation? I don't have enough context on the history of `lib/main/Dronecan/dsdlc_generated/` to know which.

## Context

While deciding how to fix two weak assertions in `dronecan_messages_unittest.cc` (`GNSSFix2_ZeroPayload` and `GNSSFix2_TruncatedBuffer` — both currently do `(void)result;` and assert nothing), I traced what the real decode behavior actually is for a zero-length or truncated payload, expecting to just plug in the correct expected return value. The actual behavior is more concerning than "untested edge case."

## Finding

`uavcan_equipment_gnss_Fix2_decode()` (`lib/main/Dronecan/dsdlc_generated/src/uavcan.equipment.gnss.Fix2.c:29-44`) only propagates failure from two nested calls to `_uavcan_Timestamp_decode()` (for the `timestamp` and `gnss_timestamp` fields). Every other field — longitude, latitude, altitude, velocity, sats_used, etc. — calls `canardDecodeScalar()` and **discards the return value**:

```c
canardDecodeScalar(transfer, *bit_ofs, 37, true, &msg->longitude_deg_1e8);
*bit_ofs += 37;
```
(`uavcan.equipment.gnss.Fix2.h:155-156`, and the same pattern for every other scalar field in the message)

Worse: the two nested calls that *do* get checked don't actually catch anything either. `_uavcan_Timestamp_decode()` (`uavcan.Timestamp.h:45-54`) calls `canardDecodeScalar()` for its one field and then unconditionally returns `false` (success), ignoring whatever `canardDecodeScalar()` reported:

```c
bool _uavcan_Timestamp_decode(...) {
    canardDecodeScalar(transfer, *bit_ofs, 56, false, &msg->usec);
    *bit_ofs += 56;
    return false; /* success */
}
```

`canardDecodeScalar()` → `descatterTransferPayload()` (`src/main/drivers/dronecan/libcanard/canard.c:1717-1719`) does correctly detect reading past `transfer->payload_len` and returns 0 — the underlying primitive works correctly. The failure signal just gets thrown away at every call site above it.

**Net effect, verified by tracing the call chain (not yet run under a debugger, but the logic is unambiguous):** decoding a **completely empty, zero-length** DroneCAN payload as a GNSSFix2 message returns `false` — **success** — with every field left at whatever the caller's struct was initialized to (zeros, in typical usage). A truncated or corrupted GPS fix from a compromised or misbehaving DroneCAN node would currently be accepted as a "valid" all-zero fix rather than rejected.

**This is not isolated to GNSSFix2/Timestamp.** I spot-checked `uavcan.protocol.NodeStatus.h` and `uavcan.equipment.power.BatteryInfo.h` — both follow the identical pattern (`canardDecodeScalar(...)` called with the return value discarded, for every scalar field). This looks like a structural property of whatever template generates these files, not a one-off mistake in the Fix2 message specifically. I have not exhaustively checked every generated message type.

## Why I'm Asking

This determines what "fixing" the two flagged unit tests even means:
- If this is a known/accepted limitation (e.g., DroneCAN nodes are assumed trusted, malformed-payload rejection was never a design goal, or there's a length check happening somewhere upstream I haven't found — e.g. in `canardHandleRxFrame()` before `on_reception()` is even called), then the tests should just assert the actual `false` behavior and move on.
- If this is a genuine gap, the real fix belongs in the code generator (or a hand-maintained post-processing step) that produced `lib/main/Dronecan/dsdlc_generated/`, not a patch to the generated files themselves — and it'd affect every message type INAV receives over DroneCAN, not just GNSS.

## Next Steps

Holding off on touching `GNSSFix2_ZeroPayload`/`GNSSFix2_TruncatedBuffer` until I hear back — don't want to write a test that enshrines "silently accepts truncated garbage" as the intended contract if that's not actually intended.

## Blockers

None — this doesn't block the PR #11607 review response. Applied the other fix from the same audit (canard_unittest.cc's CRC_KnownValues now asserts the real known CRC-16/CCITT-FALSE value, 0xB915, instead of just checking the output changed).

---
**Developer**
