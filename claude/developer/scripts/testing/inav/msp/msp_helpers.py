"""
Shared helpers for the PR #11675 (BUZZER runtime timer output mode) hardware
verification scripts. MSP-only, no CLI.

All scripts in this directory operate on a BrotherHobby H743 FC connected at
/dev/ttyACM0, running maintenance-10.x with PR #11675 applied.
"""
import os
import sys
import time

sys.path.insert(0, "/home/raymorris/inavflight/mspapi2")
from mspapi2 import MSPApi, InavMSP  # noqa: E402


def open_and_check(port, baudrate=115200, label=""):
    """Open a connection and verify the FC responds to a harmless read-only
    query. Returns the MSPApi instance, or None on failure (with diagnostics
    printed)."""
    tag = f" ({label})" if label else ""
    print(f"Connecting to {port}{tag} ...")
    try:
        api = MSPApi(port=port, baudrate=baudrate)
        api.open()
    except Exception as e:
        print(f"FAILED to open serial port {port}: {e}")
        print("  Check: Is the FC plugged in? Is the Configurator or another script "
              "already connected?")
        print("  If running in sandbox: retry with dangerouslyDisableSandbox: true")
        return None

    try:
        info, payload = api._request_raw(InavMSP.MSP_API_VERSION, b"", timeout=1.0)
        print(f"  Connected, FC responding OK ({len(payload)} bytes for MSP_API_VERSION)")
    except Exception as e:
        print(f"FAILED: FC not responding to MSP_API_VERSION: {e}")
        print("  FC may be stuck in CLI mode from a previous session -- that requires "
              "a power cycle / reset (CLI has no MSP-safe exit).")
        api.close()
        return None
    return api


def wait_for_port(port, timeout=15.0, stable_for=1.5, poll_interval=0.25):
    """
    Poll for the serial device node to reappear after a reboot, and require
    it to remain continuously present for `stable_for` seconds before
    declaring success. This avoids a race where the node flickers through a
    brief bootloader-then-application double-enumeration cycle (seen in
    practice on this H743 board) and a caller's open() call lands in the gap.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if os.path.exists(port):
            stable_since = time.time()
            still_there = True
            while time.time() - stable_since < stable_for:
                time.sleep(poll_interval)
                if not os.path.exists(port):
                    still_there = False
                    break
            if still_there:
                return True
            # else: node disappeared again mid-stability-check, keep polling
        else:
            time.sleep(poll_interval)
    return False


def save_and_reboot(api, port, baudrate=115200, port_wait_timeout=15.0):
    """
    Send MSP_EEPROM_WRITE then MSP_REBOOT on an already-open `api`, close it,
    wait for the device node to reappear, and reconnect.

    Returns a new, connected MSPApi instance, or None on failure (with
    diagnostics printed). Caller is responsible for closing the returned api.
    """
    try:
        info, resp = api._request_raw(InavMSP.MSP_EEPROM_WRITE, b"", timeout=3.0)
        print(f"  MSP_EEPROM_WRITE ACK ({len(resp)} bytes) -- config saved to flash")
    except Exception as e:
        print(f"FAILED to send MSP_EEPROM_WRITE: {e}")
        return None

    print("  Sending MSP_REBOOT ...")
    try:
        api._request_raw(InavMSP.MSP_REBOOT, b"", timeout=1.0)
        print("  MSP_REBOOT ACK received, FC rebooting.")
    except Exception as e:
        print(f"  (No ACK read for MSP_REBOOT -- expected if reboot raced the reply: {e})")
    api.close()

    print(f"  Waiting for {port} to reappear ...")
    if not wait_for_port(port, timeout=port_wait_timeout):
        print(f"FAILED: {port} did not reappear within {port_wait_timeout}s after reboot.")
        print("  Check USB connection; the FC may need a manual power cycle.")
        return None
    print(f"  {port} is back.")

    new_api = None
    for attempt in range(20):
        try:
            new_api = MSPApi(port=port, baudrate=baudrate)
            new_api.open()
            info, payload = new_api._request_raw(InavMSP.MSP_API_VERSION, b"", timeout=1.0)
            print("  Reconnected, FC responding post-reboot.")
            return new_api
        except Exception:
            if new_api:
                try:
                    new_api.close()
                except Exception:
                    pass
            time.sleep(0.5)
    print("FAILED: FC did not respond to MSP after reboot (10 attempts over ~5s).")
    return None
