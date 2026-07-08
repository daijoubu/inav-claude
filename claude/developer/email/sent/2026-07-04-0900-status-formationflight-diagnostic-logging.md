# Status Update: FormationFlight Post-Flight Packet Diagnostics

**Date:** 2026-07-04 09:00
**From:** Developer
**To:** Manager
**Re:** feature-formationflight-diagnostic-logging

## Current Status

Phase 0 research complete. Recommending **Option A (MSP-to-blackbox)** over Option B (on-module SPIFFS flash log).

## Key Finding

The original task write-up's premise for Option B was inaccurate: FormationFlight does NOT currently use SPIFFS to serve its web UI. `min_spiffs.csv` in platformio.ini is just a stock ESP32 Arduino-core partition table (chosen for its OTA-friendly two-app-slot layout), not a project-specific file. The web UI is compiled directly into firmware flash as C data via `scripts/build_html.py` at build time. Confirmed via repo-wide grep: zero references to SPIFFS/LittleFS anywhere in FormationFlight's src/. The 128KB SPIFFS partition exists in flash but is completely unused today.

So Option B would be greenfield filesystem work (mount SPIFFS for the first time, build a rotating log writer, add a download endpoint), not "extend an existing mechanism" as originally assumed.

## Why Option A

Option A is close to pure replication of two already-proven patterns:

- **FormationFlight side:** Existing counters (packetsReceived, packetsBadCrc, packetsBadSize, packetsBadValidation, peer count) already live in RadioManager.h/PeerManager.cpp. Adding a `sendDiagnostics()` next to the existing `sendRadar()` (MSPManager.cpp:214) follows the identical `msp->command2()` fire-and-forget pattern already in use.

- **INAV side:** Confirmed via inav-architecture agent research — inbound MSP2 "set" messages are handled in `mspFcProcessInCommand()` (fc_msp.c:2102), with `MSP2_COMMON_SET_RADAR_POS`'s handler (fc_msp.c:3250) serving as an almost line-for-line template for a new sibling message. Recommend a new ID in the INAV-specific range (msp_protocol_v2_inav.h, next free ~0x2044) rather than the shared COMMON block.

- **Blackbox wiring:** Blackbox slow-frame wiring is already fully scoped by the feature-canbus-errors-blackbox PLAN.md (3-file change: struct extend + field defs + loadSlowState + writeSlowFrame in blackbox.c, ~90 lines) — same mechanism, different data source.

Option A wins outright on the two criteria the task asked to weigh:
- **Retrieval ergonomics:** Same blackbox pull the pilot already does after every flight, no extra manual step or Wi-Fi reconnection
- **Flight-timeline correlation:** Same log, same clock — free, vs. needing extra work in Option B for approximate correlation

## Risk / Coordination Note

Confirmed coordination need flagged in the original task: must coordinate `blackbox.c` slow-frame field-array edits with whoever picks up `feature-canbus-errors-blackbox`, since both would add new slow-frame fields around the same time and touch the same struct/array/function triplet.

## Research Detail

Full findings, file/line references, and the effort-comparison table are documented in the workspace notes: `claude/developer/workspace/feature-formationflight-diagnostic-logging/notes.md`

## Next Steps

Awaiting go-ahead to proceed to Phase 1 (implement Option A):
1. New MSP message definition + FormationFlight sendDiagnostics()
2. INAV-side handler + storage struct
3. Blackbox slow-frame wiring
4. Bench-test with induced packet loss/CRC errors

## Estimated Completion

Phase 1 implementation and testing: pending your approval to proceed

---
**Developer**
