# Project: DroneCAN Magnetometer Support

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-06-09
**Estimated Time:** 4-8 hours

## Overview

Add magnetometer/compass support to the INAV DroneCAN driver, enabling use of external mag sensors connected via DroneCAN bus.

## Problem

INAV currently has no DroneCAN magnetometer driver. Users with DroneCAN-connected GPS/compass modules (which are common in the DroneCAN ecosystem) cannot use the compass over the DroneCAN bus.

## Objectives

1. Receive the three DroneCAN magnetometer message types in `dronecan.c`
2. Write a `mag_dronecan.c` driver modelled on `gps_dronecan.c`
3. Wire into INAV's compass/mag subsystem

## Scope

**In Scope:**
- `uavcan.equipment.ahrs.MagneticFieldStrength` (DTID 1001) — original UAVCAN message
- `uavcan.equipment.ahrs.MagneticFieldStrength2` (DTID 1002) — adds `sensor_id` for multi-mag (preferred)
- `dronecan.sensors.magnetometer.MagneticFieldStrengthHiRes` (DTID 1043) — higher precision extension
- New `src/main/drivers/compass/compass_dronecan.c` (and `.h`)
- Wiring into compass subsystem (`compassDetect()` or equivalent)
- Targeting `maintenance-10.x`

**Out of Scope:**
- Multi-mag arbitration beyond what INAV's existing compass layer provides
- Configurator UI changes (unless trivially needed for driver selection)

## Implementation Steps

1. Review `gps_dronecan.c` and `compass_virtual.c` as reference patterns
2. Add message subscriptions for all three DTID variants in `dronecan.c`
3. Write `compass_dronecan.c`: register driver, receive field data, convert units (Tesla → Gauss or whatever INAV uses internally)
4. Handle `sensor_id` from MagneticFieldStrength2 for multi-instance support
5. Wire into compass detection and init
6. Build full matrix and verify

## Success Criteria

- [ ] DroneCAN magnetometer data received and passed to compass subsystem
- [ ] All three message types handled (1001, 1002, 1043)
- [ ] `sensor_id` from MagneticFieldStrength2 respected
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] PR opened against `maintenance-10.x`
- [ ] Completion report sent to manager

## Estimated Time

4-8 hours

## Priority Justification

Natural complement to DroneCAN GPS work. Enables common DroneCAN GPS/compass module setups to work fully with INAV.
