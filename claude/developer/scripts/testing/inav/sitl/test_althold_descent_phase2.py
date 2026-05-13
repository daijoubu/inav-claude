#!/usr/bin/env python3
"""
Phase 2: Altitude Hold Descent Behavior Test
Assumes FC is already armed (run sitl_arm_test.py first on port 5761).

This script connects on port 5760 and:
1. Sends GPS + RC to keep the FC alive
2. Configures NAV_ALTHOLD on AUX2
3. Sets altitude via GPS injection
4. Enables ALTHOLD mode
5. Tests throttle low -> descent, throttle high -> climb, mid -> hold

Usage:
    python3 test_althold_descent_phase2.py [port]
    # Default port: 5760

Note: If running in sandbox use dangerouslyDisableSandbox=true
"""

import sys
import time
import struct
import threading
import argparse

# ---------------------------------------------------------------------------
# MSP constants
# ---------------------------------------------------------------------------
MSP_API_VERSION    = 1
MSP_SET_RAW_RC     = 200
MSP_SET_RAW_GPS    = 201
MSP_SET_MODE_RANGE = 35
MSP_EEPROM_WRITE   = 250
MSP_ALTITUDE       = 109
MSP_NAV_STATUS     = 121
MSP_STATUS_EX      = 150
MSP_SIMULATOR      = 0x201F
MSP2_INAV_STATUS   = 0x2000

HITL_ENABLE = (1 << 0)
SIMULATOR_MSP_VERSION = 2

BOXNAVALTHOLD = 3   # NAV ALTHOLD permanent box ID

RC_LOW  = 1000
RC_MID  = 1500
RC_HIGH = 2000

PASS = "PASS"
FAIL = "FAIL"
results = []

ARMED_FLAG = (1 << 2)


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
# MSP framing
# ---------------------------------------------------------------------------

def _crc8_dvb_s2(data):
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc


def build_v1(cmd, data=None):
    if data is None:
        data = []
    d = bytes(data)
    size = len(d)
    cs = size ^ cmd
    for b in d:
        cs ^= b
    return bytes([0x24, 0x4D, 0x3C, size, cmd]) + d + bytes([cs])


def build_v2(cmd, data=None):
    if data is None:
        data = []
    p = bytes(data)
    h = bytes([0x24, 0x58, 0x3C, 0x00,
               cmd & 0xFF, (cmd >> 8) & 0xFF,
               len(p) & 0xFF, (len(p) >> 8) & 0xFF])
    crc = _crc8_dvb_s2(h[3:] + p)
    return h + p + bytes([crc])


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

class Conn:
    def __init__(self, host, port):
        import socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, int(port)))
        self.sock.settimeout(2.0)
        self._lock = threading.Lock()

    def send(self, frame):
        with self._lock:
            self.sock.sendall(frame)

    def recv(self, timeout=1.0):
        import socket
        self.sock.settimeout(timeout)
        buf = b""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                chunk = self.sock.recv(1024)
                if not chunk:
                    break
                buf += chunk
                # Try to parse from buffer
                result = self._parse(buf)
                if result[0] is not None:
                    return result
            except socket.timeout:
                break

        return self._parse(buf)

    @staticmethod
    def _parse(buf):
        i = 0
        while i < len(buf) - 4:
            if buf[i] == 0x24:
                if i+1 < len(buf):
                    if buf[i+1] == 0x4D and i+5 <= len(buf):  # v1
                        size = buf[i+3]
                        cmd  = buf[i+4]
                        if i+5+size <= len(buf):
                            return cmd, list(buf[i+5:i+5+size])
                    elif buf[i+1] == 0x58 and i+9 <= len(buf):  # v2
                        size = buf[i+6] | (buf[i+7] << 8)
                        cmd  = buf[i+4] | (buf[i+5] << 8)
                        if i+9+size <= len(buf):
                            return cmd, list(buf[i+8:i+8+size])
            i += 1
        return None, None

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# RC sender thread
# ---------------------------------------------------------------------------

class RCSender:
    def __init__(self, conn):
        self.conn = conn
        self.throttle = RC_LOW
        self.aux1 = RC_LOW
        self.aux2 = RC_LOW
        self.gps_alt_cm = 1000
        self.running = False
        self.thread = None
        self._lock = threading.Lock()

    def set(self, **kw):
        with self._lock:
            for k, v in kw.items():
                setattr(self, k, v)

    def _loop(self):
        while self.running:
            with self._lock:
                t = self.throttle
                a1 = self.aux1
                a2 = self.aux2
                galt = self.gps_alt_cm
            try:
                # RC: Roll, Pitch, Throttle, Yaw, AUX1, AUX2, ...
                channels = [RC_MID, RC_MID, t, RC_MID, a1, a2] + [RC_MID]*10
                data = []
                for ch in channels:
                    data.extend([ch & 0xFF, (ch >> 8) & 0xFF])
                self.conn.send(build_v1(MSP_SET_RAW_RC, data))
                self.conn.recv(timeout=0.02)

                # GPS: fix=3D, sats=14, lat=51.5 lon=-1.28, alt, speed=0
                gps = list(struct.pack('<BBiiHH', 2, 14, 515074000, -1278000, galt, 0))
                self.conn.send(build_v1(MSP_SET_RAW_GPS, gps))
                self.conn.recv(timeout=0.02)
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
# Helpers
# ---------------------------------------------------------------------------

def ping(conn):
    conn.send(build_v1(MSP_API_VERSION, []))
    cmd, data = conn.recv(timeout=2.0)
    return data is not None


def enable_hitl(conn):
    conn.send(build_v2(MSP_SIMULATOR, [SIMULATOR_MSP_VERSION, HITL_ENABLE]))
    conn.recv(timeout=0.2)


def setup_althold_mode(conn):
    """Configure NAV_ALTHOLD on AUX2 (channel 1, index 1) range 1700-2100."""
    # slot 2 (don't overwrite ARM at slot 0), BOXNAVALTHOLD=3, AUX2=ch1, 1700-2100 steps 32-48
    payload = [2, BOXNAVALTHOLD, 1, 32, 48]
    conn.send(build_v1(MSP_SET_MODE_RANGE, payload))
    conn.recv(timeout=0.1)
    conn.send(build_v1(MSP_EEPROM_WRITE, []))
    conn.recv(timeout=0.5)
    log("  NAV_ALTHOLD configured on AUX2")


def read_altitude(conn):
    """Returns (est_alt_cm, variometer_cms) or (None, None)."""
    conn.send(build_v1(MSP_ALTITUDE, []))
    cmd, data = conn.recv(timeout=1.0)
    if data and len(data) >= 6:
        est_alt = struct.unpack('<i', bytes(data[0:4]))[0]
        variometer = struct.unpack('<h', bytes(data[4:6]))[0]
        return est_alt, variometer
    return None, None


def read_status(conn):
    """Returns (arming_flags, mode_flags) or (None, None)."""
    conn.send(build_v2(MSP2_INAV_STATUS, []))
    cmd, data = conn.recv(timeout=1.0)
    if data and len(data) >= 18:
        arming_flags = struct.unpack('<I', bytes(data[10:14]))[0]
        mode_flags = struct.unpack('<I', bytes(data[14:18]))[0]
        return arming_flags, mode_flags
    return None, None


def is_armed(af):
    return bool(af & ARMED_FLAG) if af is not None else False


NAV_ALTHOLD_MODE_FLAG = (1 << 3)  # from runtime_config.h


def althold_active(mf):
    return bool(mf & NAV_ALTHOLD_MODE_FLAG) if mf is not None else False


def read_nav_status(conn):
    """Read MSP_NAV_STATUS. Returns raw bytes or None."""
    conn.send(build_v1(MSP_NAV_STATUS, []))
    cmd, data = conn.recv(timeout=1.0)
    return data


def monitor_variometer(conn, duration, label):
    """Poll altitude for duration seconds. Returns list of (t, alt_cm, vario_cms)."""
    samples = []
    start = time.time()
    log(f"  Polling altitude for {duration}s ({label})...")
    count = 0
    while time.time() - start < duration:
        alt, vario = read_altitude(conn)
        elapsed = time.time() - start
        if alt is not None:
            samples.append((elapsed, alt, vario))
            count += 1
            if count % 5 == 1:
                log(f"    t={elapsed:.1f}s  alt={alt/100:.2f}m  variometer={vario:+d} cm/s")
        time.sleep(0.1)
    log(f"  Collected {len(samples)} samples")
    return samples


def analyze(samples, label):
    """Returns (direction, avg_vario) where direction is 'DESCENT', 'CLIMB', or 'HOLD'."""
    if not samples:
        return "UNKNOWN", 0.0

    vario_vals = [v for (_, _, v) in samples if v is not None]
    if not vario_vals:
        return "UNKNOWN", 0.0

    avg = sum(vario_vals) / len(vario_vals)
    alts = [a for (_, a, _) in samples]
    delta = (alts[-1] - alts[0]) / 100.0 if len(alts) >= 2 else 0.0

    log(f"  {label}: avg_variometer={avg:+.1f} cm/s, alt_change={delta:+.2f}m over {len(samples)} samples")

    if avg < -15:
        return "DESCENT", avg
    elif avg > 15:
        return "CLIMB", avg
    else:
        return "HOLD", avg


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs="?", default="5760", help="SITL TCP port")
    args = parser.parse_args()

    host = "localhost"
    port = int(args.port)

    log("=" * 60)
    log("ALTHOLD DESCENT BEHAVIOR TEST - Phase 2")
    log("=" * 60)
    log(f"Connecting to SITL at {host}:{port}...")
    log("(FC should already be armed by sitl_arm_test.py)")
    log("Note: Requires dangerouslyDisableSandbox if in sandbox")

    try:
        conn = Conn(host, port)
    except Exception as e:
        log(f"ERROR: Cannot connect to {host}:{port}: {e}")
        log("Make sure SITL is running and sitl_arm_test.py was run first.")
        return 1

    if not ping(conn):
        log("ERROR: FC not responding to MSP. Is SITL running?")
        conn.close()
        return 1

    log("  FC is responding")

    rc_sender = RCSender(conn)

    try:
        # Keep HITL active
        log("\n[1] Refreshing HITL mode...")
        enable_hitl(conn)
        time.sleep(0.1)

        # Check armed state
        log("\n[2] Checking armed state...")
        af, mf = read_status(conn)
        log(f"  arming_flags=0x{(af or 0):08X}, mode_flags=0x{(mf or 0):08X}")
        if not is_armed(af):
            log("  WARNING: FC is NOT armed. Run sitl_arm_test.py first.")
            log("  Attempting to continue anyway - some tests may fail.")
            armed_ok = False
        else:
            log("  FC is ARMED")
            armed_ok = True
        record("FC_ARMED_CHECK", PASS if armed_ok else FAIL,
               "armed" if armed_ok else "NOT armed - run sitl_arm_test.py first")

        # Start RC sender - send GPS altitude 50m = 5000cm
        log("\n[3] Starting RC sender (throttle mid, AUX1 high=armed, AUX2 low=no althold)...")
        rc_sender.set(throttle=RC_MID, aux1=RC_HIGH, gps_alt_cm=5000)
        rc_sender.start()
        time.sleep(1.0)

        # Configure NAV_ALTHOLD on AUX2
        log("\n[4] Configuring NAV_ALTHOLD on AUX2...")
        setup_althold_mode(conn)
        time.sleep(1.0)

        # Check current altitude
        alt, vario = read_altitude(conn)
        log(f"  Current: alt={alt/100 if alt else '?'}m, vario={vario} cm/s")

        # Enable ALTHOLD
        log("\n[5] Enabling NAV_ALTHOLD (AUX2 high)...")
        rc_sender.set(aux2=RC_HIGH, throttle=RC_MID)
        time.sleep(2.0)

        # Confirm ALTHOLD active
        af, mf = read_status(conn)
        althold_on = althold_active(mf)
        log(f"  mode_flags=0x{(mf or 0):08X}  NAV_ALTHOLD_MODE active: {althold_on}")
        if not althold_on:
            log("  WARNING: NAV_ALTHOLD not showing as active in mode flags!")
            log("  This may mean the mode was not accepted. Checking nav_status...")
            nav_data = read_nav_status(conn)
            if nav_data:
                log(f"  NAV_STATUS raw: {nav_data[:8]}")

        # Read baseline
        baseline_samples = monitor_variometer(conn, 2.0, "baseline at throttle mid")
        _, baseline_avg = analyze(baseline_samples, "BASELINE")

        # ----------------------------------------------------------------
        # TEST 1: Throttle LOW -> expect DESCENT
        # ----------------------------------------------------------------
        log("\n[6] TEST 1: Throttle LOW (1200) -> expect DESCENT")
        log("    (stick below deadband = command descent)")
        rc_sender.set(throttle=1200)
        time.sleep(1.5)  # Give controller time to respond
        samples_low = monitor_variometer(conn, 5.0, "throttle=1200 (LOW)")
        dir_low, avg_low = analyze(samples_low, "LOW throttle result")

        if dir_low == "DESCENT":
            record("TEST1_LOW_THROTTLE_DESCENDS", PASS,
                   f"avg_vario={avg_low:+.1f} cm/s (negative = descent, CORRECT)")
        elif dir_low == "CLIMB":
            record("TEST1_LOW_THROTTLE_DESCENDS", FAIL,
                   f"BUG: avg_vario={avg_low:+.1f} cm/s (POSITIVE = copter CLIMBS when stick is LOW!)")
        else:
            record("TEST1_LOW_THROTTLE_DESCENDS", FAIL,
                   f"Inconclusive: avg_vario={avg_low:+.1f} cm/s (expected < -15, direction={dir_low})")

        # Return to mid to stabilize
        rc_sender.set(throttle=RC_MID)
        time.sleep(2.0)

        # ----------------------------------------------------------------
        # TEST 2: Throttle HIGH -> expect CLIMB
        # ----------------------------------------------------------------
        log("\n[7] TEST 2: Throttle HIGH (1800) -> expect CLIMB")
        log("    (stick above deadband = command climb)")
        rc_sender.set(throttle=1800)
        time.sleep(1.5)
        samples_high = monitor_variometer(conn, 5.0, "throttle=1800 (HIGH)")
        dir_high, avg_high = analyze(samples_high, "HIGH throttle result")

        if dir_high == "CLIMB":
            record("TEST2_HIGH_THROTTLE_CLIMBS", PASS,
                   f"avg_vario={avg_high:+.1f} cm/s (positive = climb, CORRECT)")
        elif dir_high == "DESCENT":
            record("TEST2_HIGH_THROTTLE_CLIMBS", FAIL,
                   f"BUG: avg_vario={avg_high:+.1f} cm/s (NEGATIVE = copter DESCENDS when stick is HIGH!)")
        else:
            record("TEST2_HIGH_THROTTLE_CLIMBS", FAIL,
                   f"Inconclusive: avg_vario={avg_high:+.1f} cm/s (expected > +15, direction={dir_high})")

        # Return to mid
        rc_sender.set(throttle=RC_MID)
        time.sleep(2.0)

        # ----------------------------------------------------------------
        # TEST 3: Throttle MID -> expect HOLD
        # ----------------------------------------------------------------
        log("\n[8] TEST 3: Throttle MID (1500) -> expect HOLD (within deadband)")
        samples_mid = monitor_variometer(conn, 5.0, "throttle=1500 (MID)")
        dir_mid, avg_mid = analyze(samples_mid, "MID throttle result")

        if dir_mid == "HOLD":
            record("TEST3_MID_THROTTLE_HOLDS", PASS,
                   f"avg_vario={avg_mid:+.1f} cm/s (near zero = hold, CORRECT)")
        else:
            record("TEST3_MID_THROTTLE_HOLDS", FAIL,
                   f"avg_vario={avg_mid:+.1f} cm/s (expected near-zero hold, got {dir_mid})")

        # ----------------------------------------------------------------
        # Summary
        # ----------------------------------------------------------------
        log("\n" + "=" * 60)
        log("FINAL TEST RESULTS")
        log("=" * 60)
        passed = failed = 0
        for label, result, detail in results:
            icon = "+" if result == PASS else "x"
            log(f"  [{icon}] {label}: {result}")
            if detail:
                log(f"        {detail}")
            if result == PASS:
                passed += 1
            else:
                failed += 1
        log(f"\n  Passed: {passed}  Failed: {failed}")
        log("=" * 60)

        # Diagnosis
        log("\nDIAGNOSIS:")
        t1 = next((r for r in results if "TEST1" in r[0]), None)
        t2 = next((r for r in results if "TEST2" in r[0]), None)
        if t1 and t2:
            t1_pass = t1[1] == PASS
            t2_pass = t2[1] == PASS
            if t1_pass and t2_pass:
                log("  VERDICT: CORRECT - Stick low=descent, stick high=climb (expected behavior)")
            elif not t1_pass and not t2_pass:
                log("  VERDICT: BUG CONFIRMED - INVERTED: stick low causes CLIMB, stick high causes DESCENT")
                log(f"           LOW throttle vario: {avg_low:+.1f} cm/s (should be negative)")
                log(f"           HIGH throttle vario: {avg_high:+.1f} cm/s (should be positive)")
            elif not t1_pass:
                log(f"  VERDICT: BUG - Low stick CLIMBS: vario={avg_low:+.1f} cm/s (should be negative)")
            elif not t2_pass:
                log(f"  VERDICT: BUG - High stick DESCENDS: vario={avg_high:+.1f} cm/s (should be positive)")
        else:
            log("  Incomplete test results - could not determine verdict")

        return 0 if failed == 0 else 1

    finally:
        rc_sender.stop()
        conn.close()
        log("\nDisconnected.")


if __name__ == "__main__":
    sys.exit(main())
