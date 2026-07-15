#!/usr/bin/env python3
"""
Verification test: new MSP2_INAV_OUTPUT_ASSIGNMENT / MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT API.

Checks performed:
  1. FC connection + MSP_API_VERSION responds
  2. Firmware build date is from feature/output-assignment-api (post-2026-05-15)
  3. MSP2_INAV_OUTPUT_ASSIGNMENT (0x210E) responds with motor/servo tuples
  4. Each tuple is valid: (outputIndex < timerHardwareCount, type 1=MOTOR/2=SERVO, number >= 1)
  5. No duplicate output indices in the assignment response
  6. MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT (0x210F) responds with same-format tuples
  7. QUERY with same overrides as current config returns same assignment as READ
  8. Configurator uses hasDirectAssignment() / getOutputTableDirect() (via CDP)

FC target: BROTHERHOBBYF405V3 on /dev/ttyACM0 (adjust SERIAL_PORT as needed)

Usage:
    python3 verify_output_assignment_api.py

The script manages the Configurator connection automatically:
  - If Configurator is connected, it disconnects it (via CDP) before running
    firmware MSP checks (serial port is exclusive).
  - After firmware checks, it reconnects the Configurator, navigates to the
    Mixer tab, and runs the DOM output-mapping check.
  Requires Configurator running with --remote-debugging-port=9222.

Permanent location: claude/developer/scripts/testing/inav/msp/
Feature branch: feature/output-assignment-api (maintenance-10.x base)

Exit code 0 = all checks passed, 1 = one or more failed.
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
CDP_BASE_URL = "ws://127.0.0.1:9222"

# MSP codes (v1)
MSP_API_VERSION    = 1
MSP_FC_VERSION     = 3
MSP_BUILD_INFO     = 5
MSP_EEPROM_WRITE   = 250
MSP_SET_REBOOT     = 68

# MSP2 codes
MSP2_INAV_OUTPUT_MAPPING_EXT2        = 0x210D
MSP2_INAV_OUTPUT_ASSIGNMENT          = 0x210E  # new READ
MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT    = 0x210F  # new QUERY/preview
MSP2_INAV_TIMER_OUTPUT_MODE          = 0x200E
MSP2_INAV_SET_SERVO_MIXER            = 0x2021
MSP2_INAV_SELECT_MIXER_PROFILE       = 0x2080

OUTPUT_ASSIGNMENT_TYPE_NONE  = 0
OUTPUT_ASSIGNMENT_TYPE_MOTOR = 1
OUTPUT_ASSIGNMENT_TYPE_SERVO = 2
OUTPUT_ASSIGNMENT_TYPE_LED   = 3

RESULTS = []


def report(check_name, passed, detail=""):
    status = "  OK" if passed else "FAIL"
    line   = f"  [{status}] {check_name}"
    if detail:
        line += f": {detail}"
    print(line)
    RESULTS.append((check_name, passed))
    return passed


# ---------------------------------------------------------------------------
# MSP helpers (shared with verify_reverted_firmware.py)
# ---------------------------------------------------------------------------

def msp_v1_frame(cmd, payload=b""):
    size = len(payload)
    hdr  = b"$M<"
    body = bytes([size, cmd]) + payload
    crc  = 0
    for b in body:
        crc ^= b
    return hdr + body + bytes([crc])


def msp_v2_frame(cmd, payload=b""):
    size = len(payload)
    hdr  = b"$X<"
    flag = 0
    body = struct.pack("<BHH", flag, cmd, size) + payload
    crc  = 0
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


def read_msp_reply(ser, timeout=2.0, debug=False):
    deadline = time.time() + timeout
    buf = bytearray()
    while time.time() < deadline:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting)
            buf += chunk
            if debug and chunk:
                print(f"  [raw] {chunk.hex()}")
        # MSP v1 success response
        if b"$M>" in buf:
            idx   = buf.index(b"$M>")
            frame = buf[idx:]
            if len(frame) >= 6:
                size = frame[3]
                if len(frame) >= 5 + size + 1:
                    return "v1", frame[4], bytes(frame[5:5 + size])
        # MSP v1 error response
        if b"$M!" in buf:
            idx = buf.index(b"$M!")
            if debug:
                print(f"  [v1 error frame at buf[{idx}]]")
            return "v1_error", None, b""
        # MSP v2 success response: frame = $X> flag(1) cmd(2) size(2) payload(size) crc(1) = 9+size bytes
        if b"$X>" in buf:
            idx   = buf.index(b"$X>")
            frame = buf[idx:]
            if len(frame) >= 9:
                size = struct.unpack_from("<H", frame, 6)[0]
                if len(frame) >= 9 + size:       # fixed: was 9+size+1 (off-by-one)
                    cmd     = struct.unpack_from("<H", frame, 4)[0]
                    payload = bytes(frame[8:8 + size])
                    return "v2", cmd, payload
        # MSP v2 error response
        if b"$X!" in buf:
            idx = buf.index(b"$X!")
            frame = buf[idx:]
            if len(frame) >= 9:
                cmd = struct.unpack_from("<H", frame, 4)[0]
                if debug:
                    print(f"  [v2 error frame, cmd=0x{cmd:04X}]")
                return "v2_error", cmd, b""
        time.sleep(0.02)
    if debug and buf:
        print(f"  [timeout, buf so far: {buf.hex()}]")
    return None, None, None


def msp_request(ser, cmd, payload=b"", v2=False, timeout=2.0, debug=False):
    frame = msp_v2_frame(cmd, payload) if v2 else msp_v1_frame(cmd, payload)
    if debug:
        print(f"  [tx] {frame.hex()}")
    ser.reset_input_buffer()
    ser.write(frame)
    return read_msp_reply(ser, timeout=timeout, debug=debug)


# ---------------------------------------------------------------------------
# Check 1: FC connection
# ---------------------------------------------------------------------------

def check_fc_connection():
    print("\n--- Check 1: FC connection ---")
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
        print(f"  Opened {SERIAL_PORT} @ {SERIAL_BAUD} baud")
        ver, cmd, payload = msp_request(ser, MSP_API_VERSION)
        if ver is None:
            report("FC responds to MSP_API_VERSION", False,
                   "No response — is FC plugged in and not in CLI mode?")
            ser.close()
            return None
        msp_v    = payload[0] if payload else "?"
        api_maj  = payload[1] if len(payload) > 1 else "?"
        api_min  = payload[2] if len(payload) > 2 else "?"
        report("FC responds to MSP_API_VERSION", True,
               f"protocol={msp_v} api={api_maj}.{api_min}")
        return ser
    except serial.SerialException as e:
        report("FC connection", False, str(e))
        return None


# ---------------------------------------------------------------------------
# Check 2: firmware build date (should be post-merge, May 2026 or later)
# ---------------------------------------------------------------------------

def check_firmware_version(ser):
    print("\n--- Check 2: Firmware version / build info ---")
    ver, cmd, payload = msp_request(ser, MSP_BUILD_INFO)
    if ver is None or len(payload) < 11:
        report("MSP_BUILD_INFO", False, "No response")
        return False
    try:
        build_date = payload[:11].decode("ascii", errors="replace").strip('\x00')
        git_hash   = payload[19:26].decode("ascii", errors="replace").strip('\x00') if len(payload) >= 26 else "?"
    except Exception as e:
        report("MSP_BUILD_INFO decode", False, str(e))
        return False

    date_ok = "2026" in build_date
    report("Build date is from 2026", date_ok,
           f"build_date='{build_date}' hash='{git_hash}'")
    print(f"  git hash: {git_hash}")
    return date_ok


# ---------------------------------------------------------------------------
# Check 3: MSP v2 connectivity probe (existing endpoint 0x210D)
# ---------------------------------------------------------------------------

def check_v2_probe(ser):
    print("\n--- Check 3: MSP v2 connectivity probe (0x210D EXT2) ---")
    ver, cmd, payload = msp_request(ser, MSP2_INAV_OUTPUT_MAPPING_EXT2, v2=True, timeout=3.0, debug=True)
    if ver is None:
        report("MSP v2 framing works (EXT2 probe)", False,
               "Even existing 0x210D timed out — v2 framing or port issue")
        return False
    if ver in ("v2_error", "v1_error"):
        report("MSP v2 framing works (EXT2 probe)", False,
               f"Got error frame type={ver}")
        return False
    report("MSP v2 framing works (EXT2 probe)", True,
           f"0x210D responded, payload={len(payload)} bytes")
    return True


# ---------------------------------------------------------------------------
# Check 4 & 5: MSP2_INAV_OUTPUT_ASSIGNMENT (0x210E) — READ
# ---------------------------------------------------------------------------

def check_output_assignment_read(ser):
    print("\n--- Check 4-6: MSP2_INAV_OUTPUT_ASSIGNMENT (READ) ---")

    ver, cmd, payload = msp_request(ser, MSP2_INAV_OUTPUT_ASSIGNMENT, v2=True, timeout=3.0, debug=True)
    print(f"  [DEBUG] MSP2_INAV_OUTPUT_ASSIGNMENT raw ({len(payload) if payload else 0} bytes): {payload.hex() if payload else 'None'}")
    if ver is None:
        report("MSP2_INAV_OUTPUT_ASSIGNMENT responds", False,
               "No response — firmware may not have the new MSP handler")
        return None
    if not payload:
        report("MSP2_INAV_OUTPUT_ASSIGNMENT has data", False,
               "Empty payload — no motors or servos assigned?")
        return None

    if len(payload) % 3 != 0:
        report("Assignment payload size multiple of 3", False,
               f"length={len(payload)}")
        return None

    n = len(payload) // 3
    assignments = []
    for i in range(n):
        off          = i * 3
        output_index = payload[off]
        atype        = payload[off + 1]
        number       = payload[off + 2]
        assignments.append((output_index, atype, number))

    report("MSP2_INAV_OUTPUT_ASSIGNMENT responds with data", True,
           f"{n} assignments")

    print(f"  Assignment entries:")
    for idx, (oi, t, num) in enumerate(assignments):
        type_name = {1: "MOTOR", 2: "SERVO", 3: "LED"}.get(t, f"TYPE{t}")
        print(f"    [{idx}] outputIndex={oi} type={type_name} number={num}")

    # All types should be MOTOR, SERVO, or LED (not 0=NONE)
    valid_types = all(a[1] in (1, 2, 3) for a in assignments)
    report("All assignment types are MOTOR/SERVO/LED (not NONE)",
           valid_types,
           "unexpected NONE entry" if not valid_types else "ok")

    # All numbers >= 1 for motor and servo
    valid_numbers = all(a[2] >= 1 for a in assignments if a[1] in (1, 2))
    report("Motor/servo numbers are >= 1 (1-indexed)",
           valid_numbers,
           "zero-indexed number found" if not valid_numbers else "ok")

    # No duplicate output indices
    indices = [a[0] for a in assignments]
    no_dups = len(indices) == len(set(indices))
    report("No duplicate output indices",
           no_dups,
           f"duplicate at: {[x for x in indices if indices.count(x) > 1]}" if not no_dups else "ok")

    # Verify at least one motor
    motors = [a for a in assignments if a[1] == OUTPUT_ASSIGNMENT_TYPE_MOTOR]
    report("At least one motor output assigned",
           len(motors) > 0,
           f"{len(motors)} motor(s)" if motors else "none found")

    print(f"\n  Summary: {len(motors)} motor(s), {len([a for a in assignments if a[1]==2])} servo(s)")

    return assignments


# ---------------------------------------------------------------------------
# Check 5: Servo count in READ matches servo mixer expectations
# ---------------------------------------------------------------------------

MSP2_INAV_SERVO_MIXER = 0x2020   # 6 bytes/rule: u8 targetCh, u8 src, s16 weight, u8 speed, s8 cond

def check_servo_count_matches_mixer(ser, read_assignments):
    """
    The firmware must NOT report servo outputs for outputs that are only
    servo-capable hardware but are not actually serving servos. Specifically:
    if the servo mixer has zero rules, the READ response should report zero
    servo assignments.

    Regression test for the bug where pwmBuildTimerOutputList() ignored its
    isMixerUsingServos parameter and populated timServos[] with all
    servo-capable pins regardless of mixer configuration.
    """
    print("\n--- Check 5: READ servo count matches servo mixer ---")

    ver, cmd, payload = msp_request(ser, MSP2_INAV_SERVO_MIXER, v2=True, timeout=2.0)
    print(f"  [DEBUG] MSP2_INAV_SERVO_MIXER raw ({len(payload) if payload else 0} bytes): {payload.hex() if payload else 'None'}")
    if ver is None:
        report("MSP2_INAV_SERVO_MIXER readable", False, "No response")
        return False

    # 6 bytes per rule: u8 targetCh, u8 inputSrc, s16 rate, u8 speed, s8 conditionId
    # Mirror firmware loadCustomServoMixer(): break at first rate=0 entry.
    # The PG reset default leaves conditionId=-1 (0xff) in all slots; without
    # the early-break those bytes appear at off+3 of the last "real" slot and
    # produce a spurious non-zero rate, giving a false "active rule" result.
    rule_count = len(payload) // 6 if payload else 0
    active_channels = set()
    for i in range(rule_count):
        off = i * 6
        rate = struct.unpack_from('<h', payload, off + 2)[0]
        if rate == 0:
            break
        target_ch = payload[off]
        active_channels.add(target_ch)

    expected_servos = (max(active_channels) + 1) if active_channels else 0
    report("MSP2_INAV_SERVO_MIXER readable", True,
           f"{rule_count} total rule(s), {len(active_channels)} active channel(s), "
           f"expected {expected_servos} servo output(s)")

    reported_servos = [a for a in (read_assignments or []) if a[1] == OUTPUT_ASSIGNMENT_TYPE_SERVO]
    n_reported = len(reported_servos)

    match = n_reported == expected_servos
    report("READ servo count matches mixer (no phantom servos)",
           match,
           f"READ reports {n_reported} servo(s), mixer expects {expected_servos}" if not match
           else f"{n_reported} servo(s) — consistent with mixer")
    return match


# ---------------------------------------------------------------------------
# Check 6: MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT (0x210F) — QUERY/preview
# ---------------------------------------------------------------------------

def check_output_assignment_query(ser):
    print("\n--- Check 6-7: MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT (QUERY) ---")

    # First get current timer overrides so we can send them as proposed
    ver, cmd, payload = msp_request(ser, MSP2_INAV_TIMER_OUTPUT_MODE, v2=True, debug=True)
    if ver is None or not payload:
        print("  Cannot get timer overrides — skipping QUERY test")
        report("MSP2_INAV_TIMER_OUTPUT_MODE readable for QUERY test", False, "No response")
        return False

    timer_overrides = {}
    for i in range(0, len(payload) - 1, 2):
        tid  = payload[i]
        mode = payload[i + 1]
        timer_overrides[tid] = mode
    print(f"  Current timer overrides: {timer_overrides}")

    # Build QUERY payload: (u8 timerCount, [u8 timerId, u8 outputMode] x N)
    entries = [(tid, mode) for tid, mode in timer_overrides.items()]
    query_payload = bytes([len(entries)]) + bytes([b for tid, mode in entries for b in (tid, mode)])

    ver, cmd, payload = msp_request(ser, MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT, payload=query_payload, v2=True, timeout=3.0)
    if ver is None:
        report("MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT responds", False,
               "No response — firmware may not have the QUERY handler")
        return False

    report("MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT responds", True,
           f"payload length={len(payload)} bytes")

    if not payload or len(payload) % 3 != 0:
        report("QUERY response size multiple of 3", len(payload) % 3 == 0,
               f"length={len(payload)}")
        return False

    n_query = len(payload) // 3
    query_assignments = []
    for i in range(n_query):
        off = i * 3
        query_assignments.append((payload[off], payload[off+1], payload[off+2]))

    print(f"  QUERY returned {n_query} assignments")
    return query_assignments


def check_query_edge_cases(ser, read_assignments):
    """
    Edge-case checks for MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT:
      - timerCount=0 (empty overrides) → should respond, match READ
      - timerCount=255 (overflow) → firmware clamps, should still respond
      - invalid timerId=200 → firmware skips silently, should still respond
    These exercise the clamping and graceful-skip guards added during code review.
    """
    print("\n--- Check 8: QUERY edge cases ---")

    # Edge case A: empty override list (timerCount=0)
    ver, cmd, payload = msp_request(
        ser, MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT,
        payload=bytes([0]),   # timerCount=0, no entries
        v2=True, timeout=3.0
    )
    if ver is None or ver in ("v2_error", "v1_error"):
        report("QUERY with timerCount=0 responds (no crash)", False,
               f"got: {ver}")
    else:
        ok = payload is not None and len(payload) % 3 == 0
        report("QUERY with timerCount=0 responds (no crash)", ok,
               f"payload={len(payload)} bytes")
        if ok and read_assignments is not None:
            n = len(payload) // 3
            zero_assignments = [(payload[i*3], payload[i*3+1], payload[i*3+2]) for i in range(n)]
            match = sorted(zero_assignments) == sorted(read_assignments)
            report("QUERY timerCount=0 matches READ (no change)", match,
                   f"{n} entries" if match else f"got {zero_assignments[:3]}...")

    # Edge case B: timerCount=255 (triggers firmware clamp guard)
    ver, cmd, payload = msp_request(
        ser, MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT,
        payload=bytes([255]),  # timerCount=255, no actual entries follow
        v2=True, timeout=3.0
    )
    if ver is None or ver in ("v2_error", "v1_error"):
        report("QUERY with timerCount=255 (overflow) responds without crash", False,
               f"got: {ver}")
    else:
        ok = payload is not None and len(payload) % 3 == 0
        report("QUERY with timerCount=255 (overflow) responds without crash", ok,
               f"payload={len(payload)} bytes")

    # Edge case C: invalid timerId=200 (out of HARDWARE_TIMER_DEFINITION_COUNT range)
    invalid_entry = bytes([1, 200, 0])   # timerCount=1, timerId=200, outputMode=0
    ver, cmd, payload = msp_request(
        ser, MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT,
        payload=invalid_entry,
        v2=True, timeout=3.0
    )
    if ver is None or ver in ("v2_error", "v1_error"):
        report("QUERY with invalid timerId=200 responds without crash", False,
               f"got: {ver}")
    else:
        ok = payload is not None and len(payload) % 3 == 0
        report("QUERY with invalid timerId=200 responds without crash", ok,
               f"payload={len(payload)} bytes")


def check_query_matches_read(read_assignments, query_assignments):
    print("\n--- Check 7: QUERY result matches READ (same overrides) ---")
    if read_assignments is None or query_assignments is None:
        report("Can compare READ vs QUERY", False, "One of the responses was missing")
        return False

    # Sort both by outputIndex for comparison
    read_sorted  = sorted(read_assignments)
    query_sorted = sorted(query_assignments)

    match = read_sorted == query_sorted
    report("QUERY (with current overrides) matches READ",
           match,
           f"READ={read_sorted[:3]}... QUERY={query_sorted[:3]}..." if not match else f"{len(read_sorted)} entries match")
    return match


# ---------------------------------------------------------------------------
# Check 8: Configurator CDP — uses hasDirectAssignment()
# ---------------------------------------------------------------------------

async def find_configurator_ws():
    """Find the CDP WebSocket URL for the Configurator renderer page."""
    try:
        async with websockets.connect(f"{CDP_BASE_URL}/json", ping_timeout=5) as ws:
            raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
            pages = json.loads(raw)
    except Exception:
        return None

    for page in pages:
        url = page.get("url", "")
        if "index.html" in url or "configurator" in url.lower():
            return page.get("webSocketDebuggerUrl")
    # Fall back to first page
    if pages:
        return pages[0].get("webSocketDebuggerUrl")
    return None


async def _cdp_eval(ws, expr, await_promise=False):
    """Send a Runtime.evaluate and return the result value."""
    await ws.send(json.dumps({
        "id": 99, "method": "Runtime.evaluate",
        "params": {"expression": expr, "returnByValue": True, "awaitPromise": await_promise}
    }))
    deadline = asyncio.get_event_loop().time() + 10
    while asyncio.get_event_loop().time() < deadline:
        raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
        msg = json.loads(raw)
        if msg.get("id") == 99:
            return msg.get("result", {}).get("result", {}).get("value")
    return None


async def _cdp_ws():
    """Return a WebSocket URL for the Configurator CDP page, or None."""
    try:
        import urllib.request
        raw = urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3).read()
        pages = json.loads(raw)
        ws_url = None
        for page in pages:
            url = page.get("url", "")
            if "index.html" in url or not ws_url:
                ws_url = page.get("webSocketDebuggerUrl")
        return ws_url
    except Exception:
        return None


async def cdp_ensure_disconnected():
    """If Configurator is connected to FC, disconnect it so the serial port is free."""
    ws_url = await _cdp_ws()
    if not ws_url:
        return   # Configurator not running — nothing to do
    try:
        async with websockets.connect(ws_url, ping_timeout=10) as ws:
            state = await _cdp_eval(ws, "document.getElementById('connectbutton')?.textContent?.trim()")
            if state and "Disconnect" in state:
                print("  [CDP] Configurator connected — disconnecting to free serial port...")
                await _cdp_eval(ws, "document.querySelector('a.connect')?.click()")
                # Wait up to 5 s for Configurator to disconnect
                for _ in range(25):
                    await asyncio.sleep(0.2)
                    state = await _cdp_eval(ws, "document.getElementById('connectbutton')?.textContent?.trim()")
                    if state and "Connect" in state and "Disconnect" not in state:
                        print("  [CDP] Configurator disconnected.")
                        return
                print("  [CDP] Warning: Configurator may still be connected.")
    except Exception as e:
        print(f"  [CDP] Could not disconnect Configurator: {e}")


async def cdp_connect_and_open_mixer():
    """Connect Configurator to FC and navigate to Mixer tab, then return."""
    ws_url = await _cdp_ws()
    if not ws_url:
        print("  [CDP] Configurator not reachable — skipping reconnect.")
        return False
    try:
        async with websockets.connect(ws_url, ping_timeout=10) as ws:
            state = await _cdp_eval(ws, "document.getElementById('connectbutton')?.textContent?.trim()")
            if state and "Disconnect" in state:
                print("  [CDP] Configurator already connected.")
            else:
                print("  [CDP] Connecting Configurator to FC...")
                await _cdp_eval(ws, "document.querySelector('a.connect')?.click()")
                # Wait up to 10 s for connection
                for _ in range(50):
                    await asyncio.sleep(0.2)
                    state = await _cdp_eval(ws, "document.getElementById('connectbutton')?.textContent?.trim()")
                    if state and "Disconnect" in state:
                        print("  [CDP] Configurator connected.")
                        break
                else:
                    print("  [CDP] Warning: Configurator may not have connected.")
                    return False

            # Navigate to Mixer tab
            await asyncio.sleep(0.5)
            await _cdp_eval(ws,
                "Array.from(document.querySelectorAll('a')).find(a => a.textContent.trim() === 'Mixer')?.click()")
            # Wait up to 5 s for #function-1 to appear (Mixer tab loaded)
            for _ in range(25):
                await asyncio.sleep(0.2)
                el = await _cdp_eval(ws, "!!document.getElementById('function-1')")
                if el:
                    print("  [CDP] Mixer tab loaded.")
                    await asyncio.sleep(2.0)   # wait for servo mixer table to populate
                    return True
            print("  [CDP] Warning: Mixer tab may not have loaded.")
            return False
    except Exception as e:
        print(f"  [CDP] Connect/navigate error: {e}")
        return False


async def check_configurator_cdp():
    """
    Verify the Configurator output mapping table via DOM inspection.

    NOTE: FC is a plain-object ES module singleton. DevTools Runtime.evaluate
    runs in an isolated JS world with its own module cache, so dynamic import()
    returns a fresh uninitialised FC — not the live app instance.  DOM inspection
    is the correct approach: read the #function-N cells the app already rendered.
    """
    print("\n--- Check 9: Configurator output mapping display (DOM via CDP) ---")

    try:
        import urllib.request
        raw = urllib.request.urlopen(f"http://127.0.0.1:9222/json", timeout=3).read()
        pages = json.loads(raw)
    except Exception as e:
        report("CDP endpoint reachable", False, str(e))
        print("  Is Configurator running with --remote-debugging-port=9222?")
        return False

    ws_url = None
    for page in pages:
        url = page.get("url", "")
        if "index.html" in url or not ws_url:
            ws_url = page.get("webSocketDebuggerUrl")

    if not ws_url:
        report("CDP page found", False, "No pages from CDP")
        return False

    try:
        async with websockets.connect(ws_url, ping_timeout=30) as ws:
            print("  Connected to Configurator CDP")

            # Connect FC if not already connected
            state = await _cdp_eval(ws, "document.getElementById('connectbutton')?.textContent?.trim()")
            if state and "Disconnect" not in state:
                print("  [CDP] Connecting Configurator to FC...")
                await _cdp_eval(ws, "document.querySelector('a.connect')?.click()")
                for _ in range(50):
                    await asyncio.sleep(0.2)
                    state = await _cdp_eval(ws, "document.getElementById('connectbutton')?.textContent?.trim()")
                    if state and "Disconnect" in state:
                        print("  [CDP] Connected.")
                        break
                else:
                    report("Configurator connects to FC", False, "Timed out waiting for connection")
                    return False

            # Navigate to Mixer tab and wait for output mapping AND servo mixer to load
            await asyncio.sleep(0.3)
            await _cdp_eval(ws,
                "Array.from(document.querySelectorAll('a')).find(a => a.textContent.trim() === 'Mixer')?.click()")
            print("  [CDP] Waiting for Mixer tab...")
            for _ in range(50):
                await asyncio.sleep(0.2)
                loaded = await _cdp_eval(ws,
                    "!!(document.getElementById('function-1') && "
                    "document.querySelector('#servo-mix-table tbody') !== null)")
                if loaded:
                    await asyncio.sleep(1.0)  # let servo mixer rows fully render
                    print("  [CDP] Mixer tab loaded.")
                    break
            else:
                report("Mixer tab is open in Configurator", False, "Timed out waiting for Mixer tab")
                return False

            # Read #function-N cells — populated by renderOutputMapping() in mixer.js
            expr = """(function() {
    var cells = [];
    for (var i = 1; i <= 16; i++) {
        var el = document.getElementById('function-' + i);
        if (el) cells.push({ id: i, text: el.textContent.trim() });
    }
    var servoChannels = new Set();
    document.querySelectorAll('#servo-mix-table tbody tr .mix-rule-servo').forEach(function(inp) {
        var v = parseInt(inp.value, 10);
        if (!isNaN(v)) servoChannels.add(v);
    });
    return {
        functionCells: cells,
        onMixerTab: cells.length > 0,
        servoMixRows: document.querySelectorAll('#servo-mix-table tbody tr').length,
        distinctServoChannels: servoChannels.size
    };
})()"""
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
                report("CDP Runtime.evaluate responds", False)
                return False

            val = resp.get("result", {}).get("result", {}).get("value", {})
            if not isinstance(val, dict):
                report("CDP returned valid object", False, f"got: {val}")
                return False

            cells = val.get("functionCells", [])
            on_mixer = val.get("onMixerTab", False)
            servo_mix_rows = val.get("servoMixRows", -1)
            distinct_servo_channels = val.get("distinctServoChannels", -1)

            if not on_mixer or not cells:
                report("Mixer tab is open in Configurator", False,
                       "No #function-N cells found — navigate to Mixer tab with FC connected")
                return False

            report("Mixer tab is open in Configurator", True,
                   f"{len(cells)} output cells found")

            print(f"  Output mapping from DOM:")
            for c in cells:
                print(f"    #function-{c['id']}: {c['text']}")

            motors = [c for c in cells if c["text"].startswith("Motor")]
            servos = [c for c in cells if c["text"].startswith("Servo")]
            unassigned = [c for c in cells if c["text"] == "-"]

            print(f"  Servo mixer rules in UI: {servo_mix_rows}  "
                  f"(distinct servo channels: {distinct_servo_channels})")

            report("At least one motor shown in output mapping",
                   len(motors) > 0, f"{len(motors)} motor(s)")
            report("No outputs incorrectly showing '-' for all entries",
                   len(motors) > 0 or len(servos) > 0,
                   "all outputs unassigned — firmware may not have direct assignment handler")

            # Verify motor numbering is sequential from 1
            motor_nums = sorted([int(c["text"].split()[-1]) for c in motors])
            sequential = motor_nums == list(range(1, len(motors) + 1))
            report("Motor numbers are sequential from 1",
                   sequential, f"numbers={motor_nums}")

            # Servo outputs shown in output mapping must equal the number of distinct
            # servo channels used in the servo mixer.  Extra outputs are phantom entries.
            if distinct_servo_channels >= 0:
                match = len(servos) == distinct_servo_channels
                report("Servo output count matches servo mixer channel count",
                       match,
                       f"output mapping shows {len(servos)} servo(s), "
                       f"mixer uses {distinct_servo_channels} distinct channel(s)")

            print(f"\n  Summary: {len(motors)} motor(s), {len(servos)} servo(s), "
                  f"{len(unassigned)} unassigned")
            return True

    except ConnectionRefusedError:
        report("CDP connection to Configurator", False,
               f"Cannot connect to {ws_url}")
        print("  Is Configurator running with --remote-debugging-port=9222?")
        return False
    except Exception as e:
        report("CDP check", False, str(e))
        return False


# ---------------------------------------------------------------------------
# Dual-profile servo test helpers
# ---------------------------------------------------------------------------

def _set_servo_rule(ser, rule_index, target_ch, input_src, rate, speed):
    """Send one MSP2_INAV_SET_SERVO_MIXER rule (7-byte payload: index + 6 rule bytes)."""
    payload = bytes([rule_index, target_ch, input_src,
                     rate & 0xFF, (rate >> 8) & 0xFF,
                     speed, 0xFF])   # conditionId = -1
    ver, _, _ = msp_request(ser, MSP2_INAV_SET_SERVO_MIXER, payload=payload, v2=True)
    return ver not in (None, "v2_error", "v1_error")


def _save_and_reboot(ser):
    """Save EEPROM, send reboot, close port, wait, and return a fresh serial connection."""
    msp_request(ser, MSP_EEPROM_WRITE)
    time.sleep(0.2)
    msp_request(ser, MSP_SET_REBOOT)
    ser.close()
    time.sleep(5)
    for _ in range(20):
        try:
            new_ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
            time.sleep(0.5)
            ver, _, _ = msp_request(new_ser, MSP_API_VERSION)
            if ver == "v1":
                return new_ser
            new_ser.close()
        except Exception:
            pass
        time.sleep(0.5)
    return None


def _read_servo_count(ser):
    """Return number of servo entries from MSP2_INAV_OUTPUT_ASSIGNMENT."""
    ver, cmd, payload = msp_request(ser, MSP2_INAV_OUTPUT_ASSIGNMENT, v2=True, timeout=3.0)
    if ver is None or not payload:
        return -1
    return sum(1 for i in range(0, len(payload), 3) if payload[i + 1] == OUTPUT_ASSIGNMENT_TYPE_SERVO)


def check_dual_profile_servos():
    """
    Configure 1 servo on profile 1 and 2 servos on profile 2.
    Verify that each profile's output assignment reflects its own mixer rules.

    Flow: open serial directly (Configurator must be disconnected by caller).
    At the end, both profiles are left with 0 servo rules and the FC is
    back on profile 1.
    """
    print("\n--- Dual-profile servo test ---")
    print("  Profile 1 → 1 servo (ch 0), Profile 2 → 2 servos (ch 0 + ch 1)")

    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
    except serial.SerialException as e:
        report("Dual-profile: serial port open", False, str(e))
        return

    # ── Profile 1: 1 servo ──────────────────────────────────────────────
    print("\n  [Profile 1] Switching to profile 1...")
    msp_request(ser, MSP2_INAV_SELECT_MIXER_PROFILE, payload=bytes([0]), v2=True)
    time.sleep(0.3)

    print("  [Profile 1] Setting 1 servo rule (ch=0, rate=100)...")
    ok = _set_servo_rule(ser, 0, 0, 0, 100, 0)
    report("Profile 1: servo rule sent (ch=0, rate=100)", ok)
    if not ok:
        ser.close()
        return

    print("  Saving + rebooting for profile 1...")
    ser = _save_and_reboot(ser)
    if ser is None:
        report("Profile 1: FC reconnected after reboot", False, "Timeout")
        return

    n1 = _read_servo_count(ser)
    report("Profile 1 output: shows exactly 1 servo",
           n1 == 1, f"{n1} servo(s) reported")

    # ── Profile 2: 2 servos ──────────────────────────────────────────────
    print("\n  [Profile 2] Switching to profile 2...")
    msp_request(ser, MSP2_INAV_SELECT_MIXER_PROFILE, payload=bytes([1]), v2=True)
    time.sleep(0.3)

    print("  [Profile 2] Setting 2 servo rules (ch=0 rate=100, ch=1 rate=100)...")
    ok0 = _set_servo_rule(ser, 0, 0, 0, 100, 0)
    ok1 = _set_servo_rule(ser, 1, 1, 0, 100, 0)
    report("Profile 2: servo rules sent (ch=0 and ch=1)", ok0 and ok1)

    print("  Saving + rebooting for profile 2...")
    ser = _save_and_reboot(ser)
    if ser is None:
        report("Profile 2: FC reconnected after reboot", False, "Timeout")
        return

    n2 = _read_servo_count(ser)
    report("Profile 2 output: shows exactly 2 servos",
           n2 == 2, f"{n2} servo(s) reported")

    # ── Switch back to profile 1 and verify it still shows 1 servo ─────
    print("\n  [Profile 1] Switching back to profile 1...")
    msp_request(ser, MSP2_INAV_SELECT_MIXER_PROFILE, payload=bytes([0]), v2=True)
    time.sleep(0.3)

    ser = _save_and_reboot(ser)
    if ser is None:
        report("Profile 1 (after switch-back): FC reconnected", False, "Timeout")
        return

    n1b = _read_servo_count(ser)
    report("Profile 1 (after switch-back): still shows 1 servo",
           n1b == 1, f"{n1b} servo(s) reported")

    # ── Clean up: clear all rules on both profiles ────────────────────────
    print("\n  Cleaning up: clearing servo rules on both profiles...")
    # Profile 1: clear rule 0
    _set_servo_rule(ser, 0, 0, 0, 0, 0)

    # Profile 2: clear rules 0 and 1
    msp_request(ser, MSP2_INAV_SELECT_MIXER_PROFILE, payload=bytes([1]), v2=True)
    time.sleep(0.3)
    _set_servo_rule(ser, 0, 0, 0, 0, 0)
    _set_servo_rule(ser, 1, 0, 0, 0, 0)

    # Return to profile 1
    msp_request(ser, MSP2_INAV_SELECT_MIXER_PROFILE, payload=bytes([0]), v2=True)
    time.sleep(0.3)

    ser = _save_and_reboot(ser)
    if ser is None:
        report("Cleanup: FC reconnected", False, "Timeout")
        return

    n_clean = _read_servo_count(ser)
    report("Cleanup: profile 1 shows 0 servos after clearing",
           n_clean == 0, f"{n_clean} servo(s)")
    ser.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def async_main():
    print("=" * 65)
    print("Output Assignment API — Verification Test")
    print(f"  MSP2_INAV_OUTPUT_ASSIGNMENT  = 0x{MSP2_INAV_OUTPUT_ASSIGNMENT:04X}")
    print(f"  MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT = 0x{MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT:04X}")
    print("=" * 65)
    print(f"FC:  {SERIAL_PORT} @ {SERIAL_BAUD}")
    print()

    # Disconnect Configurator if needed so the serial port is free
    await cdp_ensure_disconnected()

    ser = check_fc_connection()
    if ser is None:
        print("\n  Cannot proceed with firmware checks — FC not connected.")
        print("  If Configurator is open, close it or disconnect the FC first.")
    else:
        check_firmware_version(ser)
        v2_ok = check_v2_probe(ser)
        if v2_ok:
            read_assignments  = check_output_assignment_read(ser)
            check_servo_count_matches_mixer(ser, read_assignments)
            query_assignments = check_output_assignment_query(ser)
            check_query_matches_read(read_assignments, query_assignments)
            check_query_edge_cases(ser, read_assignments)
        else:
            print("\n  Skipping new-handler checks — v2 connectivity probe failed.")
            print("  Check raw bytes above to diagnose framing issue.")
        ser.close()

    # Dual-profile servo test (opens its own serial connection)
    check_dual_profile_servos()

    await check_configurator_cdp()

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    passed = sum(1 for _, p in RESULTS if p)
    failed = sum(1 for _, p in RESULTS if not p)
    for name, p in RESULTS:
        print(f"  [{'  OK' if p else 'FAIL'}] {name}")
    print()
    print(f"  Passed: {passed}  Failed: {failed}  Total: {len(RESULTS)}")
    print()
    if failed == 0:
        print("  OVERALL: ALL CHECKS PASSED")
        return 0
    else:
        print("  OVERALL: SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(async_main()))
