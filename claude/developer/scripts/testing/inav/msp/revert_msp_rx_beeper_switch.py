#!/usr/bin/env python3
"""
Revert the changes made by setup_msp_rx_beeper_switch.py: restore the
original MSP_RX_CONFIG (byte-for-byte, from the backup file written at setup
time) and clear the mode range slot back to all-zero (its original state,
confirmed empty before setup). Save + reboot + verify.

Looks for backup files (original_rx_config.hex, original_mode_range_slot<N>.hex)
in `backup_dir` (default: current working directory -- pass the same
directory you ran setup_msp_rx_beeper_switch.py's backups into, e.g. your
task workspace directory, not this shared scripts/ location).

Usage:
    revert_msp_rx_beeper_switch.py [port] [backup_dir] [mode_range_slot]
"""
import sys
import os

from pathlib import Path

# Locate the mspapi2 library. Lookup order:
#   1. $MSPAPI2_PATH env var (canonical override)
#   2. <inav-claude-parent>/mspapi2 (sibling checkout convention)
#   3. ~/Documents/planes/inavflight/mspapi2 (legacy location)
_MSPAPI2_CANDIDATES = [
    os.environ.get("MSPAPI2_PATH"),
    str(Path(__file__).resolve().parents[6] / "mspapi2"),
    os.path.expanduser("~/Documents/planes/inavflight/mspapi2"),
]
for _candidate in _MSPAPI2_CANDIDATES:
    if _candidate and os.path.isdir(os.path.join(_candidate, "mspapi2")):
        if _candidate not in sys.path:
            sys.path.insert(0, _candidate)
        break

from mspapi2 import InavMSP  # noqa: E402
from msp_helpers import open_and_check, save_and_reboot  # noqa: E402

DEFAULT_MODE_RANGE_SLOT = 1


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
    backup_dir = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    mode_range_slot = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_MODE_RANGE_SLOT

    rx_config_backup = os.path.join(backup_dir, "original_rx_config.hex")
    mode_range_backup = os.path.join(backup_dir, f"original_mode_range_slot{mode_range_slot}.hex")

    if not os.path.exists(rx_config_backup) or not os.path.exists(mode_range_backup):
        print(f"FAILED: backup files not found in {backup_dir}. "
              f"Expected {rx_config_backup} and {mode_range_backup}. "
              f"Cannot safely revert without the original captured values.")
        return 1

    with open(rx_config_backup, "rb") as f:
        original_rx = f.read()
    with open(mode_range_backup, "rb") as f:
        original_slot1 = f.read()

    if len(original_rx) != 24 or len(original_slot1) != 4:
        print(f"FAILED: backup files have unexpected length "
              f"(rx={len(original_rx)}, slot1={len(original_slot1)}). Aborting.")
        return 1

    print(f"Will restore MSP_RX_CONFIG to {original_rx.hex()}")
    print(f"Will restore mode range slot {mode_range_slot} to {original_slot1.hex()}")

    api = open_and_check(port, label="revert")
    if api is None:
        return 1

    # --- Restore RX config exactly ---
    try:
        info, resp = api._request_raw(InavMSP.MSP_SET_RX_CONFIG, original_rx, timeout=1.0)
        print(f"MSP_SET_RX_CONFIG ACK ({len(resp)} bytes) -- restored in RAM")
    except Exception as e:
        print(f"FAILED to send MSP_SET_RX_CONFIG: {e}")
        api.close()
        return 1

    # --- Restore mode range slot to all-zero (permanentId=0/ARM, aux=0, 0-0) ---
    mode_range_payload = bytes([mode_range_slot, 0, 0, 0, 0])
    try:
        info, resp = api._request_raw(InavMSP.MSP_SET_MODE_RANGE, mode_range_payload, timeout=1.0)
        print(f"MSP_SET_MODE_RANGE ACK ({len(resp)} bytes) -- slot {mode_range_slot} cleared in RAM")
    except Exception as e:
        print(f"FAILED to send MSP_SET_MODE_RANGE: {e}")
        api.close()
        return 1

    api2 = save_and_reboot(api, port)
    if api2 is None:
        return 1

    ok = True
    try:
        info, rx_raw2 = api2._request_raw(InavMSP.MSP_RX_CONFIG, b"", timeout=1.0)
        if rx_raw2 == original_rx:
            print(f"VERIFY OK: MSP_RX_CONFIG fully restored ({rx_raw2.hex()})")
        else:
            print(f"VERIFY FAILED: MSP_RX_CONFIG = {rx_raw2.hex()}, expected {original_rx.hex()}")
            ok = False
    except Exception as e:
        print(f"FAILED to verify MSP_RX_CONFIG post-reboot: {e}")
        ok = False

    try:
        info, mr_raw2 = api2._request_raw(InavMSP.MSP_MODE_RANGES, b"", timeout=1.0)
        slot1_2 = mr_raw2[mode_range_slot * 4:(mode_range_slot + 1) * 4]
        if slot1_2 == original_slot1:
            print(f"VERIFY OK: mode range slot {mode_range_slot} fully restored ({slot1_2.hex()})")
        else:
            print(f"VERIFY FAILED: mode range slot {mode_range_slot} = {slot1_2.hex()}, expected {original_slot1.hex()}")
            ok = False
    except Exception as e:
        print(f"FAILED to verify MSP_MODE_RANGES post-reboot: {e}")
        ok = False

    api2.close()
    if ok:
        print("\nRevert complete: RX config and mode ranges restored to their original state.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
