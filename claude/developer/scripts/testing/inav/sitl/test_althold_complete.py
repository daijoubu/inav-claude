#!/usr/bin/env python3
"""
Altitude Hold Descent Behavior - Complete Test

Single-session test that:
1. Connects to SITL on port 5761 (UART2, MSP receiver port)
2. Configures MSP receiver type
3. Sets up ARM on AUX1, NAV_ALTHOLD on AUX2
4. Enables HITL mode
5. Reboots and reconnects
6. Arms the FC
7. Injects GPS altitude at 50m
8. Enables NAV_ALTHOLD
9. Tests:
   - Throttle LOW (1200) -> should DESCEND (variometer < 0)
   - Throttle HIGH (1800) -> should CLIMB (variometer > 0)
   - Throttle MID (1500) -> should HOLD (variometer ~0)

Key diagnostic: MSP_ALTITUDE variometer field (cm/s)
  - Negative = descending
  - Positive = climbing
  - Near zero = holding

Usage:
    python3 test_althold_complete.py [port]
    # Default: 5761 (SITL UART2)

IMPORTANT: Run with dangerouslyDisableSandbox=true in Claude sandbox environment.
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
MSP_STATUS_EX      = 150
MSP_SET_RAW_RC     = 200
MSP_SET_RAW_GPS    = 201
MSP_RX_CONFIG      = 44
MSP_SET_RX_CONFIG  = 45
MSP_SET_MODE_RANGE = 35
MSP_EEPROM_WRITE   = 250
MSP_REBOOT         = 68
MSP_ALTITUDE       = 109
MSP_NAV_STATUS     = 121
MSP_SIMULATOR      = 0x201F
MSP2_INAV_STATUS   = 0x2000

HITL_ENABLE = (1 << 0)
SIMULATOR_MSP_VERSION = 2

RX_TYPE_MSP = 2

# Box permanent IDs (from rc_modes.h enum order)
BOXARM        = 0
BOXNAVALTHOLD = 3

RC_LOW  = 1000
RC_MID  = 1500
RC_HIGH = 2000

PASS = "PASS"
FAIL = "FAIL"

# GPS at 50m altitude (5000cm), good fix
GPS_FIX = 2
GPS_SATS = 14
GPS_LAT = 515074000   # 51.5074 degrees * 1e7
GPS_LON = -1278000    # -0.1278 degrees * 1e7
GPS_ALT_CM = 5000     # 50m AGL

THROTTLE_LOW  = 1200
THROTTLE_MID  = 1500
THROTTLE_HIGH = 1800


# ---------------------------------------------------------------------------
# MSP framing helpers
# ---------------------------------------------------------------------------

def _crc8_dvb_s2(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc


def build_v1(cmd: int, data=None) -> bytes:
    """Build MSPv1 command frame."""
    if data is None:
        data = []
    d = bytes(data)
    cs = len(d) ^ cmd
    for b in d:
        cs ^= b
    return bytes([0x24, 0x4D, 0x3C, len(d), cmd]) + d + bytes([cs])


def build_v2(cmd: int, data=None) -> bytes:
    """Build MSPv2 command frame."""
    if data is None:
        data = []
    p = bytes(data)
    h = bytes([0x24, 0x58, 0x3C, 0x00,
               cmd & 0xFF, (cmd >> 8) & 0xFF,
               len(p) & 0xFF, (len(p) >> 8) & 0xFF])
    return h + p + bytes([_crc8_dvb_s2(h[3:] + p)])


def parse_msp(buf: bytes):
    """Parse first valid MSP frame from buffer. Returns (cmd, data_bytes) or (None, None)."""
    i = 0
    while i < len(buf) - 4:
        if buf[i] == 0x24:
            if buf[i+1] == 0x4D and i + 5 <= len(buf):  # MSPv1
                size = buf[i+3]
                cmd = buf[i+4]
                if i + 5 + size <= len(buf):
                    return cmd, buf[i+5:i+5+size]
            elif buf[i+1] == 0x58 and i + 9 <= len(buf):  # MSPv2
                size = buf[i+6] | (buf[i+7] << 8)
                cmd = buf[i+4] | (buf[i+5] << 8)
                if i + 9 + size <= len(buf):
                    return cmd, buf[i+8:i+8+size]
        i += 1
    return None, None


# ---------------------------------------------------------------------------
# Connection class
# ---------------------------------------------------------------------------

class FC:
    """TCP connection to SITL FC. Thread-safe."""

    def __init__(self, host: str, port: int):
        import socket
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((host, port))
        self._sock.settimeout(2.0)
        self._lock = threading.Lock()

    def send(self, frame: bytes) -> None:
        with self._lock:
            self._sock.sendall(frame)

    def recv(self, timeout: float = 1.0):
        """Receive one MSP frame. Returns (cmd, data_bytes) or (None, None)."""
        import socket
        self._sock.settimeout(timeout)
        buf = b""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                chunk = self._sock.recv(1024)
                if not chunk:
                    break
                buf += chunk
                cmd, data = parse_msp(buf)
                if cmd is not None:
                    return cmd, data
            except socket.timeout:
                break
        return parse_msp(buf)

    def exchange(self, frame: bytes, timeout: float = 1.0):
        """Send a frame and receive response. Returns (cmd, data_bytes)."""
        self.send(frame)
        return self.recv(timeout)

    def close(self):
        try:
            self._sock.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# RC sender thread
# ---------------------------------------------------------------------------

class RCSender:
    """Sends RC+GPS data continuously at 50Hz in a background thread."""

    def __init__(self, fc: FC):
        self._fc = fc
        self.throttle = RC_LOW
        self.aux1 = RC_LOW
        self.aux2 = RC_LOW
        self.gps_alt_cm = GPS_ALT_CM
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def set(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def _loop(self):
        while self._running:
            with self._lock:
                t, a1, a2, galt = self.throttle, self.aux1, self.aux2, self.gps_alt_cm
            try:
                # Channels: Roll, Pitch, Throttle, Yaw, AUX1, AUX2 + padding to 16
                chs = [RC_MID, RC_MID, t, RC_MID, a1, a2] + [RC_MID] * 10
                rc_data = b"".join(struct.pack('<H', ch) for ch in chs)
                self._fc.send(build_v1(MSP_SET_RAW_RC, rc_data))
                self._fc.recv(timeout=0.01)

                gps_payload = struct.pack('<BBiiHH', GPS_FIX, GPS_SATS,
                                         GPS_LAT, GPS_LON, galt, 0)
                self._fc.send(build_v1(MSP_SET_RAW_GPS, gps_payload))
                self._fc.recv(timeout=0.01)
            except Exception:
                pass
            time.sleep(0.02)  # 50 Hz

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)


# ---------------------------------------------------------------------------
# FC interaction helpers
# ---------------------------------------------------------------------------

def ping(fc: FC) -> bool:
    cmd, data = fc.exchange(build_v1(MSP_API_VERSION), timeout=2.0)
    return data is not None


def enable_hitl(fc: FC) -> None:
    fc.exchange(build_v2(MSP_SIMULATOR, [SIMULATOR_MSP_VERSION, HITL_ENABLE]), timeout=0.2)


def set_rx_msp(fc: FC) -> bool:
    """Set receiver type to MSP. Returns True on success."""
    cmd, data = fc.exchange(build_v1(MSP_RX_CONFIG), timeout=1.0)
    if data and len(data) >= 24:
        cfg = bytearray(data)
    else:
        print("  WARNING: Could not read RX config, using defaults")
        cfg = bytearray(24)
        cfg[1] = 0x6C; cfg[2] = 0x07  # maxcheck=1900
        cfg[3] = 0xDC; cfg[4] = 0x05  # midrc=1500
        cfg[5] = 0x4C; cfg[6] = 0x04  # mincheck=1100
        cfg[8] = 0x75; cfg[9] = 0x03  # rx_min_usec=885
        cfg[10] = 0x43; cfg[11] = 0x08  # rx_max_usec=2115

    if len(cfg) < 24:
        cfg.extend(b'\x00' * (24 - len(cfg)))

    current_type = cfg[23]
    print(f"  Current receiver type: {current_type}")

    if current_type == RX_TYPE_MSP:
        print("  Already MSP")
        return True

    cfg[23] = RX_TYPE_MSP
    fc.exchange(build_v1(MSP_SET_RX_CONFIG, bytes(cfg[:24])), timeout=0.2)
    print(f"  Set receiver type -> MSP (2)")
    return True


def setup_mode_range(fc: FC, slot: int, box_id: int, aux_ch: int,
                     start_step: int, end_step: int) -> None:
    """Configure a mode activation range."""
    payload = bytes([slot, box_id, aux_ch, start_step, end_step])
    fc.exchange(build_v1(MSP_SET_MODE_RANGE, payload), timeout=0.2)


def save_eeprom(fc: FC) -> None:
    fc.exchange(build_v1(MSP_EEPROM_WRITE), timeout=1.0)
    print("  EEPROM saved")


def reboot(fc: FC) -> None:
    fc.send(build_v1(MSP_REBOOT))
    print("  Reboot sent")


def read_status_ex(fc: FC):
    """
    Read MSP_STATUS_EX.
    Returns (armingDisableFlags, flightModeFlags) both as ints, or (None, None).

    MSP_STATUS_EX layout (from fc_msp.c):
    u16 cycleTime
    u16 i2cError
    u16 activeSensors
    u32 flightModeFlags   <- offset 6
    u8  profile
    u16 averageSystemLoad
    u8  armingDisableCount
    u32 armingDisableFlags <- offset 13
    """
    cmd, data = fc.exchange(build_v1(MSP_STATUS_EX), timeout=1.0)
    if data and len(data) >= 17:
        flight_mode = struct.unpack_from('<I', data, 6)[0]
        arming_disable = struct.unpack_from('<I', data, 13)[0]
        return arming_disable, flight_mode
    return None, None


def read_inav_status(fc: FC):
    """
    Read MSP2_INAV_STATUS.
    Returns (armingFlags, boxModeBytes) or (None, None).

    Layout (from fc_msp.c):
    u16 cycleTime          <- 0
    u16 i2cError           <- 2
    u16 sensorStatus       <- 4
    u16 averageSystemLoad  <- 6
    u8  profile            <- 8
    u32 armingFlags        <- 9
    bytes boxModeFlags     <- 13 (8 bytes for 60-item bitmask = 2xu32)
    u8  mixerProfile       <- 21
    """
    cmd, data = fc.exchange(build_v2(MSP2_INAV_STATUS), timeout=1.0)
    if data and len(data) >= 13:
        arming_flags = struct.unpack_from('<I', data, 9)[0]
        box_data = data[13:] if len(data) > 13 else b""
        return arming_flags, box_data
    return None, None


ARMED_BIT         = (1 << 2)    # armingFlags bit
WAS_EVER_ARMED    = (1 << 3)
HITL_FLAG         = (1 << 4)
SITL_FLAG         = (1 << 5)

# Flight mode flags from MSP_STATUS_EX (runtime_config.h)
MODE_ANGLE        = (1 << 0)
MODE_ALTHOLD      = (1 << 3)
MODE_NAV_POSHOLD  = (1 << 5)


def is_armed(arming_flags: int) -> bool:
    return bool(arming_flags & ARMED_BIT)


def althold_mode_active(flight_mode_flags: int) -> bool:
    return bool(flight_mode_flags & MODE_ALTHOLD)


def decode_arming_blockers(arming_flags: int):
    BLOCKER_NAMES = {
        (1<<9):  "SENSORS_CALIBRATING",
        (1<<10): "SYSTEM_OVERLOADED",
        (1<<11): "NAVIGATION_UNSAFE",
        (1<<12): "COMPASS_NOT_CALIBRATED",
        (1<<13): "ACCEL_NOT_CALIBRATED",
        (1<<14): "ARM_SWITCH",
        (1<<15): "HARDWARE_FAILURE",
        (1<<16): "BOXFAILSAFE",
        (1<<18): "RC_LINK",
        (1<<19): "THROTTLE",
        (1<<20): "CLI",
        (1<<23): "ROLLPITCH_NOT_CENTERED",
        (1<<26): "INVALID_SETTING",
        (1<<27): "PWM_OUTPUT_ERROR",
    }
    return [name for bit, name in BLOCKER_NAMES.items() if arming_flags & bit]


def read_altitude(fc: FC):
    """
    Read MSP_ALTITUDE.
    Returns (est_alt_cm, variometer_cms) or (None, None).

    Layout:
    i32 estimatedAltitude (cm)
    i16 variometer (cm/s)  <- the key metric for this test
    i32 baroAltitude (cm)
    """
    cmd, data = fc.exchange(build_v1(MSP_ALTITUDE), timeout=1.0)
    if data and len(data) >= 6:
        est_alt = struct.unpack_from('<i', data, 0)[0]
        variometer = struct.unpack_from('<h', data, 4)[0]
        return est_alt, variometer
    return None, None


# ---------------------------------------------------------------------------
# Test logic
# ---------------------------------------------------------------------------

RESULTS = []


def result(label: str, status: str, detail: str = "") -> None:
    icon = "+" if status == PASS else "x"
    msg = f"  [{icon}] {label}: {status}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    RESULTS.append((label, status, detail))


def sample_variometer(fc: FC, duration: float, label: str):
    """Poll altitude+variometer for duration seconds. Returns list of (t, alt_cm, vario_cms)."""
    samples = []
    start = time.time()
    print(f"  Monitoring {duration:.0f}s: {label}")
    count = 0
    while time.time() - start < duration:
        alt, vario = read_altitude(fc)
        t = time.time() - start
        if alt is not None:
            samples.append((t, alt, vario))
            count += 1
            if count % 5 == 1:  # print every 5th
                print(f"    t={t:.1f}s  alt={alt/100:.1f}m  vario={vario:+d} cm/s")
        time.sleep(0.1)
    print(f"  Collected {len(samples)} samples")
    return samples


def classify_motion(samples, label: str):
    """Returns (direction, avg_vario_cms). Direction: 'DESCENT', 'CLIMB', 'HOLD', 'UNKNOWN'."""
    if not samples:
        print(f"  {label}: NO DATA")
        return "UNKNOWN", 0.0

    varios = [v for (_, _, v) in samples]
    avg = sum(varios) / len(varios)
    alts = [a for (_, a, _) in samples]
    delta_m = (alts[-1] - alts[0]) / 100.0 if len(alts) >= 2 else 0.0

    print(f"  {label}: avg_vario={avg:+.1f} cm/s, alt_delta={delta_m:+.2f}m")

    THRESHOLD = 20.0  # cm/s - below this is "holding"
    if avg < -THRESHOLD:
        return "DESCENT", avg
    elif avg > THRESHOLD:
        return "CLIMB", avg
    else:
        return "HOLD", avg


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_test(host: str, port: int) -> int:
    print("=" * 65)
    print("ALTHOLD DESCENT BEHAVIOR REGRESSION TEST")
    print("=" * 65)
    print(f"Target: {host}:{port}")
    print("IMPORTANT: Run with dangerouslyDisableSandbox in Claude sandbox")
    print()

    # ---- Connect ----
    try:
        fc = FC(host, port)
    except Exception as e:
        print(f"ERROR: Cannot connect to {host}:{port}: {e}")
        print("  Is SITL running? Check: ss -tln | grep 576")
        print("  In sandbox: retry with dangerouslyDisableSandbox: true")
        return 1

    if not ping(fc):
        print("ERROR: FC not responding to MSP commands")
        print("  SITL may be starting up - wait 15s and retry")
        fc.close()
        return 1

    print("[OK] FC is responding to MSP")

    try:
        # ---- Phase 1: Configure (pre-reboot) ----
        print("\n--- Phase 1: Configure ---")

        print("[1.1] Setting receiver type to MSP...")
        set_rx_msp(fc)

        print("[1.2] Configuring mode ranges...")
        # ARM on AUX1 (ch 0), range 1700-2100 (steps 32-48)
        setup_mode_range(fc, slot=0, box_id=BOXARM, aux_ch=0, start_step=32, end_step=48)
        print("  ARM: AUX1 > 1700")

        # NAV_ALTHOLD on AUX2 (ch 1), range 1700-2100
        setup_mode_range(fc, slot=1, box_id=BOXNAVALTHOLD, aux_ch=1, start_step=32, end_step=48)
        print("  NAV_ALTHOLD: AUX2 > 1700")

        print("[1.3] Saving config...")
        save_eeprom(fc)

        print("[1.4] Rebooting to apply receiver type change...")
        reboot(fc)
        fc.close()

        # ---- Wait for reboot ----
        print("\n  Waiting 18s for SITL reboot + sensor init...")
        time.sleep(18)

        # ---- Phase 2: Reconnect ----
        print("\n--- Phase 2: Post-reboot ---")
        try:
            fc = FC(host, port)
        except Exception as e:
            print(f"ERROR: Cannot reconnect after reboot: {e}")
            print("  SITL may need more time. Try increasing sleep to 25s.")
            return 1

        if not ping(fc):
            print("ERROR: FC not responding after reboot")
            return 1

        print("[OK] Reconnected after reboot")

        # ---- Enable HITL ----
        print("[2.1] Enabling HITL mode (bypasses sensor calibration)...")
        enable_hitl(fc)
        time.sleep(0.2)

        # ---- Start RC sender ----
        print("[2.2] Starting RC link (50Hz)...")
        rc = RCSender(fc)
        rc.set(throttle=RC_LOW, aux1=RC_LOW, aux2=RC_LOW, gps_alt_cm=GPS_ALT_CM)
        rc.start()
        time.sleep(2.0)  # 2s to establish RC link
        print("  RC link established (2s of continuous 50Hz data)")

        # ---- Check arming status ----
        print("[2.3] Checking arming status...")
        arming_flags, box_mode = read_inav_status(fc)
        af2, mf2 = read_status_ex(fc)
        print(f"  armingFlags (MSP2_INAV_STATUS): 0x{(arming_flags or 0):08X}")
        print(f"  armingDisableFlags (MSP_STATUS_EX): 0x{(af2 or 0):08X}")
        print(f"  flightModeFlags (MSP_STATUS_EX): 0x{(mf2 or 0):08X}")

        if arming_flags:
            blockers = decode_arming_blockers(arming_flags)
            if blockers:
                print(f"  Arming blockers: {blockers}")
            else:
                print("  No arming blockers (besides status bits)")

        # ---- Arm ----
        print("\n[3] Arming (AUX1 high)...")
        rc.set(aux1=RC_HIGH, throttle=RC_LOW)

        armed = False
        for attempt in range(80):  # 8 seconds
            time.sleep(0.1)
            arming_flags, _ = read_inav_status(fc)
            if arming_flags is not None and is_armed(arming_flags):
                armed = True
                print(f"  Armed after {(attempt+1)*0.1:.1f}s! armingFlags=0x{arming_flags:08X}")
                break
            if attempt % 20 == 19 and arming_flags:
                blockers = decode_arming_blockers(arming_flags)
                print(f"  t={attempt*0.1:.0f}s: not armed, blockers={blockers}")

        if not armed:
            arming_flags, _ = read_inav_status(fc)
            blockers = decode_arming_blockers(arming_flags or 0)
            print(f"  FAILED to arm. Remaining blockers: {blockers}")
            result("ARM", FAIL, f"Blockers: {blockers}")
            rc.stop()
            fc.close()
            return 1

        result("ARM", PASS, "FC armed successfully")

        # ---- Confirm altitude reading ----
        print("\n[4] Checking altitude reading...")
        rc.set(throttle=RC_MID, gps_alt_cm=GPS_ALT_CM)  # throttle mid, GPS at 50m
        time.sleep(1.0)
        alt, vario = read_altitude(fc)
        if alt is not None:
            print(f"  Altitude: {alt/100:.1f}m, variometer: {vario:+d} cm/s")
        else:
            print("  WARNING: Cannot read altitude!")

        # ---- Enable NAV_ALTHOLD ----
        print("\n[5] Enabling NAV_ALTHOLD (AUX2 high)...")
        rc.set(aux2=RC_HIGH, throttle=RC_MID)
        time.sleep(2.0)

        # Check if althold is active
        af_check, mf_check = read_status_ex(fc)
        althold_on = althold_mode_active(mf_check or 0)
        print(f"  flightModeFlags=0x{(mf_check or 0):08X}  NAV_ALTHOLD active: {althold_on}")
        if not althold_on:
            print("  WARNING: NAV_ALTHOLD may not be active!")
            print("  Possible reasons: FC not airborne, nav safety checks failing")
            print("  Continuing test - variometer will show 0 if althold not engaged")

        # ---- Baseline (throttle mid) ----
        print("\n[6] BASELINE: Throttle MID (1500) - should hold altitude...")
        rc.set(throttle=THROTTLE_MID)
        time.sleep(1.0)
        base_samples = sample_variometer(fc, 3.0, "throttle MID baseline")
        base_dir, base_avg = classify_motion(base_samples, "BASELINE")
        print(f"  Baseline direction: {base_dir}, avg_vario={base_avg:+.1f} cm/s")

        # ====================================================================
        # TEST 1: Throttle LOW -> should DESCEND
        # ====================================================================
        print("\n[7] TEST 1: Throttle LOW (1200) -> expected: DESCENT (vario < -20 cm/s)")
        rc.set(throttle=THROTTLE_LOW)
        time.sleep(1.5)  # Let controller respond
        low_samples = sample_variometer(fc, 6.0, f"throttle={THROTTLE_LOW}")
        low_dir, low_avg = classify_motion(low_samples, "LOW throttle")

        if low_dir == "DESCENT":
            result("TEST1_LOW_STICK_DESCENT", PASS,
                   f"avg_vario={low_avg:+.1f} cm/s (NEGATIVE = copter descends, CORRECT)")
        elif low_dir == "CLIMB":
            result("TEST1_LOW_STICK_DESCENT", FAIL,
                   f"BUG CONFIRMED: avg_vario={low_avg:+.1f} cm/s (POSITIVE = copter CLIMBS when stick low!)")
        else:
            result("TEST1_LOW_STICK_DESCENT", FAIL,
                   f"Inconclusive: avg_vario={low_avg:+.1f} cm/s, direction={low_dir}")

        # Return to mid
        rc.set(throttle=THROTTLE_MID)
        time.sleep(2.0)

        # ====================================================================
        # TEST 2: Throttle HIGH -> should CLIMB
        # ====================================================================
        print("\n[8] TEST 2: Throttle HIGH (1800) -> expected: CLIMB (vario > +20 cm/s)")
        rc.set(throttle=THROTTLE_HIGH)
        time.sleep(1.5)
        high_samples = sample_variometer(fc, 6.0, f"throttle={THROTTLE_HIGH}")
        high_dir, high_avg = classify_motion(high_samples, "HIGH throttle")

        if high_dir == "CLIMB":
            result("TEST2_HIGH_STICK_CLIMB", PASS,
                   f"avg_vario={high_avg:+.1f} cm/s (POSITIVE = copter climbs, CORRECT)")
        elif high_dir == "DESCENT":
            result("TEST2_HIGH_STICK_CLIMB", FAIL,
                   f"BUG CONFIRMED: avg_vario={high_avg:+.1f} cm/s (NEGATIVE = copter DESCENDS when stick high!)")
        else:
            result("TEST2_HIGH_STICK_CLIMB", FAIL,
                   f"Inconclusive: avg_vario={high_avg:+.1f} cm/s, direction={high_dir}")

        # Return to mid
        rc.set(throttle=THROTTLE_MID)
        time.sleep(2.0)

        # ====================================================================
        # TEST 3: Throttle MID -> should HOLD
        # ====================================================================
        print("\n[9] TEST 3: Throttle MID (1500) -> expected: HOLD (|vario| < 20 cm/s)")
        mid_samples = sample_variometer(fc, 5.0, "throttle=MID hold check")
        mid_dir, mid_avg = classify_motion(mid_samples, "MID throttle")

        if mid_dir == "HOLD":
            result("TEST3_MID_STICK_HOLD", PASS,
                   f"avg_vario={mid_avg:+.1f} cm/s (near zero = holding, CORRECT)")
        else:
            result("TEST3_MID_STICK_HOLD", FAIL,
                   f"avg_vario={mid_avg:+.1f} cm/s, direction={mid_dir} (expected HOLD)")

        # ====================================================================
        # Summary
        # ====================================================================
        print("\n" + "=" * 65)
        print("TEST RESULTS SUMMARY")
        print("=" * 65)
        passed = failed = 0
        for label, status, detail in RESULTS:
            icon = "+" if status == PASS else "x"
            print(f"  [{icon}] {label}: {status}")
            if detail:
                print(f"        {detail}")
            if status == PASS:
                passed += 1
            else:
                failed += 1

        print(f"\n  Total: {passed} PASSED, {failed} FAILED")
        print("=" * 65)

        # Diagnosis
        print("\nDIAGNOSIS:")
        t1 = next((r for r in RESULTS if "TEST1" in r[0]), None)
        t2 = next((r for r in RESULTS if "TEST2" in r[0]), None)

        if t1 and t2:
            if t1[1] == PASS and t2[1] == PASS:
                print("  VERDICT: CORRECT BEHAVIOR")
                print("  - Low stick -> descent (correct)")
                print("  - High stick -> climb (correct)")
            elif t1[1] == FAIL and t2[1] == FAIL:
                print("  VERDICT: BUG - DIRECTION INVERTED")
                print(f"  - Low stick (1200): vario={low_avg:+.1f} cm/s (should be < -20)")
                print(f"  - High stick (1800): vario={high_avg:+.1f} cm/s (should be > +20)")
                print("  This suggests the throttle-to-velocity mapping is inverted.")
            elif t1[1] == FAIL:
                print(f"  VERDICT: BUG - Low stick causes CLIMB (vario={low_avg:+.1f} cm/s, should be negative)")
            elif t2[1] == FAIL:
                print(f"  VERDICT: BUG - High stick causes DESCENT (vario={high_avg:+.1f} cm/s, should be positive)")
        else:
            print("  Incomplete test data - cannot determine verdict")

        # Raw data for reference
        print("\nRAW VARIOMETER DATA:")
        print(f"  Baseline (mid stick): {base_avg:+.1f} cm/s")
        print(f"  Low stick (1200):     {low_avg:+.1f} cm/s")
        print(f"  High stick (1800):    {high_avg:+.1f} cm/s")
        print(f"  Mid stick hold:       {mid_avg:+.1f} cm/s")

        rc.stop()
        fc.close()
        return 0 if failed == 0 else 1

    except Exception as e:
        import traceback
        print(f"\nERROR: {e}")
        traceback.print_exc()
        return 1


def main():
    parser = argparse.ArgumentParser(description="ALTHOLD descent behavior test")
    parser.add_argument("port", nargs="?", default="5761", help="SITL TCP port (default: 5761)")
    parser.add_argument("--host", default="localhost", help="SITL host")
    args = parser.parse_args()
    return run_test(args.host, int(args.port))


if __name__ == "__main__":
    sys.exit(main())
