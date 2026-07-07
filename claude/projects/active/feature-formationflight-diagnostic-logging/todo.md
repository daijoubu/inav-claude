# Todo: FormationFlight Post-Flight Packet Diagnostics

## Phase 0: Research & Design Decision — ✅ COMPLETE (2026-07-04)

- [x] Fork/clone https://github.com/FormationFlight/FormationFlight locally for development
- [x] Confirm current MSP link usage between FormationFlight and FC (`src/lib/MSP/MSPManager.cpp`, `sendRadar()`)
- [x] Evaluate Option A (MSP-to-blackbox) vs Option B (on-module flash) — Option B's SPIFFS premise was false (partition is stock/unused); Option A chosen
- [x] Scope finalized to 3 pieces after user review: aggregate RF counters, per-peer lost/age state, MSP link health via receive-side timestamp
- [x] Recommendation approved by manager — proceed to Phase 1

## Phase 1: Implementation (approved 2026-07-04)

**Piece 1 — Aggregate RF counters:**
- [ ] Define new MSP message (INAV-specific range, `msp_protocol_v2_inav.h`, next free ID ~0x2044) carrying: packetsReceived, packetsBadCrc, packetsBadSize, packetsBadValidation, peer count
- [ ] Implement `sendDiagnostics()` in FormationFlight `MSPManager.cpp` (fire-and-forget `command2()` pattern, alongside existing `sendRadar()`)
- [ ] Implement INAV-side handler in `mspFcProcessInCommand()` (`fc_msp.c`) modelled on `MSP2_COMMON_SET_RADAR_POS` (fc_msp.c:3250) — store latest values

**Piece 2 — Per-peer lost/age state:**
- [ ] Add `peer_t.lost` and `lq` (from FormationFlight `PeerManager.h`) to the new diagnostics message
- [ ] Wire into INAV-side storage alongside piece 1

**Piece 3 — MSP link health (no new wire field):**
- [ ] Add `lastReceivedMs` field to INAV's `radar_pois_t`
- [ ] Stamp `lastReceivedMs = millis()` in `mspFcProcessInCommand()` on **any** inbound FormationFlight message, globally (not per-peer slot) — keep distinct from per-peer piece 2 checks
- [ ] At blackbox slow-frame time, compute elapsed time since last receipt; threshold 300-500ms (~3-5 missed TDMA cycles)

**Blackbox wiring (all pieces):**
- [ ] Extend struct + field defs + `loadSlowState`/`writeSlowFrame` in `blackbox.c` (~90 lines, same shape as `feature-canbus-errors-blackbox`)
- [ ] Coordinate with `feature-canbus-errors-blackbox` owner to avoid `blackbox.c` / field-definition merge conflicts — both touch the same struct/array/function triplet around the same time

## Phase 2: Testing

- [ ] Bench test: induce packet loss/CRC errors between two modules, confirm counters + per-peer state captured
- [ ] Bench test: simulate module→FC serial link drop, confirm `lastReceivedMs` threshold correctly flags it
- [ ] Flight test: confirm blackbox log contains all three pieces correlated with flight timeline

## Completion

- [ ] Feature implemented and tested
- [ ] PR opened (FormationFlight upstream `master` + INAV `maintenance-10.x`)
- [ ] Send completion report to manager
