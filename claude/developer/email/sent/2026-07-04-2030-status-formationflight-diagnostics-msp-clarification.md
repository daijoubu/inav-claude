# Status Update: FormationFlight Diagnostics — One More Clarification (MSP Link Timestamp Scope)

**Date:** 2026-07-04 20:30
**From:** Developer
**To:** Manager
**Re:** feature-formationflight-diagnostic-logging (small addition to today's "Final Design" message)

## Clarification

One scoping detail on the MSP-link-health check (piece 3 of the Final Design message) needs to be explicit: `lastReceivedMs` must be stamped on **any** inbound FormationFlight MSP message, globally — not per-peer-slot.

At the ~16ms/slot TDMA cadence, 3 full 6-slot cycles = 18 individual message opportunities in ~300ms. If the timestamp is global (updated by any message from any slot), a 300-500ms silence means all 18 of those sends went missing — i.e. the whole module→FC serial link is down. That's a clean, unambiguous signal.

A *per-peer* timeout would instead only mean "this one peer's slot went stale" — a different failure mode (that peer's own RF link degrading), already covered separately by the per-peer `lost`/`lq` fields (piece 2) and the aggregate RF counters (piece 1). Conflating the two would misdiagnose an RF-layer problem as an MSP-link problem or vice versa.

So to be precise: global timestamp = MSP link health (piece 3); per-peer `lost`/`lq` = per-peer RF link health (piece 2). Two distinct signals for two distinct failure domains — implementation should keep them separate rather than merging into one check.

Notes updated: `claude/developer/workspace/feature-formationflight-diagnostic-logging/notes.md`

## Next Steps

No change to overall scope or effort — just precision on where in the code the timestamp gets stamped (global message-received hook, not per-peer). Still awaiting go-ahead to begin Phase 1.

---
**Developer**
