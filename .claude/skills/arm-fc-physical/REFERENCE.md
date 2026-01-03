# Arm Physical FC - Detailed Reference

Complete reference documentation for arming physical flight controllers and downloading blackbox logs.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Complete Workflow](#complete-workflow)
- [Configuration Scripts](#configuration-scripts)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)
- [Safety Notes](#safety-notes)

---

## Prerequisites

### Hardware Setup
1. Flight controller with USB connection
2. USB cable connected to development machine
3. FC appears as `/dev/ttyACM0` (or similar)

### Software Requirements
```bash
# Python dependencies
pip3 install pyserial
pip3 install git+https://github.com/xznhj8129/mspapi2

# Verify FC connection
ls -l /dev/ttyACM*
```

### FC Configuration Requirements

**CRITICAL**: The FC must be configured before arming:

1. **Accelerometer calibration** - FC must be level and calibrated
2. **MSP receiver** - `rx_spi_protocol = MSP`
3. **ARM mode on AUX1** - Configured to arm when AUX1 > 1700
4. **Blackbox logging** - `blackbox_device = SPIFLASH`, `blackbox_rate_denom = 100`

---

## Complete Workflow

### Step 1: Check FC Status

```bash
# Check if FC can be armed
~/.claude/skills/flash-firmware-dfu/fc-cli.py status /dev/ttyACM0
```

Look for "Arming disabled flags" - should ideally show only "CLI" when connected.

### Step 2: Calibrate Accelerometer (If Needed)

If status shows "ACC" flag:
1. Place FC on level surface
2. Open INAV Configurator
3. Go to Setup tab
4. Click "Calibrate Accelerometer"
5. Wait for completion

### Step 3: Configure FC for MSP Arming

Run the configuration script:
```bash
cd claude/developer/scripts/testing/inav/gps
python3 configure_fc_for_msp_arming.py /dev/ttyACM0
```

Or configure manually via CLI:
```bash
# Set MSP receiver
set rx_spi_protocol = MSP
set min_check = 1100
set max_check = 1900
set rx_min_usec = 885
set rx_max_usec = 2115

# Configure ARM mode on AUX1 (range 1700-2100)
# This requires MSP commands - use script above
```

### Step 4: Configure Blackbox

```bash
cd claude/developer/scripts/testing/inav/gps
python3 configure_fc_blackbox.py /dev/ttyACM0
```

Or via CLI:
```bash
set blackbox_device = SPIFLASH
set blackbox_rate_denom = 100
save
```

### Step 5: Arm FC and Generate Log

**IMPORTANT**: Make sure propellers are removed or FC is in a safe location!

```bash
cd claude/developer/scripts/testing/inav/gps

# Arm for 30 seconds at 50Hz (default)
python3 continuous_msp_rc_sender.py /dev/ttyACM0

# Arm for custom duration/rate
python3 continuous_msp_rc_sender.py /dev/ttyACM0 --duration 60 --rate 100
```

The script will:
1. Connect to FC
2. Wait 5 seconds (sensor stabilization, disarmed)
3. Arm the FC (throttle low)
4. Fly armed at mid-throttle for specified duration
5. Disarm and exit

### Step 6: Download Blackbox Log

```bash
cd claude/developer/scripts/testing/inav/gps

# Download to default filename
python3 download_blackbox_from_fc.py /dev/ttyACM0

# Download to specific file
python3 download_blackbox_from_fc.py /dev/ttyACM0 test_results/my_log.TXT
```

Download takes ~2-3 minutes for a typical log.

### Step 7: Decode Blackbox Log

```bash
cd claude/developer/scripts/testing/inav/gps
blackbox_decode test_results/my_log.TXT
```

This creates a CSV file with decoded data.

---

## Configuration Scripts

### configure_fc_for_msp_arming.py

Configures MSP receiver and ARM mode.

**What it does**:
1. Sets receiver type to MSP (RX_TYPE_MSP = 2)
2. Configures ARM mode on AUX1 (range 1700-2100)
3. Sets valid RX channel limits
4. Saves and reboots

### configure_fc_blackbox.py

Configures blackbox logging.

**What it does**:
1. Sets `blackbox_device = SPIFLASH`
2. Sets `blackbox_rate_denom = 100` (logs every 100th loop)
3. Saves configuration

---

## Troubleshooting

### FC Won't Arm

**Check arming flags**:
```bash
~/.claude/skills/flash-firmware-dfu/fc-cli.py status /dev/ttyACM0
```

Common arming blockers:

| Flag | Meaning | Solution |
|------|---------|----------|
| ACC | Accelerometer not calibrated | Calibrate via Configurator |
| CAL | Sensors calibrating | Wait 5+ seconds after boot |
| RX | No RC link | Script sends RC - check connection |
| CLI | CLI mode active | Script connects/disconnects properly |
| SETTINGFAIL | Invalid settings | Check min_check, rx_min_usec values |
| ANGLE | FC not level | Level FC or disable small_angle check |

**Fix invalid RX settings**:
```bash
set min_check = 1100
set max_check = 1900
set rx_min_usec = 885
set rx_max_usec = 2115
save
```

**Check ARM mode configuration**:
```bash
# View mode ranges
~/.claude/skills/flash-firmware-dfu/fc-cli.py "aux" /dev/ttyACM0
```

Should show ARM on AUX1 with range 1700-2100.

### No Blackbox Data Logged (0 bytes)

**Common causes**:

1. **HITL mode enabled** - HITL bypasses blackbox!
   - Solution: Use `continuous_msp_rc_sender.py` (does NOT use HITL)
   - Verify: Check script doesn't call MSP_SIMULATOR

2. **FC not actually armed**
   - Check arming flags with `status` command
   - Calibrate accelerometer if needed

3. **Blackbox not configured**
   ```bash
   set blackbox_device = SPIFLASH
   set blackbox_rate_denom = 100
   save
   ```

4. **Flash full**
   - Check with download script (shows "Used size")
   - Erase via Configurator if needed

### Download Script Shows Wrong Size

If download shows 16.7 MB (entire chip) instead of actual log size:
1. Reflash firmware (resets flash state)
2. Reconfigure blackbox
3. Generate fresh log

### Serial Port Permission Denied

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in for changes to take effect
```

### Port Busy / Already in Use

```bash
# Kill any processes using the port
sudo lsof /dev/ttyACM0
sudo kill <PID>

# Or force disconnect
pkill -9 -f "download_blackbox"
```

---

## Technical Details

### MSP Commands Used

| Code | Name | Purpose |
|------|------|---------|
| 70 | MSP_DATAFLASH_SUMMARY | Query flash status [flags:1, sectors:4, totalSize:4, usedSize:4] |
| 71 | MSP_DATAFLASH_READ | Read chunks [address:4, length:2] → [address:4, data:...] |
| 72 | MSP_DATAFLASH_ERASE | Erase entire flash chip |
| 200 | MSP_SET_RAW_RC | Send RC channels [ch1:2, ch2:2, ..., ch18:2] |
| 250 | MSP_EEPROM_WRITE | Save config to EEPROM |
| 68 | MSP_REBOOT | Reboot FC |

### RC Channel Mapping

INAV uses AETR mapping by default:
- Channel 1: Roll (1500 = center)
- Channel 2: Pitch (1500 = center)
- Channel 3: **Throttle** (1000 = low, 1600 = mid, 2000 = high)
- Channel 4: Yaw (1500 = center)
- Channel 5: AUX1 - ARM (1000 = disarm, 1800 = arm)
- Channels 6-18: Additional AUX channels (1500 = center)

### Why Not Use HITL Mode?

HITL (Hardware-In-The-Loop) mode:
- ✓ Bypasses sensor calibration requirements
- ✓ Allows quick arming for testing
- ✗ **Prevents blackbox logging** (HITL mode bypasses blackbox subsystem)
- ✗ Not realistic for flight testing

For blackbox testing, use real sensor calibration without HITL.

### Blackbox Rate Settings

`blackbox_rate_denom` controls logging frequency:
- `1` = Log every loop iteration (highest resolution, large files)
- `10` = Log every 10th iteration
- `100` = Log every 100th iteration (good for 30s+ flights)

For a 5-second nav cycle, use `rate_denom = 100` to ensure full cycle captured.

### Performance Notes

**Arming Script**:
- Target rate: 50 Hz (matches CRSF standard)
- Actual rate: ~70 Hz (depends on system load)
- CPU usage: Minimal (<5%)

**Download Script**:
- Speed: ~2.5 KB/s average
- 50 KB log: ~20 seconds
- 500 KB log: ~3-4 minutes
- 5 MB log: ~30+ minutes

**Chunk Size**:
- Current: 128 bytes (reliable)
- Larger chunks may timeout on some FCs
- Smaller chunks reduce speed

---

## Safety Notes

- **ALWAYS remove propellers** before arming on the bench
- Secure FC to prevent movement when armed
- Have a way to quickly disconnect power if needed
- Don't arm FC when connected via Configurator (conflicts)
- Be aware that ESCs may beep/initialize when armed

---

## Related Skills

- **flash-firmware-dfu** - Flash firmware to FC before testing
- **build-inav-target** - Build custom firmware for testing
- **sitl-arm** - Arm SITL (software simulator) via MSP
- **msp-protocol** - MSP protocol reference

---

## Example: Automated Test Loop

```bash
#!/bin/bash
# Run multiple test iterations

for i in {1..5}; do
    echo "=== Test $i of 5 ==="

    # Generate log
    python3 continuous_msp_rc_sender.py /dev/ttyACM0 --duration 30

    # Download
    python3 download_blackbox_from_fc.py /dev/ttyACM0 test_results/test_$i.TXT

    # Decode
    blackbox_decode test_results/test_$i.TXT

    # Brief pause
    sleep 5
done

echo "✓ All tests complete"
```
