# Status Update: FormationFlight Diagnostics — Final Design (supersedes prior 2 messages on MSP link health)

**Date:** 2026-07-04 20:28
**From:** Developer
**To:** Manager
**Re:** feature-formationflight-diagnostic-logging

## Summary — Full Current Design (all iterations folded in)

Still **Option A (MSP-to-blackbox)**. Final scope, after user review, has three pieces:

1. **Aggregate RF counters** (original task scope): packetsReceived, packetsBadCrc, packetsBadSize, packetsBadValidation, peer count — new MSP message from FormationFlight to INAV, logged to blackbox slow frame (mirrors the feature-canbus-errors-blackbox precedent).

2. **Per-peer lost/age state** (first addendum, unchanged): add `peer_t.lost` (and `lq`) to the same new message — lets the blackbox show exactly when a peer's radar entry goes stale.

3. **MSP link (module→FC) health — final design, no new message field needed:** Two prior proposals for this were superseded during review:
   - Originally proposed an ACK-based heartbeat — rejected: the module can't act on a detected failure, and a "link is down" report can't reliably travel over the same link it's reporting as down.
   - Then proposed a monotonic send-counter — superseded by something simpler.
   - **Final design:** INAV already has no timestamp on `radar_pois_t` at all today, so add one. Stamp `lastReceivedMs = millis()` in the existing MSP handler (`fc_msp.c`, `mspFcProcessInCommand()`, `SET_RADAR_POS` case and/or the new diagnostics case) whenever a message arrives — arrival itself is the "link is up" signal, no new field required from FormationFlight. At blackbox slow-frame time, compute elapsed time since last receipt and compare to a threshold.
   - **Threshold: 300-500ms**, set by the user directly. FormationFlight's per-peer relay cadence is ~96-100ms (confirmed from code: 6-slot TDMA round, ~16ms/slot spacing), so 300-500ms is ~3-5 missed cycles — absorbs normal single-cycle jitter while still catching a real sustained link loss quickly. User's rationale: "missing 3 messages is a problem."
   - Net effect: this piece needs **zero new bytes sent from FormationFlight** — it's entirely a receive-side timestamp-and-threshold check on the INAV side.

## Why So Much Back-and-Forth

The MSP-link-health piece went through 3 design iterations in review before landing here, each simpler and lower-risk than the last. Documenting this so the design history is clear if anyone revisits it later — this final version has no ACK/heartbeat scheduling complexity and no new wire-format bytes for the link-health piece, just a timestamp and a threshold compare using data already flowing.

## Full Detail

`claude/developer/workspace/feature-formationflight-diagnostic-logging/notes.md` has the complete research trail, code references, and rejected-alternative rationale for anyone who wants the full history.

## Next Steps

This is the complete, final Phase 0 scope. Awaiting a single go-ahead to begin Phase 1 implementation.

---
**Developer**
