# Project: FormationFlight Post-Flight Packet Diagnostics

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-07-04
**Estimated Time:** TBD — Phase 0 complete, Phase 1 implementation approved 2026-07-04

## Overview

Give FormationFlight (external ESP-NOW drone swarm/formation telemetry project, https://github.com/FormationFlight/FormationFlight) a way to persist packet-reception diagnostics so problems can be troubleshot after a flight, not just observed live.

## Problem

Confirmed via code research 2026-07-04 (repo at v5.0.0/master): FormationFlight has no packet-level or diagnostic-counter logging. `ESPNOW.cpp` tracks `packetsReceived`/`packetsBadCrc`/`packetsBadSize`/`packetsBadValidation` and `PeerManager`/`RadioManager` expose peer count and these counters via `statusJson()` — but all of it is RAM-only, surfaced solely through the module's on-board web config UI. The official troubleshooting guidance (formationflight.org/troubleshooting) is explicitly "watch the counters live while connected" — there is no SD card, flash log, or serial packet log, and no open GitHub issues requesting one. If a swarm/formation issue happens mid-flight, there's currently no way to diagnose it afterward.

## Solution

**Decided 2026-07-04: Option A (MSP-to-blackbox).** Phase 0 research found Option B's premise false — FormationFlight's SPIFFS partition is stock/unused (web UI is compiled into flash via `scripts/build_html.py`, not served from SPIFFS), so Option B would have been greenfield filesystem work, not an extension of an existing mechanism. Option A wins on both retrieval ergonomics (same blackbox pull the pilot already does) and flight-timeline correlation (same log, same clock).

**Final scope, three pieces** (converged after design review with the user — see `claude/developer/workspace/feature-formationflight-diagnostic-logging/notes.md` for full trail):

1. **Aggregate RF counters** (original scope): `packetsReceived`/`packetsBadCrc`/`packetsBadSize`/`packetsBadValidation`/peer count — new MSP message, FormationFlight → INAV, logged to blackbox slow frame (mirrors `feature-canbus-errors-blackbox`).
2. **Per-peer lost/age state**: add `peer_t.lost` (and `lq`) to the same message — shows exactly when a peer's radar entry goes stale. Motivated by the actual reported symptom: FormationFlight marker sometimes not appearing in INAV when flying with another pilot.
3. **MSP link (module→FC) health — no new field needed**: add `lastReceivedMs` timestamp to INAV's `radar_pois_t`, stamped in `mspFcProcessInCommand()` on **any** inbound FormationFlight message (global, not per-peer). Blackbox compares elapsed time since last receipt against a 300-500ms threshold (~3-5 missed TDMA cycles at FormationFlight's ~16ms/slot cadence). Rejected two earlier designs for this piece: an ACK-based heartbeat (can't self-report through the link it's diagnosing; module has no corrective action anyway) and a monotonic send-counter (superseded by the simpler timestamp-on-receipt approach, which needs zero new bytes from FormationFlight).

## Scope

**In Scope:**
- All three pieces above, wired into a single new MSP message + blackbox slow-frame fields
- A documented way to retrieve/interpret the log after a flight (same blackbox pull already used for every flight)
- Bench and flight verification that induced packet-loss/CRC errors and link drops show up in the log

**Out of Scope:**
- Changing FormationFlight's existing live/real-time web UI diagnostics
- Fixing the `RADAR_MAX_POIS` (5) vs. FormationFlight `NODES_MAX` (6) mismatch — flagged during Phase 0 as a side finding, doesn't matter for 2-person flights, not in scope here
- Anything unrelated to persisting troubleshooting data (e.g. general FormationFlight feature work)

## Implementation Steps

1. ~~Phase 0 — Research & recommend~~ ✅ Complete — Option A chosen, 3-piece scope finalized 2026-07-04
2. Phase 1 — Implement: new MSP message (FormationFlight `sendDiagnostics()` + INAV handler in `msp_protocol_v2_inav.h`/`fc_msp.c`, next free INAV-range ID ~0x2044), `radar_pois_t.lastReceivedMs`, blackbox slow-frame wiring (3-file change: struct extend + field defs + `loadSlowState`/`writeSlowFrame` in `blackbox.c`, same shape as `feature-canbus-errors-blackbox`)
3. Phase 2 — Bench-test with induced packet loss/CRC errors and simulated link drops; flight-test to confirm blackbox correlation

## Success Criteria

- [x] Approach decided and documented (Option A, 3-piece scope)
- [ ] Diagnostic data persists across a power cycle / is retrievable after flight (via existing blackbox pull)
- [ ] Verified against induced packet-loss/CRC-error conditions on the bench
- [ ] Verified MSP link-health timestamp correctly flags a simulated module→FC link drop
- [ ] Blackbox log correlates FormationFlight stats (RF + per-peer + link health) with flight timeline
- [ ] Documented retrieval/interpretation procedure for the user

## Priority Justification

Diagnostic/troubleshooting tooling for an established swarm-flying workflow; not blocking any other active project, but directly requested by the user for their own flights.

## Coordination Note

If Option A (MSP/blackbox) is chosen: coordinate with whoever's working `feature-canbus-errors-blackbox` (adds CAN bus error stats to the same blackbox slow frame) to avoid `blackbox.c` merge conflicts — both add new slow-frame fields around the same time.

## Related

- **External repo:** https://github.com/FormationFlight/FormationFlight (not checked out in this workspace — will need a local clone/fork)
- **INAV precedent:** `feature-canbus-errors-blackbox` (same blackbox slow-frame mechanism, different data source)
- **Repository:** FormationFlight (external, branch `master`) + inav (firmware, branch `maintenance-10.x`) if Option A chosen
