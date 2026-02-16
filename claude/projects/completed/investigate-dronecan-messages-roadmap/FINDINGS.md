# FINDINGS: DroneCAN Messages Roadmap Investigation

**Date:** 2026-02-15
**Project:** investigate-dronecan-messages-roadmap

## Phase 1: Current State

### Messages Currently Supported by INAV

| Message | Direction | File | Status |
|---------|-----------|------|--------|
| **uavcan.protocol.NodeStatus** | Rx/Tx | dronecan.c:50,230 | Full - broadcasts 1Hz, receives from others |
| **uavcan.protocol.GetNodeInfo** | Rx | dronecan.c:184 | Full - responds to info requests |
| **uavcan.equipment.gnss.Fix** | Rx | dronecan.c:114 | Full - GPS position data |
| **uavcan.equipment.gnss.Fix2** | Rx | dronecan.c:132 | Full - Extended GPS data |
| **uavcan.equipment.gnss.Auxiliary** | Rx | dronecan.c:103 | Full - Satellite counts, HDOP |
| **uavcan.equipment.gnss.RTCMStream** | Rx | dronecan.c:150 | Full - RTCM correction data |
| **uavcan.equipment.power.BatteryInfo** | Rx | dronecan.c:161 | Partial - Voltage/current OK, SOC missing |

### Partially Implemented Messages

**BatteryInfo (equipment.power.BatteryInfo):**
- Currently receives: voltage, current, temperature
- Missing: State of Charge (SOC) - this is a planned enhancement

### Structure (from dronecan.c)

```c
// Handlers (receiving)
void handle_NodeStatus(...)
void handle_GNSSAuxiliary(...)
void handle_GNSSFix(...)
void handle_GNSSFix2(...)
void handle_GNSSRCTMStream(...)
void handle_BatteryInfo(...)
void handle_GetNodeInfo(...)

// Senders (broadcasting)
void send_NodeStatus(void)
```

## Phase 2: Message Survey

### Available DSDL Messages (in dsdlc_generated/)

The DSDL directory contains ~80+ message types. Key categories:

#### equipment.gnss.* (GPS)
| Message | Purpose | Priority |
|---------|---------|----------|
| Fix | Position, velocity, timestamp | DONE |
| Fix2 | Extended fix with accuracy | DONE |
| Auxiliary | Satellites, HDOP | DONE |
| RTCMStream | RTK corrections | DONE |
| ECEFPositionVelocity | Raw ECEF P/V | LOW |

#### equipment.power.*
| Message | Purpose | Priority |
|---------|---------|----------|
| BatteryInfo | Voltage, current, SOC | HIGH - SOC missing |
| CircuitStatus | Power circuit status | MEDIUM |
| PrimaryPowerSupplyStatus | Main power status | LOW |

#### equipment.actuator.*
| Message | Purpose | Priority |
|---------|---------|----------|
| Command | Motor/servo commands | MEDIUM - ESC support |
| Status | ESC feedback (RPM, temp) | MEDIUM |
| ArrayCommand | Multiple commands | LOW |

#### equipment.esc.*
| Message | Purpose | Priority |
|---------|---------|----------|
| Status | RPM, voltage, temp, error | MEDIUM |
| StatusExtended | Detailed ESC status | LOW |
| RawCommand | Motor command | LOW |

#### equipment.ahrs.*
| Message | Purpose | Priority |
|---------|---------|----------|
| Solution | AHRS/INS solution | LOW |
| RawIMU | Raw IMU data | LOW |
| MagneticFieldStrength | Mag data | LOW |

#### equipment.air_data.*
| Message | Purpose | Priority |
|---------|---------|----------|
| IndicatedAirspeed | IAS | MEDIUM - pitot tube |
| TrueAirspeed | TAS | LOW |
| StaticPressure | Baro | LOW |
| RawAirData | Combined air data | LOW |

#### equipment.safety.*
| Message | Purpose | Priority |
|---------|---------|----------|
| ArmingStatus | Arming state | MEDIUM |

#### equipment.camera_gimbal.*
| Message | Purpose | Priority |
|---------|---------|----------|
| Status | Gimbal status | LOW |
| AngularCommand | Gimbal angles | LOW |
| Mode | Gimbal mode | LOW |

#### protocol.*
| Message | Purpose | Priority |
|---------|---------|----------|
| dynamic_node_id.Allocation | DNA (auto node ID) | HIGH - planned |
| param.* | Parameter protocol | MEDIUM - planned |
| RestartNode | Remote reboot | LOW |
| GlobalTimeSync | Time sync | LOW |

## Phase 3: Evaluation

### Priority Rankings

#### HIGH Priority

| Message | Functionality | User Value | Complexity | Notes |
|---------|---------------|------------|------------|-------|
| BatteryInfo SOC | State of Charge | High | Low | Already receiving message, just need to parse field |
| dynamic_node_id.Allocation | Auto node ID | High | Medium | Simplifies setup, DNA already in DSDL |
| ESC Status | Telemetry from ESCs | High | Medium | Popular with BLHeli_32 users |

#### MEDIUM Priority

| Message | Functionality | User Value | Complexity | Notes |
|---------|---------------|------------|------------|-------|
| equipment.safety.ArmingStatus | Show arming status | Medium | Low | Nice to have |
| Airspeed (indicated/true) | Airspeed data | Medium | Low | Already have pitot support |
| ESC Command | Motor control | High | High | Complex, safety concerns |
| param.GetSet | Remote config | Medium | High | Better through MSP |

#### LOW Priority

| Message | Functionality | User Value | Complexity | Notes |
|---------|---------------|------------|------------|-------|
| Gimbal control | Camera gimbal | Low | Medium | Niche use case |
| AHRS solutions | External IMU | Low | Medium | Rare hardware |
| File transfer | Firmware updates | Low | High | Overkill |

## Phase 4: Recommendations

### Recommended Implementation Order

1. **BatteryInfo SOC** - Low effort, high value
   - Just parse the `remaining_capacity_anounce` field
   - Already receiving the message

2. **Dynamic Node Allocation** - Medium effort, high value
   - DNA simplifies setup for new users
   - DSDL files already available
   - Need to implement Allocation handler

3. **ESC Status** - Medium effort, high value
   - BLHeli_32 supports DroneCAN telemetry
   - Show RPM, voltage, temperature on OSD
   - Add handle_ESCStatus()

4. **Airspeed via DroneCAN** - Low effort, medium value
   - If user has DroneCAN pitot
   - Standard message format

5. **ArmingStatus** - Low effort, nice to have
   - Share arming state over CAN

### Dependencies

- **BatteryInfo SOC**: None - just parse existing field
- **DNA**: Requires understanding of allocation protocol (see libcanard examples)
- **ESC Status**: Need to understand BLHeli_32 DroneCAN protocol specifics

### Estimated Effort

| Feature | Hours |
|---------|-------|
| BatteryInfo SOC | 1-2 |
| Dynamic Node Allocation | 8-12 |
| ESC Status | 8-12 |
| Airspeed | 2-4 |
| ArmingStatus | 2-4 |

## Summary

INAV currently supports 7 DroneCAN messages (GPS x4, Battery x1, NodeInfo x1, NodeStatus x1) with BatteryInfo SOC as the main gap in existing functionality.

The recommended roadmap prioritizes:
1. BatteryInfo SOC (quick win)
2. Dynamic Node Allocation (usability improvement)
3. ESC Status (popular feature)

Lower priority: gimbal, file transfer, remote parameters.
