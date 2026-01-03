# GPS Testing Workflows

**Complete automated workflows** integrating GPS injection, RC control, telemetry, and blackbox logging.

## Quick Start

```bash
# Motion simulation + CRSF telemetry (RECOMMENDED)
./test_motion_simulator.sh climb 30

# GPS + blackbox logging
./run_gps_blackbox_test.sh climb 60

# Replay blackbox + capture SITL output
./replay_and_capture_blackbox.sh
```

## Primary Workflows

### test_motion_simulator.sh ⭐ **RECOMMENDED**
**Motion simulation orchestrator** - GPS injection + CRSF telemetry validation

```bash
./test_motion_simulator.sh [PROFILE] [DURATION]

# Examples:
./test_motion_simulator.sh climb 20   # 0m→100m at 5m/s
./test_motion_simulator.sh descent 30 # 100m→0m at 2m/s
./test_motion_simulator.sh hover 15   # Constant 50m
./test_motion_simulator.sh sine 30    # Oscillating ±30m
```

**What it does:**
1. Starts CRSF RC sender (port 5761) - Keeps SITL armed + receives telemetry
2. Waits 3 seconds for connection establishment
3. Starts GPS altitude injection (port 5760) - Injects motion profile
4. Both processes run concurrently for specified duration
5. Displays telemetry results showing GPS altitude validation

**Architecture:** Dual processes - crsf_rc_sender.py (port 5761: RC+telemetry) + inject_gps_altitude.py (port 5760: GPS injection). Port separation = zero protocol interference.

**Logs:**
- `/tmp/motion_test_telemetry.log` - CRSF telemetry with GPS altitude
- `/tmp/motion_test_gps_injection.log` - GPS injection status

**Use case:** Primary test for validating CRSF telemetry reports GPS altitude correctly

---

### run_gps_blackbox_test.sh
**Complete GPS + blackbox workflow** - Configuration + injection + logging

```bash
./run_gps_blackbox_test.sh [PROFILE] [DURATION]

# Example:
./run_gps_blackbox_test.sh climb 60
```

**What it does:**
1. Checks if SITL is running (starts if needed)
2. Configures MSP receiver + ARM mode
3. Enables blackbox FILE logging with DEBUG_POS_EST
4. Arms SITL
5. Injects GPS altitude for specified duration
6. Captures blackbox log

**Output:** Blackbox .TXT file in `inav/build_sitl/` with GPS and navEPH data

**Use case:** Capturing blackbox logs for EPH analysis and GPS debugging

---

### configure_and_run_sitl_test_flight.py
**One-command SITL setup + test flight**

```bash
python3 configure_and_run_sitl_test_flight.py
```

Complete SITL configuration and automated test flight sequence.

---

## Blackbox Replay Workflows

**Moved to:** `../../blackbox/replay/`

- **replay_and_capture_blackbox.sh** - Replay blackbox + capture SITL output
- **run_20field_test.sh** - 20-field blackbox diagnostic test

**See:** `../../blackbox/docs/REPLAY_BLACKBOX_README.md` for replay workflow documentation

## Choosing the Right Workflow

| I Want To... | Use This |
|--------------|----------|
| **Test CRSF telemetry** | `test_motion_simulator.sh` ⭐ |
| **Capture blackbox logs** | `run_gps_blackbox_test.sh` |
| **Test position estimator** | `../../blackbox/replay/replay_and_capture_blackbox.sh` |
| **Quick SITL test** | `configure_and_run_sitl_test_flight.py` |

## Dependencies

- **SITL:** Built and running
- **mspapi2:** `pip3 install ~/Documents/planes/inavflight/mspapi2`
- **crsf_rc_sender.py:** For test_motion_simulator.sh (in parent crsf/ directory)

## Notes

**Port Usage:**
- **5760** - UART1 (MSP) - GPS injection, configuration
- **5761** - UART2 (CRSF) - RC commands, telemetry

**SITL Must Be Running:**
```bash
cd ~/Documents/planes/inavflight/inav/build_sitl
./bin/SITL.elf &
```

**First-Time Setup:**
- Delete `eeprom.bin` for fresh configuration
- Workflows handle configuration automatically

## See Also

- `../injection/` - GPS injection scripts used by workflows
- `../../sitl/` - SITL configuration scripts
- `../../blackbox/` - Blackbox configuration and replay workflows
- `../docs/README_GPS_BLACKBOX_TESTING.md` - Complete GPS+blackbox workflow
- `../../blackbox/docs/REPLAY_BLACKBOX_README.md` - Replay workflow documentation
