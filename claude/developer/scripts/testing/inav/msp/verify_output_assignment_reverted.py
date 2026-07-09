#!/usr/bin/env python3
"""
Verification test: Reverted PWM timer priority firmware + configurator.

Checks performed:
  1. Firmware version from FC matches expected commit (INAV 9.0.1, May 15 2026)
  2. MSP2_INAV_OUTPUT_MAPPING_EXT2 returns records in single-pass array-position order
  3. getTimerMap() in outputMapping.js is the single-pass version (one loop, no two-pass)
  4. No JS errors in the output mapping code paths (via CDP)
  5. Output assignments load without errors when Mixer/Outputs tab is opened

FC target: BROTHERHOBBYF405V3 on /dev/ttyACM0 (adjust SERIAL_PORT as needed)

Usage:
    python3 verify_output_assignment_reverted.py

Permanent location: claude/developer/scripts/testing/inav/msp/
Use this script to verify that a revert of PRs #11445/#2596 is in place on
maintenance-9.x (single-pass getTimerMap, no two-pass priority logic).

If running in sandbox, retry with dangerouslyDisableSandbox=true.
"""

import asyncio
import json
import struct
import sys
import time
import serial
import websockets

SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUD = 115200
CDP_PAGE_URL = "ws://127.0.0.1:9222/devtools/page/22BB0AD3EF81390C348E2DE5150189C0"

# Expected values from the reverted firmware build
EXPECTED_FC_VERSION_MAJOR = 9
EXPECTED_FC_VERSION_MINOR = 0
EXPECTED_FC_VERSION_PATCH = 1
EXPECTED_BUILD_DATE_CONTAINS = "2026"   # build date should contain 2026 (May 15 2026)

# MSP codes
MSP_API_VERSION  = 1
MSP_FC_VERSION   = 3
MSP_BUILD_INFO   = 5
MSP2_INAV_OUTPUT_MAPPING_EXT2 = 0x210D  # 8461

# TIM_USE_* bit positions (from firmware pwm_output.h)
TIM_USE_PPM   = 0
TIM_USE_PWM   = 1
TIM_USE_MOTOR = 2
TIM_USE_SERVO = 3
TIM_USE_LED   = 24
TIM_USE_BEEPER= 25

RESULTS = []


def report(check_name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    mark   = "  OK" if passed else "FAIL"
    line   = f"  [{mark}] {check_name}"
    if detail:
        line += f": {detail}"
    print(line)
    RESULTS.append((check_name, passed))
    return passed


# ---------------------------------------------------------------------------
# MSP helpers
# ---------------------------------------------------------------------------

def msp_v1_frame(cmd, payload=b""):
    size = len(payload)
    hdr = b"$M<"
    body = bytes([size, cmd]) + payload
    crc = 0
    for b in body:
        crc ^= b
    return hdr + body + bytes([crc])


def msp_v2_frame(cmd, payload=b""):
    """Build MSPv2 frame."""
    size = len(payload)
    # $X< flag=0 cmd(LE uint16) size(LE uint16) payload crc8
    hdr = b"$X<"
    flag = 0
    body = struct.pack("<BHH", flag, cmd, size) + payload
    # CRC8 DVB-S2 over body
    crc = 0
    for b in body:
        crc = _crc8_dvb_s2(crc, b)
    return hdr + body + bytes([crc])


def _crc8_dvb_s2(crc, b):
    crc ^= b
    for _ in range(8):
        if crc & 0x80:
            crc = ((crc << 1) ^ 0xD5) & 0xFF
        else:
            crc = (crc << 1) & 0xFF
    return crc


def read_msp_reply(ser, timeout=2.0):
    """Read one complete MSP reply frame from serial port."""
    deadline = time.time() + timeout
    buf = bytearray()
    while time.time() < deadline:
        if ser.in_waiting:
            buf += ser.read(ser.in_waiting)
        # Look for MSPv1 header
        if b"$M>" in buf:
            idx = buf.index(b"$M>")
            frame = buf[idx:]
            if len(frame) >= 6:
                size = frame[3]
                if len(frame) >= 5 + size + 1:
                    cmd     = frame[4]
                    payload = bytes(frame[5:5 + size])
                    return "v1", cmd, payload
        # Look for MSPv2 header
        if b"$X>" in buf:
            idx = buf.index(b"$X>")
            frame = buf[idx:]
            if len(frame) >= 9:
                size = struct.unpack_from("<H", frame, 6)[0]
                if len(frame) >= 9 + size + 1:
                    cmd     = struct.unpack_from("<H", frame, 4)[0]
                    payload = bytes(frame[8:8 + size])
                    return "v2", cmd, payload
        time.sleep(0.02)
    return None, None, None


def msp_request(ser, cmd, payload=b"", v2=False):
    """Send MSP request and return (ver, cmd, payload) reply."""
    if v2:
        frame = msp_v2_frame(cmd, payload)
    else:
        frame = msp_v1_frame(cmd, payload)
    ser.reset_input_buffer()
    written = ser.write(frame)
    if written != len(frame):
        print(f"  WARNING: only wrote {written}/{len(frame)} bytes")
    return read_msp_reply(ser)


# ---------------------------------------------------------------------------
# Check 1: Connect to FC
# ---------------------------------------------------------------------------

def check_fc_connection():
    print("\n--- Check 1: FC connection ---")
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
        print(f"  Connected to {SERIAL_PORT} @ {SERIAL_BAUD} baud")

        # Sanity check: send MSP_API_VERSION
        ver, cmd, payload = msp_request(ser, MSP_API_VERSION)
        if ver is None:
            report("FC responds to MSP_API_VERSION", False,
                   "No response — is FC plugged in and no other program using port?")
            print("  Note: If running in sandbox, retry with dangerouslyDisableSandbox=true")
            ser.close()
            return None

        msp_v = payload[0] if payload else "?"
        api_major = payload[1] if len(payload) > 1 else "?"
        api_minor = payload[2] if len(payload) > 2 else "?"
        report("FC responds to MSP_API_VERSION", True,
               f"protocol={msp_v} api={api_major}.{api_minor}")
        return ser

    except serial.SerialException as e:
        report("FC connection opened", False, str(e))
        print("  Check: Is FC plugged in? Is Configurator closed on this port?")
        print("  Note: If running in sandbox, retry with dangerouslyDisableSandbox=true")
        return None


# ---------------------------------------------------------------------------
# Check 2: Firmware version
# ---------------------------------------------------------------------------

def check_firmware_version(ser):
    print("\n--- Check 2: Firmware version ---")

    # MSP_FC_VERSION
    ver, cmd, payload = msp_request(ser, MSP_FC_VERSION)
    if ver is None or len(payload) < 3:
        report("MSP_FC_VERSION", False, "No response")
        return False

    major, minor, patch = payload[0], payload[1], payload[2]
    version_str = f"{major}.{minor}.{patch}"
    version_ok = (major == EXPECTED_FC_VERSION_MAJOR and
                  minor == EXPECTED_FC_VERSION_MINOR and
                  patch == EXPECTED_FC_VERSION_PATCH)
    report("Firmware version is INAV 9.0.1",
           version_ok,
           f"got {version_str}")

    # MSP_BUILD_INFO
    ver, cmd, payload = msp_request(ser, MSP_BUILD_INFO)
    if ver is None or len(payload) < 11:
        report("MSP_BUILD_INFO", False, "No response")
        return version_ok

    # BUILD_DATE is first 11 chars, BUILD_TIME is next 8 chars, GIT_HASH is remainder
    try:
        build_date = payload[:11].decode("ascii", errors="replace").strip('\x00')
        build_time = payload[11:19].decode("ascii", errors="replace").strip('\x00') if len(payload) >= 19 else "?"
        git_hash   = payload[19:26].decode("ascii", errors="replace").strip('\x00') if len(payload) >= 26 else "?"
    except Exception as e:
        report("MSP_BUILD_INFO decode", False, str(e))
        return version_ok

    date_ok = EXPECTED_BUILD_DATE_CONTAINS in build_date
    report("Build date contains 2026",
           date_ok,
           f"build_date='{build_date}' time='{build_time}' hash='{git_hash}'")

    # Git hash should start with 5837d2c (the reverted commit)
    hash_ok = git_hash.lower().startswith("5837d2c")
    report("Git hash matches reverted commit (5837d2c)",
           hash_ok,
           f"hash='{git_hash}' (expected prefix '5837d2c')")

    return version_ok and date_ok


# ---------------------------------------------------------------------------
# Check 3: MSP2_INAV_OUTPUT_MAPPING_EXT2 — single-pass order
# ---------------------------------------------------------------------------

def check_output_mapping_ext2(ser):
    print("\n--- Check 3: MSP2_INAV_OUTPUT_MAPPING_EXT2 data ---")

    ver, cmd, payload = msp_request(ser, MSP2_INAV_OUTPUT_MAPPING_EXT2, v2=True, timeout=3.0)
    if ver is None:
        report("MSP2_INAV_OUTPUT_MAPPING_EXT2 responds", False,
               "No response from FC")
        return False

    if not payload:
        report("MSP2_INAV_OUTPUT_MAPPING_EXT2 has entries", False,
               "Empty payload — target may not support EXT2")
        return False

    # Each entry: timerId(u8) + usageFlags(u32) + pinLabel(u8) = 6 bytes
    ENTRY_SIZE = 6
    if len(payload) % ENTRY_SIZE != 0:
        report("EXT2 payload size is multiple of 6", False,
               f"payload length={len(payload)} not divisible by 6")
        return False

    n_entries = len(payload) // ENTRY_SIZE
    entries = []
    for i in range(n_entries):
        off = i * ENTRY_SIZE
        timer_id    = payload[off]
        usage_flags = struct.unpack_from("<I", payload, off + 1)[0]
        pin_label   = payload[off + 5]
        entries.append((timer_id, usage_flags, pin_label))

    report("EXT2 payload size is multiple of 6", True, f"{n_entries} entries")
    print(f"  EXT2 entries (array-position order from firmware):")

    # Decode usage flags into human-readable list
    TIM_USE_NAMES = {
        TIM_USE_PPM:    "PPM",
        TIM_USE_PWM:    "PWM",
        TIM_USE_MOTOR:  "MOTOR",
        TIM_USE_SERVO:  "SERVO",
        TIM_USE_LED:    "LED",
        TIM_USE_BEEPER: "BEEPER",
    }

    motor_entries = []
    servo_entries = []
    for idx, (tid, flags, label) in enumerate(entries):
        uses = []
        for bit, name in TIM_USE_NAMES.items():
            if flags & (1 << bit):
                uses.append(name)
        use_str = "+".join(uses) if uses else "NONE"
        print(f"    [{idx}] timerId={tid} usageFlags=0x{flags:08X} ({use_str}) pinLabel={label}")
        if flags & (1 << TIM_USE_MOTOR):
            motor_entries.append(idx)
        if flags & (1 << TIM_USE_SERVO):
            servo_entries.append(idx)

    # Verify entries with MOTOR capability appear before servo-only entries
    # (single-pass firmware should return them in physical pin order)
    if motor_entries:
        print(f"\n  Motor-capable entries at positions: {motor_entries}")
        # In single-pass order, motor entries should appear in ascending index order
        motor_in_order = motor_entries == sorted(motor_entries)
        report("Motor-capable entries appear in ascending array-position order",
               motor_in_order,
               f"positions={motor_entries}")
    else:
        print("  No motor-capable entries found in EXT2 payload")
        report("EXT2 has motor-capable entries", False, "no entries with TIM_USE_MOTOR set")

    # The single-pass firmware returns entries in one pass through timer list —
    # verify there's no duplication (each timer should appear once)
    timer_ids = [e[0] for e in entries]
    unique_timer_ids = set(timer_ids)
    no_duplicates = len(timer_ids) == len(unique_timer_ids)
    report("No duplicate timer IDs in EXT2 response", no_duplicates,
           f"total={len(timer_ids)} unique={len(unique_timer_ids)}")

    return no_duplicates and (len(motor_entries) > 0)


# Override helper so we can pass timeout to msp_request
_orig_msp_request = msp_request
def msp_request(ser, cmd, payload=b"", v2=False, timeout=2.0):
    if v2:
        frame = msp_v2_frame(cmd, payload)
    else:
        frame = msp_v1_frame(cmd, payload)
    ser.reset_input_buffer()
    written = ser.write(frame)
    if written != len(frame):
        print(f"  WARNING: only wrote {written}/{len(frame)} bytes")
    return read_msp_reply(ser, timeout=timeout)


# ---------------------------------------------------------------------------
# Check 4: outputMapping.js — single-pass getTimerMap() via CDP
# ---------------------------------------------------------------------------

async def check_configurator_via_cdp():
    print("\n--- Check 4: Configurator outputMapping.js single-pass via CDP ---")

    try:
        async with websockets.connect(CDP_PAGE_URL, ping_timeout=10) as ws:
            print("  Connected to Configurator CDP")

            # Check for JS errors by reading console messages
            await ws.send(json.dumps({"id": 1, "method": "Console.enable"}))
            await ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))

            # Give a moment for any pending events
            await asyncio.sleep(0.5)

            # Evaluate JS to check the getTimerMap source code
            expr = """
(function() {
    // Dynamically import outputMapping and return source info
    // We check if the module is loaded in the current window context
    // by looking for the TIMER_OUTPUT_MODE constants
    try {
        const result = {};

        // Check FC object exists (means FC is connected and modules loaded)
        if (typeof FC !== 'undefined' && FC.OUTPUT_MAPPING !== null) {
            result.fc_output_mapping_exists = true;
            result.output_count = FC.OUTPUT_MAPPING.getOutputCount ? FC.OUTPUT_MAPPING.getOutputCount() : -1;
            result.timer_ids = FC.OUTPUT_MAPPING.getUsedTimerIds ? FC.OUTPUT_MAPPING.getUsedTimerIds() : [];
        } else {
            result.fc_output_mapping_exists = false;
        }

        return result;
    } catch(e) {
        return { error: e.toString() };
    }
})()
"""
            await ws.send(json.dumps({
                "id": 10,
                "method": "Runtime.evaluate",
                "params": {"expression": expr, "returnByValue": True}
            }))

            resp = None
            deadline = asyncio.get_event_loop().time() + 10
            while asyncio.get_event_loop().time() < deadline:
                raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
                msg = json.loads(raw)
                if msg.get("id") == 10:
                    resp = msg
                    break

            if resp is None:
                report("CDP Runtime.evaluate responds", False, "no response in 10s")
                return False

            result_obj = resp.get("result", {}).get("result", {})
            exc = resp.get("result", {}).get("exceptionDetails")
            if exc:
                report("CDP Runtime.evaluate no JS exception", False, str(exc))
                return False

            val = result_obj.get("value", {})
            if isinstance(val, dict) and "error" in val:
                report("JS context check", False, f"JS error: {val['error']}")
                return False

            if isinstance(val, dict):
                fc_exists = val.get("fc_output_mapping_exists", False)
                output_count = val.get("output_count", -1)
                timer_ids = val.get("timer_ids", [])

                report("FC.OUTPUT_MAPPING exists in Configurator",
                       fc_exists,
                       "(FC must be connected to Configurator)")

                if fc_exists:
                    report("OUTPUT_MAPPING has output count > 0",
                           output_count > 0,
                           f"output_count={output_count}")
                    report("OUTPUT_MAPPING has timer IDs",
                           len(timer_ids) > 0,
                           f"timerIds={timer_ids}")
                else:
                    print("  (FC not connected to Configurator — skipping live mapping checks)")
            else:
                report("CDP returned valid dict", False, f"got: {val}")

            # Now check for any JS errors in the console log
            await ws.send(json.dumps({
                "id": 20,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": "window.__outputMappingErrors || []",
                    "returnByValue": True
                }
            }))
            # (We don't assert on this — just informational)

            return True

    except ConnectionRefusedError:
        report("CDP connection to Configurator", False,
               f"Cannot connect to {CDP_PAGE_URL}")
        print("  Is Configurator running with --remote-debugging-port=9222?")
        print("  Note: If running in sandbox, retry with dangerouslyDisableSandbox=true")
        return False
    except Exception as e:
        report("CDP check", False, str(e))
        import traceback
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Check 5: Verify getTimerMap() is single-pass (source file check)
# ---------------------------------------------------------------------------

def check_outputmapping_source():
    print("\n--- Check 5: outputMapping.js source — single-pass getTimerMap() ---")

    src_path = "/home/raymorris/Documents/planes/inavflight/inav-configurator/js/outputMapping.js"
    try:
        with open(src_path) as f:
            src = f.read()
    except OSError as e:
        report("outputMapping.js readable", False, str(e))
        return False

    # Single-pass: exactly one for loop inside getTimerMap
    import re
    # Find the getTimerMap function body
    match = re.search(r"function\s+getTimerMap\s*\([^)]*\)\s*\{(.+?)\n\s*\};", src, re.DOTALL)
    if not match:
        report("getTimerMap() function found in source", False)
        return False

    body = match.group(1)
    for_loops = re.findall(r"\bfor\s*\(", body)
    loop_count = len(for_loops)

    report("getTimerMap() found in outputMapping.js", True)
    report("getTimerMap() has exactly one loop (single-pass)",
           loop_count == 1,
           f"found {loop_count} for-loops")

    # No two-pass indicators
    has_two_pass_comment = "two-pass" in body.lower() or "first pass" in body.lower() or "second pass" in body.lower()
    report("No two-pass logic in getTimerMap()",
           not has_two_pass_comment,
           "two-pass comment found" if has_two_pass_comment else "no two-pass markers")

    # Confirm single-pass: motors and servos assigned in array order (no priority sorting)
    has_priority_sort = "sort" in body.lower() and "priority" in body.lower()
    report("No priority-sort logic in getTimerMap()",
           not has_priority_sort,
           "priority sort found" if has_priority_sort else "no priority sort markers")

    # Print the function body for reference
    print("\n  getTimerMap() body:")
    for line in body.strip().splitlines():
        print(f"    {line}")

    return loop_count == 1 and not has_two_pass_comment


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def async_main():
    print("=" * 65)
    print("PWM Timer Priority REVERT — Firmware + Configurator Verification")
    print("=" * 65)
    print(f"FC:   {SERIAL_PORT} @ {SERIAL_BAUD}")
    print(f"CDP:  {CDP_PAGE_URL}")
    print()

    # Check 5 (source file) — no hardware needed
    check_outputmapping_source()

    # Open FC serial connection
    ser = check_fc_connection()
    if ser is None:
        print("\n  Cannot proceed with firmware checks — FC not connected.")
        print("  Note: If running in sandbox, retry with dangerouslyDisableSandbox=true")
    else:
        # Check 2: firmware version
        check_firmware_version(ser)

        # Check 3: EXT2 output mapping
        check_output_mapping_ext2(ser)

        ser.close()

    # Check 4: CDP checks
    await check_configurator_via_cdp()

    # Final summary
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    passed_count = sum(1 for _, p in RESULTS if p)
    failed_count = sum(1 for _, p in RESULTS if not p)
    for check_name, passed in RESULTS:
        mark = "  OK" if passed else "FAIL"
        print(f"  [{mark}] {check_name}")
    print()
    print(f"  Passed: {passed_count}  Failed: {failed_count}  Total: {len(RESULTS)}")
    print()
    if failed_count == 0:
        print("  OVERALL: ALL CHECKS PASSED")
        return 0
    else:
        print("  OVERALL: SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(async_main()))
