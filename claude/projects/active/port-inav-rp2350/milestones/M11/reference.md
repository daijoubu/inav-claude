# M11: Navigation — RTH, Position Hold, Waypoints — Reference

**Goal:** Aircraft executes RTH, holds position, flies 3-waypoint mission.

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py --doc PDF navigation
./search.py --doc CHAT RTH
./search.py --doc CHAT GPS navigation
./search.py --doc MD GPS
./search.py --list-sections | grep -iE 'nav|rth|gps|position|waypoint|mission'
grep -n -i 'navigation\|rth\|waypoint\|position' inav_rp2350_port_plan.md | head -20
```

---

## Overview: Navigation Is Platform-Agnostic

INAV's navigation stack operates **above the HAL layer** — it uses GPS, baro, and IMU data
through standard interfaces already established in M5, M6, M9.

Once M6 (GPS UART working) and M9 (baro altitude) are solid, navigation should
"just work" with minimal RP2350-specific code. This milestone is mostly integration
and tuning rather than new driver work.

---

## Prerequisites (must be solid)

| Milestone | What Nav Needs |
|-----------|---------------|
| M5 (gyro) | IMU attitude estimate (roll/pitch) |
| M6 (GPS) | Position, velocity, course, satellites |
| M9 (baro) | Altitude estimate |
| M10 (flight) | Stable base flight mode |

---

## GPS Integration Checklist

```bash
# CLI verification before nav testing:
gpspassthrough   # Raw GPS output (verify NMEA/UBX parsing)
status           # Check: gpsSol.numSat >= 6 for 3D fix
status           # Check: gpsSol.fixType == GPS_FIX_3D
```

INAV GPS configuration (should already work from M6):
- Protocol: UBLOX (preferred) or NMEA
- Baud: 115200
- Dynamic model: airborne (for fixed-wing) or pedestrian (for initial testing)

---

## Baro Fusion

INAV fuses barometer altitude with GPS altitude using a complementary filter.
The nav estimator (`nav_estimator.c`) is platform-agnostic — only needs:
- `getEstimatedActualPosition(Z)` ← from baro (M9)
- `gpsSol.llh.alt` ← from GPS (M6)

---

## Home Position

```c
// Home is saved on ARM (when GPS fix is present):
// navSetHomePosition() called in arming code
// home.lat, home.lon, home.alt saved

// RTH uses:
// target_lat = home.lat
// target_lon = home.lon
// climb to rth_altitude, then fly home
```

---

## Position Hold (POSHOLD)

- Requires GPS 3D fix + sufficient satellites (≥6)
- INAV maintains position using horizontal PID controllers
- Vertical position via baro (Z-axis)
- Wind compensation via accelerometer velocity estimate

Typical POSHOLD PID values (start conservative):
```
posXY_P: 50  posXY_I: 0  posXY_D: 0
velXY_P: 200 velXY_I: 50 velXY_D: 0
```

---

## Return to Home (RTH)

INAV RTH sequence:
1. Climbs to RTH altitude (`nav_rth_altitude` setting)
2. Flies toward home waypoint
3. Descends when over home
4. Landing detection → motors stop

Verify settings:
```bash
set nav_rth_altitude = 2000    # 20m in cm
set nav_rth_altitude_mode = AT_LEAST   # minimum altitude
```

---

## Waypoint Missions

INAV waypoint format — 3-waypoint test mission:
```
WP 1: LAT, LON, ALT=20m, ACTION=WAYPOINT
WP 2: LAT, LON, ALT=30m, ACTION=WAYPOINT
WP 3: LAT, LON, ALT=20m, ACTION=RTH
```
Upload via Configurator → Missions tab, or via MSP.

Mission execution is entirely platform-agnostic (nav stack).

---

## INAV's Navigation Advantage vs BF

BF does NOT have a navigation stack — this is INAV's key differentiator.
The RP2350 port preserving full navigation capability is the primary reason
to port INAV rather than just running BF on the Pico 2.

---

## Common Navigation Issues

| Problem | Likely Cause |
|---------|-------------|
| No 3D fix | GPS not initialized, too few sats, dynamic model wrong |
| Position drift | Magnetometer not calibrated, interference |
| RTH overshoots | Nav PIDs too aggressive |
| Altitude unstable | Baro interference (wind, propwash) |
| Mission won't start | Home not set (arm without GPS fix) |

---

## Testing Sequence

1. **Pre-flight:** Confirm GPS fix (≥6 sats), home set on arm
2. **POSHOLD hover:** hover at 5m, enable POSHOLD → aircraft should hold position
3. **RTH test:** fly 30m away → switch RTH → aircraft returns and descends
4. **Waypoint mission:** upload 3-WP mission, arm, switch AUTO → mission executes
