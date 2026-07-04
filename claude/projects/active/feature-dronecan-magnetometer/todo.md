# Todo: DroneCAN Magnetometer Support

## Phase 1: Research & Reference

- [ ] Read `src/main/drivers/compass/compass_virtual.c` — understand compass driver interface
- [ ] Read `src/main/io/gps_dronecan.c` — understand DroneCAN driver pattern to follow
- [ ] Read DSDL headers for DTID 1001, 1002, 1043 — confirm field names and units
- [ ] Identify `compassDetect()` or equivalent wiring point in compass subsystem

## Phase 2: Implementation

- [ ] Add subscriptions for MagneticFieldStrength (1001), MagneticFieldStrength2 (1002), MagneticFieldStrengthHiRes (1043) in `dronecan.c`
- [ ] Write `src/main/drivers/compass/compass_dronecan.c` and `.h`
  - [ ] Driver registration and init
  - [ ] Field data reception and unit conversion
  - [ ] `sensor_id` handling from MagneticFieldStrength2 for multi-instance
- [ ] Wire into compass detection/init

## Phase 3: Verify

- [ ] DroneCAN mag data flows to compass subsystem
- [ ] All three message types handled (check with DSDL tool or SITL if possible)
- [ ] Full build matrix: F4, F7, H7, AT32, SITL — all clean

## Completion

- [ ] Build matrix clean
- [ ] PR opened against `maintenance-10.x`
- [ ] Completion report sent to manager
