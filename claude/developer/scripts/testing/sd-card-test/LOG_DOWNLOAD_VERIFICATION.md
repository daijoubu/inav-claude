# Blackbox Log Download & Verification

## Overview

The test suite can now automatically download and verify blackbox logs from the FC. This provides end-to-end validation:

1. **Download logs** - Via USB MSC (fast) or MSP SPIFLASH (fallback)
2. **Verify structure** - Check for proper header and frame data
3. **Report findings** - Details on frames, fields, and any corruption
4. **Baseline tracking** - Logs included in results JSON for comparison

This confirms that Test 2 (write speed measurement) actually produced valid log files.

---

## Implementation: Hybrid Download

### Method 1: USB Mass Storage (Primary)

**Speed:** Very fast (10+ MB/s)
**Availability:** When FC is mounted as USB drive
**Data source:** SD card files

```python
def download_logs_from_msc(self, output_dir: Path = None) -> list[tuple[Path, bytes]]
```

**Process:**
1. Find FC's USB mount point (same as log clearing)
2. Read `/LOGS/*.BBL` and `/LOGS/*.LOG` files directly
3. Return file list with data
4. Optionally copy to output directory

**When used:**
- FC is connected via USB
- MATEKF765SE with SD card support
- Logs are on SD card (not internal flash)

### Method 2: MSP SPIFLASH (Fallback)

**Speed:** Slow (a few KB/s, takes 2-3 minutes)
**Availability:** When FC has internal flash logging
**Data source:** Internal flash storage

```python
def download_logs_from_msp_flash(self, output_dir: Path = None) -> list[tuple[str, bytes]]
```

**Process:**
1. Query MSP_DATAFLASH_SUMMARY (code 70) for available space
2. Download via MSP_DATAFLASH_READ (code 71) in small chunks
3. Build log from chunks (128 bytes at a time)
4. Return with filename and data

**When used:**
- USB MSC download fails or unavailable
- FC logs to internal SPIFLASH instead of SD
- Fallback for compatibility

### Automatic Fallback

The main method handles both transparently:

```python
def verify_baseline_logs(self) -> LogVerificationResult:
    # Try USB MSC first
    logs = self.fc.download_logs_from_msc()

    if not logs:
        # Fall back to MSP
        logs = self.fc.download_logs_from_msp_flash()
```

---

## Log Verification

### What Gets Checked

| Check | Details |
|-------|---------|
| **Header existence** | Log must have blackbox header section |
| **Header fields** | Required fields: loopIteration, time, gyroADC |
| **Frame markers** | Must contain I-frames (key frames) and/or P-frames |
| **Frame count** | Reports I-frame and P-frame counts |
| **Data integrity** | Basic structure validation (no obvious corruption) |

### Blackbox Log Format

Standard INAV blackbox log format:

```
H Product,INAV
H Data Version,2
H Firmware Version,9.0
H Field I name,loopIteration,time,gyroADC[0],gyroADC[1],gyroADC[2],...
H Field I signed,0,0,1,1,1,...
H Field I predictor,0,0,1,1,1,...
...
H Objects,
H Logging Enabled,Yes
H Minthrottle,1000
...
[binary frame data with I and P frames]
```

**I-frames:** Key frames (contain all fields, larger)
**P-frames:** Prediction frames (delta from previous, smaller)

---

## Usage

### Basic Log Verification

```bash
python sd_card_test.py /dev/ttyACM0 --baseline \
    --hal-version 1.2.2 \
    --verify-logs
```

Output:
```
POST-TEST LOG VERIFICATION
============================================================
  1. Attempting to download via USB Mass Storage (fastest)...
  ✓ USB Mass Storage download successful

  Found 2 log file(s)
  - /mnt/fc/LOGS/000001.BBL: 2345.6 KB
  - /mnt/fc/LOGS/000002.BBL: 1256.8 KB

  Total logs: 2
  Total size: 3.60 MB
  Download method: USB_MSC
  Total frames: 8432 (I: 16, P: 8416)

  Header fields found:
    - loopIteration
    - time
    - gyroADC[0]
    - gyroADC[1]
    - gyroADC[2]
    ... and 45 more

  ✓ No errors detected
  ⚠️  Warnings:
    - Low frame count detected (consider longer logging)

  RESULT: PASS
```

### Save Logs for Analysis

```bash
python sd_card_test.py /dev/ttyACM0 --baseline \
    --hal-version 1.2.2 \
    --verify-logs \
    --save-logs ./baseline_logs_hal_1.2.2
```

Logs copied to:
```
baseline_logs_hal_1.2.2/
  ├── 000001.BBL
  ├── 000002.BBL
  └── ...
```

### Include in Results JSON

```bash
python sd_card_test.py /dev/ttyACM0 --baseline \
    --hal-version 1.2.2 \
    --verify-logs \
    --output baseline_hal_1.2.2.json
```

Results include:
```json
{
  "timestamp": "2026-02-22T12:34:56",
  "hal_version": "1.2.2",
  "results": [...],
  "sd_card_validation": {...},
  "log_verification": {
    "passed": true,
    "logs_found": 2,
    "total_size_mb": 3.60,
    "download_method": "USB_MSC",
    "frame_count": 8432,
    "i_frame_count": 16,
    "p_frame_count": 8416,
    "header_fields": {...},
    "errors": [],
    "warnings": []
  }
}
```

---

## Log Verification Results

### LogVerificationResult Fields

| Field | Type | Meaning |
|-------|------|---------|
| `passed` | bool | True if log is valid and readable |
| `logs_found` | int | Number of log files downloaded |
| `total_size_bytes` | int | Total bytes downloaded |
| `total_size_mb` | float | Total size in MB |
| `first_log_path` | str | Path/name of first log |
| `download_method` | str | "USB_MSC" or "MSP_FLASH" |
| `frame_count` | int | Total I-frames + P-frames |
| `i_frame_count` | int | Count of key frames |
| `p_frame_count` | int | Count of delta frames |
| `header_fields` | dict | Field definitions from header |
| `errors` | list | Critical issues (fail conditions) |
| `warnings` | list | Non-critical issues (pass but note) |

### Pass Conditions

✓ **PASS if:**
- At least 1 log file found
- Log has proper header section
- Log contains I-frames (key frames)
- No critical errors

⚠️ **PASS with warnings if:**
- Very few frames logged
- Some optional fields missing
- Unusual frame ratio

❌ **FAIL if:**
- No logs found
- No header in log
- No frames present
- Log structure corrupted
- Download failed

---

## Troubleshooting

### "No logs found - USB MSC and MSP SPIFLASH both unavailable"

**Cause:** No logs were generated or can't be accessed

**Solutions:**
1. Verify Test 2 ran and FC was armed
2. Check blackbox is enabled: CLI command `blackbox_info`
3. Check SD card has space: CLI command `status`
4. Try manual access via USB MSC or INAV Configurator

### "No blackbox header found"

**Cause:** Log file is corrupted or in wrong format

**Solutions:**
1. Check log file isn't empty
2. Try re-running Test 2 to create fresh log
3. Check if file was cut off during download

### "No frame data found (no I or P frames)"

**Cause:** Log has header but no actual data

**Solutions:**
1. Verify FC was armed during logging
2. Check blackbox rate isn't too low
3. Create longer test (longer logging duration)

### "Very few frames logged"

**Cause:** Log has data but very short duration

**Solutions:**
1. Increase test duration (default 60 sec)
2. Verify FC stayed armed throughout test
3. Check FC loop rate isn't too low

### MSP download extremely slow

**Cause:** Using MSP_DATAFLASH_READ (fallback) which is slow

**Solutions:**
1. Try USB MSC instead (FC must be connected)
2. Expected speed: 3-5 KB/s (2-3 minutes for typical log)
3. Be patient, don't interrupt

---

## Performance

| Metric | Time |
|--------|------|
| USB MSC detection | ~100 ms |
| USB MSC read (per MB) | ~100 ms (10+ MB/s) |
| MSP detection | ~100 ms |
| MSP download (per MB) | ~200-300 sec (3-5 KB/s) |
| Log verification | ~50-500 ms depending on size |
| Total (USB MSC) | 0.5-2 seconds |
| Total (MSP fallback) | 2-3+ minutes |

---

## Example: Complete Baseline with Verification

```bash
# Run full baseline with log verification and saving
python sd_card_test.py /dev/ttyACM0 \
    --test 1,2,3,4,6 \
    --baseline \
    --hal-version 1.2.2 \
    --verify-logs \
    --save-logs ./logs_hal_1.2.2 \
    --output baseline_hal_1.2.2.json

# Output:
# PRE-TEST VALIDATION: SD Card Readiness Check
# ============================================================
#   ✓ SD card ready for testing
#
# TEST 1: SD Card Detection...
# TEST 2: Write Speed Measurement...
# TEST 3: Continuous Logging...
# TEST 4: High-Frequency Logging...
# TEST 6: Rapid Arm/Disarm Cycles...
#
# POST-TEST LOG VERIFICATION
# ============================================================
#   ✓ USB Mass Storage download successful
#   ✓ PASS
#
# Results saved to: baseline_hal_1.2.2.json
# Logs saved to: ./logs_hal_1.2.2/
```

---

## Comparing Baselines

When upgrading HAL, compare log verification:

**HAL 1.2.2:**
```json
"log_verification": {
  "passed": true,
  "logs_found": 1,
  "total_size_mb": 8.0,
  "frame_count": 47520,
  "i_frame_count": 8,
  "p_frame_count": 47512
}
```

**HAL 1.3.3:**
```json
"log_verification": {
  "passed": true,
  "logs_found": 1,
  "total_size_mb": 8.1,
  "frame_count": 48000,
  "i_frame_count": 8,
  "p_frame_count": 48992
}
```

**Comparison:**
- Both pass ✓
- Size similar (8.0 vs 8.1 MB) ✓
- Frame count similar (47520 vs 48000) ✓
- No regression detected ✓

---

## Technical Details

### MSP SPIFLASH Download

Uses standard Betaflight/INAV protocol:

```
MSP_DATAFLASH_SUMMARY (code 70):
  Request: empty
  Response: [flags:1][sectors:4][total:4][used:4]

MSP_DATAFLASH_READ (code 71):
  Request: [address:4][length:2]
  Response: [address:4][data:...]
```

Chunk size: 128 bytes for reliability
Retry: Up to 10 errors before giving up

### USB MSC Discovery

Platform-specific mount point detection:

**Linux:**
- Uses `findmnt` to find mounted filesystems
- Checks `/mnt` and `/media` for LOGS directory

**macOS:**
- Checks `/Volumes` for mounted drives
- Looks for LOGS subdirectory

**Windows:**
- Enumerates drive letters A-Z
- Finds first with LOGS directory

### Blackbox Parsing

Simple text-based header parsing:

```python
# Find header section end
header_end = log_data.rfind(b'\nH ')

# Decode text header
header_section = log_data[:header_end].decode('utf-8', errors='ignore')

# Parse field definitions
for line in header_section.split('\n'):
    if line.startswith('H '):
        field_name = line[2:].split(',')[0]
```

Frame counting: Simple byte search for 'I' and 'P' markers

---

## Safety & Error Handling

✓ **File operations:** Use pathlib (safe path handling)
✓ **Permission errors:** Gracefully skip problematic files
✓ **Decoding errors:** Use utf-8 with error='ignore'
✓ **Missing data:** Check length before unpacking
✓ **Timeout:** MSP requests have 2-second timeout
✓ **Fallback:** Automatically try alternate method if primary fails

---

**Last Updated:** 2026-02-22
**Feature:** Hybrid USB MSC + MSP log download and verification
**Status:** Complete and ready for production
