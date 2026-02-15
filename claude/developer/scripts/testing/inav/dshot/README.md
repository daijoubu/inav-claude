# DShot Testing Scripts

Test scripts for DShot motor control features, including the motor locate (beacon) functionality.

## Test Scripts

### test_motor_locate.py

Comprehensive test script for the `MSP2_INAV_MOTOR_LOCATE` command.

**Features:**
- Tests individual motors or all motors sequentially
- Verifies safety checks (armed state)
- Clear colored output with success/error indicators
- Comprehensive error handling and diagnostics
- Auto-stop after each test

**Usage:**
```bash
# Test motor 0 (default)
./test_motor_locate.py /dev/ttyACM0

# Test specific motor
./test_motor_locate.py /dev/ttyACM0 --motor 2

# Test all motors in sequence
./test_motor_locate.py /dev/ttyACM0 --all-motors

# Test with SITL
./test_motor_locate.py localhost:5760 --all-motors

# Test safety checks
./test_motor_locate.py /dev/ttyACM0 --test-safety
```

**Output:**
- ✓ Success (green)
- ✗ Error (red)
- ⚠ Warning (yellow)
- ℹ Info (blue)

### test_motor_locate_simple.py

Minimal test script for quick verification.

**Features:**
- No dependencies except mspapi2
- Minimal output
- Quick one-shot test

**Usage:**
```bash
# Test motor 0
python3 test_motor_locate_simple.py /dev/ttyACM0 0

# Test motor 2
python3 test_motor_locate_simple.py /dev/ttyACM0 2

# Stop all motors
python3 test_motor_locate_simple.py /dev/ttyACM0 255
```

## MSP2_INAV_MOTOR_LOCATE Protocol

**Command Code:** `0x2042`

**Payload:**
- 1 byte: motor index (0-based, or 255 to stop)

**Behavior:**
1. Validates FC is disarmed (required)
2. Validates DShot protocol is active (required)
3. Validates motor index is valid
4. Starts ~2 second sequence:
   - 100ms motor jerk at 12% throttle
   - 100ms pause
   - 4 ascending beeps (80ms on, 80ms off)
5. Auto-stops after sequence completes

**Safety:**
- Only works when disarmed
- Only works with DShot protocol
- Auto-stops if FC becomes armed during sequence
- Can be stopped early by sending motor_index=255

## Motor Locate Implementation

The firmware implementation is in:
- `/home/raymorris/Documents/planes/inavflight/inav/src/main/fc/motor_locate.c`
- `/home/raymorris/Documents/planes/inavflight/inav/src/main/fc/motor_locate.h`

**MSP handler** (incomplete, needs finishing):
- `/home/raymorris/Documents/planes/inavflight/inav/src/main/fc/fc_msp.c:3659`

## Testing Workflow

### 1. Physical Flight Controller

```bash
# Props OFF!
# FC disarmed
# DShot protocol configured

# Test single motor
./test_motor_locate.py /dev/ttyACM0 --motor 0

# Test all motors
./test_motor_locate.py /dev/ttyACM0 --all-motors
```

**Expected result:**
- Motor jerks briefly (you'll feel/hear it)
- 4 ascending beeps over ~2 seconds
- Motor stops automatically

### 2. SITL Testing

SITL doesn't have real ESCs, so you won't hear beeps. But you can:
- Verify the MSP command is accepted
- Check that safety checks work (armed/disarmed)
- Test the command protocol

```bash
# Start SITL first
cd ~/Documents/planes/inavflight
./claude/developer/scripts/testing/start_sitl.sh

# Test motor locate
./test_motor_locate.py localhost:5760 --motor 0
```

### 3. Configurator Testing

After verifying the firmware MSP command works, test the configurator:

1. Open configurator
2. Go to Mixer tab
3. Click "Motor Wizard" button (new)
4. Follow wizard flow
5. Verify motors beep when expected

## Troubleshooting

### "FC is ARMED - aborting!"

Motor locate only works when disarmed. Disarm the FC first.

### "Failed to connect"

- Check FC is plugged in
- Close INAV Configurator (conflicts with test script)
- Check serial port permissions: `sudo usermod -a -G dialout $USER`
- If in sandbox: retry with `dangerouslyDisableSandbox: true`

### "FC not responding"

- Verify cable connection
- Try power cycling the FC
- Check baudrate is correct (115200)

### No beeps heard

Check:
1. Is DShot protocol configured? (Check Configurator → Motors tab)
2. Are ESCs BLHeli_S or BLHeli_32? (Older ESCs may not support beacons)
3. Are ESC signal wires connected?
4. Battery connected? (ESCs need power to beep)
5. Is the MSP handler complete in fc_msp.c? (Check for commented code)

### Motors jerk but no beeps

The jerk works but DShot beacon commands aren't being sent. Check:
1. ESC firmware supports beacon commands (most modern ESCs do)
2. DShot protocol is actually active (not PWM/Oneshot)
3. Motor locate implementation is sending beacon commands correctly

## Reference: Betaflight Implementation

Betaflight's similar feature:
- Command: `MSP2_SEND_DSHOT_COMMAND` (different from INAV)
- Handler: `betaflight/src/main/msp/msp.c:3572`
- Supports command queue with multiple commands
- More complex protocol (commandType, motorIndex, commandCount, commands[])

INAV's simpler approach:
- Command: `MSP2_INAV_MOTOR_LOCATE`
- Just motor index (or 255 to stop)
- Handles timing/sequences in firmware
- Easier for configurator to use

## DShot Beacon Commands

From `inav/src/main/drivers/pwm_output.h`:

```c
typedef enum {
    DSHOT_CMD_MOTOR_STOP = 0,
    DSHOT_CMD_BEACON1 = 1,  // Lowest tone
    DSHOT_CMD_BEACON2 = 2,
    DSHOT_CMD_BEACON3 = 3,
    DSHOT_CMD_BEACON4 = 4,
    DSHOT_CMD_BEACON5 = 5,  // Highest tone
    // ... other commands
} dshotCommands_e;
```

Motor locate uses ascending tones (BEACON1→BEACON4) to help with directional hearing.

## Files Modified/Created

### Test Scripts (this directory)
- `test_motor_locate.py` - Comprehensive test script
- `test_motor_locate_simple.py` - Minimal test script
- `README.md` - This file

### Firmware (under development)
- `inav/src/main/fc/motor_locate.c` - Motor locate implementation (complete)
- `inav/src/main/fc/motor_locate.h` - Motor locate header (complete)
- `inav/src/main/fc/fc_msp.c:3659` - MSP handler (needs completion)
- `inav/src/main/msp/msp_protocol_v2_inav.h:96` - MSP2_INAV_MOTOR_LOCATE = 0x2042

### Configurator (planned)
- New motor wizard UI using this MSP command

---

## test_dshot_beeper_arming_loop_fix.py

**Purpose:** Verify the fix for the DShot beeper feedback loop issue.

**Problem:**
When unable to arm due to `ARMING_DISABLED_DSHOT_BEEPER`, the FC would beep on arming failure. This beep would trigger the DShot beeper, which would reset the guard delay timer, keeping the flag set and causing continuous beeping - a feedback loop that prevented arming.

**Fix:**
Modified `inav/src/main/fc/fc_core.c` line 599 to NOT beep when the ONLY arming blocker is `ARMING_DISABLED_DSHOT_BEEPER`:

```c
if (armingFlags & ~ARMING_DISABLED_DSHOT_BEEPER) {
    beeperConfirmationBeeps(1);
}
```

**Test Coverage:**
1. ✓ Arming DOES beep when blocked by real issues (GPS, calibration, etc.)
2. ✓ Arming does NOT beep when blocked ONLY by DSHOT_BEEPER
3. ✓ Feedback loop is broken (can arm after guard delay expires)
4. ✓ DShot beeper still works normally when not arming

**Usage:**
```bash
# Full test with physical FC
./test_dshot_beeper_arming_loop_fix.py /dev/ttyACM0

# Quick logical verification (no delays)
./test_dshot_beeper_arming_loop_fix.py /dev/ttyACM0 --quick

# Test with SITL
./test_dshot_beeper_arming_loop_fix.py localhost:5760 --quick
```

**Requirements:**
- FC with DShot protocol configured
- DShot beeper enabled
- FC must be DISARMED
- mspapi2 library installed

**Expected Output:**
```
======================================================================
Test Results Summary
======================================================================

✓ Test 1: Beeps on real issues: PASSED
✓ Test 2: No beep when only DSHOT_BEEPER: PASSED
✓ Test 3: Can arm after guard delay: PASSED
✓ Test 4: DShot beeper works normally: PASSED

Overall: 4/4 tests passed

🎉 ALL TESTS PASSED\!
ℹ The DShot beeper arming loop fix is working correctly
```

**Related Files:**
- Fix: `/home/raymorris/Documents/planes/inavflight/inav/src/main/fc/fc_core.c:599`
- Arming flags: `/home/raymorris/Documents/planes/inavflight/inav/src/main/fc/runtime_config.h`
- Beeper logic: `/home/raymorris/Documents/planes/inavflight/inav/src/main/io/beeper.c`

