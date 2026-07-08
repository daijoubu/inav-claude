# Task Assignment: FormationFlight Post-Flight Packet Diagnostics

**Date:** 2026-07-04 10:00
**From:** Manager
**To:** Developer
**Project:** feature-formationflight-diagnostic-logging
**Priority:** MEDIUM
**Estimated Effort:** TBD — Phase 0 research first

## Task

Give FormationFlight (external ESP-NOW drone swarm/formation telemetry project, https://github.com/FormationFlight/FormationFlight) a way to persist packet-reception diagnostics so the user can troubleshoot swarm/formation issues after a flight, not just observe them live.

## Background

Research confirmed FormationFlight (v5.0.0/master) has no packet-level or diagnostic-counter logging. `ESPNOW.cpp` tracks packetsReceived/packetsBadCrc/packetsBadSize/packetsBadValidation, and PeerManager/RadioManager expose these plus peer count via statusJson() — but it's all RAM-only, surfaced only through the module's on-board web config UI while connected live. No SD/flash/serial packet log exists upstream, and no GitHub issues request one.

The user is fine with either of two approaches — pick whichever is easier to implement well:

- **Option A (MSP-to-blackbox):** FormationFlight already talks to the FC over MSP (see `src/lib/MSP/MSPManager.cpp`, `sendRadar()`, used for peer position/radar data). Add a new or extended MSP message carrying the diagnostic counters from the module to INAV, and log them into the blackbox slow frame. Precedent: `feature-canbus-errors-blackbox` does the same thing for DroneCAN bus error stats via the same slow-frame mechanism.
- **Option B (on-module flash):** FormationFlight already uses a SPIFFS partition (`min_spiffs.csv`) to serve its web UI assets. Add a small rotating/bounded diagnostic log written periodically to that flash, retrievable after the flight via the existing web UI.

## What to Do

1. Fork/clone https://github.com/FormationFlight/FormationFlight for development.
2. Phase 0: evaluate both options (implementation effort, retrieval ergonomics, correlation with flight timeline) and recommend one (or a hybrid) back to the manager before implementing.
3. Implement the chosen approach per the project todo.md.
4. Bench-test with induced packet loss/CRC errors; flight-test if the MSP/blackbox path is chosen.
5. If Option A is chosen: coordinate with whoever owns `feature-canbus-errors-blackbox` to avoid `blackbox.c` / field-definition merge conflicts, since both would add new slow-frame fields around the same time.

## Success Criteria

- [ ] Approach decided and documented (Option A, B, or hybrid) — recommendation sent to manager before implementation begins
- [ ] Diagnostic data persists across a power cycle / is retrievable after flight
- [ ] Verified against induced packet-loss/CRC-error conditions on the bench
- [ ] If MSP/blackbox path: blackbox log correlates FormationFlight stats with flight timeline
- [ ] Documented retrieval/interpretation procedure

## Project Directory

`claude/projects/active/feature-formationflight-diagnostic-logging/`

## Branch / PR Target

- FormationFlight: PR against upstream `FormationFlight/FormationFlight`, base `master`
- INAV (only if Option A chosen): PR against `inavflight/inav`, base `maintenance-10.x`

---
**Manager**
