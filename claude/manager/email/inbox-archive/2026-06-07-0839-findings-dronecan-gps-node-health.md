# Findings Report: DroneCAN GPS — Node Health & Device Associations

**Date:** 2026-06-07 08:39
**From:** Developer
**To:** Manager
**Re:** review-dronecan-gps-node-health
**Type:** Findings Report

## Status: REVIEW COMPLETE — No code changes yet

The review is complete. Two success criteria are not met and require fixes. Full findings are in `claude/developer/workspace/review-dronecan-gps-node-health/FINDINGS.md`.

## Finding 1 — GPS data accepted regardless of node health [SAFETY]

The GPS message handlers (`handle_GNSSFix`, `handle_GNSSFix2`, `handle_GNSSAuxiliary`) do not check the sending node's UAVCAN health state before forwarding data. A GPS node that reports `HEALTH_ERROR` or `HEALTH_CRITICAL` but continues transmitting GPS frames will have its data accepted without question.

What IS handled: a totally silent node times out via the existing 1 s GPS timeout. What is NOT handled: a degraded-but-still-transmitting node.

The infrastructure to fix this already exists — `dronecanGetNodeByID()` returns the node's current health. The fix is to reject frames from ERROR/CRITICAL nodes, emit a `LOG_WARNING`, and let the existing GPS timeout + dead reckoning take over naturally. No new failure paths needed.

**Do not** wire this into `isHardwareHealthy()` or any arming block — see escalation notes below.

## Finding 2 — No node-ID filtering [CORRECTNESS]

All GPS handlers accept data from any node on the bus. In a multi-GPS setup (primary + redundant), both nodes write to the same `gpsSolDRV` buffer with undefined last-write-wins interleaving. Recommended fix: add an optional `dronecan_gps_node_id` setting (0 = accept any, preserving current behaviour).

## Finding 3 — Node table stale timeout [MINOR]

INAV removes nodes after 10,000 ms of silence; the UAVCAN spec defines 3,000 ms as offline. Mitigated in practice by the 1 s GPS data timeout. Only visible effect is the configurator can report a node as present when UAVCAN considers it offline. Recommend lowering to 3,500 ms, low priority.

## Feature Gap — UTC time not implemented

`dronecanGPSReceiveGNSSFix2()` has time fields commented out. U-blox and MSP both provide UTC time; DroneCAN carries it in `gnss_timestamp.usec` (Unix epoch µs) but it requires a Gregorian calendar decomposition to convert — the other protocols get pre-parsed fields from the sensor. AP_Periph always sends UTC-standard Unix microseconds. Technical details and conversion approach documented in `claude/developer/workspace/review-dronecan-gps-node-health/todo-utc-time.md`. Recommend as a separate small task.

## Escalation: Why No Arming Block

Considered wiring DroneCAN node health into `isGPSHealthy()` → `isHardwareHealthy()` → `ARMING_DISABLED_HARDWARE_FAILURE`. Decided against it for safety reasons:

If a GPS node degrades in flight, dead reckoning takes over. If the pilot accidentally disarms, they need to re-arm immediately. The existing emergency re-arm bypass (`IN_FLIGHT_EMERG_REARM`) would normally handle this, but for **fixed-wing it relies on `isGPSHeadingValid()`** — which requires GPS. A GPS failure disables both the arming check bypass and the GPS itself simultaneously. The pilot cannot re-arm.

LOG_WARNING on node health change is appropriate. Arming blocks are not.

## Recommendation: Position Estimator Investigation

`isProbablyStillFlying()` uses GPS heading as its sole in-flight indicator for fixed wing. This is a circular dependency: GPS failure triggers the arming concern and also disables the mechanism that would bypass it. Recommend investigating whether an IMU/barometer-based airborne confidence signal could be substituted, which would make a health-gated arming block safe in future. This should be tracked as a separate investigation task.

## Success Criteria Status

- Node health monitored; data invalidated on ERROR: **PARTIAL** (silent node OK, degraded-transmitting NOT OK)
- Device associations used correctly: **NOT MET**
- Consistent with other DroneCAN drivers: **MET** (battery sensor has same gaps)
- Full build matrix: **N/A** (no code changes this session)

## Recommended Priority Order

1. Finding 1 — health-gated frame rejection + LOG_WARNING (safety)
2. Finding 2 — node-ID filter setting (correctness)
3. Position estimator investigation (prerequisite for future arming work)
4. Finding 3 — stale timeout alignment (minor)
5. UTC time — separate small task

## Next Steps

Awaiting manager direction. Ready to proceed to implementation of Findings 1 and 2 on `maintenance-10.x` if approved.

---
**Developer**
