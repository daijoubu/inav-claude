#!/usr/bin/env python3
"""
Set a runtime timer-output-mode override via MSP, save to EEPROM, reboot the
FC, reconnect, and read the value back to confirm it stuck.

MSP-only (no CLI). Uses:
  - MSP2_INAV_SET_TIMER_OUTPUT_MODE (0x200F): payload = [timerIndex, outputMode]
    (fc_msp.c: dataSize must be exactly 2 -- single timer per call, in-RAM only)
  - MSP_EEPROM_WRITE (250): persists config to flash (writeEEPROM(); readEEPROM();)
  - MSP_REBOOT (68): reboots the FC (required -- timerHardwareOverride() /
    pwmBuildTimerOutputList() only re-applies the override at boot, in
    pwm_mapping.c / drivers/sound_beeper.c beeperInit())
  - MSP2_INAV_TIMER_OUTPUT_MODE (0x200E): read back (dataSize==1 -> single
    timer query) after reboot to confirm.

outputMode values (flight/mixer.h outputMode_e):
  0=AUTO 1=MOTORS 2=SERVOS 3=LED 4=PINIO 5=BEEPER

Usage:
    apply_timer_override.py <port> <timer_index> <output_mode>

Example (set TIM2/PA15 to explicit BEEPER):
    apply_timer_override.py /dev/ttyACM0 1 5

Example (revert TIM2/PA15 to AUTO):
    apply_timer_override.py /dev/ttyACM0 1 0
"""
import sys
import time
import os

sys.path.insert(0, "/home/raymorris/inavflight/mspapi2")
from mspapi2 import MSPApi, InavMSP  # noqa: E402

MODE_NAMES = {0: "AUTO", 1: "MOTORS", 2: "SERVOS", 3: "LED", 4: "PINIO", 5: "BEEPER"}


def wait_for_port(port, timeout=15.0):
    """Poll for the serial device node to reappear after reboot."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if os.path.exists(port):
            # Give the OS/USB stack a moment to finish enumerating.
            time.sleep(1.5)
            return True
        time.sleep(0.25)
    return False


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <port> <timer_index> <output_mode>")
        return 2

    port = sys.argv[1]
    timer_index = int(sys.argv[2])
    output_mode = int(sys.argv[3])
    mode_name = MODE_NAMES.get(output_mode, f"unknown({output_mode})")

    print(f"Target: port={port} timerIndex={timer_index} outputMode={output_mode} ({mode_name})")

    # --- Step 1: connect and sanity-check ---
    try:
        api = MSPApi(port=port, baudrate=115200)
        api.open()
    except Exception as e:
        print(f"FAILED to open serial port: {e}")
        print("  If running in sandbox: retry with dangerouslyDisableSandbox: true")
        return 1

    try:
        info, payload = api._request_raw(InavMSP.MSP_API_VERSION, b"", timeout=1.0)
        print(f"Connected, FC responding OK ({len(payload)} bytes for MSP_API_VERSION)")
    except Exception as e:
        print(f"FAILED: FC not responding to MSP_API_VERSION: {e}")
        print("  FC may be stuck in CLI mode from a previous session -- requires "
              "power cycle / reset, CLI has no MSP-safe exit.")
        api.close()
        return 1

    # --- Step 2: SET the override (in-RAM only at this point) ---
    try:
        set_payload = bytes([timer_index & 0xFF, output_mode & 0xFF])
        info, resp = api._request_raw(InavMSP.MSP2_INAV_SET_TIMER_OUTPUT_MODE, set_payload, timeout=1.0)
        print(f"MSP2_INAV_SET_TIMER_OUTPUT_MODE ACK ({len(resp)} bytes) -- set in RAM")
    except Exception as e:
        print(f"FAILED to send MSP2_INAV_SET_TIMER_OUTPUT_MODE: {e}")
        api.close()
        return 1

    # Sanity: read back (still in RAM, pre-reboot) to make sure the SET landed
    # before we commit to EEPROM_WRITE + REBOOT.
    try:
        query_payload = bytes([timer_index & 0xFF])
        info, resp = api._request_raw(InavMSP.MSP2_INAV_TIMER_OUTPUT_MODE, query_payload, timeout=1.0)
        if len(resp) == 2 and resp[0] == timer_index and resp[1] == output_mode:
            print(f"Pre-reboot RAM readback OK: timerIndex={resp[0]} outputMode={resp[1]} ({MODE_NAMES.get(resp[1], '?')})")
        else:
            print(f"FAILED: pre-reboot readback mismatch, got raw bytes {list(resp)}, "
                  f"expected [{timer_index}, {output_mode}]")
            api.close()
            return 1
    except Exception as e:
        print(f"FAILED to read back MSP2_INAV_TIMER_OUTPUT_MODE: {e}")
        api.close()
        return 1

    # --- Step 3: persist to EEPROM ---
    try:
        info, resp = api._request_raw(InavMSP.MSP_EEPROM_WRITE, b"", timeout=3.0)
        print(f"MSP_EEPROM_WRITE ACK ({len(resp)} bytes) -- config saved to flash")
    except Exception as e:
        print(f"FAILED to send MSP_EEPROM_WRITE: {e}")
        api.close()
        return 1

    # --- Step 4: reboot (fire-and-forget; FC replies then reboots via
    # mspPostProcessFn, so a read timeout here is expected/harmless) ---
    print("Sending MSP_REBOOT ...")
    try:
        api._request_raw(InavMSP.MSP_REBOOT, b"", timeout=1.0)
        print("MSP_REBOOT ACK received, FC rebooting.")
    except Exception as e:
        print(f"(No ACK read for MSP_REBOOT -- expected if reboot raced the reply: {e})")
    api.close()

    # --- Step 5: wait for device to re-enumerate and reconnect ---
    print(f"Waiting for {port} to reappear ...")
    if not wait_for_port(port, timeout=15.0):
        print(f"FAILED: {port} did not reappear within 15s after reboot.")
        print("  Check USB connection; the FC may need a manual power cycle.")
        return 1
    print(f"{port} is back.")

    try:
        api2 = MSPApi(port=port, baudrate=115200)
        api2.open()
    except Exception as e:
        print(f"FAILED to reopen serial port after reboot: {e}")
        return 1

    # Give firmware a moment to finish booting / init MSP.
    connected = False
    for attempt in range(10):
        try:
            info, payload = api2._request_raw(InavMSP.MSP_API_VERSION, b"", timeout=1.0)
            connected = True
            break
        except Exception:
            time.sleep(0.5)
    if not connected:
        print("FAILED: FC did not respond to MSP after reboot (10 attempts over ~5s).")
        api2.close()
        return 1
    print("Reconnected, FC responding post-reboot.")

    # --- Step 6: verify persisted value via read-only query ---
    try:
        query_payload = bytes([timer_index & 0xFF])
        info, resp = api2._request_raw(InavMSP.MSP2_INAV_TIMER_OUTPUT_MODE, query_payload, timeout=1.0)
        if len(resp) == 2 and resp[0] == timer_index and resp[1] == output_mode:
            print(f"POST-REBOOT VERIFY OK: timerIndex={resp[0]} outputMode={resp[1]} ({MODE_NAMES.get(resp[1], '?')})")
            result = 0
        else:
            print(f"VERIFY FAILED: got raw bytes {list(resp)}, expected [{timer_index}, {output_mode}]")
            result = 1
    except Exception as e:
        print(f"FAILED to verify post-reboot: {e}")
        result = 1

    api2.close()
    return result


if __name__ == "__main__":
    sys.exit(main())
