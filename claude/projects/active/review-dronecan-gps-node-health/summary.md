# Project: DroneCAN GPS — Health Guard, Node-ID Filter & FW Flight Detection

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM-HIGH
**Type:** Feature / Bug Fix
**Created:** 2026-06-06
**Updated:** 2026-06-07
**Estimated Time:** 4-8 hours
**Branch:** `feature/dronecan-dna-server` (base) → new branch TBD
**PRs:** Draft against `maintenance-10.x` (firmware) + `maintenance-10.x` (configurator)

## Overview

Expand the DroneCAN GPS driver to reject data from unhealthy nodes, filter by node ID, and align the node table stale timeout with the UAVCAN spec. Also fix `isProbablyStillFlying()` for fixed-wing to remove GPS dependency from the emergency re-arm path.

Node-ID filter work from `feature/dronecan-node-filter` (2 commits) will be cherry-picked onto the new branch. Configurator UI support for `dronecan_gps_node_id` and `dronecan_battery_node_id` is in scope.

## Problem

**Finding 1 — Health guard (safety):** `handle_GNSSFix`, `handle_GNSSFix2`, and `handle_GNSSAuxiliary` do not check the sending node's UAVCAN health state. A GPS node with a hardware fault continues broadcasting plausible-looking data while reporting `HEALTH_ERROR` or `HEALTH_CRITICAL`; INAV accepts and navigates on this data.

**Finding 2 — Node-ID filter (correctness):** All three handlers accept data from any node ID. Two GPS nodes on the same bus interleave writes into the same buffer — last-write-wins with no ordering guarantees.

**Finding 3 — Stale timeout (minor):** `process1HzTasks()` removes nodes not seen for >10,000 ms. UAVCAN spec defines OFFLINE at 3,000 ms. Node table reports nodes as present when UAVCAN would consider them OFFLINE.

**Finding 4 — isProbablyStillFlying() fixed-wing GPS dependency (safety):** The emergency in-flight re-arm gate (`fc_core.c:536`) calls `isProbablyStillFlying()`, which for fixed-wing uses `isGPSHeadingValid()` — requiring GPS lock + 6 sats + 300 cm/s ground speed. When a DroneCAN GPS node fails and health-guard frame rejection is active, GPS times out → `isGPSHeadingValid()` collapses → `isProbablyStillFlying()` returns false → pilot cannot emergency re-arm in flight. This is a double-fault scenario (GPS node failure + accidental disarm) but foreseeable. Target: `maintenance-10.x` only (not a 9.x emergency fix).

**Fix:** Replace `isGPSHeadingValid()` in `isProbablyStillFlying()` with `posControl.actualState.velXY >= 300.0f` (plus pitot airspeed fallback if available). The position estimator velocity survives dead reckoning without GPS; if both GPS and dead reckoning are lost, `velXY` is 0 and the check fails safely.

## Scope

**Firmware (`inav/`):**
- Health guard in `handle_GNSSFix`, `handle_GNSSFix2`, `handle_GNSSAuxiliary` (`dronecan.c`)
- Rate-limited `LOG_WARNING(CAN, ...)` on node health degradation
- `dronecan_gps_node_id` setting in `settings.yaml` (cherry-pick from `feature/dronecan-node-filter`)
- Node-ID filter in GPS handlers
- Node table stale timeout 10,000 ms → 3,500 ms (`dronecan.c:674`)
- `isProbablyStillFlying()` fixed-wing branch: replace `isGPSHeadingValid()` with pos-estimator velocity (`navigation.c`)

**Configurator (`inav-configurator/`):**
- UI control for `dronecan_gps_node_id` setting

**Out of scope:**
- Battery monitor changes (separate project: `review-dronecan-battery-monitor`)
- `isGPSHeadingValid()` uses in wind estimator, IMU COG, launch detection, trackback — those are correct uses unrelated to flight detection
- UTC time implementation
- `isGPSHealthy()` stub / blackbox integration
- Position estimator investigation for future arming-block approach

## Success Criteria

- [ ] `HEALTH_ERROR`/`HEALTH_CRITICAL` GPS nodes rejected in all three handlers
- [ ] Rate-limited `LOG_WARNING` on health degradation
- [ ] `dronecan_gps_node_id` setting added (0 = accept any, default)
- [ ] Node-ID filter active in handlers when setting is non-zero
- [ ] Configurator UI for `dronecan_gps_node_id`
- [ ] Node stale timeout lowered to 3,500 ms
- [ ] `isProbablyStillFlying()` fixed-wing no longer calls `isGPSHeadingValid()`
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] Draft PRs opened against `maintenance-10.x`

## Key Files

| File | Change |
|------|--------|
| `src/main/drivers/dronecan/dronecan.c` | Health guard, node-ID filter, stale timeout |
| `src/main/sensors/settings.yaml` | `dronecan_gps_node_id` setting |
| `src/main/navigation/navigation.c:3598` | `isProbablyStillFlying()` FW branch |
| `inav-configurator/` | Node-ID UI control |

## Branch Strategy

Base: `feature/dronecan-dna-server`
Cherry-pick: 2 commits from `feature/dronecan-node-filter` (`2c2be593c`, `0d5638af3`)
PR target: `maintenance-10.x`
