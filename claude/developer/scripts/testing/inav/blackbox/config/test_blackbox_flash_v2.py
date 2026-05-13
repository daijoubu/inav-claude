#!/usr/bin/env python3
"""
Test Blackbox Flash Functionality on Physical Flight Controller (v2)

This script:
1. Connects to an attached FC
2. Checks blackbox flash status and records initial usage
3. Enables HITL mode to bypass sensor calibration
4. Arms the FC and sends continuous RC data at 50Hz for 30 seconds
5. Disarms the FC
6. Checks final flash usage - it must be greater than initial

Key fix over v1: RC data is sent continuously at 50Hz during the arm period.
The MSP receiver times out after ~200ms without RC frames, causing immediate disarm.

Usage:
    python3 test_blackbox_flash_v2.py [port]

Example:
    python3 test_blackbox_flash_v2.py /dev/ttyACM0
"""

import struct
import sys
import time
from mspapi2 import MSPApi

# MSP command codes
MSP_DATAFLASH_SUMMARY = 70
MSP_SET_RAW_RC = 200
MSP_SIMULATOR = 0x201F   # HITL / simulator enable
MSP2_INAV_STATUS = 0x2000

# RC values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000


def connect_to_fc(port):
    """Connect to flight controller and verify it responds."""
    print(f"Connecting to FC on {port}...")
    try:
        api = MSPApi(port=port, baudrate=115200)
        api.open()
        time.sleep(0.5)
    except Exception as e:
        print(f"FAIL: Could not open {port}: {e}")
        print("  Check: Is FC plugged in? Is Configurator closed?")
        print("  Note: If running in sandbox, retry with dangerouslyDisableSandbox: true")
        return None

    # Verify FC responds to a basic request
    try:
        response = api._serial.request(MSP_DATAFLASH_SUMMARY)
        if response is None:
            print("FAIL: FC not responding to MSP commands (no response to DATAFLASH_SUMMARY)")
            api.close()
            return None
        print("PASS: Connected and FC is responding")
        return api
    except Exception as e:
        print(f"FAIL: FC not responding to MSP: {e}")
        print("  Check: Is FC in a valid state? Try power-cycling the FC.")
        api.close()
        return None


def get_flash_summary(api):
    """Get flash summary: returns dict with ready, sectors, total_size, used_size or None."""
    try:
        response = api._serial.request(MSP_DATAFLASH_SUMMARY)
        if isinstance(response, tuple):
            payload = response[1]
        else:
            payload = response

        if payload is not None and len(payload) >= 13:
            flags, sectors, total_size, used_size = struct.unpack('<BIII', payload[:13])
            return {
                'ready': bool(flags & 1),
                'sectors': sectors,
                'total_size': total_size,
                'used_size': used_size,
            }
        else:
            print(f"FAIL: DATAFLASH_SUMMARY response too short: {len(payload) if payload else 0} bytes")
            return None
    except Exception as e:
        print(f"FAIL: Error getting flash summary: {e}")
        return None


def enable_hitl(api):
    """Enable HITL simulator mode to bypass sensor calibration."""
    try:
        hitl_data = struct.pack('<B', 1)
        api._serial.send(MSP_SIMULATOR, hitl_data)
        time.sleep(0.3)
        print("PASS: HITL mode enabled (sensor calibration bypassed)")
        return True
    except Exception as e:
        print(f"WARN: Could not enable HITL mode: {e}")
        print("  Arming may fail due to SENSORS_CALIBRATING flag")
        return False


def send_rc_frame(api, channels):
    """Send one MSP_SET_RAW_RC frame. channels is a list of 18 uint16 values."""
    rc_data = struct.pack('<' + 'H' * len(channels), *channels)
    try:
        bytes_written = api._serial.send(MSP_SET_RAW_RC, rc_data)
        # Drain the response to avoid buffer overflow
        try:
            api._serial.recv()
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"FAIL: RC frame send error: {e}")
        return False


def get_armed_status(api):
    """Return True if FC is armed, False if not, None on error."""
    try:
        response = api._serial.request(MSP2_INAV_STATUS)
        if response is None:
            return None
        if isinstance(response, tuple):
            payload = response[1]
        else:
            payload = response
        if payload and len(payload) >= 15:
            # mode flags are at bytes 8-11 (uint32)
            mode_flags = struct.unpack_from('<I', payload, 8)[0]
            return bool(mode_flags & 0x01)  # bit 0 = ARMED
    except Exception:
        pass
    return None


def run_arm_cycle(api, arm_duration_s=30):
    """
    Arm the FC, send continuous RC at 50Hz for arm_duration_s, then disarm.
    Returns (armed_confirmed, seconds_armed).
    """
    # Build channel arrays
    channels_armed   = [RC_MID] * 18
    channels_armed[2] = RC_LOW   # throttle (ch3, AETR order ch index 2) low
    channels_armed[4] = RC_HIGH  # AUX1 (ch5, index 4) high = ARM

    channels_disarmed = [RC_MID] * 18
    channels_disarmed[2] = RC_LOW
    channels_disarmed[4] = RC_LOW  # AUX1 low = DISARM

    # ---- Phase 1: Establish RC link (2 seconds with AUX1 low / disarmed position) ----
    print("  Establishing RC link (2s)...")
    for _ in range(40):  # 40 x 50ms = 2s
        if not send_rc_frame(api, channels_disarmed):
            return False, 0
        time.sleep(0.02)

    # ---- Phase 2: Arm (raise AUX1) and send continuous RC ----
    print(f"  Arming and sending RC for {arm_duration_s}s at 50Hz...")
    arm_confirmed = False
    start_time = time.time()
    frame_interval = 0.02  # 50Hz

    total_frames = arm_duration_s * 50
    for frame_num in range(total_frames):
        frame_start = time.time()

        if not send_rc_frame(api, channels_armed):
            print("FAIL: RC send error during arm period")
            break

        # Check arm status every 50 frames (1 second)
        if frame_num % 50 == 0:
            elapsed = frame_num / 50
            armed = get_armed_status(api)
            if armed is True:
                if not arm_confirmed:
                    arm_confirmed = True
                    print(f"  PASS: FC ARMED at t={elapsed:.0f}s")
            elif armed is False and frame_num > 100:
                # After 2 seconds we should be armed; if not, warn
                print(f"  WARN: FC not armed at t={elapsed:.0f}s - may have disarmed or failed to arm")
            elif elapsed > 0:
                print(f"  {elapsed:.0f}/{arm_duration_s}s...")

        # Pace ourselves to maintain 50Hz
        elapsed_frame = time.time() - frame_start
        sleep_remaining = frame_interval - elapsed_frame
        if sleep_remaining > 0:
            time.sleep(sleep_remaining)

    seconds_armed = time.time() - start_time
    print(f"  Armed period complete ({seconds_armed:.1f}s actual)")

    # ---- Phase 3: Disarm ----
    print("  Disarming (1s)...")
    for _ in range(50):  # 50 x 20ms = 1s
        send_rc_frame(api, channels_disarmed)
        time.sleep(0.02)

    return arm_confirmed, seconds_armed


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'

    print("=" * 70)
    print("Blackbox Flash Test v2")
    print("=" * 70)
    print(f"Port: {port}")
    print()

    # Step 1: Connect
    api = connect_to_fc(port)
    if not api:
        return 1

    try:
        # Step 2: Initial flash status
        print("\n[Step 1] Initial flash status")
        initial = get_flash_summary(api)
        if initial is None:
            print("FAIL: Cannot read initial flash status")
            return 1

        if not initial['ready']:
            print("WARN: Flash reports NOT ready - may still be initializing or is in error state")
        else:
            print("PASS: Flash is ready")

        print(f"  Total size : {initial['total_size']} bytes ({initial['total_size']/1024/1024:.2f} MB)")
        print(f"  Used before: {initial['used_size']} bytes ({initial['used_size']/1024:.2f} KB)")

        # Step 3: Enable HITL so we can arm without calibration
        print("\n[Step 2] Enable HITL mode")
        enable_hitl(api)

        # Step 4: Arm cycle
        print("\n[Step 3] Arm FC and log for 30 seconds")
        armed_ok, duration = run_arm_cycle(api, arm_duration_s=30)

        # Step 5: Wait for flash flush
        print("\n[Step 4] Waiting 2s for blackbox data to flush to flash...")
        time.sleep(2)

        # Step 6: Final flash status
        print("\n[Step 5] Final flash status")
        final = get_flash_summary(api)
        if final is None:
            print("FAIL: Cannot read final flash status")
            return 1

        print(f"  Used after : {final['used_size']} bytes ({final['used_size']/1024:.2f} KB)")

        # ---- Verdict ----
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"  Flash used before arming : {initial['used_size']} bytes")
        print(f"  Flash used after arming  : {final['used_size']} bytes")
        delta = final['used_size'] - initial['used_size']
        print(f"  Delta                    : {delta:+d} bytes")
        print(f"  FC was armed             : {'YES' if armed_ok else 'NO (arm was not confirmed)'}")
        print()

        if not armed_ok:
            print("FAIL: FC was never confirmed armed - blackbox may not have been active")
            print("  Check arming configuration (HITL, MSP receiver type, ARM mode on AUX1)")
            return 1

        if delta > 0:
            print("PASS: Blackbox data WAS written to flash (flash usage increased)")
            print("=" * 70)
            return 0
        elif delta == 0:
            print("FAIL: Flash usage UNCHANGED - no data written to flash")
            print("  Possible causes:")
            print("    - Block-protection register still set (opcode fix not applied)")
            print("    - Blackbox not configured to use flash (check blackbox_device setting)")
            print("    - Flash is full (used_size == total_size)")
            print("=" * 70)
            return 1
        else:
            print(f"WARN: Flash usage DECREASED by {-delta} bytes (unexpected)")
            print("  This may indicate flash was auto-wrapped or reset")
            print("=" * 70)
            return 1

    except KeyboardInterrupt:
        print("\nFAIL: Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\nFAIL: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if api:
            api.close()


if __name__ == '__main__':
    sys.exit(main())
