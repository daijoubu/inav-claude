# MSC Workflow Function

## Overview

The `msc_download_and_verify_logs()` function provides a complete automated workflow for:
1. Enabling USB MSC mode
2. Mounting the SD card
3. Downloading blackbox log files
4. Verifying log integrity
5. Cleanly exiting MSC mode and restoring CDC operation

This eliminates the need for manual steps and provides comprehensive error handling.

## Function Signature

```python
def msc_download_and_verify_logs(self, output_dir: Path = None) -> LogVerificationResult
```

## Parameters

- **output_dir** (Path, optional): Directory to save downloaded log files. If None, logs are processed in memory.

## Return Value

Returns a `LogVerificationResult` object with:
- **passed**: bool - True if all steps succeeded and logs verified OK
- **logs_found**: int - Number of log files downloaded
- **frame_count**: int - Total frames across all logs
- **i_frame_count**: int - I-frames (inertial) count
- **p_frame_count**: int - P-frames (performance) count
- **download_method**: str - "USB_MSC" (only method for this function)
- **errors**: list - Any errors encountered
- **warnings**: list - Non-critical warnings

## Workflow Steps

### Step 1: Enable MSC Mode (30s timeout)
- Sends CLI command to enter USB Mass Storage mode
- Waits for FC to reboot and enumerate as USB storage

### Step 2: Mount SD Card
- Searches for MSC mount point automatically
- Falls back to manual mount via udisksctl if needed
- Verifies mount point accessibility

### Step 3: Download Log Files
- Downloads all available blackbox logs from SD card
- Saves to output directory if specified
- Reports file sizes and counts

### Step 4: Verify Logs
- Parses each blackbox log file
- Validates header structure and frame integrity
- Counts I-frames and P-frames
- Reports any errors or warnings

### Step 5: Exit MSC Mode
- Cleanly unmounts SD card
- Uses ST-Link to reset FC to normal CDC operation
- Waits for USB re-enumeration
- Verifies FC is responsive

## Usage Examples

### Basic Usage

```python
from sd_card_test import FCConnection, SDCardTestSuite
from pathlib import Path

# Connect to FC
fc = FCConnection(port='/dev/ttyACM0', baudrate=115200)
fc.connect()

# Create test suite
suite = SDCardTestSuite(fc=fc, verbose=True)

# Run MSC workflow
result = suite.msc_download_and_verify_logs()

# Check results
if result.passed:
    print(f"✓ Success! Downloaded and verified {result.logs_found} logs")
    print(f"  Total frames: {result.frame_count:,}")
else:
    print(f"✗ Failed: {result.errors}")
```

### With Output Directory

```python
# Download logs to a specific directory
result = suite.msc_download_and_verify_logs(
    output_dir=Path('/tmp/baseline_logs')
)

# Access downloaded files
for path in output_dir.glob('*.TXT'):
    print(f"Downloaded: {path}")
```

### Handling Results

```python
result = suite.msc_download_and_verify_logs()

# Check overall status
if result.passed:
    print("✅ Workflow completed successfully")
else:
    print("❌ Workflow failed")

# Access detailed metrics
print(f"Logs found: {result.logs_found}")
print(f"Total frames: {result.frame_count:,}")
print(f"I-frames: {result.i_frame_count:,}")
print(f"P-frames: {result.p_frame_count:,}")

# Check for errors
if result.errors:
    for error in result.errors:
        print(f"Error: {error}")

if result.warnings:
    for warning in result.warnings:
        print(f"Warning: {warning}")
```

### Integration with Test Suite

```python
# Run a test, then download and verify logs
result = suite.run_test(2)  # Test 2: Write Speed

if result.passed:
    # Test passed, download the logs to verify
    log_result = suite.msc_download_and_verify_logs(
        output_dir=Path('test_results')
    )
    
    if log_result.passed:
        print("✅ Test and log verification passed!")
    else:
        print("⚠ Test passed but logs have issues")
```

## Error Handling

The function handles several error scenarios gracefully:

1. **MSC Enable Failure**: Returns with `passed=False`
2. **Mount Point Not Found**: Attempts manual mount via udisksctl
3. **No Logs Found**: Returns with `logs_found=0`
4. **Log Verification Errors**: Collects errors and continues with other logs
5. **MSC Exit Failure**: Reports error but provides recovery suggestion

## Requirements

- **ST-Link Debugger**: Connected to FC for proper MSC exit via NVIC_SystemReset
- **udisksctl**: For automatic SD card mounting (optional, function can attempt manual mount)
- **Linux/macOS**: Primary testing platform
- **Administrator access**: For SD card operations (though typically works without sudo for USB devices)

## Performance Characteristics

- **MSC Enable**: ~2-5 seconds
- **SD Card Mount**: ~1 second
- **Log Download**: Depends on log file size (typically 30-100 MB/s on USB 2.0)
- **Log Verification**: ~1-2 seconds per log file
- **MSC Exit**: ~3-5 seconds
- **Total Time**: 10-30 seconds depending on number and size of logs

## Troubleshooting

### "Could not find MSC mount point"
- The FC may not have properly entered MSC mode
- Check if `/dev/sdb` appears in `lsblk` after MSC enable
- May need to manually mount: `udisksctl mount -b /dev/sdb1`

### "Failed to exit MSC mode cleanly"
- ST-Link may not be responding
- Check ST-Link connection and power
- May need manual USB reconnect
- Device will fall back to CDC eventually

### Timeouts during download
- SD card may have bad sectors or slow performance
- Increase timeout in FC configuration
- Try downloading via MSP SPIFLASH instead

### "Frame count mismatch"
- Check if logs are being continuously overwritten
- Ensure sufficient SD card free space (>150 MB recommended)
- Verify blackbox format is compatible

## Future Enhancements

Potential improvements to this function:
- Parallel log download and verification
- Checksum validation for downloaded files
- Automatic log cleanup/archival
- Log compression before download
- HTTP upload integration for cloud storage
