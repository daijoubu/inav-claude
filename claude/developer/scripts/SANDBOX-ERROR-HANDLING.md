# Sandbox-Aware Error Handling Patterns

This document describes the error handling patterns added to scripts to provide helpful messages when running in sandboxed environments.

## Summary of Changes

Scripts that interact with `/dev/` devices, serial ports, or TCP connections have been updated to detect failures and provide helpful error messages indicating that sandbox restrictions may be the cause.

## Pattern 1: Serial Port Access (pyserial)

For scripts using `serial.Serial()` directly:

```python
try:
    ser = serial.Serial(port_name, baudrate, timeout=1.0)
except (serial.SerialException, FileNotFoundError, PermissionError) as e:
    print(f"ERROR: Cannot access serial port {port_name}: {e}")
    print(f"       If running in a sandboxed environment, device files in /dev/ may not be accessible.")
    print(f"       Try running with sandbox disabled or check device permissions.")
    raise  # or return, depending on function
```

**Updated files:**
- `claude/developer/scripts/build/fc-cli.py` (line 93-96)
- `claude/developer/scripts/build/reboot-to-dfu.py` (line 81-85)
- `claude/developer/scripts/testing/inav/msp/benchmark/msp_benchmark_serial.py` (line 60-65)
- `claude/developer/scripts/testing/inav/msp/mock/msp_mock_responder.py` (line 85-90)
- `claude/developer/scripts/testing/inav/usb_throughput_test.py` (line 13-18)

## Pattern 2: TCP Socket Connections

For scripts using `socket.connect()`:

```python
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.settimeout(1.0)
except (ConnectionRefusedError, OSError, TimeoutError) as e:
    print(f"ERROR: Cannot connect to {host}:{port}: {e}")
    print(f"       If running in a sandboxed environment, network access may be restricted.")
    print(f"       Try running with sandbox disabled or check if SITL is running.")
    raise
```

**Updated files:**
- `claude/developer/scripts/testing/test_msp_commands.py` (line 30-35)
- `claude/developer/scripts/testing/inav/gps/historical/gps_test_v1.py` (line 77-83)
- `claude/developer/scripts/testing/inav/gps/historical/gps_test_v2.py` (line 77-83)

## Pattern 3: Combined TCP/Serial (MSPConnection class)

For the `MSPConnection` class that handles both:

```python
def connect(self):
    if ':' in self.target:
        # TCP connection
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((host, int(port)))
            self.conn.settimeout(1.0)
        except (ConnectionRefusedError, OSError, TimeoutError) as e:
            print(f"ERROR: Cannot connect to {self.target}: {e}")
            print(f"       If running in a sandboxed environment, network access may be restricted.")
            raise
    else:
        # Serial connection
        try:
            self.conn = serial.Serial(self.target, 115200, timeout=1)
        except (serial.SerialException, FileNotFoundError, PermissionError) as e:
            print(f"ERROR: Cannot access serial port {self.target}: {e}")
            print(f"       If running in a sandboxed environment, device files in /dev/ may not be accessible.")
            raise
```

**Updated files:**
- `claude/developer/scripts/testing/inav/gps/historical/gps_test_v1.py`
- `claude/developer/scripts/testing/inav/gps/historical/gps_test_v2.py`

## Pattern 4: mspapi2.MSPApi

For scripts using the `MSPApi` library:

```python
api = MSPApi(port=port, baudrate=115200)
try:
    api.open()
    time.sleep(0.5)
except Exception as e:
    print(f"ERROR: Cannot connect to {port}: {e}")
    print(f"       If running in a sandboxed environment, device files in /dev/ may not be accessible.")
    print(f"       Try running with sandbox disabled or check device permissions.")
    raise  # or return False
```

**Updated files:**
- `claude/developer/scripts/testing/inav/sitl/arm_fc_physical.py` (line 27-33)
- `claude/developer/scripts/testing/inav/blackbox/config/download_blackbox_from_fc.py` (line 23-29)
- `claude/developer/scripts/testing/inav/blackbox/config/configure_fc_blackbox.py` (line 103-109)
- `claude/developer/scripts/testing/inav/blackbox/analysis/replay_blackbox_to_fc.py` (line 434-442)

## Pattern 5: Shell Scripts (Bash)

For shell scripts checking device files:

```bash
if [ ! -e "$SERIAL_PORT" ]; then
    echo "ERROR: Serial port $SERIAL_PORT not found"
    echo "       If running in a sandboxed environment, device files in /dev/ may not be accessible."
    echo "       Try running with sandbox disabled or check device permissions."
    exit 1
fi
```

And for operations that might fail in sandbox:

```bash
if ! stty -F "$SERIAL_PORT" raw -echo 115200 2>/dev/null; then
    echo "ERROR: Cannot configure serial port $SERIAL_PORT"
    echo "       If running in a sandboxed environment, device access may be restricted."
    echo "       Try running with sandbox disabled or check device permissions."
    exit 1
fi
```

**Updated files:**
- `.claude/skills/flash-firmware-dfu/reboot-to-dfu.sh` (lines 12-16, 56-62)

## Update Status

### ✅ Completed Updates - ALL FILES DONE

All Python scripts that access `/dev/` devices, serial ports, or TCP connections have been updated with sandbox-aware error handling.

**MSPApi scripts:** 19 files - ALL UPDATED ✅
- 10 files updated via batch script
- 4 files manually updated before batch script
- 5 files manually updated with nested try-except blocks (had outer generic handlers)

**Serial port scripts:** 5 files - ALL UPDATED ✅

**TCP socket scripts:** 3 files - ALL UPDATED ✅

**Shell scripts:** 2 files - ALL UPDATED ✅

All scripts now provide clear, helpful error messages when device or network access fails in sandboxed environments.

### Batch Update Tool

The automated update tool is located at:
`claude/developer/scripts/analysis/add_mspapi_sandbox_errors.py`

Features:
- Dry-run mode by default (safe)
- Shows diffs before applying
- Creates `.bak` backup files
- Skips files that already have error handling
- Detailed reporting

Usage:
```bash
# Dry run (shows what will change)
python3 claude/developer/scripts/analysis/add_mspapi_sandbox_errors.py

# Apply changes
python3 claude/developer/scripts/analysis/add_mspapi_sandbox_errors.py --apply

# Process specific file
python3 claude/developer/scripts/analysis/add_mspapi_sandbox_errors.py --file path/to/script.py --apply
```

## Application Instructions

To apply these patterns to remaining files:

1. **Identify the connection type** (serial, TCP, MSPApi, shell)
2. **Find the connection/open call** in the code
3. **Wrap with try-except** using the appropriate pattern above
4. **Test the error message** by running in sandbox or with missing device

## Testing

To verify the error messages work:

```bash
# Test serial port error
python3 script.py /dev/ttyNONEXISTENT

# Test TCP connection error
python3 script.py localhost:9999  # assuming nothing listens on 9999

# Test in sandbox (if sandbox blocks the access)
# Error message should mention sandbox
```

Expected output should include:
- Clear "ERROR:" prefix
- Specific failure reason
- Sandbox-aware hint
- Suggestion to disable sandbox or check permissions
