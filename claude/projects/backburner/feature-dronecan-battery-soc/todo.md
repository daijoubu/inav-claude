# Todo List: DroneCAN Battery SOC Support

## Phase 1: Extraction

- [ ] Extract `remaining_capacity_wh`, `full_charge_capacity_wh`, `state_of_charge_pct`, `state_of_charge_pct_stdev`, `state_of_health_pct` in `battery_sensor_dronecan.c`
- [ ] Add getters in `battery_sensor_dronecan.h`

## Phase 2: Setting & Hybrid Logic

- [ ] Add `battery_capacity_source` (ADC/CAN) to `settings.yaml`
- [ ] Implement hybrid rule in `battery.c`: Wh-based → SOC-pct → current-integration fallback

## Phase 3: Validation

- [ ] Full build matrix: F4, F7, H7, AT32 (IFLIGHT_BLITZ_ATF435), SITL
- [ ] Verify default ADC behaviour unchanged
- [ ] Verify CAN mode against simulated/real BMS SOC data

## Completion

- [ ] Draft PR opened against `maintenance-10.x`
- [ ] Send completion report to manager
