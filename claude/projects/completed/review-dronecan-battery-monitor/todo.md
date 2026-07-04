# Todo: Review DroneCAN Battery Monitor — Node Health, Device Associations & Field Coverage

## Phase 1: Audit

- [ ] Locate DroneCAN battery monitor driver source files
- [ ] Check node health monitoring — is battery data invalidated on node OFFLINE/ERROR?
- [ ] Check device association usage — is battery data tied to the correct node ID?
- [ ] Audit BatteryInfo fields — currently only voltage + current are used; evaluate each ignored field:
  - `state_of_charge_pct` — SOC % from smart BMS (high value)
  - `remaining_capacity_wh` + `full_charge_capacity_wh` — Wh-based capacity (high value)
  - `temperature` — battery temperature
  - `status_flags` — pack fault/status flags
  - `state_of_health_pct` — battery health %
  - `hours_to_full_charge` — time to full (charging)
  - `average_power_10sec` — short-term average power
- [ ] Evaluate `battery_capacity_source` setting (ADC vs CAN): see daijoubu/inav #3 for proposed design
- [ ] Evaluate charging current display (OSD, MSP telemetry, or both)
- [ ] Compare against other DroneCAN sensor drivers for consistency
- [ ] Document all findings

## Phase 2: Fix & Enhance

- [ ] Fix node health monitoring if missing or incorrect
- [ ] Fix device association usage if incorrect
- [ ] Implement agreed additional fields (based on audit findings)
- [ ] Implement charging current display if agreed

## Phase 3: Verify

- [ ] Full build matrix passes (F4/F7/H7/AT32/SITL)
- [ ] Battery data correctly invalidated when node health degrades

## Completion

- [ ] Completion report sent to manager (findings, decisions made on new fields, what was implemented)
