# Replay Blackbox to Flight Controller

**Tool:** `replay_blackbox_to_fc.py`

Replay GPS, IMU, barometer, and magnetometer data from decoded blackbox logs to a flight controller (SITL or HITL) via MSP_SIMULATOR.

## ⚠️ FIRMWARE MODIFICATION REQUIRED

**CRITICAL:** This tool sends real GPS EPH and EPV values from blackbox data to test navEPH calculations with actual GPS accuracy values.

**Stock INAV firmware HARDCODES EPH=100cm and EPV=100cm** and ignores the values sent by this tool.

### Required Firmware Modification

**Modified file:** `inav/src/main/fc/fc_msp.c`

**Changes:** Lines 4233-4260 modified to read EPH and EPV from MSP_SIMULATOR packet instead of hardcoding to 100cm.

**Build modified SITL:**
```bash
cd ~/Documents/planes/inavflight/inav/build_sitl
cmake -DSITL=ON ..
make
```

**Why this is needed:**
- Stock firmware: GPS EPH always = 100cm → navEPH calculations based on fixed value
- Modified firmware: GPS EPH from real log → navEPH calculations match real flight conditions
- This allows testing if oscillations in navEPH are caused by GPS EPH variations

**Verification:** After modification, SITL will log actual GPS EPH values instead of hardcoded 100cm.

## Quick Start

### 1. Decode Blackbox Log

```bash
~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode flight.TXT
# Creates: flight.01.csv (main sensor data)
#          flight.01.gps.csv (GPS data at 10 Hz)
```

**Note:** blackbox_decode creates two files:
- `.01.csv` - All sensor data at high rate (~100-1000 Hz)
- `.01.gps.csv` - GPS-only data at GPS update rate (~5-10 Hz)

### 2. Replay to SITL

```bash
# Start SITL
cd ~/Documents/planes/inavflight/inav/build_sitl
./bin/SITL.elf &
sleep 3

# Replay
python3 claude/test_tools/inav/gps/replay_blackbox_to_fc.py \\
    --csv flight.01.csv \\
    --port tcp:localhost:5761
```

### 3. Replay to Physical FC (HITL)

```bash
python3 claude/test_tools/inav/gps/replay_blackbox_to_fc.py \\
    --csv flight.01.csv \\
    --port /dev/ttyACM0
```

## Use Cases

- **Debug navigation bugs** - Reproduce issues in controlled environment
- **Test position estimator** - Validate navEPH calculations
- **Validate firmware fixes** - Ensure changes work with real flight data
- **Reproduce oscillations** - Debug GPS/EPH issues (Issue #11202)

## Features

- ✅ Works with both SITL (TCP) and HITL (serial)
- ✅ Replays GPS, accelerometer, gyro, barometer, magnetometer
- ✅ **Replays real GPS EPH and EPV values** (requires modified firmware)
- ✅ Preserves original timing or adjustable speed
- ✅ **Preserves GPS update rate** (loads from .gps.csv, keeps ~10 Hz)
- ✅ Time range filtering (--start-time, --duration)
- ✅ Handles missing GPS data gracefully
- ✅ Auto-detects sample rate

## Parameters

```bash
replay_blackbox_to_fc.py [OPTIONS]

Required:
  --csv FILE            Decoded blackbox CSV file

Optional:
  --port PORT           Port (default: tcp:localhost:5761)
                        SITL: tcp:localhost:5761
                        HITL: /dev/ttyACM0, /dev/ttyUSB0
  --start-time SECONDS  Start time (default: 0.0)
  --duration SECONDS    Duration (default: entire log)
  --speed MULTIPLIER    Playback speed (default: 1.0)
                        1.0=real-time, 2.0=2x, 0.5=half
```

## Examples

### Replay Specific Time Range

```bash
# Replay seconds 10-40 from log
python3 replay_blackbox_to_fc.py \\
    --csv flight.01.csv \\
    --start-time 10.0 \\
    --duration 30.0
```

### Replay at Different Speeds

```bash
# Fast replay (2x speed)
python3 replay_blackbox_to_fc.py --csv flight.01.csv --speed 2.0

# Slow replay (half speed)
python3 replay_blackbox_to_fc.py --csv flight.01.csv --speed 0.5
```

### HITL with Physical FC

```bash
# Replay to FC on /dev/ttyACM0
python3 replay_blackbox_to_fc.py \\
    --csv flight.01.csv \\
    --port /dev/ttyACM0 \\
    --start-time 20.0 \\
    --duration 10.0
```

## Complete Workflow

### SITL Testing

```bash
# 1. Build SITL (if not already built)
cd inav
mkdir -p build_sitl
cd build_sitl
cmake -DSITL=ON ..
make

# 2. Start SITL
./bin/SITL.elf &
sleep 3

# 3. Replay blackbox
cd ~/Documents/planes/inavflight
python3 claude/test_tools/inav/gps/replay_blackbox_to_fc.py \\
    --csv blackbox_real_log.01.csv \\
    --port tcp:localhost:5761 \\
    --start-time 11.0 \\
    --duration 11.0

# 4. Find SITL blackbox
ls -lt ~/*.TXT | head -1

# 5. Decode SITL log
~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode <sitl_log>.TXT

# 6. Analyze navEPH
# Compare original vs SITL navEPH to see if issue reproduced
```

### HITL Testing with Physical FC

```bash
# 1. Connect FC via USB
# 2. Ensure FC not in CLI mode
# 3. Replay
python3 claude/test_tools/inav/gps/replay_blackbox_to_fc.py \\
    --csv flight.01.csv \\
    --port /dev/ttyACM0

# 4. Download blackbox from FC
python3 claude/test_tools/inav/gps/download_blackbox_from_fc.py --port /dev/ttyACM0

# 5. Decode and analyze
```

## Requirements

### Python Packages

```bash
pip install mspapi2
```

Or install from project:

```bash
cd ~/Documents/planes/inavflight/mspapi2
pip install .
```

### Blackbox Tools

Already available at: `~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode`

## Technical Details

### MSP_SIMULATOR (0x201F)

Sends all sensor data to FC in HITL mode:

**Flags:**
- `0x0001` - HITL_ENABLE
- `0x0002` - HITL_HAS_NEW_GPS_DATA (only set when GPS timestamp matches)

**Data Sent:**
- GPS: position (lat/lon/alt), velocity (NED), EPH, satellites, HDOP
  - **GPS rate preserved:** Loaded from `.gps.csv`, sent only when timestamp matches (~10 Hz)
  - **Not artificially repeated:** GPS stays at real update rate, not IMU rate
- Accelerometer: X/Y/Z in milli-G (firmware divides by 1000)
- Gyro: X/Y/Z in deg/s × 16 (firmware divides by 16)
- Barometer: Pressure in Pa
- Magnetometer: X/Y/Z (firmware divides by 20)

**Firmware Reference:** `inav/src/main/fc/fc_msp.c:4160-4290`

### Field Conversions

| Blackbox Field | Units | MSP Format | Conversion |
|----------------|-------|------------|------------|
| `accSmooth[0-2]` | 1/512 G | milli-G (int16) | `/ 512.0 * 1000.0` |
| `gyroADC[0-2]` | deg/s × 16 | deg/s × 16 (int16) | Direct copy |
| `magADC[0-2]` | Raw | Scaled (int16) | `* 20` |
| `BaroAlt (cm)` | cm | Pressure (Pa) | `101325 - (alt_m * 12)` |
| `GPS_coord[0]` | degrees | degrees × 10^7 | `* 1e7` |
| `GPS_speed (m/s)` | m/s | cm/s (uint16) | `* 100` |

## Troubleshooting

### "mspapi2 not found"

```bash
cd ~/Documents/planes/inavflight/mspapi2
pip install .
```

### "Serial port is not open"

**For SITL:**
```bash
# Check SITL is running
ps aux | grep SITL
netstat -an | grep 5761
```

**For HITL:**
```bash
# Check serial port exists
ls -l /dev/ttyACM*

# Check permissions
sudo usermod -a -G dialout $USER
# Log out and back in
```

### "Could not enable HITL mode"

- Wait 3-5 seconds after starting SITL
- For HITL: Exit CLI mode on FC (type 'exit')
- Check connection is working

### No GPS Data Replayed

**GPS data is loaded from `.gps.csv` file (created by blackbox_decode):**

```bash
# Check if GPS file exists
ls -lh flight.01.gps.csv

# Verify GPS data
head -5 flight.01.gps.csv
```

**If no .gps.csv file:**
- GPS may not have been logged in blackbox settings
- Ensure GPS had fix during original flight
- Skip to GPS-lock time: `--start-time 10.0`

**GPS rate preservation:**
- GPS data sent at real rate (~10 Hz), not repeated at IMU rate
- Display shows "GPS: EPH=XXcm" when GPS sent (~every 100ms)
- Display shows "IMU only (no new GPS)" between GPS updates

### Data Replays Too Fast/Slow

```bash
# Adjust speed
--speed 2.0   # 2x faster
--speed 0.5   # Half speed
--speed 1.0   # Real-time (default)
```

## Related Tools

- **build-sitl** - Build INAV SITL for testing: `/build-sitl`
- **sitl-arm** - Arm SITL via MSP: `/sitl-arm`
- **download_blackbox_from_fc.py** - Download blackbox from FC
- **configure_sitl_blackbox_serial.py** - Configure SITL blackbox logging

## Related Investigations

- **GPS EPH Oscillation:** `claude/developer/investigations/gps-fluctuation-issue-11202/`
- **Blackbox Parsing:** `claude/developer/investigations/blackbox-parsing-issue/`

## See Also

- **Skill:** Use `/replay-blackbox` for interactive usage
- **Documentation:** `.claude/skills/replay-blackbox/SKILL.md`
- **Original tool:** Based on `replay_full_sensors.py` (Dec 31, 2025)
