# GPS Data Injection Scripts

Scripts for injecting synthetic GPS data into SITL or physical FC via MSP for testing position estimation and navigation algorithms.

## Quick Start

```bash
# Inject GPS altitude with climb profile (0m → 100m)
python3 inject_gps_altitude.py --profile climb --duration 30

# Simulate GPS fluctuation (Issue #11202)
python3 simulate_gps_fluctuation_issue_11202.py
```

## Scripts

### inject_gps_altitude.py
**Primary GPS altitude injection script**

Injects simulated altitude data via MSP_SET_RAW_GPS. Designed to work with CRSF RC sender on separate port.

```bash
python3 inject_gps_altitude.py [OPTIONS]

Options:
  --profile PROFILE    Motion profile: climb, descent, hover, sine (default: climb)
  --duration SECONDS   Duration in seconds (default: 20)
  --port PORT         MSP port (default: 5760)
```

**Profiles:**
- `climb` - 0m → 100m at 5 m/s
- `descent` - 100m → 0m at 2 m/s
- `hover` - Constant 50m
- `sine` - Oscillating ±30m around 50m

**Port:** Uses port 5760 (UART1 MSP) - can run concurrent with CRSF on 5761

---

### simulate_gps_fluctuation_issue_11202.py
**Reproduces GPS signal instability from Issue #11202**

Simulates EPH spikes, HDOP fluctuations, and satellite count variations observed in real-world u-blox GPS modules.

```bash
python3 simulate_gps_fluctuation_issue_11202.py
```

**What it simulates:**
- HDOP fluctuations (2.0-5.0 range instead of stable ~1.3)
- Satellite count variations (15-25 instead of stable 25+)
- EPH spikes similar to flight log observations

**Issue:** https://github.com/iNavFlight/inav/issues/11202

---

### simulate_altitude_motion.py
**Standalone altitude motion generator**

Alternative GPS altitude injection script. Similar to inject_gps_altitude.py but standalone implementation.

```bash
python3 simulate_altitude_motion.py
```

**Note:** Consider using `inject_gps_altitude.py` for new work (more flexible, actively maintained).

---

### gps_inject_no_arming.py
**GPS injection without ARM requirement**

Injects GPS data without requiring SITL/FC to be armed. Useful for pre-arm testing.

```bash
python3 gps_inject_no_arming.py
```

---

### gps_with_rc_keeper.py
**GPS injection + RC sender combined**

Combines GPS altitude injection with continuous RC commands to keep SITL armed during test.

```bash
python3 gps_with_rc_keeper.py --profile climb --duration 60
```

**Note:** For better separation, use `../workflows/test_motion_simulator.sh` which coordinates separate processes.

---

### set_gps_provider_msp.py
**Configure GPS provider to MSP**

Sets GPS provider to MSP so that injected GPS data is used by FC.

```bash
python3 set_gps_provider_msp.py [--port PORT]
```

**Required:** Must run before GPS injection scripts will work.

## Dependencies

- **mspapi2:** Modern MSP library - `pip3 install ~/Documents/planes/inavflight/mspapi2`
- **uNAVlib:** Legacy library (used by some older scripts)

## Common Usage Patterns

**Basic GPS altitude test:**
```bash
# 1. Set GPS provider to MSP
python3 set_gps_provider_msp.py

# 2. Inject GPS data
python3 inject_gps_altitude.py --profile climb --duration 30
```

**With telemetry monitoring:**
```bash
# Use workflow script instead (recommended)
cd ../workflows
./test_motion_simulator.sh climb 30
```

**GPS fluctuation testing:**
```bash
# Reproduce Issue #11202
python3 simulate_gps_fluctuation_issue_11202.py
```

## Notes

- All scripts use MSP port **5760** by default (UART1)
- Can run concurrent with CRSF telemetry on port **5761**
- GPS provider must be set to MSP before injection works
- SITL must be armed for navigation to activate (except gps_inject_no_arming.py)

## See Also

- `../workflows/` - Integration workflows using these scripts
- `../testing/` - GPS navigation tests that use injected data
- `../docs/README_GPS_BLACKBOX_TESTING.md` - Complete testing workflows
