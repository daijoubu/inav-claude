# INAV Flight Controller DFU Flashing Guide

## Script Locations

**Primary scripts are located at:**
```
/home/raymorris/Documents/planes/inavflight/claude/developer/scripts/build/
```

### Recommended: flash-dfu-node.js (ALWAYS use for production flashing)

**File:** `flash-dfu-node.js`

**Usage:**
```bash
node /home/raymorris/Documents/planes/inavflight/claude/developer/scripts/build/flash-dfu-node.js <firmware.hex>
```

**Features:**
- Direct port of INAV Configurator's DFU protocol
- Auto-detects flash layout from DFU device descriptor
- Auto-detects DFU transfer size (critical for H7 targets)
- Selective page erase (preserves FC settings)
- Works on all MCU types (F4, F7, H7, AT32, etc.)
- Clean progress reporting (1% increments)
- Proper DFU mode exit and FC reboot

**Dependencies:**
- Node.js 14+
- npm install (usb@2.17.0 already installed)

**Why prefer this:**
- ✅ Proven implementation from configurator
- ✅ Handles H7 transfer size correctly (1024 bytes)
- ✅ Settings preserved automatically
- ✅ Most reliable flashing method

### Alternative: flash-dfu-preserve-settings.py

**File:** `flash-dfu-preserve-settings.py`

**Usage:**
```bash
python3 /home/raymorris/Documents/planes/inavflight/claude/developer/scripts/build/flash-dfu-preserve-settings.py <firmware.hex>
```

**Features:**
- Python implementation with PyUSB
- Selective page erase
- Settings preservation
- **Note:** Does NOT auto-detect DFU transfer size (hardcoded 2048)
- **Fails on H7 targets** at ~69.5% (known issue - use Node.js version)

**When to use:**
- When Node.js is unavailable
- F4/F7/AT32 targets only (NOT H7)

## Flashing Workflow

### 1. Put FC into DFU mode

**Method A: Hardware Button (Recommended)**
- Disconnect USB
- Hold BOOT button
- Reconnect USB while holding BOOT
- Release BOOT after 2 seconds

**Method B: CLI command (if FC is running)**
```bash
python3 reboot-to-dfu.py /dev/ttyACM0
```

### 2. Verify DFU mode

```bash
dfu-util -l
```

Should show:
```
Found DFU: [0483:df11] ... @Internal Flash ...
```

### 3. Flash firmware

```bash
node /home/raymorris/Documents/planes/inavflight/claude/developer/scripts/build/flash-dfu-node.js \
  /path/to/inav_9.1.0_DAKEFPVF405.hex
```

### 4. Wait for reboot

Script automatically handles:
- Selective erase (firmware only)
- Settings preservation
- DFU mode exit
- FC reboot verification

### 5. Verify connection

```bash
ls /dev/ttyACM*
```

FC should reappear at `/dev/ttyACM0` or `/dev/ttyACM1`

## Script Details

### flash-dfu-node.js

**What it does:**
1. Parses Intel HEX firmware file
2. Opens DFU device (0483:df11)
3. **Queries USB descriptor for flash layout** - Critical!
4. **Auto-detects DFU transfer size from descriptor** - Critical!
5. Calculates which sectors contain firmware
6. Erases only those sectors (settings area preserved)
7. Writes firmware in chunks with progress
8. Verifies written data
9. Exits DFU mode (`:leave` equivalent)
10. Waits for FC to reconnect

**Key differences from alternatives:**
- Auto-detects transfer size (handles H7 correctly)
- Uses native libusb (node-usb) like configurator
- Proper progress reporting (write + verify)
- Automatic DFU exit and reboot

### flash-dfu-preserve-settings.py

**What it does:**
1. Parses Intel HEX firmware file
2. Uses PyUSB to open DFU device
3. **Hardcoded transfer size: 2048 bytes** ← Problem on H7!
4. Calculates erase sectors
5. Erases and writes
6. Uses dfu-util for final transfer

**Known issues:**
- Transfer size hardcoded (doesn't query device)
- H7 devices need 1024-byte transfers (fails at ~69.5%)
- Slower progress reporting
- Relies on dfu-util exit handling

## Settings Preservation

Both scripts use **selective page erase**:

1. Parse firmware hex file to find address range
2. Map that range to flash sectors
3. Erase ONLY sectors containing firmware
4. Leave config/settings sectors untouched

**Example:**
```
F405 flash: 0x08000000 - 0x080FFFFF (1MB)
├─ Firmware:  0x08000000 - 0x080A0000 (640KB) ← ERASE THESE
└─ Settings:  0x080A0000 - 0x080FFFFF (384KB) ← PRESERVE THESE
```

## Important Notes

1. **Always use Node.js version** for production unless Node.js is unavailable
2. **Never use dfu-util directly** for DFU flashing (doesn't preserve settings)
3. **H7 targets MUST use Node.js version** (Python version fails)
4. **Transfer size is critical** and must be queried from device
5. **Settings are automatically preserved** by both proper scripts
6. **FC reboots automatically** after successful flash

## Troubleshooting

### "No DFU device found"
1. Verify FC is in DFU mode: `dfu-util -l`
2. Put FC into DFU mode (hold BOOT, reconnect USB)
3. Verify USB connection

### Flash fails midway (Python version)
- This is the H7 transfer size bug
- Use Node.js version instead
- Or reduce transfer size in Python script (advanced)

### FC doesn't reconnect after flash
1. Wait 5 more seconds (boot can be slow)
2. Check `/dev/ttyACM*` again
3. If still not found, may need to manually exit DFU mode

### "Permission denied" for /dev/ttyACM0
```bash
# Add udev rules for DFU
sudo bash -c 'cat > /etc/udev/rules.d/45-stm32dfu.rules << RULE
SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="df11", MODE="0666"
RULE'

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Reference

**INAV Configurator Source:**
- DFU protocol implementation: `inav-configurator/src/js/protocols/stm32usbdfu.js`
- This Node.js script is a direct translation of that code

**MCU Flash Layouts:**
- F405: 4×16K + 1×64K + 7×128K = 1024KB
- F722: 4×16K + 1×64K + 3×128K = 512KB
- H743: 16×128K = 2048KB
- AT32F435: 512×2K = 1024KB
