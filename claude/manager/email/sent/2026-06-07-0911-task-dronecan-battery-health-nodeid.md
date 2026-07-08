# Task Assignment: DroneCAN Battery Monitor — Health Guard, Staleness & Node-ID Filter

**Date:** 2026-06-07 09:11
**From:** Manager
**To:** Developer
**Project:** review-dronecan-battery-monitor
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 3-5 hours

## Task

Implement the findings from your battery monitor review as a single self-contained PR against `maintenance-10.x`. The findings are documented in your workspace at `claude/developer/workspace/review-dronecan-battery-monitor/FINDINGS.md`.

## What to Do

**Finding B1 — Health guard + staleness timer** (`dronecan.c` + `battery_sensor_dronecan.c`):
- In `handle_BatteryInfo` (`dronecan.c:155–163`): reject frames from `HEALTH_ERROR`/`HEALTH_CRITICAL` nodes; emit rate-limited `LOG_WARNING`
- Add a `last_batt_msg_ms` timestamp updated on each accepted frame
- Expose a staleness check to `battery_sensor_dronecan.c`/`battery.c` so battery treats the sensor as absent when no message has arrived within a configurable window (suggest 5000 ms — battery updates are slow)

**Status flags warnings** (`dronecan.c`):
- Emit `LOG_WARNING(CAN, ...)` for safety-relevant `status_flags` bits: `TEMP_HOT`, `TEMP_COLD`, `OVERLOAD`, `BAD_BATTERY`, `NEED_SERVICE`, `BMS_ERROR`
- Rate-limit to avoid log flooding

**Finding B2 — Node-ID filter** (`dronecan.c` + `settings.yaml`):
- Add an optional `dronecan_battery_node_id` setting (uint8_t, 0 = accept any, default 0)
- When non-zero, reject battery frames from any other node ID

**Finding 3 — Stale timeout** (`dronecan.c:674`):
- If you cut your branch before the GPS branch, also lower the node-table stale threshold from 10,000 ms to 3,500 ms. If the GPS PR was cut first and already includes this change, skip it and rebase past it.

## Branch & PR

- Branch off: `maintenance-10.x`
- Open as draft PR to: `maintenance-10.x`
- Do NOT target master

## Success Criteria

- [ ] `HEALTH_ERROR`/`HEALTH_CRITICAL` nodes rejected in `handle_BatteryInfo`
- [ ] Rate-limited `LOG_WARNING` on health degradation
- [ ] Staleness timer implemented; battery treated as absent after 5 s silence
- [ ] `LOG_WARNING` emitted for safety-relevant `status_flags`
- [ ] `dronecan_battery_node_id` setting added (0 = accept any)
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] Draft PR opened against `maintenance-10.x`

## Project Directory

`claude/projects/active/review-dronecan-battery-monitor/`

---
**Manager**
