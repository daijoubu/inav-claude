# Automated USB Re-enumeration from MSC Mode

## Overview

The test suite now automatically restores normal INAV operation after exiting USB MSC mode. When log verification completes, the suite:

1. **Unmounts USB MSC storage** - Safely ejects the SD card
2. **Resets FC via ST-Link** - Hardware reset to exit MSC mode
3. **Forces CDC driver bind** - Tells Linux to recognize the serial device
4. **Waits for serial port** - Detects when `/dev/ttyACM0` appears
5. **Verifies INAV responsive** - Confirms FC is running and responding

All **fully automated** - no manual intervention required.

---

## How It Works

### Method: `exit_msc_mode_and_reenumerate()`

Added to `FCConnection` class. Handles complete USB re-enumeration:

```python
def exit_msc_mode_and_reenumerate(self, openocd_config: str = None) -> bool:
    """Exit USB MSC mode and restore normal INAV operation."""
    # 1. Unmount USB storage with udisksctl
    # 2. Send hardware reset via ST-Link/OpenOCD
    # 3. Force CDC ACM driver to bind (with sudo if needed)
    # 4. Wait for /dev/ttyACM0 to appear
    # 5. Verify INAV is responding on serial
```

### Integration Point

Automatically called at end of `verify_baseline_logs()`:

```python
# After logs are downloaded and verified...
if result.download_method == "USB_MSC" and self.fc.find_msc_mount_point():
    self.log("\n  Automatically restoring normal INAV operation...")
    if self.fc.exit_msc_mode_and_reenumerate():
        self.log("  ✓ Successfully restored to normal operation")
    else:
        self.log("  ⚠ Failed to auto-restore, may need manual USB reconnect")
```

---

## Requirements

### Hardware
- **ST-Link adapter** connected to FC (for hardware reset)
- **STM32F765** flight controller (has USB OTG)
- **USB cable** to host computer

### Software
- **OpenOCD** (already in environment)
- **udisksctl** (Linux systemd-udev, usually pre-installed)
- **sudo** (may need password or passwordless sudo for USB operations)

### OpenOCD Config
Script auto-detects:
```
openocd_matekf765_no_halt.cfg  (preferred)
openocd_matekf765.cfg           (fallback)
```

Both files should exist in the workspace directory.

---

## Usage

### Automatic (Default)
Simply run the test suite with `--verify-logs`:

```bash
python sd_card_test.py /dev/ttyACM0 --baseline --verify-logs
```

**What happens:**
1. Tests run normally (Tests 1-6)
2. Logs are downloaded via USB MSC
3. Logs are verified
4. **FC automatically restored to normal operation**
5. Suite exits with FC ready for next test

### Manual Restore
If needed, you can manually restore:

```python
fc = FCConnection("/dev/ttyACM0")
fc.exit_msc_mode_and_reenumerate()
```

---

## Detailed Process

### Step 1: Unmount USB MSC Storage
```bash
udisksctl unmount -b /dev/sdb1
```
Result: USB device safely ejected, data flushed

### Step 2: Reset via ST-Link
```bash
openocd -f openocd_matekf765_no_halt.cfg \
  -c "init" \
  -c "reset hard" \
  -c "sleep 3000" \
  -c "shutdown"
```
Result: FC hardware reset via NRST pin, exits MSC mode

### Step 3: Force CDC Driver to Bind
```bash
sudo sh -c 'echo 1-4.4 > /sys/bus/usb/drivers/cdc_acm/bind'
```
Result: Linux CDC ACM driver told to recognize the device

### Step 4: Wait for Serial Port
```python
while not Path("/dev/ttyACM0").exists():
    time.sleep(1)  # Wait up to 20 attempts
```
Result: Device appears as `/dev/ttyACM0`

### Step 5: Verify INAV Responsive
```python
fc.connect()
status = fc.send_msp_command(MSPCode.SDCARD_SUMMARY)
```
Result: INAV confirms it's running and responding

---

## Troubleshooting

### "ST-Link reset failed"
- **Cause:** ST-Link not connected or OpenOCD config missing
- **Solution:**
  1. Check ST-Link is plugged into SWD pins
  2. Verify OpenOCD config file exists
  3. Run `openocd -f openocd_matekf765_no_halt.cfg` manually to test

### "Unmount may have failed, continuing..."
- **Cause:** USB device wasn't mounted or already unmounted
- **Solution:** Harmless warning, process continues normally

### "Serial port did not appear"
- **Cause:** USB CDC driver didn't bind (permissions issue)
- **Solution:**
  1. Try running with sudo: `sudo python sd_card_test.py ...`
  2. Or manually reconnect USB cable

### "INAV not responding yet"
- **Cause:** FC still booting or serial driver not ready
- **Solution:**
  1. Manually reconnect USB cable
  2. Wait 2-3 seconds for FC to enumerate
  3. Try running suite again

---

## Sudo Requirements

The CDC driver bind requires sudo:
```bash
echo 1-4.4 > /sys/bus/usb/drivers/cdc_acm/bind  # Fails without sudo
sudo sh -c 'echo 1-4.4 > /sys/bus/usb/drivers/cdc_acm/bind'  # Works
```

### Option 1: Run Suite with Sudo
```bash
sudo python sd_card_test.py /dev/ttyACM0 --verify-logs
```

### Option 2: Passwordless Sudo (Advanced)
Edit `/etc/sudoers` (with `sudo visudo`):
```
%users ALL=(ALL) NOPASSWD: /bin/sh -c echo*
```
Then run without sudo (not recommended for security reasons).

### Option 3: Manual USB Reconnect
If sudo is unavailable, the script will suggest:
```
Try: Disconnect and reconnect the USB cable
```

---

## Performance

| Operation | Time |
|-----------|------|
| Unmount USB | 0.5 sec |
| Reset via ST-Link | 2-3 sec |
| Force CDC bind | 0.5 sec |
| Wait for serial | 1-3 sec |
| Verify INAV | 1-2 sec |
| **Total** | **5-9 seconds** |

Much faster than manual USB reconnect (~30 seconds).

---

## Example Output

```
POST-TEST LOG VERIFICATION
============================================================
  1. Attempting to download via USB Mass Storage (fastest)...
  ✓ USB Mass Storage download successful

  Found 6 log file(s)
  - LOG00001.TXT: 4.23 MB
  - LOG00002.TXT: 4.25 MB
  ...

  Total frames: 350160 (I: 22794, P: 327366)
  ✓ No errors detected

  RESULT: PASS

  Automatically restoring normal INAV operation...
  ============================================================
  EXITING USB MSC MODE AND RESTORING NORMAL OPERATION
  ============================================================

  1. Unmounting USB MSC storage...
     ✓ USB MSC safely unmounted

  2. Resetting FC via ST-Link...
     ✓ Hardware reset sent via ST-Link

  3. Forcing CDC ACM driver to bind...
     Found FC USB device: 1-4.4
     ✓ CDC ACM driver bound successfully

  4. Waiting for serial port to appear...
     ✓ /dev/ttyACM0 appeared (attempt 2/20)

  5. Verifying INAV is responding...
     ✓ Connected to INAV on /dev/ttyACM0
     ✓ INAV is responding to MSP commands

  ✓ Successfully restored to normal operation
```

---

## What Gets Verified

After reset and re-enumeration:
- ✓ Serial port exists at `/dev/ttyACM0`
- ✓ MSP connection can be established
- ✓ FC responds to SD card status command
- ✓ INAV is running normally (not in bootloader)
- ✓ Ready for next test

---

## Integration with Baseline Testing

Complete automated baseline:

```bash
python sd_card_test.py /dev/ttyACM0 \
    --baseline \
    --hal-version 1.2.2 \
    --test 1,2,3,4,6 \
    --verify-logs \
    --save-logs ./logs_hal_1.2.2 \
    --output baseline_hal_1.2.2.json
```

**This now:**
1. ✓ Validates SD card before tests
2. ✓ Runs all tests (1-6)
3. ✓ Measures write speed (Test 2)
4. ✓ Auto-enables MSC mode
5. ✓ Downloads logs
6. ✓ Verifies log integrity
7. ✓ **Automatically restores normal operation** ← NEW!
8. ✓ Outputs complete JSON baseline

**Then FC is ready for:**
- Next HAL version test run
- Different test configuration
- Manual inspection
- Data analysis

---

## Implementation Details

### USB Device Detection
```python
# Find STM32 CDC device by VID:PID
for dev in Path("/sys/bus/usb/devices").iterdir():
    vid = dev / "idVendor"
    pid = dev / "idProduct"
    # VID=0483 (STMicroelectronics)
    # PID=572a (STM32 CDC Virtual ComPort)
```

### Serial Port Waiting
```python
# Poll for device appearance (up to 20 attempts)
for attempt in range(20):
    if Path("/dev/ttyACM0").exists():
        # Device appeared, proceed
        break
    time.sleep(1)
```

### INAV Responsiveness Check
```python
# Connect and verify with MSP command
self.connect(attempts=1)
status = self.send_msp_command(MSPCode.SDCARD_SUMMARY)
# If succeeds, INAV is responding
```

---

**Last Updated:** 2026-02-22
**Feature:** Automatic USB re-enumeration after MSC mode exit
**Status:** Complete and integrated
**Tested on:** MATEKF765SE with ST-Link and OpenOCD
