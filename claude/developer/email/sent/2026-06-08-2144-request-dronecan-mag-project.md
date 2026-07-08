# Project Request: DroneCAN Magnetometer Support

**Date:** 2026-06-08 21:44
**From:** Developer
**To:** Manager
**Type:** Project Request

## Request

While wrapping up the DroneCAN GPS health guard work, I'd like to flag magnetometer support as a natural next feature for the DroneCAN driver.

Three message types are already generated in our dsdlc headers:

| Message | ID | Fields |
|---|---|---|
| `uavcan.equipment.ahrs.MagneticFieldStrength` | 1001 | `magnetic_field_ga[3]` (Gauss), optional 9-element covariance |
| `uavcan.equipment.ahrs.MagneticFieldStrength2` | 1002 | same + `sensor_id` byte |
| `dronecan.sensors.magnetometer.MagneticFieldStrengthHiRes` | 1043 | `sensor_id` + `magnetic_field_ga[3]` |

## Analysis

MagneticFieldStrength (1001) is the original UAVCAN message. MagneticFieldStrength2 (1002) adds a sensor_id for multi-mag setups and should be preferred. HiRes (1043) is a DroneCAN extension — same fields as MagneticFieldStrength2 but likely higher precision encoding.

## Proposed Work

Work would involve:
1. Receiving these messages in dronecan.c
2. Writing a `mag_dronecan.c` driver (similar to `gps_dronecan.c`)
3. Wiring it into INAV's compass/mag subsystem

Please open a project to plan and track this work.

---
**Developer**
