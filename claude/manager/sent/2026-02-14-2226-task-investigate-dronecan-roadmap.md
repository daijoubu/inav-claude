# Task Assignment: Investigate DroneCAN Messages Roadmap

**From:** Manager
**To:** Developer
**Date:** 2026-02-14
**Priority:** MEDIUM
**Type:** Investigation
**Estimated Effort:** 3-4 hours

---

## Task

Research the DroneCAN/UAVCAN message catalog and identify which additional messages INAV should support. Produce a **prioritized roadmap** with justifications for each recommended message type.

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

## Deliverables

### 1. Survey Available Messages
- Review UAVCAN v0 DSDL definitions
- Identify messages relevant to flight controllers
- Note which are commonly implemented by peripherals

### 2. Evaluate Candidates
For each candidate message, assess:
- What functionality does it provide?
- What hardware/peripherals use it?
- How complex is implementation?
- What user value does it add?

### 3. Prioritized Roadmap
Produce a ranked list with:
- **Priority:** HIGH / MEDIUM / LOW
- **Justification:** Why this priority?
- **Effort estimate:** Hours to implement
- **Dependencies:** Prerequisites if any

## Categories to Consider

- **Sensors:** Optical flow, LIDAR, IMU, temperature, humidity
- **Actuators:** Motor/servo feedback, gimbal control
- **Power:** Detailed battery monitoring, fuel cells, power distribution
- **Navigation:** GNSS augmentation, RTK, heading sources
- **Communication:** Telemetry bridges, transponders (ADS-B)
- **System:** Node management, firmware update, time sync

## Output Format

Create FINDINGS.md with structure:
```markdown
# DroneCAN Messages Roadmap

## Currently Supported
<list of current messages>

## Recommended Additions

### HIGH Priority
#### 1. <Message Name>
- **What:** <description>
- **Why:** <justification>
- **Effort:** X hours
- **Peripherals:** <what uses this>

### MEDIUM Priority
...

### LOW Priority
...

## Not Recommended
<messages evaluated but not worth implementing, with reasons>
```

## Project Directory

`claude/projects/active/investigate-dronecan-messages-roadmap/`

Send FINDINGS.md and completion report to Manager when done.
