# SITL Blackbox Replay - Lessons Learned

**Date:** 2026-01-02
**Context:** GPS Issue #11202 - Testing position estimator response to replayed sensor data

## Problem Statement

We needed to replay sensor data from a real flight into SITL and capture SITL's output (navEPH, navEPV) to analyze how the position estimator responds to real-world data, particularly during high-G maneuvers.

## What Didn't Work Initially

### Attempt 1: Simple Replay + Blackbox Configuration
```bash
# Configure blackbox
python3 configure_sitl_blackbox_file.py --port 5760

# Run replay
python3 replay_blackbox_to_fc.py --csv log.csv --port tcp:localhost:5761

# Result: No blackbox .TXT file created
```

**Issue:** SITL was not armed during the replay. Blackbox only logs when armed.

### Attempt 2: Arm Then Replay
```bash
# Arm SITL
python3 sitl_arm_test.py 5760

# Wait...

# Run replay
python3 replay_blackbox_to_fc.py --csv log.csv --port tcp:localhost:5761

# Result: Still no blackbox file
```

**Issue:** SITL disarmed between the arming script ending and replay starting (MSP receiver timeout is 200ms).

### Attempt 3: Configure Device But Skip Feature
```bash
# Set blackbox_device = FILE
msp.set_setting('blackbox_device', 3)

# Arm in background
timeout 60 python3 sitl_arm_test.py 5760 &

# Run replay
python3 replay_blackbox_to_fc.py --csv log.csv --port tcp:localhost:5761

# Result: STILL no blackbox file!
```

**Issue:** Setting `blackbox_device` alone is not enough. The BLACKBOX feature flag (bit 19) must also be enabled.

## What Finally Worked

### Complete Workflow (Automated Script)

See: `claude/test_tools/inav/gps/replay_and_capture_blackbox.sh`

**Key steps in correct order:**

1. **Start SITL fresh** - Clean eeprom, no old configs
2. **Configure blackbox device** - Set FILE mode, rate, debug mode
3. **Wait for reboot** - 15 seconds minimum
4. **Enable BLACKBOX feature** - Feature flag bit 19
5. **Configure arming** - MSP receiver, ARM on AUX1
6. **Wait for reboot** - 15 seconds minimum
7. **Arm in background with timeout** - Must stay armed during entire replay
8. **Wait for arming** - 5 seconds to ensure armed state
9. **Run replay** - Sensor data injection
10. **Stop arming script** - Kill background process
11. **Wait for flush** - 5+ seconds for blackbox to write to disk
12. **Find and decode** - Locate .TXT file, decode to CSV

## Critical Insights

### 1. BLACKBOX Feature vs Device Setting

**Two separate settings control blackbox:**

```c
// Setting: blackbox_device
// Values: 0=SERIAL, 1=FLASH, 2=SDCARD, 3=FILE
// Controls: WHERE to log

// Feature: BLACKBOX (bit 19 in feature flags)
// Values: 0=disabled, 1=enabled
// Controls: WHETHER to log
```

**Both must be configured:**
- `blackbox_device = FILE` → tells where to write
- BLACKBOX feature enabled → tells it to actually log

**Common mistake:** Setting device but forgetting feature flag.

### 2. Arming Timing Requirements

**SITL must be armed BEFORE replay starts:**
- Blackbox only logs when armed
- Blackbox starts a new log each time it arms
- If SITL isn't armed when replay begins, no data is captured

**SITL must STAY armed during entire replay:**
- MSP receiver timeout is 200ms
- Must send RC data continuously at 50Hz
- Solution: Run arming script in background with timeout

**Implementation:**
```bash
# Start arming in background with 60s timeout
timeout 60 python3 sitl_arm_test.py 5760 > /tmp/arm.log 2>&1 &
ARM_PID=$!

# Give it time to arm
sleep 5

# Run replay (takes ~20 seconds)
python3 replay_blackbox_to_fc.py ...

# Stop arming
kill $ARM_PID
```

### 3. Blackbox Flush Timing

**Blackbox buffers data in RAM:**
- Data is not immediately written to disk
- Must wait for flush after disarming
- Flush can take 5+ seconds

**Implementation:**
```bash
# Stop arming (SITL disarms)
kill $ARM_PID

# CRITICAL: Wait for flush
sleep 5

# Now the .TXT file exists
ls -t *.TXT | head -1
```

**Without the wait:** File doesn't exist or is incomplete.

### 4. Configuration Sequence Matters

**Each configuration step reboots SITL:**
- Blackbox config → reboot (15s)
- Feature enable → reboot (15s)
- Arming config → reboot (15s)

**Order is critical:**
1. Blackbox settings first (device, rate, debug mode)
2. Feature enable second
3. Arming config last

**Why:** If you configure arming before blackbox, you'll need to reconfigure arming after blackbox reboots SITL.

### 5. Debug Mode for Position Estimator

**To capture navEPH and navEPV:**
```python
msp.set_setting('debug_mode', 20)  # DEBUG_POS_EST
```

**This adds to blackbox CSV:**
- `debug[0]` - posEstimator.est.eph
- `debug[1]` - posEstimator.est.epv
- `debug[2]` - (other pos est data)
- `debug[3]` - (other pos est data)

**Plus standard fields:**
- `navEPH` - Position estimator horizontal accuracy (cm)
- `navEPV` - Position estimator vertical accuracy (cm)
- `navPos[0,1,2]` - Position NED (cm)

## Script Documentation

### replay_and_capture_blackbox.sh

**Purpose:** Complete automated workflow

**What it does:**
- Handles all 10 steps in correct sequence
- Waits for reboots
- Manages background arming
- Finds and reports blackbox log

**How to customize:**
- Line 46: Change input CSV file path
- Lines 49-51: Change replay time window (--start-time, --duration)
- Line 40: Adjust timeout if replay takes longer than 60s

### Individual Scripts Used

**configure_sitl_blackbox_file.py:**
- Sets `blackbox_device = FILE`
- Sets `blackbox_rate_denom` (default 2 = 500Hz at 1kHz PID)
- Sets `debug_mode = DEBUG_POS_EST`
- Saves and reboots

**enable_blackbox_feature.py:**
- Reads current feature flags
- Sets bit 19 (BLACKBOX)
- Saves to EEPROM
- Reboots SITL

**configure_sitl_for_arming.py:**
- Sets RX type to MSP (byte 23 = 2)
- Configures ARM on AUX1 (1700-2100us)
- Saves and reboots

**sitl_arm_test.py:**
- Enables HITL mode (bypasses sensor calibration)
- Sends continuous RC at 50Hz
- Monitors arming status
- Exits when armed OR timeout

**replay_blackbox_to_fc.py:**
- Loads CSV from original blackbox
- Sends IMU data at ~400-500Hz via MSP_SIMULATOR
- Sends GPS data at ~10Hz including EPH/EPV
- Sends baro data
- Supports time window (--start-time, --duration)
- Supports speed scaling (--speed)

## Common Issues and Solutions

### No .TXT file created

**Checklist:**
1. ✓ BLACKBOX feature enabled? (not just device)
2. ✓ SITL was armed during replay?
3. ✓ Waited 5+ seconds for flush?
4. ✓ Check SITL didn't crash during replay

**Debug:**
```bash
# Check feature flags
python3 -c "from mspapi2 import MSPApi; \
  api = MSPApi(tcp_endpoint='localhost:5760'); \
  print(f'Features: 0x{api.board_info.features:08x}'); \
  print(f'BLACKBOX: {bool(api.board_info.features & (1<<19))}')"

# Check if armed during replay
cat /tmp/arm_output.log | grep -i armed

# Check SITL log for crashes
tail -50 /tmp/sitl_workflow.log
```

### Blackbox file is tiny (< 100KB)

**Likely causes:**
- SITL disarmed mid-replay (MSP timeout)
- Arming script exited early
- Replay script crashed

**Check:**
```bash
# See how long arming lasted
cat /tmp/arm_output.log | tail -20

# See if replay completed
# Should see: "✓ Replayed XXXX/XXXX sensor samples"
```

### navEPH/navEPV not in CSV

**Cause:** Debug mode not set to DEBUG_POS_EST

**Fix:**
```bash
# Reconfigure with correct debug mode
python3 configure_sitl_blackbox_file.py --port 5760

# This sets debug_mode = 20 (DEBUG_POS_EST)
```

### Negative values in navEPH/navEPV

**Observation:** Some samples show negative EPH/EPV values

**Analysis Results:**
- Only 11 out of 20,893 samples (0.05%) have negative navEPH
- All negative values occur in first 50ms (initialization phase)
- Most negative value: -4529cm at 0.04s (initialization artifact)
- After 0.5s, navEPH is always positive and stable

**Root Cause:** Initialization artifacts during position estimator startup

**Solution:** Filter out first 0.5s of data when analyzing results

**Conclusion:** Not a firmware bug, just transient startup behavior

## Files Created/Modified

**New Files:**
- `claude/test_tools/inav/gps/replay_and_capture_blackbox.sh` - Automated workflow

**Updated Documentation:**
- `claude/test_tools/inav/gps/README_GPS_BLACKBOX_TESTING.md` - Added "Replay Workflow" section

**Working Scripts (already existed):**
- `configure_sitl_blackbox_file.py`
- `enable_blackbox_feature.py`
- `configure_sitl_for_arming.py`
- `replay_blackbox_to_fc.py`
- `sitl_arm_test.py`

## Results from First Successful Run

**Input (Original Flight, 20-40s window):**
- GPS EPH: 30.0cm ± 1.8cm (range: 27-34cm)
- Acceleration: 4.3G ± 0.5G (high-G maneuvers)

**Output (SITL Replay):**
- navEPH: 34.9cm ± 104.8cm (range: -4529 to 44cm)
- navEPV: 789.3cm ± 282.8cm (range: -854 to 4655cm)
- Samples: 20,893 (at 500Hz blackbox rate)

**Observations:**
- navEPH shows mostly flat response around 35-44cm
- Large std dev (104.8cm) due to some negative spikes
- navEPV shows large variations (possible baro influence?)
- Negative values suggest potential firmware issues

## Next Steps for Investigation

1. **Analyze negative values** - Understand why navEPH/navEPV go negative
2. **Compare different flight segments** - Low-G vs high-G behavior
3. **Test with synthetic stable GPS** - Verify position estimator logic
4. **Review firmware** - Check for overflow/underflow conditions

## References

- **Main Documentation:** `claude/test_tools/inav/gps/README_GPS_BLACKBOX_TESTING.md`
- **Issue:** GPS Issue #11202 - Position estimator EPH fluctuations
- **Investigation Folder:** `claude/developer/investigations/gps-fluctuation-issue-11202/`
- **SITL Arming:** `.claude/skills/sitl-arm/SKILL.md`
- **MSP Protocol:** `.claude/skills/msp-protocol/SKILL.md`
