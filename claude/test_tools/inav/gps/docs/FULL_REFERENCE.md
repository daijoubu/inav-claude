# GPS Testing Tools

Comprehensive GPS testing infrastructure for INAV firmware, supporting motion simulation, blackbox logging, position estimation analysis, and automated test workflows for both SITL (Software-in-the-Loop) and physical flight controllers.

**Directory:** `claude/test_tools/inav/gps/`
**Tools:** 44 Python scripts and shell wrappers
**Primary Use Cases:**
- GPS navigation testing (RTH, position hold, waypoints)
- Motion simulation with CRSF telemetry validation
- Blackbox logging for EPH/navEPH analysis
- GPS signal fluctuation investigation (Issue #11202)
- Position estimator debugging

---

## Quick Start Guide

### 1. Motion Simulation with Telemetry (Recommended)

**Test CRSF telemetry with simulated GPS altitude changes:**

```bash
cd ~/Documents/planes/inavflight/claude/test_tools/inav/gps

# Run 20-second climb test (0m → 100m at 5 m/s)
./test_motion_simulator.sh climb 20

# Run descent test (100m → 0m at 2 m/s)
./test_motion_simulator.sh descent 30

# Available profiles: climb, descent, hover, sine
```

**What it does:**
- Starts CRSF RC sender (port 5761) to keep SITL armed and receive telemetry
- Injects GPS altitude via MSP (port 5760) using selected motion profile
- Displays live CRSF telemetry including GPS altitude from FC
- Saves logs to `/tmp/motion_test_*.log`

**Result:** Validates that GPS altitude injected via MSP appears correctly in CRSF telemetry.

---

### 2. GPS + Blackbox Logging

**Capture blackbox logs while injecting GPS data:**

```bash
# Complete automated workflow
./run_gps_blackbox_test.sh climb 60

# Manual step-by-step approach (see README_GPS_BLACKBOX_TESTING.md)
```

**What it does:**
- Configures SITL for MSP receiver and blackbox FILE logging
- Arms SITL and injects GPS altitude for specified duration
- Captures blackbox log with GPS and debug fields (navEPH, navEPV)

**Result:** Blackbox .TXT file in `inav/build_sitl/` for analysis.

---

### 3. Reproduce GPS Fluctuation (Issue #11202)

**Simulate GPS signal instability with synthetic data:**

```bash
python3 simulate_gps_fluctuation_issue_11202.py
```

**What it does:**
- Injects GPS data with fluctuating HDOP (2.0-5.0) and satellite count (15-25)
- Simulates EPH spikes similar to real-world u-blox GPS behavior
- Helps debug position estimator response to unstable GPS signals

**Issue:** https://github.com/iNavFlight/inav/issues/11202

---

### 4. Monitor GPS Status

**Check GPS configuration and real-time status:**

```bash
# Check GPS settings
python3 check_gps_config.py

# Monitor GPS data stream
python3 monitor_gps_status.py

# Test GPS reading
python3 test_gps_read.py
```

---

## Tools and Scripts by Category

### Motion Simulation & Orchestration

| Script | Purpose | Dependencies | Usage Example |
|--------|---------|--------------|---------------|
| **test_motion_simulator.sh** | **Primary orchestrator** - Coordinates CRSF RC sender + GPS injection | crsf_rc_sender.py, inject_gps_altitude.py | `./test_motion_simulator.sh climb 30` |
| inject_gps_altitude.py | Injects GPS altitude via MSP_SET_RAW_GPS | mspapi2, SITL on port 5760 | `python3 inject_gps_altitude.py --profile descent --duration 20` |
| simulate_altitude_motion.py | Standalone altitude motion generator | mspapi2 | `python3 simulate_altitude_motion.py` |
| simulate_gps_fluctuation_issue_11202.py | Reproduce Issue #11202 GPS instability | mspapi2 | `python3 simulate_gps_fluctuation_issue_11202.py` |

**test_motion_simulator.sh Deep Dive:**

This orchestrator script is the **recommended entry point** for motion simulation testing. It solves the key challenge of coordinating two independent MSP connections on different ports:

**Architecture:**
```
┌─────────────────────────────────────┐
│   test_motion_simulator.sh          │
│   (Bash orchestrator)                │
└────┬─────────────────────┬──────────┘
     │                     │
     ▼                     ▼
┌──────────────┐    ┌──────────────┐
│ CRSF RC      │    │ GPS Altitude │
│ Sender       │    │ Injection    │
│ (port 5761)  │    │ (port 5760)  │
│              │    │              │
│ - Keeps ARM  │    │ - Injects    │
│ - RX telem   │    │   GPS data   │
└──────┬───────┘    └───────┬──────┘
       │                    │
       └──────┬─────────────┘
              ▼
        ┌──────────┐
        │   SITL   │
        │  UART1   │ ◄─── MSP (5760)
        │  UART2   │ ◄─── CRSF (5761)
        └──────────┘
```

**Key Features:**
1. **Port Separation:** CRSF on 5761, MSP on 5760 - zero protocol interference
2. **3-Second Delay:** RC sender starts first, then 3s delay for connection before GPS injection
3. **Process Management:** Both processes run in background, script waits for completion
4. **Automatic Logs:** Saves to `/tmp/motion_test_telemetry.log` and `/tmp/motion_test_gps_injection.log`
5. **Result Display:** Shows last 40 lines of telemetry + 20 lines of GPS injection log

**Motion Profiles:**
- `climb` - 0m → 100m at 5 m/s
- `descent` - 100m → 0m at 2 m/s
- `hover` - Constant 50m
- `sine` - Oscillating ±30m around 50m baseline

**Timing Considerations:**
- RC sender must establish connection before GPS injection starts
- 3-second delay ensures CRSF link is ready
- Duration applies to both processes (synchronized completion)

---

### GPS Testing & Navigation Scripts

| Script | Purpose | Target |
|--------|---------|--------|
| gps_with_rc_keeper.py | GPS injection + continuous RC (keeps SITL armed) | SITL |
| gps_with_naveph_logging.py | GPS injection with EPH logging (uNAVlib) | SITL |
| gps_with_naveph_logging_mspapi2.py | GPS injection with EPH logging (mspapi2) | SITL |
| gps_recovery_test.py | Test GPS recovery after signal loss | SITL |
| gps_rth_test.py | Return-to-home testing | SITL |
| gps_rth_bug_test.py | RTH bug reproduction | SITL |
| gps_test_v6.py | General GPS testing suite (version 6) | SITL |
| gps_inject_no_arming.py | GPS injection without ARM requirement | SITL |
| gps_hover_test_30s.py | 30-second hover test with GPS | SITL |
| set_gps_provider_msp.py | Configure GPS provider to MSP | SITL/FC |

---

### Blackbox Logging Tools

**Complete Workflow Scripts:**

| Script | Purpose | Notes |
|--------|---------|-------|
| **run_gps_blackbox_test.sh** | **Complete automated workflow** | Recommended - handles all steps |
| replay_and_capture_blackbox.sh | Replay existing blackbox + capture SITL output | For replay testing |
| run_20field_test.sh | Test 20-field blackbox configuration | Diagnostic tool |

**Configuration Scripts:**

| Script | Target | Purpose |
|--------|--------|---------|
| configure_sitl_blackbox_file.py | SITL | Configure FILE logging (saves to .TXT) |
| configure_sitl_blackbox_serial.py | SITL | Configure SERIAL logging (MSP port) |
| configure_fc_blackbox.py | Physical FC | Configure FC blackbox via MSP |
| configure_blackbox_arm_controlled.py | SITL/FC | Advanced configuration with ARM control |
| configure_blackbox_via_cli.py | SITL/FC | Configuration via CLI commands |
| enable_blackbox.py | SITL/FC | Enable blackbox device |
| enable_blackbox_feature.py | SITL/FC | Enable BLACKBOX feature flag (bit 19) |

**Blackbox Data Scripts:**

| Script | Purpose |
|--------|---------|
| capture_blackbox_serial_simple.py | Capture blackbox data via MSP serial |
| download_blackbox_from_fc.py | Download blackbox from FC flash/SD |
| erase_blackbox_flash.py | Erase blackbox flash memory |
| test_blackbox_serial.py | Test serial blackbox connection |
| decode_blackbox_frames.py | Decode raw blackbox frames |
| create_single_field_blackbox.py | Create minimal single-field blackbox log |
| replay_blackbox_to_fc.py | Replay blackbox data to FC |

**Important Notes:**
- **BLACKBOX feature flag:** Must be enabled (bit 19) - `blackbox_device` setting alone is insufficient
- **FILE vs SERIAL:** FILE writes to .TXT files, SERIAL streams via MSP
- **Rate settings:** `blackbox_rate_denom` controls logging frequency (1 = every frame, 2 = every other frame)
- **Debug mode:** Set `debug_mode = DEBUG_POS_EST` to capture navEPH/navEPV

---

### SITL Configuration Scripts

| Script | Purpose | What It Configures |
|--------|---------|-------------------|
| configure_sitl_for_arming.py | MSP receiver + ARM mode | RX type = MSP, ARM on AUX1 |
| configure_sitl_gps.py | GPS settings | GPS provider, baud rate |
| configure_and_run_sitl_test_flight.py | Complete SITL setup + test | One-command setup + flight test |

---

### Flight Controller Configuration

| Script | Purpose | Target |
|--------|---------|--------|
| configure_fc_msp_rx.py | Configure MSP receiver on FC | Physical FC |
| configure_fc_blackbox.py | Configure FC blackbox settings | Physical FC |
| arm_fc_physical.py | Arm physical FC via MSP | Physical FC |
| check_rx_config.py | Verify RX configuration | SITL/FC |

---

### Monitoring & Diagnostic Tools

| Script | Purpose | Output |
|--------|---------|--------|
| monitor_gps_status.py | Real-time GPS data stream | Live GPS position, sats, HDOP |
| check_gps_config.py | Verify GPS configuration | GPS settings summary |
| test_gps_read.py | Test GPS data reading | Raw GPS data |
| query_fc_sensors.py | Query all FC sensors | Sensor status |
| benchmark_msp2_debug_rate.py | Measure MSP2_INAV_DEBUG rate | Performance metrics |
| analyze_naveph_spectrum.py | Frequency analysis of navEPH | FFT spectrum of position error |

---

### RC & Arming Utilities

| Script | Purpose |
|--------|---------|
| continuous_msp_rc_sender.py | Send continuous RC commands to keep SITL armed |
| arm_fc_physical.py | Arm physical flight controller |

---

## Common Workflows

### Workflow 1: Test GPS Navigation (RTH, Position Hold)

**Goal:** Test GPS navigation modes in SITL

```bash
# 1. Start SITL
cd ~/Documents/planes/inavflight/inav/build_sitl
./bin/SITL.elf &
sleep 10

# 2. Configure for arming
cd ~/Documents/planes/inavflight/claude/test_tools/inav/gps
python3 configure_sitl_for_arming.py

# 3. Run RTH test
python3 gps_rth_test.py
```

---

### Workflow 2: Investigate GPS Fluctuation (Issue #11202)

**Goal:** Reproduce and analyze GPS signal instability

```bash
# 1. Run fluctuation simulator
python3 simulate_gps_fluctuation_issue_11202.py

# 2. Enable blackbox logging and capture data
python3 configure_sitl_blackbox_file.py --port 5760 --rate-denom 2
python3 enable_blackbox_feature.py --port 5760

# 3. Decode and analyze
# (Use blackbox-tools to decode .TXT file)

# 4. Analyze navEPH spectrum
python3 analyze_naveph_spectrum.py <blackbox.csv>
```

---

### Workflow 3: Motion Simulation + Telemetry Validation

**Goal:** Verify CRSF telemetry reports GPS altitude correctly

```bash
# Single command - recommended
./test_motion_simulator.sh climb 30

# View live telemetry
tail -f /tmp/motion_test_telemetry.log
```

---

### Workflow 4: Blackbox Logging GPS Data

**Goal:** Capture blackbox logs with GPS/EPH data for analysis

**Automated (Recommended):**
```bash
./run_gps_blackbox_test.sh climb 60
```

**Manual (Full Control):**

See **[README_GPS_BLACKBOX_TESTING.md](README_GPS_BLACKBOX_TESTING.md)** for complete step-by-step manual workflow including:
- SITL configuration
- Arming procedures
- GPS injection
- Blackbox capture
- Troubleshooting

---

### Workflow 5: Replay Blackbox to Test Position Estimator

**Goal:** Replay sensor data from existing blackbox to test SITL response

```bash
# Replay blackbox and capture SITL output
./replay_and_capture_blackbox.sh
```

See **[REPLAY_BLACKBOX_README.md](REPLAY_BLACKBOX_README.md)** for complete replay workflow documentation.

---

## Dependencies & Prerequisites

### Python Libraries

**mspapi2** (Recommended - Modern Library)
```bash
cd ~/Documents/planes/inavflight/mspapi2
pip3 install .
```
- **Repository:** https://github.com/xznhj8129/mspapi2
- **Used by:** Most modern scripts (configure_sitl_*.py, inject_gps_altitude.py, simulate_*.py)
- **Benefits:** Clean API, codec/transport separation, multi-client server support

**uNAVlib** (Legacy Library)
```bash
# Already available in ~/Documents/planes/inavflight/uNAVlib
```
- **Used by:** Legacy scripts (gps_with_naveph_logging.py, some older test scripts)
- **Status:** Still functional, but new scripts use mspapi2

### SITL Requirements

**Built SITL Binary:**
```bash
cd ~/Documents/planes/inavflight/inav
mkdir -p build_sitl
cd build_sitl
cmake -DSITL=ON ..
make
```

**Running SITL:**
```bash
cd ~/Documents/planes/inavflight/inav/build_sitl
./bin/SITL.elf &
```

**Ports:**
- **5760** - UART1 (MSP)
- **5761** - UART2 (CRSF/MSP)

**Configuration Persistence:**
- Settings saved to `eeprom.bin` in SITL working directory
- Delete `eeprom.bin` to reset to defaults

### Physical Flight Controller

**USB Connection:**
- FC typically appears as `/dev/ttyACM0` (Linux) or `/dev/tty.usbmodem*` (macOS)
- Some scripts auto-detect, others require `--port` parameter

---

## Script Reference Table

### Quick Lookup: What Script Do I Need?

| I Want To... | Use This Script | Notes |
|--------------|-----------------|-------|
| Test motion simulation with telemetry | `test_motion_simulator.sh` | **Recommended** - Most comprehensive |
| Just inject GPS altitude | `inject_gps_altitude.py` | No telemetry monitoring |
| Reproduce GPS fluctuation bug | `simulate_gps_fluctuation_issue_11202.py` | Issue #11202 |
| Capture blackbox log | `run_gps_blackbox_test.sh` | Complete automated workflow |
| Configure SITL for arming | `configure_sitl_for_arming.py` | MSP RX + ARM on AUX1 |
| Enable blackbox logging | `configure_sitl_blackbox_file.py` | FILE mode (saves to .TXT) |
| Test RTH (Return to Home) | `gps_rth_test.py` | RTH navigation test |
| Monitor GPS status | `monitor_gps_status.py` | Real-time GPS data |
| Download blackbox from FC | `download_blackbox_from_fc.py` | Physical FC flash/SD |
| Replay blackbox data | `replay_and_capture_blackbox.sh` | Test position estimator |
| Arm physical FC | `arm_fc_physical.py` | Physical hardware |

---

## Related Documentation

This directory contains several specialized documentation files covering specific topics in detail:

### Blackbox Logging

- **[README_GPS_BLACKBOX_TESTING.md](README_GPS_BLACKBOX_TESTING.md)** (300+ lines)
  Comprehensive blackbox testing workflow: configuration, arming, GPS injection, log capture, troubleshooting

- **[BLACKBOX_SERIAL_WORKFLOW.md](BLACKBOX_SERIAL_WORKFLOW.md)**
  Serial blackbox logging specifics (SERIAL mode vs FILE mode)

- **[BLACKBOX_TESTING_PROCEDURE.md](BLACKBOX_TESTING_PROCEDURE.md)**
  Detailed testing procedures for blackbox validation

- **[BLACKBOX_STORAGE_ISSUE.md](BLACKBOX_STORAGE_ISSUE.md)**
  Investigation of blackbox storage problems

### Replay Workflows

- **[REPLAY_BLACKBOX_README.md](REPLAY_BLACKBOX_README.md)**
  Complete guide to replaying blackbox logs to SITL

- **[REPLAY_WORKFLOW_LESSONS.md](REPLAY_WORKFLOW_LESSONS.md)**
  Lessons learned from replay workflow development

- **[TRANSITION_PLAN.md](TRANSITION_PLAN.md)**
  Transition plan for replay workflow improvements

### GPS & Position Estimation

- **[HARDWARE_FC_MSP_RX_STATUS.md](HARDWARE_FC_MSP_RX_STATUS.md)**
  MSP receiver status on physical flight controllers

- **[NULL_BYTE_INVESTIGATION.md](NULL_BYTE_INVESTIGATION.md)**
  Investigation of null byte issues in GPS data

### Performance & Debugging

- **[HIGH_FREQUENCY_LOGGING_STATUS.md](HIGH_FREQUENCY_LOGGING_STATUS.md)**
  High-frequency blackbox logging performance analysis

- **[MSP2_INAV_DEBUG_FIX.md](MSP2_INAV_DEBUG_FIX.md)**
  MSP2_INAV_DEBUG command fixes and improvements

- **[MSP_QUERY_RATE_ANALYSIS.md](MSP_QUERY_RATE_ANALYSIS.md)**
  Analysis of MSP query rates and performance

### Bug Investigations

- **[MOTORS_CONDITION_BUG.md](MOTORS_CONDITION_BUG.md)**
  Investigation of blackbox MOTORS condition bug (Issue: zero-motor aircraft decoder failures)

---

## Troubleshooting

### SITL Connection Issues

**Problem:** Scripts can't connect to SITL

**Solutions:**
1. Verify SITL is running: `ps aux | grep SITL`
2. Check port: Default is 5760 for MSP
3. Try: `pkill -9 SITL.elf && ./bin/SITL.elf &`
4. Wait 10 seconds after starting SITL before running scripts

---

### Blackbox Not Logging

**Problem:** No .TXT files created

**Check:**
1. **BLACKBOX feature enabled?** `python3 enable_blackbox_feature.py`
2. **blackbox_device set?** Should be `FILE` (3) or `SERIAL` (2)
3. **SITL armed?** Blackbox only logs when armed
4. **Disk space?** Check `inav/build_sitl/` directory

**Debug:**
```bash
# Check blackbox settings via CLI
# (connect to SITL on port 5760)
get blackbox
```

---

### Motion Simulator No Telemetry

**Problem:** test_motion_simulator.sh shows no telemetry data

**Check:**
1. **RC sender started?** Check for "RC sender started (PID: ...)"
2. **3-second delay completed?** Ensure connection established
3. **View logs:** `tail -f /tmp/motion_test_telemetry.log`
4. **CRSF port:** Should be 5761 (UART2)

---

### GPS Injection Not Working

**Problem:** GPS data not updating in FC

**Check:**
1. **MSP RX configured?** Run `configure_sitl_for_arming.py`
2. **GPS provider = MSP?** Check with `check_gps_config.py`
3. **Port correct?** GPS injection uses port 5760 (UART1)
4. **SITL armed?** Some tests require ARM

---

### Physical FC Not Responding

**Problem:** Scripts can't communicate with FC

**Check:**
1. **USB connected?** `ls /dev/ttyACM*` or `ls /dev/tty.usbmodem*`
2. **Permissions?** May need `sudo` or add user to `dialout` group
3. **Port parameter?** Use `--port /dev/ttyACM0`
4. **FC booted?** Wait 5 seconds after connecting

---

### "BLACKBOX feature not enabled" Error

**Problem:** Script reports BLACKBOX feature not enabled

**Solution:**
```bash
python3 enable_blackbox_feature.py --port 5760
```

**Explanation:** The BLACKBOX feature flag (bit 19) must be set. Simply configuring `blackbox_device` is insufficient.

---

## Notes & Best Practices

### Port Usage Convention

**SITL Ports:**
- **5760** - UART1 (MSP) - Used for GPS injection, configuration
- **5761** - UART2 (CRSF/MSP) - Used for RC, telemetry

**Why Two Ports?**
- Allows concurrent MSP connections without interference
- CRSF on 5761, MSP on 5760 - zero protocol conflicts
- test_motion_simulator.sh exploits this for simultaneous RC + GPS

### EEPROM Persistence

**Configuration Saved to `eeprom.bin`:**
- Settings persist across SITL restarts
- Located in SITL working directory (usually `build_sitl/`)
- Delete `eeprom.bin` to reset to defaults

**First-Time Setup:**
```bash
rm -f eeprom.bin  # Start fresh
# Run configuration scripts
# Settings now saved to eeprom.bin
```

### MSP Libraries: mspapi2 vs uNAVlib

**Use mspapi2 for new scripts:**
- Modern, clean API
- Better structure (codec, transport, API layers)
- Supports multi-client server
- Actively maintained

**uNAVlib still used for:**
- Legacy scripts
- Backward compatibility
- Scripts not yet migrated

### Blackbox Logging Rates

**blackbox_rate_denom:**
- `1` - Log every PID loop (1000Hz if PID = 1000Hz)
- `2` - Log every other loop (500Hz)
- `10` - Log every 10th loop (100Hz)

**Recommended:**
- **GPS testing:** `2` (500Hz) - Good balance
- **High-frequency analysis:** `1` (1000Hz) - Full detail
- **Long flights:** `10` (100Hz) - Smaller files

---

## Project History

These tools were developed across multiple projects:

### Issue #11202 GPS Fluctuation Investigation (Dec 2025)
- Created `simulate_gps_fluctuation_issue_11202.py`
- Enhanced blackbox testing infrastructure
- Developed replay workflow tools
- Documented in `claude/developer/investigations/gps-fluctuation-issue-11202/`

### GPS Testing Infrastructure (Nov-Dec 2025)
- Developed motion simulation orchestration
- Created CRSF telemetry validation tools
- Built blackbox logging automation
- MSP2_INAV_DEBUG fixes and improvements

---

## Summary

**For Quick Testing:**
- Motion simulation: `./test_motion_simulator.sh climb 30`
- Blackbox logging: `./run_gps_blackbox_test.sh climb 60`

**For In-Depth Work:**
- Read specialized docs: `README_GPS_BLACKBOX_TESTING.md`, `REPLAY_BLACKBOX_README.md`
- Use individual scripts for fine-grained control

**For Debugging:**
- Check GPS: `monitor_gps_status.py`
- Verify config: `check_gps_config.py`, `check_rx_config.py`
- Analyze performance: `benchmark_msp2_debug_rate.py`

**Dependencies:**
- mspapi2 (recommended) or uNAVlib
- SITL built with `cmake -DSITL=ON`
- Python 3.6+

**Key Insight:**
The test_motion_simulator.sh orchestrator demonstrates the power of port separation - running CRSF and MSP concurrently on separate ports (5761 and 5760) enables sophisticated test scenarios with zero protocol interference.

---

**Questions or Issues?**
Refer to specialized documentation files listed above, or examine script source code - most scripts have detailed docstrings explaining usage and implementation.
