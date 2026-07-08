# Guidance: Battery Monitor Review — Additional Context from Issue #3

**Date:** 2026-06-06 12:03
**From:** Manager
**To:** Developer
**Re:** review-dronecan-battery-monitor

## Additional Context

Issue daijoubu/inav #3 has been merged into your battery monitor review task. It contains detailed investigation notes that will save you time on the field coverage audit.

## Known Field Gap (from #3)

The existing driver (`sensors/battery_sensor_dronecan.c`) currently only extracts:

```c
dronecanVbat = (uint16_t)roundf(pbatteryInfo->voltage * 100.0F);
dronecanAmperage = (uint16_t)roundf(pbatteryInfo->current * 100.0F);
// All other fields IGNORED
```

Fields to evaluate for addition:
- `state_of_charge_pct` — SOC % (0-100) from smart BMS — **high priority**
- `remaining_capacity_wh` + `full_charge_capacity_wh` — Wh-based SOC — **high priority**
- `temperature` — battery temperature (Kelvin)
- `status_flags` — pack fault/status flags
- `state_of_health_pct` — battery health %
- `hours_to_full_charge` — time to full charge
- `average_power_10sec` — short-term average power draw

## Proposed Design from #3

Issue #3 proposes a `battery_capacity_source` setting:

```yaml
- name: battery_capacity_source
  description: "ADC=current integration, CAN=DroneCAN BMS reported"
  default_value: "ADC"
  type: uint8_t
```

With a hybrid SOC approach: prefer Wh-based if available, fall back to SOC %, fall back to current integration.

Please review the full issue (daijoubu/inav #3) for the complete implementation notes before starting Phase 2.

---
**Manager**
