# Investigation: How INAV Uses EPH and GPS Accuracy Data

**Date:** 2026-02-14
**Investigator:** Developer

---

## Executive Summary

**Can INAV estimate EPH internally?**

**NO** - INAV cannot currently estimate EPH from HDOP or other parameters. While a constant `GPS_HDOP_TO_EPH_MULTIPLIER` is defined, it is **never used** in the codebase. When a GPS driver doesn't provide EPH/EPV, INAV falls back to hardcoded defaults (200cm horizontal, 500cm vertical).

---

## Key Findings

### 1. GPS Accuracy Data Flow

```
GPS Hardware
    │
    ▼
[GPS Driver] ─────────────────────────────────────────────────────────────
    │  gps_ublox.c:  eph/epv from POSLLH or PVT messages (millimeters/10)
    │  gps_msp.c:    eph/epv from MSP packet
    │  gps_dronecan.c: eph/epv NOT SET (validEPE = false) ← GAP
    │
    ▼
gpsConstrainEPE() ─ Caps values at 9999cm (99.99m max)
    │
    ▼
gpsSol.eph, gpsSol.epv, gpsSol.flags.validEPE
    │
    ▼
[Position Estimator] ─ navigation_pos_estimator.c:251-258
    │
    ├─ if (validEPE == true)  → Use GPS-provided eph/epv
    │
    └─ if (validEPE == false) → Use defaults:
                                  INAV_GPS_DEFAULT_EPH = 200cm (2m)
                                  INAV_GPS_DEFAULT_EPV = 500cm (5m)
    │
    ▼
Compare eph/epv against max_eph_epv setting (CLI: inav_max_eph_epv)
    │
    ├─ eph < max_eph_epv AND epv < max_eph_epv → EST_GPS_XY_VALID | EST_GPS_Z_VALID
    ├─ eph < max_eph_epv only                  → EST_GPS_XY_VALID (no altitude)
    └─ eph >= max_eph_epv                      → GPS NOT USED for navigation
```

### 2. Where EPH Comes From (By GPS Protocol)

| Protocol | EPH Source | EPV Source | validEPE |
|----------|------------|------------|----------|
| **u-blox binary** | POSLLH.horizontal_accuracy or PVT.horizontal_accuracy | POSLLH.vertical_accuracy or PVT.vertical_accuracy | true |
| **MSP GPS** | mspSensorGpsDataMessage_t.horizontalPosAccuracy | mspSensorGpsDataMessage_t.verticalPosAccuracy | true |
| **NMEA** | Not directly available (would need GST sentence) | Not directly available | false |
| **DroneCAN** | **NOT IMPLEMENTED** (TODO in code) | **NOT IMPLEMENTED** | false |
| **Fake GPS** | Hardcoded 100cm | Hardcoded 100cm | true |

### 3. The Unused HDOP-to-EPH Multiplier

```c
// File: src/main/io/gps_private.h:24
#define GPS_HDOP_TO_EPH_MULTIPLIER      2   // empirical value
```

This constant is **defined but never used** anywhere in the codebase. There's also a `FIXME` comment in the position estimator:

```c
// File: navigation_pos_estimator.c:250
/* FIXME: use HDOP/VDOP */
```

This suggests the feature was planned but never implemented.

### 4. How EPH Affects Navigation

The position estimator uses EPH/EPV to gate GPS usage:

```c
// navigation_pos_estimator.c
const float max_eph_epv = positionEstimationConfig()->max_eph_epv;

if (posEstimator.gps.eph < max_eph_epv) {
    if (posEstimator.gps.epv < max_eph_epv) {
        newFlags |= EST_GPS_XY_VALID | EST_GPS_Z_VALID;  // Full 3D nav
    } else {
        newFlags |= EST_GPS_XY_VALID;  // XY only, no altitude hold
    }
}
```

**Settings:**
- `inav_max_eph_epv`: Maximum uncertainty for valid GPS (default: 1000cm = 10m)

### 5. DroneCAN GPS Gap

The DroneCAN driver (`gps_dronecan.c`) has TODO comments and sets `validEPE = false`:

```c
// Lines 98-103
// TODO where to get EPH gpsSolDRV.eph = gpsConstrainEPE(pgnssFix-> / 10);
// TODO where to get EPV gpsSolDRV.epv = gpsConstrainEPE(pkt->verticalPosAccuracy / 10);
gpsSolDRV.hdop = gpsConstrainHDOP(pgnssFix->pdop);
gpsSolDRV.flags.validVelNE = true;
gpsSolDRV.flags.validVelD = true;
gpsSolDRV.flags.validEPE = false;  // ← Always false
```

**However**, the DroneCAN Fix2 message **does contain a covariance matrix**:

```c
// uavcan.equipment.gnss.Fix2.h
struct uavcan_equipment_gnss_Fix2 {
    // ...
    struct { uint8_t len; float data[36]; } covariance;  // ← Position/velocity covariance
    float pdop;
    // ...
};
```

The covariance matrix can provide EPH/EPV:
- `covariance[0]` = variance in X (longitude)
- `covariance[1]` = covariance X-Y
- `covariance[2]` = variance in Y (latitude)
- `covariance[5]` = variance in Z (altitude)

**EPH = sqrt(covariance[0] + covariance[2])** (horizontal position variance)
**EPV = sqrt(covariance[5])** (vertical position variance)

---

## Recommendations

### Option 1: Use DroneCAN Covariance (Preferred)

Extract EPH/EPV from the Fix2 covariance matrix:

```c
if (pgnssFix2->covariance.len >= 6) {
    float var_x = pgnssFix2->covariance.data[0];  // meters²
    float var_y = pgnssFix2->covariance.data[2];  // meters²
    float var_z = pgnssFix2->covariance.data[5];  // meters²

    gpsSolDRV.eph = gpsConstrainEPE((uint32_t)(sqrtf(var_x + var_y) * 100));  // cm
    gpsSolDRV.epv = gpsConstrainEPE((uint32_t)(sqrtf(var_z) * 100));          // cm
    gpsSolDRV.flags.validEPE = true;
}
```

### Option 2: Estimate from HDOP (Fallback)

If covariance is not available, use the already-defined multiplier:

```c
if (pgnssFix->covariance.len == 0) {
    // HDOP * multiplier gives rough EPH estimate
    // HDOP is in 0.01 units, EPH is in cm
    gpsSolDRV.eph = gpsConstrainEPE(pgnssFix->pdop * GPS_HDOP_TO_EPH_MULTIPLIER);
    gpsSolDRV.epv = gpsConstrainEPE(pgnssFix->pdop * GPS_HDOP_TO_EPH_MULTIPLIER * 2);  // VDOP typically worse
    gpsSolDRV.flags.validEPE = false;  // Mark as estimated, not actual
}
```

### Option 3: Keep Default Fallback

Current behavior - when `validEPE = false`, position estimator uses defaults (200cm/500cm). This is conservative and safe but may not be optimal for high-accuracy GPS receivers.

---

## Units Reference

| Field | Storage Unit | Range | Max Value |
|-------|--------------|-------|-----------|
| eph | centimeters | 0-9999 | 99.99m |
| epv | centimeters | 0-9999 | 99.99m |
| hdop | centiunits | 0-9999 | 99.99 |
| u-blox accuracy | millimeters | - | - |
| DroneCAN covariance | meters² | - | - |

---

## Files Referenced

| File | Purpose |
|------|---------|
| `io/gps.h` | GPS solution data structure, flags |
| `io/gps.c` | GPS constraint functions |
| `io/gps_private.h` | GPS_HDOP_TO_EPH_MULTIPLIER constant |
| `io/gps_ublox.c` | u-blox protocol (POSLLH, PVT messages) |
| `io/gps_dronecan.c` | DroneCAN GPS (Fix, Fix2 messages) |
| `io/gps_msp.c` | MSP GPS data |
| `navigation/navigation_pos_estimator.c` | Position estimator, EPH usage |
| `navigation/navigation_pos_estimator_private.h` | Default EPH/EPV constants |
| `fc/settings.yaml` | inav_max_eph_epv setting |

---

## Conclusion

INAV **requires** EPH/EPV from the GPS receiver for optimal navigation. It cannot estimate these values internally. The DroneCAN implementation should extract EPH/EPV from the covariance matrix in Fix2 messages. If covariance is not provided, the defaults (2m horizontal, 5m vertical) will be used, which is acceptable for most navigation but may not leverage the full accuracy of high-precision GPS receivers.
