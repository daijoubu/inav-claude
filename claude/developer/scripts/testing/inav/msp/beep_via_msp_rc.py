#!/usr/bin/env python3
"""
Trigger BOXBEEPERON via MSP_SET_RAW_RC (continuous stream), then silence it.

Requires setup_msp_rx_beeper_switch.py to have already been run (receiverType
== RX_TYPE_MSP, AUX2 mapped to BOXBEEPERON over 1700-2100us). This script
verifies both preconditions via read-only queries before sending any RC data,
and aborts with a clear error if either is not satisfied -- it will NOT
silently do nothing.

RC frame sent (8 channels, index : name):
  0 roll=1500  1 pitch=1500  2 throttle=1000  3 yaw=1500
  4 aux1=1000 (unused/ARM slot is inactive by default, harmless regardless)
  5 aux2=<ACTIVE 2000 | INACTIVE 1000>  6 aux3=1500  7 aux4=1500

Sequence:
  1. Verify receiverType == RX_TYPE_MSP and mode range slot 1 == BOXBEEPERON/AUX2.
  2. Send AUX2=1000 (inactive) for ~0.5s first, to establish a known baseline.
  3. Print "BEEP STARTING NOW" and send AUX2=2000 (active) continuously at
     ~30Hz for `duration` seconds (default 3s).
  4. Send AUX2=1000 (inactive) continuously at ~30Hz for ~1.5s to silence and
     confirm it stops.
  5. Stop sending entirely and close.

Usage:
    beep_via_msp_rc.py [port] [duration_seconds]
"""
import sys
import time
import struct

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
from msp_helpers import open_and_check  # noqa: E402

RX_TYPE_MSP = 2
MODE_RANGE_SLOT = 1
BOXBEEPERON_PERMANENT_ID = 13
AUX_CHANNEL_INDEX = 1
RANGE_START_STEP = 32
RANGE_END_STEP = 48

RATE_HZ = 30
BASELINE_S = 0.5
SILENCE_S = 1.5


def send_frame(api, aux2_value):
    channels = [1500, 1500, 1000, 1500, 1000, aux2_value, 1500, 1500]
    payload = struct.pack(f"<{len(channels)}H", *channels)
    api._request_raw(InavMSP.MSP_SET_RAW_RC, payload, timeout=0.3)


def stream(api, aux2_value, duration_s):
    period = 1.0 / RATE_HZ
    end = time.time() + duration_s
    sent = 0
    failed = 0
    while time.time() < end:
        t0 = time.time()
        try:
            send_frame(api, aux2_value)
            sent += 1
        except Exception as e:
            failed += 1
            if failed <= 3:
                print(f"  WARNING: MSP_SET_RAW_RC send failed: {e}")
        dt = time.time() - t0
        if dt < period:
            time.sleep(period - dt)
    return sent, failed


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0

    api = open_and_check(port, label="beep trigger")
    if api is None:
        return 1

    # --- Precondition checks (read-only) ---
    try:
        info, rx_raw = api._request_raw(InavMSP.MSP_RX_CONFIG, b"", timeout=1.0)
        if len(rx_raw) != 24 or rx_raw[-1] != RX_TYPE_MSP:
            print(f"ABORT: receiverType is not RX_TYPE_MSP (raw last byte = "
                  f"{rx_raw[-1] if len(rx_raw) == 24 else 'N/A'}). "
                  f"Run setup_msp_rx_beeper_switch.py first.")
            api.close()
            return 1
    except Exception as e:
        print(f"FAILED to read MSP_RX_CONFIG: {e}")
        api.close()
        return 1

    try:
        info, mr_raw = api._request_raw(InavMSP.MSP_MODE_RANGES, b"", timeout=1.0)
        slot1 = mr_raw[MODE_RANGE_SLOT * 4:(MODE_RANGE_SLOT + 1) * 4]
        expected = bytes([BOXBEEPERON_PERMANENT_ID, AUX_CHANNEL_INDEX, RANGE_START_STEP, RANGE_END_STEP])
        if slot1 != expected:
            print(f"ABORT: mode range slot {MODE_RANGE_SLOT} = {slot1.hex()}, expected {expected.hex()} "
                  f"(BOXBEEPERON/AUX2/1700-2100us). Run setup_msp_rx_beeper_switch.py first.")
            api.close()
            return 1
    except Exception as e:
        print(f"FAILED to read MSP_MODE_RANGES: {e}")
        api.close()
        return 1

    print("Preconditions OK: receiverType=RX_TYPE_MSP, BOXBEEPERON mapped to AUX2/1700-2100us.")

    # --- Baseline (aux2 inactive) ---
    print(f"Sending baseline (AUX2=1000, inactive) for {BASELINE_S}s ...")
    sent, failed = stream(api, 1000, BASELINE_S)
    if failed:
        print(f"  WARNING: {failed}/{sent + failed} baseline frames failed to send.")

    # --- Active (beep should start) ---
    print(f"\n>>> BEEP STARTING NOW -- sending AUX2=2000 (active) for {duration}s. LISTEN. <<<\n")
    sent, failed = stream(api, 2000, duration)
    print(f"  Sent {sent} active frames ({failed} failed).")
    if failed > sent * 0.1:
        print(f"  WARNING: high failure rate sending RC frames -- FC may not have "
              f"reliably seen the active AUX2 value continuously.")

    # --- Silence ---
    print(f"\nSilencing: sending AUX2=1000 (inactive) for {SILENCE_S}s ...")
    sent, failed = stream(api, 1000, SILENCE_S)
    print(f"  Sent {sent} silence frames ({failed} failed). Beeper should now be OFF.")

    api.close()
    print("\nDone. Please confirm: did you hear the beeper during the ACTIVE window, "
          "and did it stop during the SILENCE window?")
    return 0


if __name__ == "__main__":
    sys.exit(main())
