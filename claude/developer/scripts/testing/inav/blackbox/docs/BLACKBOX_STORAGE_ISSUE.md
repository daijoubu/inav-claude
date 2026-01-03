# Blackbox Storage Issue - Status

**Date:** 2025-12-28
**FC:** BROTHERHOBBYH743
**Issue:** Blackbox not logging to storage despite correct configuration

---

## Configuration Applied

✓ **BLACKBOX feature:** Enabled (bit 19 set in features = 0x20480C06)
✓ **BLACKBOX mode:** Always active (AUX1 range 900-2100us)
✓ **blackbox_arm_control:** -1 (log from boot)
✓ **blackbox_rate_denom:** 2 (500 Hz)
✓ **debug_mode:** 20 (DEBUG_POS_EST)

## Problem

**MSP_DATAFLASH_SUMMARY** returns:
- Total size: 0 bytes
- Used size: 0 bytes
- Flags: 0x00

This suggests **no storage device is detected**.

## Devices Tried

1. **SPIFLASH (device=1):** No flash detected (total size = 0)
2. **SDCARD (device=2):** Currently set, but likely no SD card slot or card inserted

## Possible Causes

1. **No onboard flash chip:** This FC model may not have SPI flash
2. **No SD card:** No card inserted or no SD card slot on this board
3. **Flash not initialized:** Driver issue or hardware fault
4. **Wrong device setting:** Need to determine what storage this FC actually has

## Next Steps

### Option 1: Check Hardware Capabilities

Use INAV Configurator to determine what blackbox storage options are available for this specific FC:
1. Connect to FC
2. CLI tab → type `get blackbox_device`
3. Try setting different values and check which ones work

### Option 2: Use SERIAL Blackbox Streaming

If no onboard storage exists, use **SERIAL mode** to stream blackbox data over MSP:

```python
# Set blackbox_device = SERIAL (0)
setting_name = b'blackbox_device\0'
setting_value = struct.pack('<i', 0)  # 0 = SERIAL
api._serial.send(0x1004, setting_name + setting_value)
```

Then capture the stream during GPS injection test.

### Option 3: Use SITL Instead

Fall back to SITL testing, but note the 15ms FILE blackbox bug from previous session.

---

## Commands to Diagnose

```bash
# Check what blackbox devices are supported
# Via CLI in configurator:
get blackbox_device

# Check if flash chip is detected (via Python)
python3 -c "
from mspapi2 import MSPApi
import struct

api = MSPApi(port='/dev/ttyACM0', baudrate=115200)
api.open()

# MSP_DATAFLASH_SUMMARY (70)
code, response = api._serial.request(70, b'')
if response:
    flags, totalSize, usedSize = struct.unpack('<BII', response[:9])
    print(f'Flash: {totalSize} bytes total, {usedSize} used')

api.close()
"
```

---

## Alternative: Manual Arming + Real RC

If we can get a physical RC transmitter connected:
1. Use real RC for arming
2. Blackbox logs while armed (arm_control=0)
3. GPS injection via MSP continues to work
4. No need for MSP-based arming or BLACKBOX mode tricks

---

## Status

**Blocked on:** Determining what blackbox storage this FC board actually has, if any.

**Next action:** User to check INAV Configurator Logging tab for available storage options.
