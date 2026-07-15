#!/usr/bin/env python3
"""
Configure the FC (MSP-only) so BOXBEEPERON can be toggled purely via
MSP_SET_RAW_RC, without touching CLI, arming, or accelerometer calibration.

There is no physical receiver connected to this bench FC, so switching
receiverType away from CRSF carries no risk of losing a real control link.

Steps (all via MSP):
  1. Read current MSP_RX_CONFIG (24 raw bytes) and MSP_MODE_RANGES (160 raw
     bytes / 40 slots x 4 bytes) -- confirm nothing else has already claimed
     the target mode-range slot, and save the original raw bytes to
     original_rx_config.hex / original_mode_range_slot<N>.hex in the backup
     directory (default: current working directory -- NOT this script's own
     directory, so re-runs from a task workspace don't pollute a shared,
     git-tracked scripts/ location) so revert_msp_rx_beeper_switch.py can
     restore byte-for-byte even if this script is re-run later.
  2. MSP_SET_RX_CONFIG: same 24 bytes as read, with only the last byte
     (receiverType) changed from RX_TYPE_SERIAL(1) to RX_TYPE_MSP(2).
  3. MSP_SET_MODE_RANGE: slot -> box permanentId=13 (BOXBEEPERON),
     auxChannelIndex=1 (AUX2 / RC channel index 5), startStep=32 (1700us),
     endStep=48 (2100us). Slot 0 (used by ARM by default, currently zeroed /
     inactive) is left untouched.
  4. MSP_EEPROM_WRITE + MSP_REBOOT (single combined reboot for both changes),
     reconnect.
  5. Verify via read-only MSP_RX_CONFIG / MSP_MODE_RANGES that both changes
     persisted.

To test a different BOX mode instead of BOXBEEPERON, change
BOXBEEPERON_PERMANENT_ID below to the target mode's permanentId (see
src/main/fc/fc_msp_box.c) -- everything else (RX config swap, mode range
mechanics, save/reboot/verify) is generic.

Only use this on a bench FC with NO physical receiver connected -- it
switches receiverType away from the board's configured serial receiver
(e.g. CRSF), which would drop a real control link. revert_msp_rx_beeper_switch.py
restores the original receiverType/mode-range afterward.

Usage:
    setup_msp_rx_beeper_switch.py [port] [backup_dir]
"""
import sys
import os

sys.path.insert(0, "/home/raymorris/inavflight/mspapi2")
from mspapi2 import InavMSP  # noqa: E402
from msp_helpers import open_and_check, save_and_reboot  # noqa: E402

WORKDIR = os.getcwd()
RX_CONFIG_BACKUP_NAME = "original_rx_config.hex"
MODE_RANGE_BACKUP_NAME_FMT = "original_mode_range_slot{}.hex"

RX_TYPE_SERIAL = 1
RX_TYPE_MSP = 2

MODE_RANGE_SLOT = 1          # arbitrary unused slot (slot 0 is ARM's default/inactive slot)
BOXBEEPERON_PERMANENT_ID = 13
AUX_CHANNEL_INDEX = 1        # AUX2 (RC channel array index 5)
RANGE_START_STEP = 32        # 900 + 32*25 = 1700us
RANGE_END_STEP = 48          # 900 + 48*25 = 2100us


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
    backup_dir = sys.argv[2] if len(sys.argv) > 2 else WORKDIR
    rx_config_backup = os.path.join(backup_dir, RX_CONFIG_BACKUP_NAME)
    mode_range_backup = os.path.join(backup_dir, MODE_RANGE_BACKUP_NAME_FMT.format(MODE_RANGE_SLOT))

    api = open_and_check(port, label="setup")
    if api is None:
        return 1

    # --- Step 1: read + save original state ---
    try:
        info, rx_raw = api._request_raw(InavMSP.MSP_RX_CONFIG, b"", timeout=1.0)
        info, mr_raw = api._request_raw(InavMSP.MSP_MODE_RANGES, b"", timeout=1.0)
    except Exception as e:
        print(f"FAILED to read current config: {e}")
        api.close()
        return 1

    if len(rx_raw) != 24:
        print(f"FAILED: MSP_RX_CONFIG returned {len(rx_raw)} bytes, expected 24. Aborting.")
        api.close()
        return 1
    if rx_raw[-1] != RX_TYPE_SERIAL:
        print(f"WARNING: current receiverType byte is {rx_raw[-1]}, expected {RX_TYPE_SERIAL} "
              f"(RX_TYPE_SERIAL). Proceeding, but double-check this is the state you expect.")

    slot1 = mr_raw[MODE_RANGE_SLOT * 4:(MODE_RANGE_SLOT + 1) * 4]
    if slot1 != b"\x00\x00\x00\x00":
        print(f"FAILED: mode range slot {MODE_RANGE_SLOT} is not empty (raw={slot1.hex()}). "
              f"Refusing to overwrite an existing mode range. Pick a different slot.")
        api.close()
        return 1

    with open(rx_config_backup, "wb") as f:
        f.write(rx_raw)
    with open(mode_range_backup, "wb") as f:
        f.write(slot1)
    print(f"Backed up original MSP_RX_CONFIG ({rx_raw.hex()}) -> {rx_config_backup}")
    print(f"Backed up original mode range slot {MODE_RANGE_SLOT} ({slot1.hex()}) -> {mode_range_backup}")

    # --- Step 2: SET_RX_CONFIG with receiverType changed to MSP ---
    new_rx = bytearray(rx_raw)
    new_rx[-1] = RX_TYPE_MSP
    try:
        info, resp = api._request_raw(InavMSP.MSP_SET_RX_CONFIG, bytes(new_rx), timeout=1.0)
        print(f"MSP_SET_RX_CONFIG ACK ({len(resp)} bytes) -- receiverType set to RX_TYPE_MSP in RAM")
    except Exception as e:
        print(f"FAILED to send MSP_SET_RX_CONFIG: {e}")
        api.close()
        return 1

    # --- Step 3: SET_MODE_RANGE for BOXBEEPERON on AUX2 ---
    mode_range_payload = bytes([
        MODE_RANGE_SLOT,
        BOXBEEPERON_PERMANENT_ID,
        AUX_CHANNEL_INDEX,
        RANGE_START_STEP,
        RANGE_END_STEP,
    ])
    try:
        info, resp = api._request_raw(InavMSP.MSP_SET_MODE_RANGE, mode_range_payload, timeout=1.0)
        print(f"MSP_SET_MODE_RANGE ACK ({len(resp)} bytes) -- BOXBEEPERON mapped to AUX2 "
              f"range {RANGE_START_STEP}-{RANGE_END_STEP} steps "
              f"({900 + RANGE_START_STEP*25}-{900 + RANGE_END_STEP*25}us) in RAM")
    except Exception as e:
        print(f"FAILED to send MSP_SET_MODE_RANGE: {e}")
        api.close()
        return 1

    # --- Step 4: persist + reboot ---
    api2 = save_and_reboot(api, port)
    if api2 is None:
        return 1

    # --- Step 5: verify ---
    ok = True
    try:
        info, rx_raw2 = api2._request_raw(InavMSP.MSP_RX_CONFIG, b"", timeout=1.0)
        if len(rx_raw2) == 24 and rx_raw2[-1] == RX_TYPE_MSP:
            print(f"VERIFY OK: receiverType = {rx_raw2[-1]} (RX_TYPE_MSP)")
        else:
            print(f"VERIFY FAILED: MSP_RX_CONFIG raw = {rx_raw2.hex()}, expected receiverType byte = {RX_TYPE_MSP}")
            ok = False
    except Exception as e:
        print(f"FAILED to verify MSP_RX_CONFIG post-reboot: {e}")
        ok = False

    try:
        info, mr_raw2 = api2._request_raw(InavMSP.MSP_MODE_RANGES, b"", timeout=1.0)
        slot1_2 = mr_raw2[MODE_RANGE_SLOT * 4:(MODE_RANGE_SLOT + 1) * 4]
        expected = bytes([BOXBEEPERON_PERMANENT_ID, AUX_CHANNEL_INDEX, RANGE_START_STEP, RANGE_END_STEP])
        if slot1_2 == expected:
            print(f"VERIFY OK: mode range slot {MODE_RANGE_SLOT} = {slot1_2.hex()} (BOXBEEPERON/AUX2/1700-2100us)")
        else:
            print(f"VERIFY FAILED: mode range slot {MODE_RANGE_SLOT} = {slot1_2.hex()}, expected {expected.hex()}")
            ok = False
    except Exception as e:
        print(f"FAILED to verify MSP_MODE_RANGES post-reboot: {e}")
        ok = False

    api2.close()
    if ok:
        print("\nSetup complete: FC is now configured for MSP RX input, with BOXBEEPERON "
              "mapped to AUX2 (channel index 5) >= 1700us.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
