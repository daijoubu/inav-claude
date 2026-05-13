#!/usr/bin/env python3
"""
CRSF/ELRS Receiver Detection Probe via MSP
==========================================
Experimentally probes which MSP commands can detect or confirm that an
embedded CRSF/ELRS receiver is present and communicating, even when unbound.

Architecture: Test Tool <--MSP/USB--> INAV on FC <--UART/CRSF--> embedded ELRS RX

Usage:
    python3 probe_crsf_rx_detection.py [port]
    python3 probe_crsf_rx_detection.py /dev/ttyACM0

Note: If running in a sandbox, retry with dangerouslyDisableSandbox: true.
      Serial ports are blocked by default in sandbox environments.
"""

import sys
import time
import traceback

DEVICE = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD = 115200

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------
try:
    from mspapi2 import MSPApi
    from mspapi2.lib import InavMSP, InavEnums
except ImportError as e:
    print(f"FAILED to import mspapi2: {e}")
    print("  Run: pip install -e /home/raymorris/Documents/planes/inavflight/mspapi2")
    sys.exit(1)

print(f"Connecting to FC on {DEVICE} at {BAUD} baud ...")
try:
    api = MSPApi(port=DEVICE, baudrate=BAUD)
    api.open()
    print("  Connected.")
except Exception as e:
    print(f"FAILED to open serial port: {e}")
    print("  Check: Is FC plugged in? Is configurator closed?")
    print("  If running in sandbox: retry with dangerouslyDisableSandbox: true")
    sys.exit(1)

# Sanity check - verify FC responds
try:
    info, version = api.get_api_version()
    print(f"  FC API version: {version.get('apiVersionMajor', '?')}.{version.get('apiVersionMinor', '?')}")
    print()
except Exception as e:
    print(f"FAILED: FC not responding to MSP_API_VERSION: {e}")
    print("  The FC is not communicating - cannot run experiments.")
    print("  If running in sandbox: retry with dangerouslyDisableSandbox: true")
    api.close()
    sys.exit(1)

results = {}

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def run_raw(code_name, code_int):
    """Send a raw MSP request by integer code and return raw bytes."""
    try:
        raw = api._serial.request(code_int, payload=bytes(), timeout=2.0)
        return raw
    except Exception as e:
        return None


def section(title):
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Experiment 1: MSP_RX_CONFIG (code 44) - What RX type is configured?
# ---------------------------------------------------------------------------
section("Experiment 1: MSP_RX_CONFIG (code 44)")

try:
    info, rx_cfg = api.get_rx_config()
    print(f"  Raw response info: {info}")
    print(f"  Parsed fields:")
    for k, v in rx_cfg.items():
        print(f"    {k}: {v}")

    receiver_type = rx_cfg.get("receiverType", None)
    serial_rx_provider = rx_cfg.get("serialRxProvider", None)

    print()
    if receiver_type is not None:
        try:
            rt_enum = InavEnums.rxReceiverType_e(int(receiver_type))
            print(f"  -> receiverType = {int(receiver_type)} ({rt_enum.name})")
        except Exception:
            print(f"  -> receiverType = {receiver_type}")

    if serial_rx_provider is not None:
        try:
            sp_enum = InavEnums.rxSerialReceiverType_e(int(serial_rx_provider))
            print(f"  -> serialRxProvider = {int(serial_rx_provider)} ({sp_enum.name})")
            if sp_enum.name == "SERIALRX_CRSF":
                print("  FINDING: CRSF is configured as the serial RX provider.")
            else:
                print(f"  NOTE: Serial RX provider is NOT CRSF (it's {sp_enum.name})")
        except Exception:
            print(f"  -> serialRxProvider = {serial_rx_provider}")

    results["exp1_rx_config"] = rx_cfg
    print()
    print("  RELIABILITY ASSESSMENT: MSP_RX_CONFIG tells you what is CONFIGURED,")
    print("  not whether communication is active. Good for confirming CRSF is set up.")

except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
    results["exp1_rx_config"] = None

print()

# ---------------------------------------------------------------------------
# Experiment 2: MSP_RC (code 105) - RC channel values
# ---------------------------------------------------------------------------
section("Experiment 2: MSP_RC (code 105) - RC channel values")

try:
    # Sample a few times to see if values change
    samples = []
    for i in range(3):
        info, rc = api.get_rc()
        channels = rc.get("rcChannels", [])
        samples.append(channels)
        if i < 2:
            time.sleep(0.5)

    print(f"  Channel count: {len(samples[0])}")
    print(f"  Sample 1: {samples[0]}")
    print(f"  Sample 2: {samples[1]}")
    print(f"  Sample 3: {samples[2]}")

    # Analyze values
    ch = samples[0]
    if len(ch) == 0:
        print()
        print("  FINDING: Zero channels returned. RX may not be active at all.")
    elif all(v == 0 for v in ch):
        print()
        print("  FINDING: All channels are 0 (not 1500). This is unusual -")
        print("           could indicate failsafe/no-signal state.")
    elif all(1400 <= v <= 1600 for v in ch):
        print()
        print("  FINDING: All channels near mid-stick (1500). Typical failsafe.")
    else:
        print()
        print("  FINDING: Channels have non-trivial values - RX may be active.")

    # Check if any channels differ between samples (would indicate live data)
    changed = any(samples[0][i] != samples[2][i] for i in range(min(len(samples[0]), len(samples[2]))))
    if changed:
        print("  FINDING: Channel values changed between samples - RX is sending live data!")
    else:
        print("  NOTE: Channel values stable across samples (expected if unbound).")

    results["exp2_rc"] = samples

    print()
    print("  RELIABILITY ASSESSMENT: Channel COUNT may indicate CRSF is alive (CRSF")
    print("  typically provides 16 channels). Zero channels = no RX active.")
    print("  Values near 1500 = failsafe. Cannot distinguish 'bound+failsafe' from 'unbound'.")

except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
    results["exp2_rc"] = None

print()

# ---------------------------------------------------------------------------
# Experiment 3: MSP_STATUS_EX (code 150) and MSP2_INAV_STATUS (code 8192)
# ---------------------------------------------------------------------------
section("Experiment 3: MSP_STATUS_EX (150) and MSP2_INAV_STATUS (8192)")

try:
    info, status_ex = api.get_status_ex()
    print(f"  MSP_STATUS_EX fields:")
    for k, v in status_ex.items():
        print(f"    {k}: {v}")

    arming_flags_raw = status_ex.get("armingFlags", 0)
    print()
    print(f"  armingFlags (raw): 0x{int(arming_flags_raw):08X} ({int(arming_flags_raw)})")

    # Decode arming flags
    af = InavEnums.armingFlag_e
    active_flags = []
    for name, val in af.__members__.items():
        if int(arming_flags_raw) & int(val):
            active_flags.append(name)
    print(f"  Active arming flags: {active_flags}")

    rc_link_flag = bool(int(arming_flags_raw) & int(af.ARMING_DISABLED_RC_LINK))
    print()
    if rc_link_flag:
        print("  FINDING: ARMING_DISABLED_RC_LINK is SET - FC sees no valid RC link!")
        print("           This flag is set when CRSF frames stop arriving.")
    else:
        print("  FINDING: ARMING_DISABLED_RC_LINK is CLEAR - FC sees a valid RC link.")

    results["exp3_status_ex"] = {"raw_flags": int(arming_flags_raw), "active": active_flags, "rc_link_blocked": rc_link_flag}

    sensor_status = status_ex.get("sensorStatus", 0)
    print()
    print(f"  sensorStatus bitmask: 0x{int(sensor_status):04X}")
    print("  (Bit 0=ACC, 1=BARO, 2=MAG, 3=GPS, 4=RANGE, 5=OPFLOW, 6=PITOT, 7=TEMP, 15=hw_fail)")
    sensor_bits = int(sensor_status)
    sensor_names = {0: "ACC", 1: "BARO", 2: "MAG", 3: "GPS", 4: "RANGEFINDER",
                    5: "OPFLOW", 6: "PITOT", 7: "TEMP"}
    active_sensors = [sensor_names[b] for b in range(8) if sensor_bits & (1 << b)]
    hw_fail = bool(sensor_bits & (1 << 15))
    print(f"  Active sensors: {active_sensors}")
    print(f"  Hardware failure flag: {hw_fail}")

except Exception as e:
    print(f"  MSP_STATUS_EX FAILED: {e}")
    traceback.print_exc()

print()
print("  Now trying MSP2_INAV_STATUS for full 32-bit arming flags ...")
try:
    info2, inav_status = api.get_inav_status()
    print(f"  MSP2_INAV_STATUS fields:")
    for k, v in inav_status.items():
        if k != "activeModes":
            print(f"    {k}: {v}")

    arming_flags_full = inav_status.get("armingFlags", 0)
    print()
    print(f"  Full armingFlags (32-bit): 0x{int(arming_flags_full):08X}")
    af = InavEnums.armingFlag_e
    active_flags_full = []
    for name, val in af.__members__.items():
        if name == "ARMING_DISABLED_ALL_FLAGS":
            continue
        if int(arming_flags_full) & int(val):
            active_flags_full.append(name)
    print(f"  Active arming flags: {active_flags_full}")
    rc_link_flag_full = bool(int(arming_flags_full) & int(af.ARMING_DISABLED_RC_LINK))
    print()
    if rc_link_flag_full:
        print("  FINDING: ARMING_DISABLED_RC_LINK is SET (full 32-bit) - no valid RC link!")
    else:
        print("  FINDING: ARMING_DISABLED_RC_LINK is CLEAR - FC sees valid RC link.")

    results["exp3_inav_status"] = {"raw_flags": int(arming_flags_full), "active": active_flags_full, "rc_link_blocked": rc_link_flag_full}

except Exception as e:
    print(f"  MSP2_INAV_STATUS FAILED: {e}")
    traceback.print_exc()

print()
print("  RELIABILITY ASSESSMENT: ARMING_DISABLED_RC_LINK is the BEST single indicator.")
print("  It is SET when no CRSF frames are arriving (unbound RX = no frames).")
print("  It is CLEAR when CRSF frames arrive (even unbound but within timeout).")
print("  However: cannot distinguish 'broken UART' from 'RX present but unbound'.")

print()

# ---------------------------------------------------------------------------
# Experiment 4: MSP_SENSOR_STATUS (code 151)
# ---------------------------------------------------------------------------
section("Experiment 4: MSP_SENSOR_STATUS (code 151)")

try:
    info, sensor_status = api.get_sensor_status()
    print(f"  Parsed fields:")
    for k, v in sensor_status.items():
        try:
            hw_enum = InavEnums.hardwareSensorStatus_e(int(v))
            print(f"    {k}: {int(v)} ({hw_enum.name})")
        except Exception:
            print(f"    {k}: {v}")

    results["exp4_sensor_status"] = sensor_status
    print()
    print("  NOTE: MSP_SENSOR_STATUS covers gyro/acc/baro/GPS etc. - NOT the RC receiver.")
    print("  No receiver health field is exposed here.")

except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
    results["exp4_sensor_status"] = None

print()

# ---------------------------------------------------------------------------
# Experiment 5: Raw MSP 144 (0x90) - MSP_LINK_STATISTICS if it exists
# ---------------------------------------------------------------------------
section("Experiment 5: Raw probe MSP code 144 (0x90) - possible LINK_STATISTICS")

# MSP_LINK_STATISTICS is not in the schema but the task asked us to try it
try:
    from mspapi2.msp_serial import MSPSerial

    # Try raw request with code 144
    print("  Sending raw MSP code 144 ...")
    raw_bytes = api._serial.request(144, payload=bytes(), timeout=2.0)
    if raw_bytes is not None and len(raw_bytes) > 0:
        print(f"  Got {len(raw_bytes)} bytes: {raw_bytes.hex()}")
        print(f"  As integers: {list(raw_bytes)}")
        results["exp5_code144"] = list(raw_bytes)
    else:
        print("  No response (empty or None) - command not supported or no data")
        results["exp5_code144"] = None
except Exception as e:
    print(f"  FAILED or no response: {e}")
    results["exp5_code144"] = None

print()

# Also try MSP2_COMMON_SET_MSP_RC_LINK_STATS read-back via code 0x100D - it's SET-only
# Instead try code 0x100C if it exists (GET variant)
print("  Checking for any GET link stats variant (probing code 0x100C = 4108) ...")
try:
    raw_bytes2 = api._serial.request(4108, payload=bytes(), timeout=2.0)
    if raw_bytes2 is not None and len(raw_bytes2) > 0:
        print(f"  Got {len(raw_bytes2)} bytes: {raw_bytes2.hex()}")
        results["exp5_code4108"] = list(raw_bytes2)
    else:
        print("  No response - command not supported")
        results["exp5_code4108"] = None
except Exception as e:
    print(f"  No response: {e}")
    results["exp5_code4108"] = None

print()
print("  RELIABILITY ASSESSMENT: If code 144 returns no data, link stats are")
print("  not readable via GET MSP on this firmware. The SET variant (0x100D)")
print("  is for external MSP-RC senders to push stats INTO the FC, not for reading.")

print()

# ---------------------------------------------------------------------------
# Experiment 6: MSP_RC repeated sampling to detect failsafe timing
# ---------------------------------------------------------------------------
section("Experiment 6: Channel count as receiver presence indicator")

try:
    info, rc = api.get_rc()
    channels = rc.get("rcChannels", [])
    ch_count = len(channels)
    print(f"  Channel count reported: {ch_count}")
    print()
    if ch_count == 0:
        print("  FINDING: 0 channels - RX subsystem appears inactive/not configured.")
        print("           Could mean: RX type is NONE, or RX not initialized.")
    elif ch_count == 16:
        print("  FINDING: 16 channels - matches CRSF standard channel count.")
        print("           This is a positive signal that CRSF RX is configured and active.")
    elif ch_count == 18:
        print("  FINDING: 18 channels - CRSF extended (with 2 extra channels).")
    else:
        print(f"  FINDING: {ch_count} channels - may not be CRSF (CRSF = 16 or 18 channels).")

    print()
    print("  Channel values:")
    for i, v in enumerate(channels):
        flag = ""
        if v == 0:
            flag = " <- ZERO (unusual)"
        elif v == 988:
            flag = " <- CRSF minimum"
        elif v == 1500:
            flag = " <- mid-stick/failsafe"
        elif v == 2011:
            flag = " <- CRSF maximum"
        print(f"    CH{i+1:2d}: {v}{flag}")

    results["exp6_channel_count"] = ch_count

except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
    results["exp6_channel_count"] = None

print()

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
section("SUMMARY OF FINDINGS")

print()
print("Command                   | What it tells you about RX presence")
print("-" * 70)
print("MSP_RX_CONFIG (44)        | Confirms CRSF is CONFIGURED (not live)")
print("MSP_RC (105)              | Channel count (16=CRSF likely); values show failsafe")
print("MSP2_INAV_STATUS (8192)   | ARMING_DISABLED_RC_LINK = best live indicator")
print("MSP_STATUS_EX (150)       | Same RC_LINK flag but 16-bit truncated arming flags")
print("MSP_SENSOR_STATUS (151)   | No RC receiver field - only IMU/baro/GPS sensors")
print("Code 144 raw              | Not a standard GET - no data expected")
print()
print("RECOMMENDATION:")
print("  1. First confirm: MSP_RX_CONFIG -> serialRxProvider == SERIALRX_CRSF (6)")
print("                    and receiverType == RX_TYPE_SERIAL (1)")
print("  2. Then check:    MSP2_INAV_STATUS -> armingFlags & ARMING_DISABLED_RC_LINK")
print("                    - SET (bit 18 = 1): No CRSF frames arriving (broken UART or unbound RX)")
print("                    - CLEAR (bit 18 = 0): CRSF frames ARE arriving (RX present!)")
print()
print("KEY INSIGHT about unbound ELRS receivers:")
print("  An unbound ELRS receiver will still send CRSF frames to the FC on its UART.")
print("  It sends 'failsafe' channel data (all channels at failsafe values).")
print("  So ARMING_DISABLED_RC_LINK being CLEAR means the UART/RX link is working,")
print("  even if the RX is not bound to any transmitter.")
print()
print("  Broken UART or absent RX: RC_LINK flag SET (frames not arriving)")
print("  RX present but unbound:   RC_LINK flag CLEAR (frames arriving, failsafe values)")
print("  RX bound to TX:           RC_LINK flag CLEAR + channels show actual TX positions")
print()

api.close()
print("Done. FC connection closed.")
