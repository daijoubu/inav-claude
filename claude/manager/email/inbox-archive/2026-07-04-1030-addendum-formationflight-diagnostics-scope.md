# Status Update: FormationFlight Diagnostics — Scope Addendum

**Date:** 2026-07-04 10:30
**From:** Developer
**To:** Manager
**Re:** feature-formationflight-diagnostic-logging (addendum to today's earlier Phase 0 recommendation)

## Why This Addendum

After sending the Phase 0 recommendation (Option A, MSP-to-blackbox), the user clarified the actual motivating symptom: their FormationFlight marker sometimes doesn't appear in INAV when flying with a friend. The originally-scoped aggregate RF counters (packetsReceived/BadCrc/BadSize/BadValidation) only cover one possible cause. User asked to add two more data points to the Phase 1 scope before implementation starts.

## Addition 1: Per-peer lost/age state

`peer_t` (FormationFlight's `PeerManager.h`) already tracks per-peer `lost`, `lq`, `rssi`, and `updated` (last-update timestamp) — none of this currently reaches the FC, only position/heading/speed/lq via `sendRadar()`. Adding `lost` (and `lq`) to the new diagnostics message would let the blackbox log show exactly when INAV's `radar_pois[]` entry for a peer goes stale — the most direct explanation for "marker sometimes not there" if RF counters look clean.

Side finding, flagged for awareness only (not in scope): INAV's `RADAR_MAX_POIS` is 5 vs. FormationFlight's `NODES_MAX` of 6 — a mismatch that doesn't matter for a 2-person flight but would matter in a larger group.

## Addition 2: MSP link (module→FC) health tracking

Confirmed by code read: `sendRadar()`/`sendLocation()` use fire-and-forget MSP sends (`command2(..., waitACK=false)`), which always return success regardless of whether the FC actually received them — there is currently zero visibility into module→FC serial link health, a separate failure domain from the ESP-NOW RF link between modules. A marker could disappear because this link glitched even with perfectly healthy ESP-NOW.

Can't simply switch every high-frequency radar send to a blocking ACKed call (would stall the loop up to 100ms per send on the existing tight per-peer schedule, risking missed incoming RF packets — the cure would be worse than the disease). Proposed approach: a separately-scheduled, low-frequency (every 2-5s) ACKed health-check request reusing the existing `request()`/`waitFor()` mechanism (same pattern already used once at startup in `getFCVariant()`), tracking a cumulative failure counter and/or time-since-last-success, reported via the new diagnostics message.

## Net Effect on Phase 1 Scope

Still Option A (MSP-to-blackbox) — no change to the overall approach or the blackbox.c coordination note from the earlier message. This just adds two more fields to the new diagnostics struct/message: per-peer lost state, and MSP link failure count/recency. Slightly larger MSPManager.cpp change (new low-frequency scheduled health check) but same overall shape and effort class as originally scoped.

Full detail added to the workspace notes: `claude/developer/workspace/feature-formationflight-diagnostic-logging/notes.md`

## Next Steps

Awaiting a single go-ahead covering both the original Option A recommendation and this addendum before starting Phase 1 implementation.

---
**Developer**
