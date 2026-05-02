# Automatic USB MSC Mode Enabling

## Overview

The test suite now automatically enables USB MSC mode to access SD card logs. This eliminates the need for manual intervention:

1. **Auto-enables MSC mode** - Via CLI command if MSC mount not found
2. **Waits for reboot** - Detects when FC appears as USB mass storage
3. **Downloads logs** - Direct filesystem access (10+ MB/s)
4. **Verifies integrity** - Validates blackbox log structure and frames

The entire process is fully automated and unattended.

---

## How It Works

### MSC Mode Activation

**Command:** `msc` (via INAV CLI)

**What happens:**
1. FC receives CLI command via serial
2. FC prints confirmation message
3. FC reboots with RESET_MSC_REQUEST flag
4. FC boots into USB MSC mode
5. FC disappears from serial, appears as USB mass storage
6. SD card mounts on host computer

### Mount Point Detection

Once in MSC mode, the `find_msc_mount_point()` method:

**Linux:**
- Parses `findmnt` output for removable media
- Checks `/mnt` and `/media` directories
- Looks for LOGS subdirectory

**macOS:**
- Checks `/Volumes` directory
- Finds first device with LOGS folder

**Windows:**
- Enumerates drive letters A-Z
- Finds first drive with LOGS directory

### Log Download

Once mounted, `download_logs_from_msc()`:

1. Reads `/LOGS/*.BBL`, `*.LOG`, and `*.TXT` files
2. Loads entire file into memory
3. Returns (file_path, file_data) tuples
4. Optionally copies to output directory

### Log Verification

For each downloaded log:

1. **Parse header** - Extract field definitions
2. **Count frames** - I-frames (key) and P-frames (delta)
3. **Validate required fields** - loopIteration, time, gyroADC
4. **Check structure** - Valid blackbox format
5. **Report results** - Passed/failed with details

---

## Usage

### Automatic (Default)

Simply run baseline tests with `--verify-logs`:

```bash
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2 \
    --test 1,2,3,4,6 \
    --verify-logs
```

**What happens:**
1. Tests run normally (Tests 1-6)
2. After tests complete, log verification begins
3. Script attempts to find MSC mount point
4. If not found, sends `msc` CLI command
5. Waits for FC to reboot into MSC mode
6. Detects when FC appears as USB device
7. Downloads and verifies logs
8. Reports results

### With Log Saving

```bash
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2 \
    --test 1,2,3,4,6 \
    --verify-logs \
    --save-logs ./logs_hal_1.2.2
```

Saves logs to:
```
logs_hal_1.2.2/
  ├── LOG00001.TXT
  ├── LOG00002.TXT
  └── ...
```

### With JSON Results

```bash
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2 \
    --test 1,2,3,4,6 \
    --verify-logs \
    --output baseline_hal_1.2.2.json
```

JSON includes:
```json
{
  "log_verification": {
    "passed": true,
    "download_method": "USB_MSC",
    "logs_found": 1,
    "total_size_mb": 4.30,
    "frame_count": 58360,
    "i_frame_count": 3779,
    "p_frame_count": 54581,
    "errors": [],
    "warnings": []
  }
}
```

---

## Example Output

```
POST-TEST LOG VERIFICATION
============================================================
  1. Attempting to download via USB Mass Storage (fastest)...
  ✗ USB MSC mount point not found
  2. Attempting to enable USB MSC mode via CLI...
  ✓ USB MSC mode enabled, waiting for mount...
  ✓ USB Mass Storage download successful

  Found 6 log file(s)
  - LOG00001.TXT: 4.23 MB
  - LOG00002.TXT: 4.25 MB
  - LOG00003.TXT: 4.27 MB
  - LOG00004.TXT: 4.27 MB
  - LOG00005.TXT: 2.17 MB
  - LOG00006.TXT: 4.30 MB

  Total logs: 6
  Total size: 23.49 MB
  Download method: USB_MSC
  Total frames: 350160 (I: 22794, P: 327366)

  Header fields found:
    - loopIteration
    - time
    - axisRate[0]
    - axisRate[1]
    - ... and 26 more

  ✓ No errors detected

  RESULT: PASS
```

---

## What Gets Verified

Each log is checked for:

| Check | Requirement | Result |
|-------|-------------|--------|
| Header | Must have proper blackbox header | FAIL if missing |
| Header format | Text section with field definitions | FAIL if invalid |
| Required fields | loopIteration, time, gyroADC | WARN if missing |
| Frame markers | Contains I and/or P frames | FAIL if no frames |
| Frame count | Reasonable number of frames | WARN if <10 total |
| Data size | Non-empty file | FAIL if empty |
| No corruption | Basic structure checks | WARN if issues found |

**PASS if:**
- Header found and valid
- At least one I-frame present
- No critical errors
- File has data

---

## File Formats Supported

The script looks for all blackbox log file extensions:

- `.BBL` - Binary blackbox format
- `.LOG` - Standard log format
- `.TXT` - Text-based blackbox format (INAV default)

Most files will be `.TXT` from modern INAV versions.

---

## Automatic Fallback Chain

If USB MSC doesn't work:

```
Try 1: Direct MSC mount
  ↓ (mount not found)
Try 2: Enable MSC mode via CLI
  ↓ (MSC enable failed)
Try 3: MSP SPIFLASH download
  ↓ (SPIFLASH not available)
FAIL: No download method available
```

The script tries each method automatically.

---

## Performance

| Operation | Time |
|-----------|------|
| Find mount point | 100-500 ms |
| Enable MSC mode | 3-5 seconds (FC reboot) |
| Download logs (per MB) | 100 ms (10+ MB/s via USB MSC) |
| Verify logs (per MB) | 10-50 ms |
| Total for 4 MB log | 0.5-1 second |

**Much faster than MSP SPIFLASH** which takes 2-3 minutes per log.

---

## Troubleshooting

### "USB MSC mode enabled but mount failed"

**Cause:** FC rebooted to MSC mode but filesystem not auto-mounted

**Solutions:**
1. Mount manually: `udisksctl mount -b /dev/sdb1`
2. Check if FC appears: `lsblk | grep STM`
3. Check permissions: Should be readable by user
4. Try different USB port or cable

### "Failed to enable USB MSC mode"

**Cause:** CLI command didn't execute or FC not responding

**Solutions:**
1. Verify FC is powered and responsive
2. Check serial port connection
3. Try manual `msc` command in INAV CLI/Configurator
4. Check if FC supports USB MSC (hardware limitation)

### "USB MSC mount point not found" (persistent)

**Cause:** FC doesn't support USB MSC or mode enable failed

**Solutions:**
1. FC reverts to serial after timeout
2. Download logs manually via Configurator
3. Check if board supports USB MSC (datasheet)
4. Verify USB cable supports data (not charge-only)

### No logs found after download

**Cause:** LOGS directory is empty (no flights logged)

**Solutions:**
1. Verify Tests 1-6 actually ran
2. Check FC was armed during Test 2
3. Verify blackbox configuration: `blackbox_info` (CLI)
4. Check SD card has space

---

## What Files Are Downloaded

By default, the script downloads the **most recent logs** (sorted by modification time).

**File order:**
1. All `.BBL` files (if any)
2. All `.LOG` files (if any)
3. All `.TXT` files (most common)

**Filtered by:**
- File is regular file (not directory)
- Readable by user
- Has data (size > 0)

---

## CLI Command Details

The `msc` command is built into INAV:

**Requirements:**
- SD card must be functional (or SPIFLASH must have data)
- FC must be connected via USB

**Behavior:**
1. Checks SD card status
2. Checks SPIFLASH status
3. If either available: `systemResetRequest(RESET_MSC_REQUEST)`
4. FC reboots with special flag
5. Bootloader/firmware recognizes flag
6. Boots into MSC mode instead of normal mode

---

## Security & Safety

✓ **No authentication** - MSC mode is part of normal FC
✓ **No extra privileges** - Uses standard mount/unmount
✓ **File operations only** - Read-only access to logs
✓ **Timeout protection** - Waits max 30 seconds for mount
✓ **Error handling** - Gracefully continues if MSC fails

---

## Hardware Compatibility

**Tested on:**
- MATEKF765SE ✓
- STM32F765 with USB OTG ✓

**Should work on:**
- Any STM32 with USB OTG
- Any board with USB MSC support in firmware
- Most modern INAV flight controllers

**May not work on:**
- Boards without USB OTG (older boards)
- Boards with USB disabled in firmware
- Boards using only SPIFLASH (no SD card)

---

## Integration with Baseline Testing

Full automated baseline:

```bash
python sd_card_test.py /dev/ttyACM0 \
    --baseline \
    --hal-version 1.2.2 \
    --test 1,2,3,4,6 \
    --verify-logs \
    --save-logs ./logs_hal_1.2.2 \
    --output baseline_hal_1.2.2.json
```

**This:**
1. ✓ Validates SD card before tests
2. ✓ Runs all tests (1-6)
3. ✓ Measures write speed (Test 2)
4. ✓ Auto-enables MSC mode
5. ✓ Downloads logs
6. ✓ Verifies log integrity
7. ✓ Saves logs for archive
8. ✓ Outputs complete JSON baseline

**Result:** Complete, verifiable baseline ready for HAL upgrade comparison!

---

**Last Updated:** 2026-02-22
**Feature:** Automatic USB MSC mode enabling with log download
**Status:** Complete and tested
**Verified on:** MATEKF765SE with HAL 1.2.2
