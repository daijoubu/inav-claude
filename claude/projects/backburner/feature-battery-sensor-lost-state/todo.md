# Todo: Battery Sensor Lost State

## Phase 1: Research

- [ ] Read `src/main/sensors/battery.c` / `battery.h` — understand state machine, `BATTERY_NOT_PRESENT` transition, and where vbat LPF feeds into state
- [ ] Find CRSF battery sensor driver — understand how it receives and updates voltage/current
- [ ] Find SmartPort battery sensor driver — same
- [ ] Review DroneCAN battery staleness implementation as reference pattern (from `fix/dronecan-battery-health` branch)
- [ ] Find OSD battery warning display code

## Phase 2: Battery State Machine

- [ ] Add `BATTERY_SENSOR_LOST` to battery state enum in `battery.h`
- [ ] Add API for drivers to signal sensor lost (e.g. `batterySetSensorLost()`)
- [ ] Ensure `BATTERY_NOT_PRESENT` transition is not triggered when in `BATTERY_SENSOR_LOST` state
- [ ] Freeze last-known vbat/amperage values on transition to `BATTERY_SENSOR_LOST`

## Phase 3: Driver Wiring

- [ ] CRSF battery driver: add staleness timer, call `batterySetSensorLost()` on timeout
- [ ] SmartPort battery driver: add staleness timer, call `batterySetSensorLost()` on timeout
- [ ] (Optional) Refactor DroneCAN battery driver to use shared state instead of its own OSD path

## Phase 4: OSD

- [ ] Add distinct OSD warning for `BATTERY_SENSOR_LOST` state (e.g. `BAT SENSOR LOST`)
- [ ] Ensure it is visually distinct from normal low-battery warnings

## Phase 5: Verify

- [ ] Full build matrix: F4, F7, H7, AT32, SITL — all clean

## Completion

- [ ] PR opened against `maintenance-10.x`
- [ ] Completion report sent to manager
