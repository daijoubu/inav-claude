# GPS Monitoring & Diagnostic Scripts

Scripts for monitoring GPS status, checking configuration, and analyzing GPS/position estimation data.

## Quick Start

```bash
# Check GPS configuration
python3 check_gps_config.py

# Monitor real-time GPS data
python3 monitor_gps_status.py

# Test GPS data reading
python3 test_gps_read.py
```

## Scripts

### monitor_gps_status.py
**Real-time GPS data monitoring**

Displays live GPS data stream including position, satellites, HDOP, and fix status.

```bash
python3 monitor_gps_status.py [--port PORT]
```

**Output Example:**
```
GPS Status:
  Fix: 3D
  Satellites: 12
  HDOP: 1.2
  Lat: 37.7749°
  Lon: -122.4194°
  Alt: 15m
  EPH: 2.4m
  EPV: 3.1m
```

**Use cases:**
- Verify GPS is receiving data
- Monitor GPS quality during tests
- Debug GPS signal issues

---

### check_gps_config.py
**Verify GPS configuration settings**

Queries and displays GPS configuration including provider, baud rate, and protocol settings.

```bash
python3 check_gps_config.py [--port PORT]
```

**Output:**
- GPS provider (UBLOX, MSP, NMEA, etc.)
- GPS auto-config status
- GPS auto-baud status
- SBAS mode
- UBLOX-specific settings

**Use case:** Verify GPS is configured correctly before testing

---

### test_gps_read.py
**Test GPS data reading** - Basic connectivity test

```bash
python3 test_gps_read.py [--port PORT]
```

---

### analyze_naveph_spectrum.py
**Frequency analysis of navEPH**

Performs FFT spectrum analysis on navEPH (estimated position error) from blackbox logs.

```bash
python3 analyze_naveph_spectrum.py <blackbox.csv>
```

**Input:** Decoded blackbox CSV with navEPH column

**Output:**
- FFT spectrum of navEPH signal
- Dominant frequencies identified
- Helps identify periodic patterns in position errors

**Use case:** Debugging position estimator oscillations or instabilities


## Common Workflows

**Check GPS:** `python3 check_gps_config.py && python3 monitor_gps_status.py`

**Debug GPS Issues:** `python3 test_gps_read.py` → `monitor_gps_status.py` → `check_gps_config.py`

**Analyze Position Estimator:**
1. Capture blackbox: `cd ../workflows && ./run_gps_blackbox_test.sh climb 60`
2. Decode: `blackbox_decode *.TXT`
3. Analyze: `python3 analyze_naveph_spectrum.py blackbox.01.csv`

## Dependencies

- **mspapi2:** GPS monitoring scripts - `pip3 install ~/Documents/planes/inavflight/mspapi2`
- **numpy, scipy:** For spectrum analysis - `pip3 install numpy scipy matplotlib`

## Port Configuration

**Default port:** 5760 (UART1 MSP)

**Override port:**
```bash
python3 monitor_gps_status.py --port 5761
```

## Notes

**Real-time vs Logged Data:**
- `monitor_gps_status.py`, `check_gps_config.py`, `test_gps_read.py` - Work with live FC/SITL
- `analyze_naveph_spectrum.py` - Analyzes logged blackbox data

**Monitoring Duration:**
- Press Ctrl+C to stop `monitor_gps_status.py`
- Script runs indefinitely by default

**SITL vs Physical FC:**
- All scripts work with both SITL (port 5760) and physical FC (usually /dev/ttyACM0)
- Use `--port` parameter to specify non-default port/device

## Troubleshooting

**No GPS data:** Check SITL running → GPS provider configured → GPS injection active
**Connection timeout:** Verify port → Check SITL responding → No port conflicts

## See Also

- `../injection/` - Scripts to inject GPS data for monitoring
- `../docs/README_GPS_BLACKBOX_TESTING.md` - Blackbox logging with GPS/EPH data
- `../docs/HIGH_FREQUENCY_LOGGING_STATUS.md` - Performance analysis
