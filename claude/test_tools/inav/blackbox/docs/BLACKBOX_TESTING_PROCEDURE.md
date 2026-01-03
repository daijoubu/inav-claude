# Blackbox Field Testing Procedure

This document explains how to selectively enable/disable blackbox fields and run clean tests to isolate encoding issues.

## ⭐ PREFERRED METHOD: Modify testBlackboxConditionUncached()

**Use this method for debugging blackbox encoder/decoder issues.**

### Why This Works

The blackbox system uses `testBlackboxCondition()` to determine which fields to include in both:
1. The log header (via `sendFieldDefinition()`)
2. The log data (via `writeIntraframe()` and `writeInterframe()`)

By modifying `testBlackboxConditionUncached()` to selectively enable conditions, you ensure perfect header/data synchronization.

### Implementation Steps

**1. Edit src/main/blackbox/blackbox.c line 643:**

**IMPORTANT:** COMMENT OUT the original switch statement - DO NOT DELETE IT!

```c
static bool testBlackboxConditionUncached(FlightLogFieldCondition condition)
{
    // DEBUGGING: Only enable ALWAYS fields (loopIteration, time, gyroADC, etc.)
    if (condition == FLIGHT_LOG_FIELD_CONDITION_ALWAYS) {
        return true;
    }
    return false;  // Disable all other fields

    /* ORIGINAL CODE COMMENTED OUT FOR DEBUGGING - RESTORE WHEN DONE:
    switch (condition) {
    case FLIGHT_LOG_FIELD_CONDITION_ALWAYS:
        return true;
    case FLIGHT_LOG_FIELD_CONDITION_MOTORS:
        return blackboxIncludeFlag(BLACKBOX_FEATURE_MOTORS);
    ... (entire original switch - lines 645-796)
    default:
        return false;
    }
    */
}
```

**2. Build, flash, and test:**

```bash
cd inav/build
make JHEMCUF435 -j4
# Flash via DFU
# Run test: ./run_20field_test.sh /dev/ttyACM0 10
# Download and decode log
```

**3. Incrementally enable conditions:**

To add accelerometer fields:
```c
if (condition == FLIGHT_LOG_FIELD_CONDITION_ALWAYS ||
    condition == FLIGHT_LOG_FIELD_CONDITION_ACC) {
    return true;
}
return false;
```

Or use switch for multiple:
```c
switch (condition) {
case FLIGHT_LOG_FIELD_CONDITION_ALWAYS:
case FLIGHT_LOG_FIELD_CONDITION_ACC:
case FLIGHT_LOG_FIELD_CONDITION_ATTITUDE:
case FLIGHT_LOG_FIELD_CONDITION_DEBUG:
    return true;
default:
    return false;
}
```

**Common field conditions:**
- `FLIGHT_LOG_FIELD_CONDITION_ALWAYS` - Core fields (loopIteration, time, axisRate, axis PID, gyroADC, navState, navFlags)
- `FLIGHT_LOG_FIELD_CONDITION_ACC` - Accelerometer (accSmooth, accVib)
- `FLIGHT_LOG_FIELD_CONDITION_ATTITUDE` - Attitude (roll, pitch, yaw)
- `FLIGHT_LOG_FIELD_CONDITION_DEBUG` - Debug values (debug[0-7])
- `FLIGHT_LOG_FIELD_CONDITION_RC_DATA` - Raw RC inputs
- `FLIGHT_LOG_FIELD_CONDITION_RC_COMMAND` - Processed RC commands
- `FLIGHT_LOG_FIELD_CONDITION_NAV_POS` - Navigation position/velocity
- `FLIGHT_LOG_FIELD_CONDITION_GYRO_RAW` - Raw gyro values
- `FLIGHT_LOG_FIELD_CONDITION_MAG` - Magnetometer
- `FLIGHT_LOG_FIELD_CONDITION_BARO` - Barometer
- See `src/main/blackbox/blackbox.h` for full list

### Advantages

✅ **Preserves original code** - Just comment out, don't delete
✅ **Perfect header/data sync** - Both use the same condition check
✅ **Clean git diff** - Single function modification
✅ **Easy to iterate** - Add one condition at a time
✅ **Reversible** - Uncomment original code when done

---

## Prerequisites

- INAV source code checked out
- Build environment configured (`cmake ..` already run in `build/` directory)
- Flight controller connected via USB
- Python tools: `mspapi2` or `pyserial` installed
- DFU flashing tools configured

## ⚠️ Important: Avoiding Common Issues

### Issue 1: CLI Mode Problem
**Never use individual CLI commands for verification during automated testing.**

Running `fc-cli.py "get setting"` leaves the FC in CLI mode, causing subsequent MSP operations to fail. See `test_results/CLI_MODE_PROBLEM.md` for details.

**Solution:** Use automated scripts like `run_20field_test.sh` that configure, save, and exit CLI properly in one session.

### Issue 2: Settings Reset After Firmware Flash
**Always configure blackbox settings after flashing firmware.**

Flashing firmware resets ALL settings to defaults, including `blackbox_rate_denom = 1` (logs every loop at ~2000 Hz). See `test_results/BLACKBOX_RATE_DENOM_ISSUE.md` for details.

**Required settings after every firmware flash:**
```bash
set blackbox_device = SPIFLASH
set blackbox_rate_num = 1
set blackbox_rate_denom = 100  # Adjust based on field count
set debug_mode = POS_EST
set blackbox_arm_control = 0   # Log only while armed (NOT -1)
save
```

## Automated Testing Script (Recommended)

For reproducible tests without manual intervention:

```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps

# Run complete automated test
./run_20field_test.sh /dev/ttyACM0 5

# This script:
# 1. Configures blackbox settings (rate_denom=100, arm_control=0)
# 2. Waits for FC to reboot into normal MSP mode
# 3. Erases blackbox flash
# 4. Runs test with proper arm/disarm sequence
# 5. Does NOT verify settings (avoids CLI mode issue)
```

## Disable Fields by Changing Conditions
To debug fields, comment out or disable suspect fields.
This method prevents fields from being logged by changing their `CONDITION()` from `ALWAYS` to `NEVER`.

### Step 1: Comment out or Modify Field Definitions

Edit `inav/src/main/blackbox/blackbox.c`:

```bash
cd /home/raymorris/Documents/planes/inavflight/inav/src/main/blackbox
```

**To disable specific fields:**
```bash
# Example: Disable all axis PID fields
sed -i '/axisRate.*CONDITION(ALWAYS)/s/CONDITION(ALWAYS)/CONDITION(NEVER)/' blackbox.c
sed -i '/axisP.*CONDITION(ALWAYS)/s/CONDITION(ALWAYS)/CONDITION(NEVER)/' blackbox.c
sed -i '/axisI.*CONDITION(ALWAYS)/s/CONDITION(ALWAYS)/CONDITION(NEVER)/' blackbox.c
sed -i '/axisD.*CONDITION(ALWAYS)/s/CONDITION(ALWAYS)/CONDITION(NEVER)/' blackbox.c
```

Or just comment them out, if you can!

**To disable ALL fields except specific ones:**
```bash
# Disable all ALWAYS conditions
sed -i '207,398s/CONDITION(ALWAYS)/CONDITION(NEVER)/g' blackbox.c

# Re-enable only the fields you want (example: loopIteration and time)
sed -i '207s/CONDITION(NEVER)/CONDITION(ALWAYS)/' blackbox.c  # loopIteration
sed -i '209s/CONDITION(NEVER)/CONDITION(ALWAYS)/' blackbox.c  # time
```

Or just comment them out, if you can!


**Verify changes:**
```bash
grep -n "CONDITION(ALWAYS)" blackbox.c | head -20
```

### Step 2: Build Firmware

```bash
cd /home/raymorris/Documents/planes/inavflight/inav/build
make JHEMCUF435  # Or your target name
```

**Check build success:**
```bash
ls -lh inav_9.0.0_JHEMCUF435.hex
```

### Step 3: Flash Firmware

**Option A: Using the flash-firmware-dfu skill**
```bash
cd /home/raymorris/Documents/planes/inavflight/inav/build

# Reboot to DFU mode
../../.claude/skills/flash-firmware-dfu/reboot-to-dfu.py /dev/ttyACM0

# Convert hex to bin
arm-none-eabi-objcopy -I ihex inav_9.0.0_JHEMCUF435.hex -O binary inav_9.0.0_JHEMCUF435.bin

# Flash (AT32 chips use device ID 2e3c:df11, STM32 use 0483:df11)
dfu-util -d 2e3c:df11 --alt 0 -s 0x08000000:force:leave -D inav_9.0.0_JHEMCUF435.bin
```

**Option B: Using automation**
```bash
/claude/skills/flash-firmware-dfu JHEMCUF435
```

**Wait for FC to boot:**
```bash
for i in {1..10}; do
  sleep 1
  if ls /dev/ttyACM0 2>/dev/null; then
    echo "✓ FC online after $i seconds"
    break
  fi
done
```

### Step 4: Erase Blackbox Flash

**CRITICAL:** The blackbox flash must be erased between tests to ensure old data doesn't interfere.

**⚠️ WARNING:** CLI `flash_erase` erases ALL flash (settings + blackbox)! DO NOT USE!

**Method A: MSP Dataflash Erase (RECOMMENDED)**
```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps

# Erase ONLY blackbox data using MSP code 72 (preserves settings)
python3 -c "
from mspapi2 import MSPApi
import time
api = MSPApi(port='/dev/ttyACM0')
api.open()
time.sleep(0.5)
api._serial.request(72)  # MSP_DATAFLASH_ERASE
print('✓ Blackbox flash erased (settings preserved)')
api.close()
"
```

**Method B: INAV Configurator GUI**
1. Connect to FC
2. Go to "Onboard Logging" tab
3. Click "Erase Flash" - Uses MSP_DATAFLASH_ERASE (settings preserved)

**Method C: Automatic overwrite**
- Generate 60+ seconds of new data to completely fill flash
- Old headers will be overwritten naturally
- Safest method if unsure

**Method D: MSC mode + manual delete**
```bash
.claude/skills/flash-firmware-dfu/fc-cli.py "msc" /dev/ttyACM0
# Delete .TXT files from mounted flash, then reboot
```

**DO NOT USE:** `flash_erase` CLI command - Erases ALL settings including calibration!

### Step 5: Generate Test Data

The FC needs to arm and run to generate blackbox data.

**Option A: Use continuous MSP RC sender (no HITL)**
```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps

# This script arms the FC and sends continuous RC data
python3 continuous_msp_rc_sender.py /dev/ttyACM0
```

**Option B: Manual arming with configurator**
1. Configure ARM switch in configurator
2. Connect radio receiver
3. Arm and move sticks

**For consistent test data:** Use the MSP RC sender - it generates identical RC patterns each time.

### Step 6: Download Blackbox Log

**Method A: MSP Download (PREFERRED)**
```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps

# Download using MSP protocol - works while FC is running
python3 download_blackbox_from_fc.py /dev/ttyACM0 test_results/blackbox_test_$(date +%Y%m%d_%H%M%S).TXT
```

**Method B: MSC Mode (if MSP fails)**
```bash
# Enter MSC mode
.claude/skills/flash-firmware-dfu/fc-cli.py "msc" /dev/ttyACM0

# Wait for flash to mount (usually auto-mounts to /media/$USER/ or /tmp/)
# Copy .TXT files from mount point
cp /path/to/mount/*.TXT test_results/

# Reboot FC
```

**Verify download:**
```bash
ls -lh test_results/blackbox_test_*.TXT
head -5 test_results/blackbox_test_*.TXT  # Check header
```

### Step 7: Decode and Analyze

```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps

# Decode the log
~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode test_results/blackbox_test_*.TXT

# Check for decode failures
~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode test_results/blackbox_test_*.TXT 2>&1 | grep "frames failed"

# Debug mode (verbose output)
~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode --debug test_results/blackbox_test_*.TXT 2>&1 | head -100
```

**Check which fields were actually logged:**
```bash
head -1 test_results/blackbox_test_*.01.csv | tr ',' '\n' | nl
```

### Step 8: Restore Original Code

```bash
cd /home/raymorris/Documents/planes/inavflight/inav
git restore src/main/blackbox/blackbox.c
```

## Method 3: Automated Testing Script

### Create Test Automation Script

```bash
cat > /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps/run_field_test.sh << 'EOF'
#!/bin/bash
# Automated blackbox field testing

set -e

TEST_NAME="$1"
TARGET="${2:-JHEMCUF435}"
DEVICE="${3:-/dev/ttyACM0}"

if [ -z "$TEST_NAME" ]; then
    echo "Usage: $0 <test_name> [target] [device]"
    echo "Example: $0 minimal_2fields JHEMCUF435 /dev/ttyACM0"
    exit 1
fi

echo "=== Blackbox Field Test: $TEST_NAME ==="
echo "Target: $TARGET"
echo "Device: $DEVICE"

# Step 1: Build firmware
echo "Building firmware..."
cd /home/raymorris/Documents/planes/inavflight/inav/build
make $TARGET

# Step 2: Flash firmware
echo "Flashing firmware..."
../../.claude/skills/flash-firmware-dfu/reboot-to-dfu.py $DEVICE
sleep 2
arm-none-eabi-objcopy -I ihex inav_9.0.0_${TARGET}.hex -O binary inav_9.0.0_${TARGET}.bin

# Detect DFU device ID (AT32 vs STM32)
if dfu-util -l | grep -q "2e3c:df11"; then
    DFU_ID="2e3c:df11"
else
    DFU_ID="0483:df11"
fi

dfu-util -d $DFU_ID --alt 0 -s 0x08000000:force:leave -D inav_9.0.0_${TARGET}.bin

# Step 3: Wait for FC to boot
echo "Waiting for FC to boot..."
for i in {1..15}; do
    sleep 1
    if ls $DEVICE 2>/dev/null; then
        echo "✓ FC online after $i seconds"
        break
    fi
done

# Step 4: Generate test data
echo "Generating test data (15 seconds)..."
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps
timeout 15 python3 continuous_msp_rc_sender.py $DEVICE || true

# Step 5: Download blackbox
echo "Downloading blackbox log..."
OUTPUT_FILE="test_results/blackbox_${TEST_NAME}_$(date +%Y%m%d_%H%M%S).TXT"
python3 download_blackbox_from_fc.py $DEVICE $OUTPUT_FILE

# Step 6: Decode and check
echo "Decoding log..."
~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode $OUTPUT_FILE

echo "=== Test Results ==="
~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode $OUTPUT_FILE 2>&1 | grep -E "frames failed|Done"

echo ""
echo "✓ Test complete: $OUTPUT_FILE"
echo "Fields logged:"
head -1 ${OUTPUT_FILE%.TXT}.01.csv | tr ',' '\n' | wc -l
EOF

chmod +x /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps/run_field_test.sh
```

**Usage:**
```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps

# After modifying blackbox.c to disable fields:
./run_field_test.sh "my_test_name" JHEMCUF435 /dev/ttyACM0
```

## Common Field Modifications for Testing

### Test 1: Only Time Field
```bash
sed -i '207,398s/CONDITION(ALWAYS)/CONDITION(NEVER)/g' blackbox.c
sed -i '207s/CONDITION(NEVER)/CONDITION(ALWAYS)/' blackbox.c  # loopIteration
sed -i '209s/CONDITION(NEVER)/CONDITION(ALWAYS)/' blackbox.c  # time
```

### Test 2: Only PID Fields
```bash
sed -i '207,398s/CONDITION(ALWAYS)/CONDITION(NEVER)/g' blackbox.c
sed -i '207,225s/CONDITION(NEVER)/CONDITION(ALWAYS)/g' blackbox.c  # loopIteration, time, PID fields
```

### Test 3: Disable Navigation Fields Only
```bash
sed -i '/nav.*CONDITION(ALWAYS)/s/CONDITION(ALWAYS)/CONDITION(NEVER)/g' blackbox.c
```

### Test 4: Only RC Data
```bash
sed -i '207,398s/CONDITION(ALWAYS)/CONDITION(NEVER)/g' blackbox.c
sed -i '207s/CONDITION(NEVER)/CONDITION(ALWAYS)/' blackbox.c  # loopIteration
sed -i '209s/CONDITION(NEVER)/CONDITION(ALWAYS)/' blackbox.c  # time
sed -i '/rcData.*CONDITION/s/CONDITION(NEVER)/CONDITION(ALWAYS)/' blackbox.c
sed -i '/rcCommand.*CONDITION/s/CONDITION(NEVER)/CONDITION(ALWAYS)/' blackbox.c
```

## Troubleshooting

### Issue: Flash Not Erased Between Tests

**Symptom:** Old fields appear in new log despite being disabled

**Solution:**
- Verify erase completed (check Configurator "Free Space" increases to 100%)
- Generate enough data to overwrite old log (run continuous RC sender longer)
- Use physical flash chip erase if available

### Issue: FC Won't Arm

**Symptom:** No blackbox data generated

**Solution:**
```bash
# Check arming blockers
.claude/skills/flash-firmware-dfu/fc-cli.py "status" /dev/ttyACM0 | grep -i arm

# Use MSP RC sender which bypasses many arming checks
python3 continuous_msp_rc_sender.py /dev/ttyACM0
```

### Issue: Build Fails After Modifications

**Symptom:** Compiler errors about missing fields or syntax

**Solution:**
```bash
# Restore and start over
git restore src/main/blackbox/blackbox.c

# Check for syntax errors in your sed commands
# Don't modify write functions - only CONDITION() in field definitions
```

### Issue: Header Shows All Fields But Log Contains Few

**Symptom:** Field header lists 78 fields but CSV only has 2 columns

**Solution:**
- This is CORRECT behavior when using CONDITION(NEVER)
- The field definitions remain in the array (for decoder compatibility)
- But the CONDITION determines what actually gets logged
- Check the I-frame encoding count: `grep "Field I encoding" log.TXT`

### Issue: DFU Device Not Found

**Symptom:** `dfu-util: No DFU capable USB device found`

**Solution:**
```bash
# Check if FC entered DFU mode
dfu-util -l

# Try manual DFU entry: Hold BOOT button while plugging USB
# Then run: dfu-util -l

# Check device ID (AT32 uses 2e3c:df11, STM32 uses 0483:df11)
lsusb | grep -i "DFU\|STM\|AT32"
```

## Quick Reference Commands

```bash
# Disable all fields except loopIteration and time
cd /home/raymorris/Documents/planes/inavflight/inav/src/main/blackbox
sed -i '207,398s/CONDITION(ALWAYS)/CONDITION(NEVER)/g' blackbox.c
sed -i '207s/CONDITION(NEVER)/CONDITION(ALWAYS)/' blackbox.c
sed -i '209s/CONDITION(NEVER)/CONDITION(ALWAYS)/' blackbox.c

# Build
cd ../../../build && make JHEMCUF435

# Flash
../../.claude/skills/flash-firmware-dfu/reboot-to-dfu.py /dev/ttyACM0
arm-none-eabi-objcopy -I ihex inav_9.0.0_JHEMCUF435.hex -O binary inav_9.0.0_JHEMCUF435.bin
dfu-util -d 2e3c:df11 --alt 0 -s 0x08000000:force:leave -D inav_9.0.0_JHEMCUF435.bin

# Generate data
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps
timeout 15 python3 continuous_msp_rc_sender.py /dev/ttyACM0

# Download and test
python3 download_blackbox_from_fc.py /dev/ttyACM0 test_results/test.TXT
~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode test_results/test.TXT 2>&1 | grep "frames failed"

# Restore
cd /home/raymorris/Documents/planes/inavflight/inav
git restore src/main/blackbox/blackbox.c
```

## References

- Field definitions: `inav/src/main/blackbox/blackbox.c` lines 205-398
- Write functions: `writeIntraframe()` (line ~852), `writeInterframe()` (line ~1091)
- Flash skill: `.claude/skills/flash-firmware-dfu/`
- Test tools: `claude/test_tools/inav/gps/`
