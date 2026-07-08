# Task Assignment: DroneCAN GPS — Health Guard & Node-ID Filter

**Date:** 2026-06-07 09:10
**From:** Manager
**To:** Developer
**Project:** review-dronecan-gps-node-health
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 2-4 hours

## Task

Implement the two findings from your GPS review as a single self-contained PR against `maintenance-10.x`. The findings are documented in your workspace at `claude/developer/workspace/review-dronecan-gps-node-health/FINDINGS.md`.

## What to Do

**Finding 1 — Health guard** (`dronecan.c`, GPS handlers at lines 108–142):
- After the `gpsConfig()->provider == GPS_DRONECAN` guard in `handle_GNSSFix`, `handle_GNSSFix2`, and `handle_GNSSAuxiliary`, look up the sending node via `dronecanGetNodeByID(transfer->source_node_id)` and reject the frame if health is `HEALTH_ERROR` or `HEALTH_CRITICAL`
- Emit a rate-limited `LOG_WARNING(CAN, ...)` on first detection of degraded health

**Finding 2 — Node-ID filter** (`dronecan.c` + `settings.yaml`):
- Add an optional `dronecan_gps_node_id` setting (uint8_t, 0 = accept any, default 0)
- When non-zero, reject GPS frames from any other node ID

**Finding 3 — Stale timeout** (`dronecan.c:674`):
- If you cut your branch before the battery branch, also lower the node-table stale threshold from 10,000 ms to 3,500 ms to align with the UAVCAN spec. If the battery PR was cut first and already includes this change, skip it and rebase past it.

## Branch & PR

- Branch off: `maintenance-10.x`
- Open as draft PR to: `maintenance-10.x`
- Do NOT target master

## Success Criteria

- [ ] `HEALTH_ERROR`/`HEALTH_CRITICAL` nodes are rejected in all three GPS handlers
- [ ] Rate-limited `LOG_WARNING` emitted on health degradation
- [ ] `dronecan_gps_node_id` setting added (0 = accept any)
- [ ] Node-ID filter active in handlers when setting is non-zero
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] Draft PR opened against `maintenance-10.x`

## Project Directory

`claude/projects/active/review-dronecan-gps-node-health/`

---
**Manager**
