# Review Findings: DroneCAN Battery Monitor — Node Health, Device Associations & Field Coverage

**Date:** 2026-06-07 09:02
**From:** Developer
**To:** Manager
**Re:** review-dronecan-battery-monitor
**Type:** Findings Report

## Status: REVIEW COMPLETE — No code changes yet

Review is complete. Two success criteria are not met and require fixes. Two feature proposals are included. Full findings in `claude/developer/workspace/review-dronecan-battery-monitor/FINDINGS.md`.

---

## Finding B1 — Battery data accepted regardless of node health [SAFETY]

`handle_BatteryInfo` does not check the sending node's UAVCAN health state. A BMS reporting `HEALTH_ERROR` or `HEALTH_CRITICAL` with plausible voltage values is accepted without question.

Unlike GPS, **battery data has no timeout mechanism**. If the DroneCAN node goes silent, the last voltage and current values are frozen indefinitely. A pilot could be relying on a stale reading from a node that died minutes ago.

Recommended fix: reject frames from ERROR/CRITICAL nodes with `LOG_WARNING`; add a staleness timestamp and expose a check to `battery.c` so it treats the sensor as absent after ~5000 ms of silence.

Also recommend `LOG_WARNING` on these `status_flags` fields currently ignored: `TEMP_HOT`, `TEMP_COLD`, `OVERLOAD`, `BAD_BATTERY`, `NEED_SERVICE`, `BMS_ERROR`.

## Finding B2 — No node-ID filtering [CORRECTNESS]

Same as GPS Finding 2. `handle_BatteryInfo` accepts from any node; multi-battery setups get last-write-wins interleaving into shared statics. Recommended fix: optional `dronecan_battery_node_id` setting (0 = accept any, default).

---

## Field Coverage

Full field audit in FINDINGS.md. Summary:

- **Use now:** `status_flags` (safety warnings as above)
- **Add as Issue #3 SOC work:** `state_of_charge_pct`, `remaining_capacity_wh`, `full_charge_capacity_wh`
- **Add if battery temp OSD element added:** `temperature`
- **Skip:** `state_of_health_pct`, `hours_to_full_charge`, `average_power_10sec`, `battery_id`, `model_name` — low practical value

---

## Feature Proposal — Charging Current Tracking

INAV currently clamps all amperage to ≥0 (`battery.c:687`). Two hardware classes can legitimately report negative current (charging):

1. **DroneCAN BMS nodes** — `BatteryInfo.current` is signed; negative = charging
2. **Center-biased ADC sensors** — some ICs are designed for bidirectional measurement

Everything downstream of the clamp (`mAhdrawnRaw`, `mWhDrawnRaw`, OSD, blackbox) already handles signed amperage correctly. The only additional fix needed is an upper clamp on `batteryRemainingCapacity` to prevent it exceeding full charge.

**Proposed setting:** `current_meter_track_charging` (bool, default OFF)

When OFF: existing clamp behaviour, no change.
When ON: charging current reduces mAh/Wh drawn, remaining capacity increases up to full. Useful for rovers with docking stations. Applies to all sources (not just CAN) since center-biased ADC sensors are real.

The `battery_sensor_dronecan.c` driver also needs a `uint16_t` → `int16_t` type fix for the amperage store to correctly preserve sign.

**Files affected:** `battery_sensor_dronecan.c/.h`, `battery.c` (2 lines), `settings.yaml`. No OSD, MSP, or blackbox changes.

---

## Feature Proposal — SOC from BMS (Issue #3)

DroneCAN BMS nodes report remaining capacity directly via `remaining_capacity_wh` / `full_charge_capacity_wh` and `state_of_charge_pct`. This is more accurate than current integration, and works after partial charges.

**Proposed setting:** `battery_capacity_source` (ADC=integration default, CAN=BMS-reported)

**Hybrid approach:** prefer Wh-based SOC when non-NaN → fall back to `state_of_charge_pct` → fall back to integration. Maximises BMS hardware compatibility.

---

## Recommended Implementation Order

1. B1 — node health rejection + staleness timeout + status_flags warnings (safety)
2. B2 — node-ID filter setting (correctness)
3. Charging current — type fix + setting + capacity upper clamp (small, well-contained)
4. SOC from BMS — Issue #3 scope (larger, separate branch)
5. Battery temperature — if/when OSD element added

## Next Steps

Awaiting manager direction. Ready to proceed to implementation on `maintenance-10.x` if approved.

---
**Developer**
