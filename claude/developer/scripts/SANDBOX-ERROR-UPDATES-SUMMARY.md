# Sandbox Error Handling Updates - Complete

## Summary

All scripts in `claude/developer/scripts/` and `.claude/skills/` that access `/dev/` devices, serial ports, or TCP connections have been updated to provide sandbox-aware error messages.

**Total Files Updated:** 29 scripts

## What Was Changed

When scripts fail to access devices or connect to ports, they now display:

```
ERROR: Cannot access/connect to [device/port]: [error details]
       If running in a sandboxed environment, device files in /dev/ may not be accessible.
       Try running with sandbox disabled or check device permissions.
```

This helps agents and users immediately recognize when sandbox restrictions are causing failures.

## Files Updated by Category

### Build Scripts (3 files)
- `claude/developer/scripts/build/fc-cli.py`
- `claude/developer/scripts/build/reboot-to-dfu.py`
- `.claude/skills/flash-firmware-dfu/reboot-to-dfu.sh`

### MSP Scripts

#### Serial Access (5 files)
- `claude/developer/scripts/testing/inav/msp/benchmark/msp_benchmark_serial.py`
- `claude/developer/scripts/testing/inav/msp/mock/msp_mock_responder.py`
- `claude/developer/scripts/testing/inav/usb_throughput_test.py`
- `claude/developer/scripts/testing/inav/gps/historical/gps_test_v1.py` (hybrid serial/TCP)
- `claude/developer/scripts/testing/inav/gps/historical/gps_test_v2.py` (hybrid serial/TCP)

#### TCP Access (1 file)
- `claude/developer/scripts/testing/inav/test_msp_commands.py`

#### MSPApi Library (19 files - all updated)

**Batch-updated via script:**
- `claude/developer/scripts/testing/inav/blackbox/config/capture_blackbox_serial_simple.py`
- `claude/developer/scripts/testing/inav/blackbox/config/enable_blackbox.py`
- `claude/developer/scripts/testing/inav/blackbox/config/enable_blackbox_feature.py`
- `claude/developer/scripts/testing/inav/blackbox/config/erase_blackbox_flash.py`
- `claude/developer/scripts/testing/inav/blackbox/config/test_blackbox_serial.py`
- `claude/developer/scripts/testing/inav/gps/injection/set_gps_provider_msp.py`
- `claude/developer/scripts/testing/inav/gps/injection/simulate_gps_fluctuation_issue_11202.py`
- `claude/developer/scripts/testing/inav/gps/workflows/configure_and_run_sitl_test_flight.py`
- `claude/developer/scripts/testing/inav/sitl/configure_sitl_for_arming.py`
- `claude/developer/scripts/testing/inav/sitl/continuous_msp_rc_sender.py`

**Manually updated (simple pattern):**
- `claude/developer/scripts/testing/inav/sitl/arm_fc_physical.py`
- `claude/developer/scripts/testing/inav/blackbox/config/download_blackbox_from_fc.py`
- `claude/developer/scripts/testing/inav/blackbox/config/configure_fc_blackbox.py`
- `claude/developer/scripts/testing/inav/blackbox/analysis/replay_blackbox_to_fc.py`

**Manually updated (nested try-except pattern):**
- `claude/developer/scripts/testing/inav/blackbox/config/configure_blackbox_arm_controlled.py`
- `claude/developer/scripts/testing/inav/blackbox/config/configure_sitl_blackbox_file.py`
- `claude/developer/scripts/testing/inav/blackbox/config/configure_sitl_blackbox_serial.py`
- `claude/developer/scripts/testing/inav/gps/testing/gps_with_naveph_logging_mspapi2.py`
- `claude/developer/scripts/testing/inav/sitl/benchmark_msp2_debug_rate.py`

### Skills (1 file)
- `.claude/skills/replay-blackbox/skill.sh` (calls replay_blackbox_to_fc.py, which was updated)

## Implementation Patterns

### Pattern 1: Direct Serial Access
```python
try:
    ser = serial.Serial(port, baudrate)
except (serial.SerialException, FileNotFoundError, PermissionError) as e:
    print(f"ERROR: Cannot access serial port {port}: {e}")
    print(f"       If running in a sandboxed environment, device files in /dev/ may not be accessible.")
    print(f"       Try running with sandbox disabled or check device permissions.")
    raise
```

### Pattern 2: TCP Socket
```python
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
except (ConnectionRefusedError, OSError, TimeoutError) as e:
    print(f"ERROR: Cannot connect to {host}:{port}: {e}")
    print(f"       If running in a sandboxed environment, network access may be restricted.")
    raise
```

### Pattern 3: MSPApi
```python
api = MSPApi(port=port)
try:
    api.open()
except Exception as e:
    print(f"ERROR: Cannot connect to {port}: {e}")
    print(f"       If running in a sandboxed environment, device files in /dev/ may not be accessible.")
    raise
```

### Pattern 4: Shell Scripts
```bash
if [ ! -e "$SERIAL_PORT" ]; then
    echo "ERROR: Serial port $SERIAL_PORT not found"
    echo "       If running in a sandboxed environment, device files may not be accessible."
    exit 1
fi
```

## Tools Created

### Batch Update Script
**Location:** `claude/developer/scripts/analysis/add_mspapi_sandbox_errors.py`

**Features:**
- Dry-run mode by default (safe to test)
- Shows diffs before applying changes
- Creates `.bak` backup files
- Skips files already updated
- Detailed progress reporting

**Usage:**
```bash
# See what will change
python3 claude/developer/scripts/analysis/add_mspapi_sandbox_errors.py

# Apply changes
python3 claude/developer/scripts/analysis/add_mspapi_sandbox_errors.py --apply
```

## Documentation

**Main documentation:** `claude/developer/scripts/SANDBOX-ERROR-HANDLING.md`

Contains:
- All error handling patterns with code examples
- Complete list of updated files
- Instructions for future updates
- Testing guidelines

## Testing

All updated scripts will now provide helpful error messages when:
1. Trying to access `/dev/ttyACM0` or other `/dev/` devices in sandbox
2. Trying to connect to TCP ports when network is restricted
3. File permissions prevent device access

Example test:
```bash
# This will now show a sandbox-aware error message
python3 claude/developer/scripts/build/fc-cli.py tasks /dev/ttyNONEXISTENT
```

## Benefits

1. **Better UX for agents:** Agents will immediately understand that sandbox restrictions may be the problem
2. **Faster debugging:** Users won't waste time troubleshooting code when it's a sandbox issue
3. **Clear guidance:** Error messages suggest specific remediation (disable sandbox or check permissions)
4. **Consistent pattern:** All scripts use the same error message format

## Date Completed

2026-01-18
