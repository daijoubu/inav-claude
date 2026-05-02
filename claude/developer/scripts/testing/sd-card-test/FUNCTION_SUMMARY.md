# New MSC Workflow Function - Summary

## What Was Added

A new comprehensive function `msc_download_and_verify_logs()` has been added to the `SDCardTestSuite` class.

## Location

File: `sd_card_test.py`  
Class: `SDCardTestSuite`  
Lines: 2427-2563 (137 lines)

## Function Definition

```python
def msc_download_and_verify_logs(self, output_dir: Path = None) -> LogVerificationResult:
```

## Key Features

✅ **Fully Automated Workflow**
- No manual steps required
- Single function call handles entire MSC process

✅ **Complete Error Handling**
- Graceful handling of mount failures
- Automatic fallback to manual mount
- Detailed error logging and reporting

✅ **Comprehensive Verification**
- Downloads all log files
- Validates each log structure
- Counts inertial and performance frames
- Detects corrupted files

✅ **Clean Exit**
- Properly unmounts SD card
- Uses ST-Link to reset FC
- Restores CDC operation
- Handles disconnection edge cases

## What It Does - Step by Step

1. **Enable MSC Mode** (CLI command)
   - Sends 'msc' to enter USB storage mode
   - Waits up to 30 seconds for enumeration

2. **Mount SD Card** (automatic or manual)
   - Searches for mount point automatically
   - Falls back to `udisksctl mount -b /dev/sdb1` if needed
   - Verifies mount point accessibility

3. **Download Log Files** (USB MSC read)
   - Copies all .TXT files from SD card LOGS directory
   - Optionally saves to output directory
   - Reports file count and total size

4. **Verify Logs** (frame-by-frame parsing)
   - Parses blackbox header
   - Counts I-frames (inertial data)
   - Counts P-frames (performance data)
   - Validates frame structure
   - Collects errors and warnings

5. **Exit MSC Mode** (ST-Link reset)
   - Unmounts SD card with udisksctl
   - Uses ST-Link to trigger NVIC_SystemReset
   - Writes RESET_NONE to RTC_BKP1
   - Waits for CDC re-enumeration
   - Verifies FC responsiveness

## Usage

### Simple Example
```python
suite = SDCardTestSuite(fc=fc)
result = suite.msc_download_and_verify_logs()
print(f"Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")
print(f"Logs: {result.logs_found}, Frames: {result.frame_count:,}")
```

### With Output Directory
```python
result = suite.msc_download_and_verify_logs(
    output_dir=Path('logs')
)
```

### Full Result Inspection
```python
result = suite.msc_download_and_verify_logs()

if result.passed:
    print(f"✓ {result.logs_found} logs verified")
    print(f"  I-frames: {result.i_frame_count:,}")
    print(f"  P-frames: {result.p_frame_count:,}")
else:
    for error in result.errors:
        print(f"✗ {error}")
```

## Return Value

Returns a `LogVerificationResult` with:
- **passed**: Success/failure status
- **logs_found**: Count of verified logs
- **frame_count**: Total frames in logs
- **i_frame_count**: Inertial frames
- **p_frame_count**: Performance frames
- **download_method**: "USB_MSC"
- **errors**: List of error messages
- **warnings**: List of warnings

## Dependencies

- **mspapi2**: MSP protocol communication
- **pyserial**: Serial port access
- **udisksctl**: SD card mount/unmount
- **OpenOCD**: ST-Link reset functionality
- **subprocess**: System commands

## Testing

The function has been verified to:
✅ Successfully enable MSC mode via CLI
✅ Automatically mount SD card
✅ Download log files correctly
✅ Parse and validate blackbox logs
✅ Cleanly exit MSC and restore CDC
✅ Handle edge cases (missing mount point, etc.)

## Documentation

Complete documentation is available in:
- `MSC_WORKFLOW.md` - Usage guide and examples
- Inline code comments - Implementation details
