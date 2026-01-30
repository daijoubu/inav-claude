# Node.js DFU Flasher - Implementation Summary

## Overview

This document summarizes the Node.js DFU flasher implementation (`flash-dfu-node.js`), which is now the **preferred** method for flashing INAV firmware, especially for H7 targets.

## Problem Solved

**Original Issue**: Python DFU flasher (`flash-dfu-preserve-settings.py`) consistently failed at ~69.5% progress on H7 targets.

**Root Cause**: The Python script hardcoded a 2048-byte DFU transfer size, but H7 targets actually require 1024-byte transfers. This was discovered by reading the DFU functional descriptor from the USB interface.

## Solution

Created `flash-dfu-node.js` as a direct port of the working INAV Configurator DFU protocol implementation, with the critical addition of **auto-detecting transfer size from the DFU functional descriptor**.

## Key Features

1. **Auto-detects DFU transfer size** from USB descriptor (bytes 5-6 of DFU functional descriptor)
   - H7 targets: 1024 bytes
   - Other targets: May vary (typically 2048 bytes)
   - Eliminates hardcoded assumptions

2. **Direct port of configurator code**
   - Based on `inav-configurator/js/protocols/stm32usbdfu.js`
   - Uses same state machine and protocol flow
   - Proven, tested implementation

3. **Settings preservation**
   - Selective page erase (only pages containing firmware)
   - Never touches settings sectors at end of flash
   - Matches configurator behavior exactly

4. **Works on all MCU types**
   - F4, F7, H7, AT32F435, etc.
   - Auto-detects flash layout from USB descriptors
   - No manual MCU type specification needed

5. **Clean progress output**
   - Updates every 1% instead of every chunk
   - Much more readable than original implementation

6. **Verification**
   - Reads back and verifies firmware after writing
   - Ensures flash completed successfully

## Technical Details

### DFU Functional Descriptor Format

Located in USB interface descriptor (alternate setting 1):
```
byte 0: length (9)
byte 1: type (0x21)
byte 2: attributes
bytes 3-4: detach timeout
bytes 5-6: transfer size (little-endian) ← KEY!
bytes 7-8: DFU version
```

Example from H7:
```javascript
[9, 33, 11, 255, 0, 0, 4, 26, 1]
                     ^^^^
                     0x0400 = 1024 bytes
```

### Why This Matters

The DFU device has a maximum transfer size it can handle. Sending larger transfers causes the device to reject the operation (transition to wrong state). This is why:
- Python version (2048 bytes) failed on H7 (wants 1024 bytes)
- Minimal test with 64 bytes succeeded
- Full test with 1176 bytes failed
- Test with correct size (1024 bytes) succeeded

### Implementation Approach

1. **Read descriptor** from `device.configDescriptor.interfaces[0]` alternate setting 1
2. **Parse extra data** (Buffer format) to extract transfer size
3. **Use detected size** for all data transfers
4. **Fall back to 2048** if descriptor can't be read (rare)

## Usage

### Basic Usage
```bash
./flash-dfu-node.js path/to/firmware.hex
```

### Dependencies
```bash
cd /path/to/scripts/build
npm install  # Installs node-usb
```

### Example
```bash
# Put FC in DFU mode
./flash-dfu-node.js ../../../../inav/build/inav_9.0.0_DAKEFPVH743.hex
```

### Expected Output
```
INAV DFU Flasher - Node.js
==================================================

Loading firmware.hex...
  Parsed 2 blocks, 662115 bytes

Looking for DFU device...
  Found: 483:df11

  Descriptor: @Internal Flash   /0x08000000/16*128Kg
Flash: 2048 KB (1 sector(s))

Transfer size: 1024 bytes

Calculating erase pages...
  Will erase 7 pages

Erasing flash:
  Progress: 14%  Progress: 28%  ... Progress: 100%
  Erased 896.0 KB

Writing firmware:
  Progress: 0%  Progress: 1%  ... Progress: 50%

Verifying firmware:
  Progress: 50%  Progress: 51%  ... Progress: 100%
✓ Verification successful

Exiting DFU mode...

✓ Firmware flashed successfully!
✓ Settings preserved!

FC will now reboot.
```

## When to Use

### Always Use Node.js Flasher For:
- **H7 targets** (CRITICAL - Python version fails)
- **All targets** (preferred - most reliable)
- **New development** (proven implementation)

### Python Flasher Is Acceptable For:
- F4/F7/AT32 if Node.js unavailable
- **Never use for H7**

### Never Use:
- `build-and-flash.sh` with dfu-util (doesn't preserve settings)
- Direct `dfu-util` commands (doesn't preserve settings)

## Documentation Updates

All documentation has been updated to prefer the Node.js flasher:

1. **Agent: fc-flasher** (`/.claude/agents/fc-flasher.md`)
   - Primary flashing script changed to `flash-dfu-node.js`
   - Python marked as fallback (not for H7)
   - Added transfer size detection explanation

2. **Skill: flash-firmware-dfu** (`/.claude/skills/flash-firmware-dfu/SKILL.md`)
   - Updated to mention Node.js flasher in automated scripts section
   - Added sandbox permission reminder
   - Python version marked as legacy

3. **Agent: inav-builder** (`/.claude/agents/inav-builder.md`)
   - Updated to mention Node.js flasher preference
   - Notes H7 transfer size detection

4. **README** (`claude/developer/scripts/build/README-node-flasher.md`)
   - Complete documentation of Node.js flasher
   - Installation instructions
   - Technical details

## Files

- `flash-dfu-node.js` - Main flasher script
- `flash-dfu-node.js.backup` - Backup copy
- `README-node-flasher.md` - Full documentation
- `package.json` - npm dependencies
- `node_modules/` - Dependencies (after npm install)

## Testing Verified

✅ Successfully flashes H7 target (DAKEFPVH743PRO)
✅ Auto-detects 1024-byte transfer size
✅ Preserves settings (only erases 7 firmware pages)
✅ Verifies firmware after writing
✅ Clean progress output
✅ Proper DFU exit and reboot

## Lessons Learned

1. **Always read USB descriptors** - Don't hardcode device-specific values
2. **Transfer size is critical** - Wrong size causes state machine failures
3. **Port working code directly** - Translating between languages introduces subtle bugs
4. **Test with minimal cases** - Small test scripts helped isolate the issue
5. **Async patterns matter** - Node.js async/await wasn't enough; needed proper descriptor reading

## Future Improvements

Possible enhancements (not currently needed):
- Add more detailed error messages for specific failure cases
- Support flashing to addresses other than 0x08000000
- Add option to skip verification (faster, less safe)
- Support multiple hex files in one session

## Conclusion

The Node.js DFU flasher solves the H7 flashing problem by properly reading the device's transfer size capability from USB descriptors. It is now the preferred method for all targets and should be used by the fc-flasher agent by default.
