# FINDINGS: DroneCAN NodeStatus Content Investigation

**Date:** 2026-02-15
**Project:** investigate-dronecan-nodestatus-content

## Phase 1: Current Implementation

### Current INAV NodeStatus Broadcasting

**File:** `inav/src/main/drivers/dronecan/dronecan.c`

```c
void send_NodeStatus(void) {
    node_status.uptime_sec = millis() / 1000UL;
    node_status.health = UAVCAN_PROTOCOL_NODESTATUS_HEALTH_OK;   // Always OK
    node_status.mode = UAVCAN_PROTOCOL_NODESTATUS_MODE_OPERATIONAL;  // Always OPERATIONAL
    node_status.sub_mode = 0;
    node_status.vendor_specific_status_code = 1234;  // Hardcoded
}
```

- **Broadcast frequency:** 1 Hz (from line 418 in dronecan.c)
- **Health:** Always `OK` - not tracking any INAV states
- **Mode:** Always `OPERATIONAL` - not tracking INAV mode
- **Vendor-specific:** Hardcoded to 1234

### NodeStatus Structure (UAVCAN v0)

From `uavcan.protocol.NodeStatus`:
| Field | Size | Description |
|-------|------|-------------|
| `uptime_sec` | 32-bit | Seconds since boot |
| `health` | 2-bit | OK(0), WARNING(1), ERROR(2), CRITICAL(3) |
| `mode` | 3-bit | OPERATIONAL(0), INITIALIZATION(1), MAINTENANCE(2), SOFTWARE_UPDATE(3), OFFLINE(7) |
| `sub_mode` | 3-bit | Reserved |
| `vendor_specific_status_code` | 16-bit | Custom encoding |

## Phase 2: INAV State Analysis

### States Relevant to "Health"

| INAV State | Condition | Proposed Health Mapping |
|------------|-----------|------------------------|
| Normal operation | All sensors OK, GPS locked | OK |
| GPS not fixed | No GPS lock or HDOP too high | WARNING |
| Low battery | Battery below warning threshold | WARNING |
| Failsafe active | In failsafe procedure (RTH/Landing) | ERROR |
| Sensor failure | Gyro/accel/baro failure | ERROR |
| Critical failsafe | Landing detected / crashed | CRITICAL |
| System overloaded | CPU overload detected | WARNING |
| Hardware failure | Hardware failure flag set | CRITICAL |

### States Relevant to "Mode"

| INAV State | Proposed Mode Mapping |
|------------|----------------------|
| Normal flight (armed) | OPERATIONAL |
| CLI active | MAINTENANCE |
| Bootloader mode | OFFLINE |
| Calibrating sensors | INITIALIZATION |
| In-flight (any mode) | OPERATIONAL |
| Crashed/Landed | OPERATIONAL |

### Candidate for vendor_specific_status_code

This 16-bit field could encode detailed status:

```
Bits 0-3:   Primary health (health enum value)
Bits 4-7:   Failsafe phase (if in failsafe)
Bits 8-11:  Flight mode (manual, RTH, PosHold, etc.)
Bits 12-13: Arming state (disarmed, arming, armed)
Bits 14-15: Reserved
```

Or alternatively, encode specific flags:
- GPS fix status (none, 2D, 3D)
- Battery percentage
- RSSI
- Number of satellites

## Phase 3: Recommendations

### Recommended Health Mapping

```c
uint8_t getNodeStatusHealth(void) {
    // CRITICAL: Hardware failure or crash
    if (ARMING_FLAG(HARDWARE_FAILURE) || STATE(LANDED)) {
        return UAVCAN_PROTOCOL_NODESTATUS_HEALTH_CRITICAL;
    }

    // ERROR: Failsafe active or critical sensor issue
    if (FLIGHT_MODE(FAILSAFE_MODE) || failsafePhase() >= FAILSAFE_LANDING) {
        return UAVCAN_PROTOCOL_NODESTATUS_HEALTH_ERROR;
    }

    // WARNING: Non-critical issues
    if (isArmingDisabled() || isSystemOverloaded()) {
        return UAVCAN_PROTOCOL_NODESTATUS_HEALTH_WARNING;
    }

    // OK: Normal operation
    return UAVCAN_PROTOCOL_NODESTATUS_HEALTH_OK;
}
```

### Recommended Mode Mapping

```c
uint8_t getNodeStatusMode(void) {
    if (isCalibrating()) {
        return UAVCAN_PROTOCOL_NODESTATUS_MODE_INITIALIZATION;
    }

    if (ARMING_FLAG(CLI)) {
        return UAVCAN_PROTOCOL_NODESTATUS_MODE_MAINTENANCE;
    }

    // Note: We cannot detect bootloader mode from the application

    return UAVCAN_PROTOCOL_NODESTATUS_MODE_OPERATIONAL;
}
```

### Recommended Vendor-Specific Encoding

Use the 16-bit field to expose useful debugging info:

```c
uint16_t getVendorSpecificStatusCode(void) {
    uint16_t code = 0;

    // GPS info (bits 0-3): Fix type
    code |= (gpsFix >= GPS_FIX_3D ? 3 : gpsFix >= GPS_FIX_2D ? 2 : 1) << 0;

    // Battery SOC (bits 4-9): Percentage / 2 (0-200 -> 0-100%)
    code |= (getBatteryRemainingCapacity() / 2) << 4;

    // Arming state (bits 10-11): 0=disarmed, 1=arming, 2=armed
    code |= (ARMING_FLAG(ARMED) ? 2 : isArmingDisabled() ? 1 : 0) << 10;

    // RSSI (bits 12-13): Quality indicator
    code |= (getRSSI() > 70 ? 3 : getRSSI() > 50 ? 2 : 1) << 12;

    return code;
}
```

## Trade-offs and Concerns

1. **Performance impact:** Calling these getters at 1 Hz is negligible, but avoid complex operations
2. **GPS access:** Need to ensure GPS data is safe to read from the DroneCAN task context
3. **Reentrancy:** Must ensure atomic reads of multi-byte values
4. **Backward compatibility:** Hardcoded 1234 may be relied upon by existing tools - consider documenting the new format
5. **Mode limitations:** Cannot detect bootloader mode from application firmware

## Implementation Notes

- Update `send_NodeStatus()` function in `dronecan.c`
- May need to expose some state functions if not already public
- Test on SITL before hardware
- Consider adding a setting to enable/disable detailed status (default: simple for compatibility)

## Summary

The current implementation broadcasts a static "OK/OPERATIONAL" status that provides no useful information to other nodes. The recommended changes would:

1. **Health:** Report actual system health (OK/WARNING/ERROR/CRITICAL based on failsafe, sensors, arming disabled)
2. **Mode:** Report CLI/maintenance mode when applicable
3. **Vendor-specific:** Encode GPS fix, battery SOC, arming state, RSSI

This enables DroneCAN GUI tools and other nodes to monitor INAV health status in real-time.
