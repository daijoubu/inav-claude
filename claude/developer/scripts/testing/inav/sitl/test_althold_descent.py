#!/usr/bin/env python3
"""
Altitude Hold Descent Behavior Regression Test

Tests whether copter DESCENDS (correct) or CLIMBS (bug) when throttle
stick is pushed below midpoint in NAV_ALTHOLD mode.

Test procedure:
1. Connect to SITL on port 5760 (or specified port)
2. Arm via MSP
3. Lift off to altitude
4. Enable NAV_ALTHOLD mode
5. Set throttle BELOW midpoint -> expect descent (negative variometer)
6. Set throttle ABOVE midpoint -> expect climb (positive variometer)
7. Set throttle AT midpoint -> expect hold (near-zero variometer)

Usage:
    python3 test_althold_descent.py [--tcp HOST:PORT]
    python3 test_althold_descent.py --tcp localhost:5760

NOTE: If running in sandbox, retry with dangerouslyDisableSandbox: true
      Network sockets may be blocked by default in sandbox.
"""

import sys
import time
import struct
import threading
import argparse

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MSP_API_VERSION    = 1
MSP_SET_RAW_RC     = 200
MSP_SET_RAW_GPS    = 201
MSP_RX_CONFIG      = 44
MSP_SET_RX_CONFIG  = 45
MSP_SET_MODE_RANGE = 35
MSP_EEPROM_WRITE   = 250
MSP_REBOOT         = 68
MSP_ALTITUDE       = 109
MSP_STATUS_EX      = 150
MSP_SIMULATOR      = 0x201F
MSP2_INAV_STATUS   = 0x2000

# Receiver type
RX_TYPE_MSP = 2

# Box permanent IDs
BOXARM         = 0
BOXANGLE       = 1
BOXNAVALTHOLD  = 3   # NAV ALTHOLD permanent ID

# HITL flags
HITL_ENABLE = (1 << 0)
SIMULATOR_MSP_VERSION = 2

# RC values
RC_LOW  = 1000
RC_MID  = 1500
RC_HIGH = 2000

# Throttle values for descent test
# Below midpoint (1200) -> should descend
THROTTLE_LOW_DESCENT  = 1200
# Above midpoint (1800) -> should climb
THROTTLE_HIGH_CLIMB   = 1800
# Midpoint (1500) -> should hold
THROTTLE_MID_HOLD     = 1500

PASS = "PASS"
FAIL = "FAIL"

results = []


def log(msg):
    print(msg, flush=True)


def record(label, result, detail=""):
    icon = "+" if result == PASS else "x"
    line = f"  [{icon}] {label}: {result}"
    if detail:
        line += f" -- {detail}"
    log(line)
    results.append((label, result, detail))


# ---------------------------------------------------------------------------
# Low-level MSP framing (uNAVlib / raw)
# ---------------------------------------------------------------------------

def build_msp_v1(cmd, data=None):
    """Build MSPv1 frame."""
    if data is None:
        data = []
    size = len(data)
    checksum = size ^ cmd
    for b in data:
        checksum ^= b
    frame = bytes([0x24, 0x4D, 0x3C, size, cmd]) + bytes(data) + bytes([checksum])
    return frame


def build_msp_v2(cmd, data=None):
    """Build MSPv2 frame for 16-bit command IDs."""
    if data is None:
        data = []
    payload = bytes(data)
    size = len(payload)
    # Header: $, X, <, flag, cmd_lo, cmd_hi, size_lo, size_hi
    header = bytes([0x24, 0x58, 0x3C, 0x00,
                    cmd & 0xFF, (cmd >> 8) & 0xFF,
                    size & 0xFF, (size >> 8) & 0xFF])
    # CRC over: flag, cmd_lo, cmd_hi, size_lo, size_hi, payload
    crc_data = header[3:] + payload
    crc = _crc8_dvb_s2(crc_data)
    return header + payload + bytes([crc])


def _crc8_dvb_s2(data):
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0xD5) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def read_msp_response(sock, timeout=1.0):
    """Read one MSP response frame from socket. Returns (cmd, data) or None."""
    import socket as _socket
    sock.settimeout(timeout)
    try:
        # Read until we get a valid frame
        buf = b""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                chunk = sock.recv(256)
                if not chunk:
                    break
                buf += chunk
            except _socket.timeout:
                break

        # Parse first valid frame from buffer
        i = 0
        while i < len(buf) - 4:
            if buf[i] == 0x24:  # '$'
                if i + 1 < len(buf):
                    if buf[i+1] == 0x4D:  # 'M' - MSPv1
                        if i + 5 <= len(buf):
                            size = buf[i+3]
                            cmd  = buf[i+4]
                            if i + 5 + size <= len(buf):
                                data = buf[i+5:i+5+size]
                                return cmd, list(data)
                    elif buf[i+1] == 0x58:  # 'X' - MSPv2
                        if i + 9 <= len(buf):
                            size = buf[i+6] | (buf[i+7] << 8)
                            cmd  = buf[i+4] | (buf[i+5] << 8)
                            if i + 9 + size <= len(buf):
                                data = buf[i+8:i+8+size]
                                return cmd, list(data)
            i += 1
    except Exception as e:
        pass
    return None, None


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

class SITLConnection:
    """Simple TCP socket connection to SITL."""

    def __init__(self, host, port):
        import socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, int(port)))
        self.sock.settimeout(2.0)
        self.lock = threading.Lock()
        log(f"  Connected to {host}:{port}")

    def send(self, frame):
        with self.lock:
            self.sock.sendall(frame)

    def recv_one(self, timeout=1.0):
        """Receive one MSP response."""
        import socket
        self.sock.settimeout(timeout)
        buf = b""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                chunk = self.sock.recv(512)
                if not chunk:
                    break
                buf += chunk
            except socket.timeout:
                break

        i = 0
        while i < len(buf) - 4:
            if buf[i] == 0x24:
                if i + 1 < len(buf):
                    if buf[i+1] == 0x4D and i + 5 <= len(buf):  # MSPv1
                        size = buf[i+3]
                        cmd  = buf[i+4]
                        if i + 5 + size <= len(buf):
                            data = list(buf[i+5:i+5+size])
                            return cmd, data
                    elif buf[i+1] == 0x58 and i + 9 <= len(buf):  # MSPv2
                        size = buf[i+6] | (buf[i+7] << 8)
                        cmd  = buf[i+4] | (buf[i+5] << 8)
                        if i + 9 + size <= len(buf):
                            data = list(buf[i+8:i+8+size])
                            return cmd, data
            i += 1
        return None, None

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# MSP command helpers
# ---------------------------------------------------------------------------

def send_rc(conn, throttle, roll=RC_MID, pitch=RC_MID, yaw=RC_MID,
            aux1=RC_LOW, aux2=RC_LOW, aux3=RC_LOW, aux4=RC_LOW):
    """Send RC channels via MSP_SET_RAW_RC. Consumes ack."""
    channels = [roll, pitch, throttle, yaw, aux1, aux2, aux3, aux4]
    while len(channels) < 16:
        channels.append(RC_MID)
    data = []
    for ch in channels:
        data.extend([ch & 0xFF, (ch >> 8) & 0xFF])
    conn.send(build_msp_v1(MSP_SET_RAW_RC, data))
    # Consume ack (best effort)
    conn.recv_one(timeout=0.05)


def send_gps(conn, fix=2, sats=14, lat=515074000, lon=-1278000, alt=5000, speed=0):
    """Send GPS data via MSP_SET_RAW_GPS. Alt in cm. Consumes ack."""
    payload = list(struct.pack('<BBiiHH', fix, sats, lat, lon, alt, speed))
    conn.send(build_msp_v1(MSP_SET_RAW_GPS, payload))
    conn.recv_one(timeout=0.05)


def enable_hitl(conn):
    """Send MSP_SIMULATOR with HITL_ENABLE flag."""
    payload = [SIMULATOR_MSP_VERSION, HITL_ENABLE]
    conn.send(build_msp_v2(MSP_SIMULATOR, payload))
    conn.recv_one(timeout=0.1)
    log("  HITL mode enabled")


def set_rx_type_msp(conn):
    """Set receiver type to MSP by sending MSP_SET_RX_CONFIG."""
    # Query current config first
    conn.send(build_msp_v1(MSP_RX_CONFIG, []))
    cmd, data = conn.recv_one(timeout=1.0)
    if data and len(data) >= 24:
        config = list(data)
    else:
        log("  WARNING: Could not read RX config, using defaults")
        config = [0, 0x6C, 0x07, 0xDC, 0x05, 0x4C, 0x04, 0, 0x75, 0x03,
                  0x43, 0x08, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, RX_TYPE_MSP]

    if len(config) < 24:
        config.extend([0] * (24 - len(config)))

    current_type = config[23]
    log(f"  Current receiver type: {current_type}")

    if current_type == RX_TYPE_MSP:
        log("  Receiver type already MSP")
        return True

    config[23] = RX_TYPE_MSP
    conn.send(build_msp_v1(MSP_SET_RX_CONFIG, config[:24]))
    conn.recv_one(timeout=0.1)
    log(f"  Set receiver type to MSP")
    return True


def setup_mode(conn, slot, box_id, aux_ch, start_step, end_step):
    """Configure a mode range via MSP_SET_MODE_RANGE."""
    payload = [slot, box_id, aux_ch, start_step, end_step]
    conn.send(build_msp_v1(MSP_SET_MODE_RANGE, payload))
    conn.recv_one(timeout=0.1)


def save_eeprom(conn):
    """Save config to EEPROM."""
    conn.send(build_msp_v1(MSP_EEPROM_WRITE, []))
    conn.recv_one(timeout=0.5)
    log("  EEPROM saved")


def read_altitude(conn):
    """Read MSP_ALTITUDE. Returns (estimatedAlt_cm, variometer_cms) or (None, None)."""
    conn.send(build_msp_v1(MSP_ALTITUDE, []))
    cmd, data = conn.recv_one(timeout=1.0)
    if data and len(data) >= 6:
        # int32 estimatedAltitude (cm), int16 variometer (cm/s)
        est_alt = struct.unpack('<i', bytes(data[0:4]))[0]
        variometer = struct.unpack('<h', bytes(data[4:6]))[0]
        return est_alt, variometer
    return None, None


def read_inav_status(conn):
    """Read MSP2_INAV_STATUS. Returns armingFlags int or None."""
    conn.send(build_msp_v2(MSP2_INAV_STATUS, []))
    cmd, data = conn.recv_one(timeout=1.0)
    if data and len(data) >= 13:
        # Bytes 0-3: task delta, 4-5: ??, 6-9: sensorStatus, 10-13: armingFlags
        arming_flags = struct.unpack('<I', bytes(data[10:14]))[0]
        mode_flags = struct.unpack('<I', bytes(data[14:18]))[0] if len(data) >= 18 else 0
        return arming_flags, mode_flags
    return None, None


ARMING_FLAG_ARMED = (1 << 2)


def is_armed(arming_flags):
    return bool(arming_flags & ARMING_FLAG_ARMED)


def decode_arming_blockers(flags):
    names = {
        (1<<6):  "ARMING_DISABLED_GEOZONE",
        (1<<7):  "ARMING_DISABLED_FAILSAFE",
        (1<<8):  "ARMING_DISABLED_NOT_LEVEL",
        (1<<9):  "ARMING_DISABLED_SENSORS_CALIBRATING",
        (1<<10): "ARMING_DISABLED_OVERLOADED",
        (1<<11): "ARMING_DISABLED_NAVIGATION_UNSAFE",
        (1<<12): "ARMING_DISABLED_COMPASS_NOT_CALIBRATED",
        (1<<13): "ARMING_DISABLED_ACCEL_NOT_CALIBRATED",
        (1<<14): "ARMING_DISABLED_ARM_SWITCH",
        (1<<15): "ARMING_DISABLED_HARDWARE_FAILURE",
        (1<<16): "ARMING_DISABLED_BOXFAILSAFE",
        (1<<18): "ARMING_DISABLED_RC_LINK",
        (1<<19): "ARMING_DISABLED_THROTTLE",
        (1<<20): "ARMING_DISABLED_CLI",
        (1<<23): "ARMING_DISABLED_ROLLPITCH_NOT_CENTERED",
        (1<<26): "ARMING_DISABLED_INVALID_SETTING",
    }
    return [name for bit, name in names.items() if flags & bit]


# ---------------------------------------------------------------------------
# RC sender thread
# ---------------------------------------------------------------------------

class RCSender:
    """Continuously sends RC at 50Hz in background thread."""
    def __init__(self, conn):
        self.conn = conn
        self.throttle = RC_LOW
        self.aux1 = RC_LOW
        self.aux2 = RC_LOW
        self.gps_alt_cm = 5000
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def set(self, throttle=None, aux1=None, aux2=None, gps_alt_cm=None):
        with self.lock:
            if throttle is not None:
                self.throttle = throttle
            if aux1 is not None:
                self.aux1 = aux1
            if aux2 is not None:
                self.aux2 = aux2
            if gps_alt_cm is not None:
                self.gps_alt_cm = gps_alt_cm

    def _loop(self):
        while self.running:
            with self.lock:
                throttle = self.throttle
                aux1 = self.aux1
                aux2 = self.aux2
                gps_alt_cm = self.gps_alt_cm
            try:
                send_rc(self.conn, throttle=throttle, aux1=aux1, aux2=aux2)
                send_gps(self.conn, alt=gps_alt_cm)
            except Exception:
                pass
            time.sleep(0.02)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)


# ---------------------------------------------------------------------------
# Main test
# ---------------------------------------------------------------------------

def verify_connection(conn):
    """Send MSP_API_VERSION to confirm FC is responding."""
    conn.send(build_msp_v1(MSP_API_VERSION, []))
    cmd, data = conn.recv_one(timeout=2.0)
    if data is not None:
        log("  FC is responding to MSP commands")
        return True
    log("  ERROR: FC is NOT responding to MSP commands!")
    log("  Possible causes:")
    log("    - SITL is not running on this port")
    log("    - Another process is using the port (check: lsof -i :5760)")
    log("  If running in sandbox: retry with dangerouslyDisableSandbox: true")
    return False


def arm_and_liftoff(conn, rc_sender):
    """Arm FC and simulate liftoff. Returns True if armed."""
    log("\n  Enabling HITL mode...")
    enable_hitl(conn)
    time.sleep(0.2)

    log("  Establishing RC link (2s)...")
    rc_sender.set(throttle=RC_LOW, aux1=RC_LOW, aux2=RC_LOW)
    rc_sender.start()
    time.sleep(2.0)

    log("  Setting ARM on AUX1 (slot 0), ALTHOLD on AUX2 (slot 1)...")
    # ARM: slot 0, BOXARM=0, AUX1 ch0, range 1700-2100 (steps 32-48)
    setup_mode(conn, 0, BOXARM, 0, 32, 48)
    # ALTHOLD: slot 1, BOXNAVALTHOLD=3, AUX2 ch1, range 1700-2100
    setup_mode(conn, 1, BOXNAVALTHOLD, 1, 32, 48)
    save_eeprom(conn)
    time.sleep(0.5)

    log("  Arming (AUX1 high)...")
    rc_sender.set(throttle=RC_LOW, aux1=RC_HIGH, aux2=RC_LOW)

    # Wait up to 8s to arm
    for i in range(80):
        time.sleep(0.1)
        af, mf = read_inav_status(conn)
        if af is not None and is_armed(af):
            log(f"  Armed! (arming_flags=0x{af:08X})")
            return True
        if i % 10 == 9 and af is not None:
            blockers = decode_arming_blockers(af)
            log(f"  t={i/10:.0f}s: Not armed (0x{af:08X}) blockers={blockers}")

    af, mf = read_inav_status(conn)
    if af is not None:
        blockers = decode_arming_blockers(af)
        log(f"  FAILED to arm. flags=0x{af:08X} blockers={blockers}")
    else:
        log("  FAILED to arm - no status response")
    return False


def monitor_altitude_for_seconds(conn, duration, label):
    """Poll altitude for `duration` seconds. Return list of (time, alt_cm, variometer_cms)."""
    samples = []
    start = time.time()
    log(f"  Monitoring altitude for {duration}s ({label})...")
    while time.time() - start < duration:
        alt, vario = read_altitude(conn)
        elapsed = time.time() - start
        if alt is not None:
            samples.append((elapsed, alt, vario))
            if len(samples) % 5 == 1:  # Print every 5th sample
                log(f"    t={elapsed:.1f}s  alt={alt/100:.2f}m  variometer={vario} cm/s")
        time.sleep(0.1)
    return samples


def analyze_direction(samples, label):
    """
    Determine if movement was UP or DOWN.
    Returns ('DESCENT', 'CLIMB', or 'HOLD', avg_vario)
    """
    if not samples:
        return "UNKNOWN", 0

    # Use variometer readings - they directly indicate commanded velocity
    vario_values = [v for (_, _, v) in samples if v is not None]
    if not vario_values:
        return "UNKNOWN", 0

    avg_vario = sum(vario_values) / len(vario_values)

    # Also look at altitude change
    alts = [a for (_, a, _) in samples]
    alt_delta = alts[-1] - alts[0] if len(alts) >= 2 else 0

    log(f"  {label}: avg_variometer={avg_vario:.1f} cm/s, alt_delta={alt_delta/100:.2f}m")

    if avg_vario < -10:
        return "DESCENT", avg_vario
    elif avg_vario > 10:
        return "CLIMB", avg_vario
    else:
        return "HOLD", avg_vario


def run_test(host, port):
    log("=" * 60)
    log("ALTHOLD DESCENT BEHAVIOR TEST")
    log("=" * 60)
    log(f"Connecting to SITL at {host}:{port}...")
    log("Note: If running in sandbox, connection errors may require")
    log("      dangerouslyDisableSandbox: true")

    try:
        conn = SITLConnection(host, port)
    except Exception as e:
        log(f"\nERROR: Could not connect to {host}:{port}: {e}")
        log("Check: Is SITL running? Is the port correct?")
        log("If in sandbox: retry with dangerouslyDisableSandbox: true")
        return 1

    # Verify FC is responding
    if not verify_connection(conn):
        conn.close()
        return 1

    rc_sender = RCSender(conn)

    try:
        # Setup RX to MSP
        log("\n[1] Setting receiver type to MSP...")
        if not set_rx_type_msp(conn):
            log("  ERROR: Could not set receiver type")
            return 1

        # Arm and liftoff
        log("\n[2] Arming FC...")
        armed = arm_and_liftoff(conn, rc_sender)
        if not armed:
            record("ARM", FAIL, "FC did not arm within timeout")
            return 1
        record("ARM", PASS, "FC armed successfully")

        # Apply some throttle to get airborne
        log("\n[3] Applying throttle to climb to ~10m...")
        rc_sender.set(throttle=1700, gps_alt_cm=5000)
        time.sleep(3.0)

        # Read current altitude
        alt, vario = read_altitude(conn)
        log(f"  Current altitude: {alt/100 if alt else '?'}m, variometer: {vario} cm/s")

        # Enable ALTHOLD (AUX2 high)
        log("\n[4] Enabling NAV_ALTHOLD mode (AUX2 high)...")
        rc_sender.set(throttle=RC_MID, aux2=RC_HIGH)
        time.sleep(2.0)

        # Read status to confirm althold is active
        af, mf = read_inav_status(conn)
        if af is not None:
            log(f"  Status after ALTHOLD enable: armed={is_armed(af)}, flags=0x{af:08X}")

        # ----------------------------------------------------------------
        # TEST 1: Throttle BELOW midpoint -> should DESCEND
        # ----------------------------------------------------------------
        log(f"\n[5] TEST 1: Throttle below midpoint ({THROTTLE_LOW_DESCENT}) -> expect DESCENT")
        rc_sender.set(throttle=THROTTLE_LOW_DESCENT)
        # Give ALTHOLD time to respond
        time.sleep(1.0)
        samples_low = monitor_altitude_for_seconds(conn, 4.0, f"throttle={THROTTLE_LOW_DESCENT}")

        direction_low, avg_vario_low = analyze_direction(samples_low, "LOW throttle")

        if direction_low == "DESCENT":
            record(
                "TEST1_THROTTLE_LOW_DESCENDS",
                PASS,
                f"avg variometer={avg_vario_low:.1f} cm/s (negative = descent, correct)"
            )
        elif direction_low == "CLIMB":
            record(
                "TEST1_THROTTLE_LOW_DESCENDS",
                FAIL,
                f"BUG CONFIRMED: avg variometer={avg_vario_low:.1f} cm/s (positive = CLIMB when throttle is LOW!)"
            )
        else:
            record(
                "TEST1_THROTTLE_LOW_DESCENDS",
                FAIL,
                f"Inconclusive: avg variometer={avg_vario_low:.1f} cm/s (expected descent)"
            )

        # ----------------------------------------------------------------
        # TEST 2: Throttle ABOVE midpoint -> should CLIMB
        # ----------------------------------------------------------------
        log(f"\n[6] TEST 2: Throttle above midpoint ({THROTTLE_HIGH_CLIMB}) -> expect CLIMB")
        rc_sender.set(throttle=THROTTLE_HIGH_CLIMB)
        time.sleep(1.0)
        samples_high = monitor_altitude_for_seconds(conn, 4.0, f"throttle={THROTTLE_HIGH_CLIMB}")

        direction_high, avg_vario_high = analyze_direction(samples_high, "HIGH throttle")

        if direction_high == "CLIMB":
            record(
                "TEST2_THROTTLE_HIGH_CLIMBS",
                PASS,
                f"avg variometer={avg_vario_high:.1f} cm/s (positive = climb, correct)"
            )
        elif direction_high == "DESCENT":
            record(
                "TEST2_THROTTLE_HIGH_CLIMBS",
                FAIL,
                f"BUG: avg variometer={avg_vario_high:.1f} cm/s (negative = DESCENT when throttle is HIGH!)"
            )
        else:
            record(
                "TEST2_THROTTLE_HIGH_CLIMBS",
                FAIL,
                f"Inconclusive: avg variometer={avg_vario_high:.1f} cm/s (expected climb)"
            )

        # ----------------------------------------------------------------
        # TEST 3: Throttle AT midpoint -> should HOLD
        # ----------------------------------------------------------------
        log(f"\n[7] TEST 3: Throttle at midpoint ({THROTTLE_MID_HOLD}) -> expect HOLD")
        rc_sender.set(throttle=THROTTLE_MID_HOLD)
        time.sleep(1.0)
        samples_mid = monitor_altitude_for_seconds(conn, 4.0, f"throttle={THROTTLE_MID_HOLD}")

        direction_mid, avg_vario_mid = analyze_direction(samples_mid, "MID throttle")

        if direction_mid == "HOLD":
            record(
                "TEST3_THROTTLE_MID_HOLDS",
                PASS,
                f"avg variometer={avg_vario_mid:.1f} cm/s (near zero = hold, correct)"
            )
        else:
            record(
                "TEST3_THROTTLE_MID_HOLDS",
                FAIL,
                f"avg variometer={avg_vario_mid:.1f} cm/s (expected near-zero hold)"
            )

        # ----------------------------------------------------------------
        # Summary
        # ----------------------------------------------------------------
        log("\n" + "=" * 60)
        log("TEST SUMMARY")
        log("=" * 60)
        passed = 0
        failed = 0
        for label, result, detail in results:
            icon = "+" if result == PASS else "x"
            log(f"  [{icon}] {label}: {result}")
            if detail:
                log(f"       {detail}")
            if result == PASS:
                passed += 1
            else:
                failed += 1

        log(f"\n  Total: {passed} passed, {failed} failed")
        log("=" * 60)

        # Key diagnosis
        log("\nKEY DIAGNOSIS:")
        if len(results) >= 2:
            t1 = next((r for r in results if "TEST1" in r[0]), None)
            t2 = next((r for r in results if "TEST2" in r[0]), None)
            if t1 and t2:
                if t1[1] == PASS and t2[1] == PASS:
                    log("  VERDICT: CORRECT BEHAVIOR - copter descends when stick low, climbs when stick high")
                elif t1[1] == FAIL and t2[1] == FAIL:
                    log("  VERDICT: BUG CONFIRMED - INVERTED: stick low CLIMBS, stick high DESCENDS")
                elif t1[1] == FAIL:
                    log(f"  VERDICT: BUG - Stick low causes CLIMB (not descent). avg_vario={avg_vario_low:.1f}")
                elif t2[1] == FAIL:
                    log(f"  VERDICT: BUG - Stick high causes DESCENT (not climb). avg_vario={avg_vario_high:.1f}")

        return 0 if failed == 0 else 1

    finally:
        rc_sender.stop()
        conn.close()
        log("\nDisconnected from SITL.")


def main():
    parser = argparse.ArgumentParser(description="ALTHOLD descent behavior regression test")
    parser.add_argument("--tcp", metavar="HOST:PORT", default="localhost:5760",
                        help="SITL TCP endpoint (default: localhost:5760)")
    args = parser.parse_args()

    parts = args.tcp.rsplit(":", 1)
    host = parts[0] if len(parts) == 2 else "localhost"
    port = int(parts[1]) if len(parts) == 2 else 5760

    return run_test(host, port)


if __name__ == "__main__":
    sys.exit(main())
