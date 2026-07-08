# Status Update: FormationFlight Diagnostics — Correction to MSP Link Health Design

**Date:** 2026-07-04 14:45
**From:** Developer
**To:** Manager
**Re:** feature-formationflight-diagnostic-logging (correction to today's earlier addendum)

## Correction

The user caught a real flaw in the "Addition 2" MSP link health design from the last addendum (periodic ACKed heartbeat request). Two problems:

1. The module has no corrective action available even if it detects a failed link — tracking the failure buys the module nothing operationally.
2. More fundamentally: if the MSP link is actually down, a "link is down" report has to travel over that same dead link to reach the blackbox. An ACK-based heartbeat can't self-report through the channel it's diagnosing — it can only ever succeed in telling you the link works, which you already know from every other message getting through.

## Replacement Design

Add a monotonically-incrementing send counter (e.g. `diagnosticsSent`, mirroring the existing `peerUpdatesSent`/`gnssUpdatesSent` counters already in `MSPManager.h`) to the new diagnostics message. No ACK, no separate schedule — it rides along with data already being sent. Link health is then derived entirely on the INAV/blackbox side: if the counter stops advancing for some N seconds in the log, the MSP link died during that window.

This is simpler than the original proposal in every respect: no new scheduling logic in `MSPManager::loop()`, no blocking `request()`/`waitFor()` call to reason about, and no risk of a health-check itself stalling the loop and degrading the RF reception it would be trying to diagnose (which was the original design's key risk, flagged in the prior addendum).

## Net Effect on Phase 1 Scope

Still Option A overall. Addition 1 (per-peer lost/age state) is unchanged. Addition 2 is now smaller and lower-risk than originally proposed — a single incrementing counter field instead of an active heartbeat mechanism.

## Documentation Updated

Notes updated: `claude/developer/workspace/feature-formationflight-diagnostic-logging/notes.md`

## Next Steps

Awaiting a single go-ahead covering the original recommendation plus both additions (now corrected) before starting Phase 1 implementation.

---
**Developer**
