# Task Assignment: DroneCAN Magnetometer Support

**Date:** 2026-06-09 14:00
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-magnetometer
**Priority:** MEDIUM
**Estimated Effort:** 4-8 hours

## Task

Add magnetometer/compass support to the INAV DroneCAN driver. Receive the three DroneCAN mag message types, write a `compass_dronecan.c` driver, and wire into INAV's compass subsystem.

## Background

Three message types are available in the dsdlc headers:
- `uavcan.equipment.ahrs.MagneticFieldStrength` (DTID 1001) — original UAVCAN message
- `uavcan.equipment.ahrs.MagneticFieldStrength2` (DTID 1002) — adds `sensor_id` for multi-mag setups (preferred)
- `dronecan.sensors.magnetometer.MagneticFieldStrengthHiRes` (DTID 1043) — higher precision DroneCAN extension

Reference patterns: `src/main/io/gps_dronecan.c` for the DroneCAN driver pattern, and `src/main/drivers/compass/compass_virtual.c` for the compass driver interface.

## What to Do

1. Review reference files to understand driver patterns
2. Add subscriptions for all three DTIDs in `dronecan.c`
3. Write `src/main/drivers/compass/compass_dronecan.c` (and `.h`): driver registration, field data reception, unit conversion, `sensor_id` handling from MagneticFieldStrength2
4. Wire into compass detection and init
5. Build full matrix: F4, F7, H7, AT32, SITL

## Branch

**Base branch: `maintenance-10.x`**

## Success Criteria

- [ ] DroneCAN magnetometer data received and passed to compass subsystem
- [ ] All three message types handled (DTIDs 1001, 1002, 1043)
- [ ] `sensor_id` from MagneticFieldStrength2 respected for multi-instance
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] PR opened against `maintenance-10.x`
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/feature-dronecan-magnetometer/`

---
**Manager**
