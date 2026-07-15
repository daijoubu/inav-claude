# INAV Test Tools

Consolidated test tools for INAV firmware and configurator development.

**Last updated:** 2025-12-07 (Consolidation from developer/test_tools/)

---

## Directory Structure

```
claude/test_tools/inav/
├── crsf/              # CRSF protocol testing and debugging
├── msp/               # MSP protocol tools
│   ├── benchmark/     # Performance benchmarking
│   ├── mock/          # Mock responders for testing
│   └── debug/         # Debugging utilities
├── gps/               # GPS and navigation testing
│   ├── historical/    # Older test versions (archived)
│   └── test_results/  # Test output logs
├── sitl/              # SITL-specific test tools
├── docs/              # Documentation
└── usb_throughput_test.py  # USB performance testing
```

---

## CRSF Tools (crsf/)

### Main Test Infrastructure

**test_crsf_telemetry.sh** - Comprehensive CRSF telemetry testing workflow
- Automated 7-step test process
- Supports multiple test modes (baseline, pr11025, pr11100)
- Verifies SITL build, enables telemetry, captures frames
- **Usage:** `./test_crsf_telemetry.sh [build_dir] [test_mode]`

**quick_test_crsf.sh** - Quick build-test cycle helper
- Options: `-r` (rebuild), `-c` (clean), `-s` (skip test)
- Streamlines development workflow
- **Usage:** `./quick_test_crsf.sh [-r|-c|-s]`

**configure_sitl_crsf.py** - SITL CRSF configuration via MSP
- Configures CRSF on UART2 for SITL testing
- Sets up RX protocol and serial ports

### Debugging Utilities

**crsf_rc_sender.py** - RC channel sender for SITL
- Sends CRSF RC frames to keep FC armed
- Supports configurable update rate
- **Usage:** `python3 crsf_rc_sender.py [uart_port] --rate [hz]`

**crsf_stream_parser.py** - Telemetry frame parser
- Captures and decodes CRSF telemetry frames
- Displays frame types and statistics
- **Usage:** `python3 crsf_stream_parser.py [uart_port]`

**analyze_frame_0x09.py** - Altitude/vario frame analyzer
- Analyzes CRSF frame 0x09 (altitude, vario)
- Validates data ranges and correlations
- **Usage:** `python3 analyze_frame_0x09.py [capture_file]`

**test_telemetry_simple.py** - Simple telemetry test
- Lightweight telemetry capture tool
- **Usage:** `python3 test_telemetry_simple.py [uart_port]`

---

## MSP Tools (msp/)

### Timer Output Mode / Buzzer Output Mapping (msp/)

Tools for verifying runtime timer-output-mode assignment (PR #11675,
"BUZZER as a runtime-assignable timer output mode") and related
output-mapping hardware behavior, entirely via MSP -- no CLI required.

- **msp_helpers.py** - Shared helpers used by the scripts below:
  `open_and_check()` (connect + sanity-check MSP_API_VERSION, with clear
  diagnostics on failure/CLI-mode), `wait_for_port()` (poll for the serial
  device node to reappear after a reboot, requiring it to stay stable for a
  bit to dodge a double-enumeration race seen on some H7 boards), and
  `save_and_reboot()` (MSP_EEPROM_WRITE + MSP_REBOOT + reconnect). Import
  this in any new script that needs to persist a config change and verify
  it survived a reboot.

- **query_output_state.py** - Read-only dump of `MSP2_INAV_TIMER_OUTPUT_MODE`
  (0x200E, all timer override slots) and `MSP2_INAV_OUTPUT_MAPPING_EXT2`
  (0x210D, per-pad usageFlags/TIM_USE_BEEPER). Use this first, before and
  after any change, to see the current state without side effects.
  **Usage:** `python3 query_output_state.py` (hardcoded to /dev/ttyACM0;
  edit the `port=` kwarg for a different device).

- **apply_timer_override.py** - Set a single timer's runtime output mode via
  `MSP2_INAV_SET_TIMER_OUTPUT_MODE` (0x200F), then EEPROM_WRITE + REBOOT +
  reconnect + read back to confirm it persisted. Works for any
  `outputMode_e` value (0=AUTO 1=MOTORS 2=SERVOS 3=LED 4=PINIO 5=BEEPER).
  **Usage:** `python3 apply_timer_override.py <port> <timer_index> <output_mode>`

- **setup_msp_rx_beeper_switch.py** / **beep_via_msp_rc.py** /
  **revert_msp_rx_beeper_switch.py** - A 3-step toolkit to trigger
  BOXBEEPERON (or any other BOX mode -- see docstring) purely via MSP, with
  no physical receiver required: temporarily switches `receiverType` to
  `RX_TYPE_MSP` and maps a spare AUX channel to the target BOX mode via
  `MSP_SET_MODE_RANGE`, then drives it with a continuous `MSP_SET_RAW_RC`
  stream. **Only use on a bench FC with no real receiver connected** --
  switching `receiverType` away from a configured serial receiver (e.g.
  CRSF) would drop a real control link. Backs up the original
  `MSP_RX_CONFIG` / mode-range slot to `.hex` files in the working directory
  (or a `backup_dir` you pass in) before changing anything, so the revert
  script can restore byte-for-byte. This is the safe alternative to using
  CLI's `play_sound` or MSP_ACC_CALIBRATION (the latter can silently wipe
  accelerometer calibration -- see the warning in the deprecated
  `trigger_beep_test.py`, kept only as a historical cautionary example, not
  copied here).
  **Usage:**
  ```
  python3 setup_msp_rx_beeper_switch.py <port> [backup_dir]
  python3 beep_via_msp_rc.py <port> [duration_seconds]
  # ... revert when done:
  python3 revert_msp_rx_beeper_switch.py <port> [backup_dir] [mode_range_slot]
  ```

### Benchmark (msp/benchmark/)

Performance testing tools for MSP protocol:

- **msp_benchmark.py** - Basic MSP benchmark
- **msp_benchmark_improved.py** - Enhanced benchmark with stats
- **msp_benchmark_ident_only.py** - MSP_IDENT only benchmark
- **msp_benchmark_serial.py** - Serial-specific benchmarking
- **test_mock_benchmark.sh** - Mock responder benchmark test
- **run_comparison_test.sh** - Comparison test runner

### Mock (msp/mock/)

Mock responders for testing MSP clients:

- **msp_mock_responder.py** - TCP mock responder
- **msp_mock_responder_tcp.py** - TCP-specific mock

### Debug (msp/debug/)

MSP debugging utilities:

- **msp_debug.py** - General MSP protocol debugging
- **msp_rc_debug.py** - MSP RC command debugging

---

## GPS Tools (gps/)

### Current Tools

**gps_test_v6.py** - Latest GPS testing tool
- Most recent version of GPS test suite
- Comprehensive GPS functionality testing

**gps_rth_test.py** - Return-to-home testing
- Tests RTH behavior and GPS recovery
- Configurable GPS loss scenarios

**gps_rth_bug_test.py** - RTH bug reproduction
- Reproduces specific RTH bugs for verification
- Documents bug behavior

**gps_recovery_test.py** - GPS recovery testing
- Tests GPS signal recovery scenarios
- Validates failsafe behavior

**inject_gps_altitude.py** - GPS altitude injection
- Injects GPS altitude data into SITL
- For altitude-specific testing

**simulate_altitude_motion.py** - Altitude motion simulator
- Simulates realistic altitude changes
- Tests altitude hold and climbing

**test_motion_simulator.sh** - Motion simulation test wrapper
- Automated motion simulation tests

### Historical (gps/historical/)

Archived older versions for reference:
- gps_test_v1.py through gps_test_v5.py

### Test Results (gps/test_results/)

Archived test output logs from GPS bug testing:
- buggy_*.log - Test results showing bug behavior
- fixed_test.log - Test results after fixes

---

## SITL Tools (sitl/)

**sitl_arm_test.py** - SITL arming test
- Tests FC arming via MSP
- Verifies arming conditions

**unavlib_bug_test.py** - uNAVlib bug testing
- Tests for uNAVlib library issues

---

## Documentation (docs/)

**README.md** - This file

**BUILDING_SITL.md** - SITL build instructions
- How to build SITL with CRSF support
- Troubleshooting build issues

**TCP_CONNECTION_LIMITATION.md** - TCP limitations in SITL
- Documents TCP connection constraints
- Workarounds for testing

**UNAVLIB.md** - uNAVlib documentation
- Python MSP library documentation
- API reference

**2025-11-25-test-instructions.md** - Historical test instructions

---

## Other Tools

**usb_throughput_test.py** - USB performance testing
- Tests USB serial throughput
- Benchmarks communication speed

---

## Usage Examples

### CRSF Telemetry Testing

```bash
# Full test with PR #11025 changes
cd ~/Documents/planes/inavflight/claude/test_tools/inav/crsf
./test_crsf_telemetry.sh build_sitl_pr11025 pr11025

# Quick rebuild and test
./quick_test_crsf.sh -r

# Manual testing with tools
python3 crsf_rc_sender.py 2 --rate 50 &  # Keep FC armed
python3 crsf_stream_parser.py 2           # Watch telemetry
```

### MSP Benchmarking

```bash
cd ~/Documents/planes/inavflight/claude/test_tools/inav/msp/benchmark
python3 msp_benchmark_improved.py
./run_comparison_test.sh
```

### GPS Testing

```bash
cd ~/Documents/planes/inavflight/claude/test_tools/inav/gps
python3 gps_test_v6.py
python3 gps_rth_test.py --loss-duration 5.0
```

---

## Migration Notes

**2025-12-07:** Consolidated test tools from two locations:
- Moved from `claude/developer/test_tools/` → `claude/test_tools/inav/`
- Organized into functional subdirectories
- Fixed cross-directory dependencies
- Archived historical versions

**Benefits:**
- Single source of truth for all INAV test tools
- Clear organization by functional area
- No cross-directory dependencies
- Role-agnostic (accessible to all roles)
- Easier discovery and maintenance

---

## Contributing

When adding new test tools:

1. **Choose the right directory:**
   - CRSF-related → `crsf/`
   - MSP-related → `msp/benchmark/`, `msp/mock/`, or `msp/debug/`
   - GPS/navigation → `gps/`
   - SITL-specific → `sitl/`
   - Documentation → `docs/`

2. **Make tools executable:**
   ```bash
   chmod +x your_tool.py
   chmod +x your_script.sh
   ```

3. **Update this README** with tool description and usage

4. **Use relative paths** when referencing other tools in the same tree

---

## Related Documentation

- Developer Guide: `claude/developer/README.md`
- CRSF Testing Status: `claude/developer/2025-12-07-crsf-telemetry-testing-status.md`
- Test Infrastructure: `claude/test_tools/inav/docs/`

---

**Maintained by:** INAV Development Team
**Location:** `claude/test_tools/inav/`
