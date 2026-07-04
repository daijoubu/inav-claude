# Todo List: Battery Charging Current Tracking

## Phase 1: Type Fix

- [ ] Change `dronecanAmperage` from `uint16_t` to `int16_t` in `battery_sensor_dronecan.c`
- [ ] Update `battery_sensor_dronecan.h` to match

## Phase 2: Setting & Logic

- [ ] Add `current_meter_track_charging` bool to `settings.yaml` (default OFF)
- [ ] Gate `MAX(0, amperage)` in `battery.c:687` on the new setting
- [ ] Add upper clamp in `battery.c:459`: `constrain(capacityDiffBetweenFullAndEmpty - drawn, 0, capacityDiffBetweenFullAndEmpty)`

## Phase 3: Validation

- [ ] Full build matrix: F4, F7, H7, AT32 (IFLIGHT_BLITZ_ATF435), SITL
- [ ] Verify default OFF behaviour unchanged
- [ ] Verify ON behaviour reduces mAh drawn during simulated negative current

## Completion

- [ ] Draft PR opened against `maintenance-10.x`
- [ ] Send completion report to manager
