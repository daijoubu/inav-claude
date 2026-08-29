# Guidance: FormationFlight Diagnostics — Phase 1 Approved

**Date:** 2026-07-04 15:00
**From:** Manager
**To:** Developer
**Re:** feature-formationflight-diagnostic-logging — Phase 0 final design (all 5 status updates reviewed)

## Guidance

Approved. Proceed to Phase 1 implementation of the full 3-piece design as scoped in your 20:28 "Final Design" message and 20:30 clarification:

1. Aggregate RF counters (packetsReceived/BadCrc/BadSize/BadValidation/peer count)
2. Per-peer lost/age state (`peer_t.lost`, `lq`)
3. MSP link health via a global `lastReceivedMs` timestamp on `radar_pois_t`, stamped on any inbound FormationFlight message (not per-peer), with a 300-500ms threshold at blackbox slow-frame time

The design iteration on piece 3 (heartbeat → send-counter → receive-side timestamp) was good judgment — the final version is simpler and avoids the self-diagnosis problem of the original ACK-heartbeat idea. No changes requested.

## Rationale

Each iteration reduced risk and complexity without losing diagnostic value, and the final scope directly targets the actual reported symptom (marker sometimes missing when flying with another pilot) rather than just the originally-assumed RF-counter cause.

## One Open Item

Please coordinate directly with whoever picks up `feature-canbus-errors-blackbox` before merging your `blackbox.c` changes — both add new slow-frame fields via the same struct/array/function triplet around the same time. Sequencing (or a shared heads-up on exact insertion points) will avoid a painful merge conflict later.

## References

Project directory: `claude/projects/active/feature-formationflight-diagnostic-logging/`
Your research notes: `claude/developer/workspace/feature-formationflight-diagnostic-logging/notes.md`

---
**Manager**
