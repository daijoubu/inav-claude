# GPS Messages and EPH Investigation Summary

**Date:** 2026-02-14
**Project:** investigate-gps-messages-eph

## Executive Summary

INAV does **not** calculate or estimate EPH (Estimated Position Horizontal). It relies entirely on GPS-provided accuracy values. When GPS doesn't provide EPH/EPV, INAV falls back to hardcoded default values (2m EPH, 5m EPV).

## Key Findings

### 1. GPS Protocols Supported

INAV supports these GPS protocols (no NMEA):

| Protocol | File | Status |
|----------|------|--------|
| u-blox binary | `gps_ublox.c` | Full support |
| MSP | `gps_msp.c` | Full support |
| DroneCAN | `gps_dronecan.c` | Partial - missing EPH/EPV |
| Fake | `gps_fake.c` | Testing only |

### 2. GPS Data Flow

```
Driver (gps_ublox.c, gps_msp.c, gps_dronecan.c)
    ↓
gpsSolDRV (filled by driver)
    ↓
gpsProcessNewDriverData()
    ↓
gpsSol (processed solution)
    ↓
Position Estimator (navigation_pos_estimator.c)
```

### 3. Accuracy Fields in gpsSolutionData_t

From `gps.h`:
```c
uint16_t eph;   // horizontal accuracy (cm)
uint16_t epv;   // vertical accuracy (cm)
uint16_t hdop;  // generic HDOP value (*HDOP_SCALE)
bool validEPE;  // EPH/EPV values are valid
```

### 4. Position Estimator Handling

From `navigation_pos_estimator.c` (lines 250-258):
```c
/* FIXME: use HDOP/VDOP */
if (gpsSol.flags.validEPE) {
    posEstimator.gps.eph = gpsSol.eph;
    posEstimator.gps.epv = gpsSol.epv;
}
else {
    posEstimator.gps.eph = INAV_GPS_DEFAULT_EPH;    // 200cm (2m)
    posEstimator.gps.epv = INAV_GPS_DEFAULT_EPV;     // 500cm (5m)
}
```

**Key insight:** The FIXME comment indicates HDOP/VDOP should be used to estimate EPH when GPS doesn't provide it directly, but this is not implemented.

### 5. DroneCAN GPS Driver Gaps

The DroneCAN GPS driver (`gps_dronecan.c`) has TODO comments for EPH/EPV:
```c
// TODO where to get EPH gpsSolDRV.eph = gpsConstrainEPE(pgnssFix-> / 10);
// TODO where to get EPV gpsSolDRV.epv = gpsConstrainEPE(pkt->verticalPosAccuracy / 10);
```

This means DroneCAN GPS currently relies on the default 2m EPH.

### 6. GPS Accuracy Requirements

The position estimator uses EPH for:
- GPS blending with other sensors (baro, optical flow)
- Navigation mode acceptance criteria
- `max_eph_epv` setting in navigation config

## Answers to Research Questions

### Q: Which GPS messages does INAV parse?
A: INAV does NOT parse NMEA messages. It uses u-blox binary protocol, MSP, and DroneCAN.

### Q: How does GPS data flow into the position estimator?
A: Driver → `gpsSolDRV` → `gpsProcessNewDriverData()` → `gpsSol` → Position estimator reads from `gpsSol`

### Q: Can INAV estimate EPH when GPS doesn't provide it?
A: **No.** INAV uses hardcoded defaults (2m EPH, 5m EPV) when GPS doesn't provide valid accuracy data. There is a FIXME comment suggesting HDOP could be used to estimate EPH, but this is not implemented.

### Q: What GPS accuracy fields are used?
A: Primary: `eph`, `epv` (cm). Secondary: `hdop` (currently not used for estimation, just stored).

## Implications for DroneCAN GPS Integration

1. **Missing EPH/EPV in DroneCAN:** The DroneCAN GPS driver needs to extract accuracy data from the DroneCAN GnssFix message to populate EPH/EPV.

2. **Fallback behavior:** Without accuracy data, INAV defaults to conservative 2m/5m values.

3. **Future enhancement:** Could implement HDOP-based EPH estimation using the formula: `EPH ≈ HDOP * DOP_scale` where typical DOP_scale is ~2-5m.

## References

- GPS driver code: `inav/src/main/io/gps.c`, `gps_ublox.c`, `gps_dronecan.c`
- Position estimator: `inav/src/main/navigation/navigation_pos_estimator.c`
- GPS data structures: `inav/src/main/io/gps.h`
- Default values: `inav/src/main/navigation/navigation_pos_estimator_private.h`
