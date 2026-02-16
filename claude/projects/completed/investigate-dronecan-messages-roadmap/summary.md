# Project: Investigate DroneCAN Messages Roadmap

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-02-14
**Estimated Effort:** 3-4 hours

## Overview

Research the DroneCAN/UAVCAN message catalog and identify which additional messages INAV should support. Produce a prioritized roadmap with justifications for each recommended message type.

## Background

INAV currently supports a subset of DroneCAN messages:
- GPS (Fix, Fix2, Auxiliary)
- Barometer (StaticPressure, StaticTemperature)
- Magnetometer (MagneticFieldStrength, MagneticFieldStrength2)
- Airspeed (RawAirData, IndicatedAirspeed, TrueAirspeed)
- Rangefinder (Range)
- Battery (BatteryInfo - partial)
- ESC (Status, RPMCommand)
- Servo (ArrayCommand)
- SafetyState
- Lights (RGB565)

Many other DroneCAN messages exist that could benefit INAV users.

## Objectives

1. **Survey available DroneCAN messages**
   - Review UAVCAN v0 DSDL definitions
   - Identify messages relevant to flight controllers
   - Note which are commonly implemented by peripherals

2. **Evaluate each candidate message**
   - What functionality does it provide?
   - What hardware/peripherals use it?
   - How complex is implementation?
   - What user value does it add?

3. **Produce prioritized recommendations**
   - Rank by priority (HIGH/MEDIUM/LOW)
   - Justify each ranking
   - Note dependencies or prerequisites
   - Estimate implementation effort

## Categories to Consider

- **Sensors:** Additional sensor types (optical flow, LIDAR, IMU, etc.)
- **Actuators:** Motor/servo feedback, gimbal control
- **Power:** Detailed battery/power monitoring, fuel cells
- **Navigation:** GNSS augmentation, RTK, heading
- **Communication:** Telemetry bridges, transponders
- **System:** Node management, firmware update, time sync

## Deliverables

- [ ] Survey of relevant DroneCAN messages
- [ ] Prioritized list with justifications
- [ ] Implementation effort estimates
- [ ] FINDINGS.md with recommendations

## Related

- **dronecan-driver-docs:** Current implementation documentation
- **investigate-dronecan-battery-soc:** Example of missing message field
- **investigate-gps-messages-eph:** Example of missing functionality
