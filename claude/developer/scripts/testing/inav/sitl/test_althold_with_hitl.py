#!/usr/bin/env python3
"""
Altitude Hold Descent Behavior Test - Using Full HITL Simulator Data

This test uses the MSP_SIMULATOR packet (with HITL_ENABLE + HITL_HAS_NEW_GPS_DATA)
to inject full sensor data into SITL, making the FC think it's actually flying at 50m.

This allows NAV_ALTHOLD to activate and properly respond to throttle input.

Test scenarios:
1. Throttle LOW (1200)  -> expect DESCENT (desired velocity < 0)
2. Throttle HIGH (1800) -> expect CLIMB   (desired velocity > 0)
3. Throttle MID (1500)  -> expect HOLD    (desired velocity ~0)

Key measurement: MSP_ALTITUDE variometer field (cm/s)
  - Negative = descending desired rate
  - Positive = climbing desired rate
  - Near zero = holding

HITL simulator packet flags:
  - HITL_ENABLE (bit 0) = 0x01
  - HITL_HAS_NEW_GPS_DATA (bit 4) = 0x10

Usage:
    python3 test_althold_with_hitl.py [port]
    # Default port: 5761

Note: Run with dangerouslyDisableSandbox in Claude sandbox.
"""

import sys
import time
import struct
import threading
import argparse

PASS = "PASS"
FAIL = "FAIL"
RESULTS = []

# HITL flags
HITL_ENABLE           = (1 << 0)
HITL_HAS_NEW_GPS_DATA = (1 << 4)
HITL_EXT_BATTERY      = (1 << 5)
SIMULATOR_MSP_VERSION = 2

# MSP commands
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
MSP_SIMULATOR      = 0x201F
MSP2_INAV_STATUS   = 0x2000

RX_TYPE_MSP = 2
BOXARM        = 0
BOXNAVALTHOLD = 3

RC_LOW  = 1000
RC_MID  = 1500
RC_HIGH = 2000

THROTTLE_LOW  = 1200  # Below midpoint: should command descent
THROTTLE_MID  = 1500  # At midpoint: within deadband, should hold
THROTTLE_HIGH = 1800  # Above midpoint: should command climb

# Simulated position - copter at 50m altitude
SIM_ALT_M    = 50.0    # 50 meters AGL
SIM_LAT      = 51.5074 # degrees
SIM_LON      = -0.1278 # degrees
SIM_BARO_PA  = 101325.0 - (SIM_ALT_M * 12.0)  # ~50m above sea level


# ---------------------------------------------------------------------------
# MSP framing
# ---------------------------------------------------------------------------

def _crc8_dvb_s2(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc


def build_v1(cmd: int, data: bytes = b"") -> bytes:
    d = bytes(data)
    cs = len(d) ^ cmd
    for b in d:
        cs ^= b
    return bytes([0x24, 0x4D, 0x3C, len(d), cmd]) + d + bytes([cs])


def build_v2(cmd: int, data: bytes = b"") -> bytes:
    p = bytes(data)
    h = bytes([0x24, 0x58, 0x3C, 0x00,
               cmd & 0xFF, (cmd >> 8) & 0xFF,
               len(p) & 0xFF, (len(p) >> 8) & 0xFF])
    return h + p + bytes([_crc8_dvb_s2(h[3:] + p)])


def parse_msp(buf: bytes):
    """Find and return first complete MSP frame. Returns (cmd, data) or (None, None)."""
    i = 0
    while i < len(buf) - 4:
        if buf[i] == 0x24:
            if buf[i+1] == 0x4D and i + 5 <= len(buf):  # v1
                size = buf[i+3]
                cmd  = buf[i+4]
                if i + 5 + size <= len(buf):
                    return cmd, buf[i+5:i+5+size]
            elif buf[i+1] == 0x58 and i + 9 <= len(buf):  # v2
                size = buf[i+6] | (buf[i+7] << 8)
                cmd  = buf[i+4] | (buf[i+5] << 8)
                if i + 9 + size <= len(buf):
                    return cmd, buf[i+8:i+8+size]
        i += 1
    return None, None


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

class FC:
    def __init__(self, host: str, port: int):
        import socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.s.settimeout(2.0)
        self._lock = threading.Lock()

    def send(self, frame: bytes):
        with self._lock:
            self.s.sendall(frame)

    def recv(self, timeout=1.0):
        import socket
        self.s.settimeout(timeout)
        buf = b""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                chunk = self.s.recv(1024)
                if not chunk:
                    break
                buf += chunk
                cmd, data = parse_msp(buf)
                if cmd is not None:
                    return cmd, data
            except socket.timeout:
                break
        return parse_msp(buf)

    def exchange(self, frame: bytes, timeout=1.0):
        self.send(frame)
        return self.recv(timeout)

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# HITL simulator packet builder
# ---------------------------------------------------------------------------

def build_hitl_packet(flags: int,
                      alt_m: float = SIM_ALT_M,
                      vel_d_ms: float = 0.0,
                      roll_deg: float = 0.0,
                      pitch_deg: float = 0.0,
                      yaw_deg: float = 90.0) -> bytes:
    """
    Build MSP_SIMULATOR v2 packet with GPS + attitude data.

    Packet layout (from fc_msp.c handler at case MSP_SIMULATOR):
    u8  simulatorVersion  = 2
    u8  flags
    --- if dataSize >= 14 ---
    u8  gpsFixType        (GPS_FIX_3D = 2)
    u8  gpsNumSat
    u32 gpsLat            (degrees * 1e7)
    u32 gpsLon            (degrees * 1e7)
    u32 gpsAlt            (cm)
    u16 gpsSpeed          (cm/s)
    u16 gpsCourse         (degrees * 10)
    i16 gpsVelN           (cm/s)
    i16 gpsVelE           (cm/s)
    i16 gpsVelD           (cm/s)  <- descent velocity: positive = down
    i16 imuRoll           (degrees * 10)
    i16 imuPitch          (degrees * 10)
    i16 imuYaw            (degrees * 10)
    i16 accX              (* 1000 in G)
    i16 accY
    i16 accZ              (1000 = 1G)
    i16 gyroX             (* 16 DPS)
    i16 gyroY
    i16 gyroZ
    u32 baroPressure      (Pa)
    i16 magX              (raw)
    i16 magY
    i16 magZ
    u8  vbat              (only if HITL_EXT_BATTERY)
    """
    gps_lat = int(SIM_LAT * 1e7)
    gps_lon = int(SIM_LON * 1e7)
    gps_alt_cm = int(alt_m * 100)
    gps_speed = 0          # stationary
    gps_course = int(yaw_deg * 10)
    gps_vel_n = 0          # cm/s north
    gps_vel_e = 0          # cm/s east
    gps_vel_d = int(vel_d_ms * 100)  # cm/s down (positive = descending)

    imu_roll  = int(roll_deg * 10)
    imu_pitch = int(pitch_deg * 10)
    imu_yaw   = int(yaw_deg * 10)

    acc_x = 0
    acc_y = 0
    acc_z = 1000   # 1G upward when level

    gyro_x = 0
    gyro_y = 0
    gyro_z = 0

    baro_pa = int(SIM_BARO_PA)

    mag_x = 230
    mag_y = 5
    mag_z = -410

    payload = struct.pack(
        '<BB'           # version, flags
        'BBiiIHH'       # gps: fixType, numSat, lat, lon, alt, speed, course
        'hhh'           # gps: velN, velE, velD
        'hhh'           # imu: roll, pitch, yaw
        'hhh'           # acc: X, Y, Z
        'hhh'           # gyro: X, Y, Z
        'I'             # baro pressure
        'hhh',          # mag: X, Y, Z
        SIMULATOR_MSP_VERSION, flags,
        2, 14,                              # fixType=3D, numSat=14
        gps_lat, gps_lon, gps_alt_cm,      # lat, lon, alt
        gps_speed, gps_course,             # speed, course
        gps_vel_n, gps_vel_e, gps_vel_d,  # velocities
        imu_roll, imu_pitch, imu_yaw,     # attitude
        acc_x, acc_y, acc_z,             # acceleration
        gyro_x, gyro_y, gyro_z,          # angular velocity
        baro_pa,                          # baro pressure
        mag_x, mag_y, mag_z,             # magnetometer
    )
    return build_v2(MSP_SIMULATOR, payload)


# ---------------------------------------------------------------------------
# RC packet builder
# ---------------------------------------------------------------------------

def build_rc(throttle: int, aux1: int = RC_LOW, aux2: int = RC_LOW) -> bytes:
    """Build MSP_SET_RAW_RC packet."""
    channels = [RC_MID, RC_MID, throttle, RC_MID, aux1, aux2] + [RC_MID] * 10
    data = b"".join(struct.pack('<H', ch) for ch in channels)
    return build_v1(MSP_SET_RAW_RC, data)


# ---------------------------------------------------------------------------
# High-level helpers
# ---------------------------------------------------------------------------

def ping(fc: FC) -> bool:
    cmd, data = fc.exchange(build_v1(MSP_API_VERSION), timeout=2.0)
    return data is not None


def set_rx_msp(fc: FC) -> None:
    cmd, data = fc.exchange(build_v1(MSP_RX_CONFIG), timeout=1.0)
    if data and len(data) >= 24:
        cfg = bytearray(data)
    else:
        cfg = bytearray(24)
        cfg[1] = 0x6C; cfg[2] = 0x07
        cfg[3] = 0xDC; cfg[4] = 0x05
        cfg[5] = 0x4C; cfg[6] = 0x04
        cfg[8] = 0x75; cfg[9] = 0x03
        cfg[10] = 0x43; cfg[11] = 0x08
    if len(cfg) < 24:
        cfg.extend(b'\x00' * (24 - len(cfg)))
    print(f"  Current rx_type={cfg[23]}")
    if cfg[23] != RX_TYPE_MSP:
        cfg[23] = RX_TYPE_MSP
        fc.exchange(build_v1(MSP_SET_RX_CONFIG, bytes(cfg[:24])), timeout=0.2)
        print("  Set receiver type -> MSP")
    else:
        print("  Receiver type already MSP")


def setup_modes(fc: FC) -> None:
    """ARM on AUX1, NAV_ALTHOLD on AUX2."""
    # ARM: slot 0, BOXARM=0, AUX1 ch0, range 1700-2100 (steps 32-48)
    fc.exchange(build_v1(MSP_SET_MODE_RANGE,
                         bytes([0, BOXARM, 0, 32, 48])), timeout=0.2)
    # NAV_ALTHOLD: slot 1, BOXNAVALTHOLD=3, AUX2 ch1
    fc.exchange(build_v1(MSP_SET_MODE_RANGE,
                         bytes([1, BOXNAVALTHOLD, 1, 32, 48])), timeout=0.2)
    print("  ARM: AUX1>1700, NAV_ALTHOLD: AUX2>1700")


def save_and_reboot(fc: FC) -> None:
    fc.exchange(build_v1(MSP_EEPROM_WRITE), timeout=1.0)
    print("  EEPROM saved")
    fc.send(build_v1(MSP_REBOOT))
    print("  Reboot sent")


def read_arming_status(fc: FC):
    """Read MSP2_INAV_STATUS. Returns (armingFlags, armingOK) where armingOK means no blockers."""
    cmd, data = fc.exchange(build_v2(MSP2_INAV_STATUS), timeout=1.0)
    if data and len(data) >= 13:
        arming_flags = struct.unpack_from('<I', data, 9)[0]
        return arming_flags, True
    return None, False


ARMED_BIT = (1 << 2)
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


def decode_blockers(af: int):
    return [name for bit, name in BLOCKER_NAMES.items() if af & bit]


def is_armed(af: int) -> bool:
    return bool(af & ARMED_BIT)


def read_flight_mode(fc: FC):
    """Read MSP_STATUS_EX flight mode flags. Returns (armingDisable, flightMode)."""
    cmd, data = fc.exchange(build_v1(MSP_STATUS_EX), timeout=1.0)
    if data and len(data) >= 17:
        flight_mode = struct.unpack_from('<I', data, 6)[0]
        arming_disable = struct.unpack_from('<I', data, 13)[0]
        return arming_disable, flight_mode
    return None, None


NAV_ALTHOLD_MODE_BIT = (1 << 3)  # from runtime_config.h: NAV_ALTHOLD_MODE = (1 << 3)


def althold_active(mf: int) -> bool:
    return bool(mf & NAV_ALTHOLD_MODE_BIT)


def read_altitude(fc: FC):
    """Returns (est_alt_cm, variometer_cms) or (None, None)."""
    cmd, data = fc.exchange(build_v1(MSP_ALTITUDE), timeout=1.0)
    if data and len(data) >= 6:
        est_alt  = struct.unpack_from('<i', data, 0)[0]
        vario    = struct.unpack_from('<h', data, 4)[0]
        return est_alt, vario
    return None, None


def log_result(label: str, status: str, detail: str = "") -> None:
    icon = "+" if status == PASS else "x"
    msg = f"  [{icon}] {label}: {status}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    RESULTS.append((label, status, detail))


# ---------------------------------------------------------------------------
# HITL sender thread
# ---------------------------------------------------------------------------

class HITLSender:
    """
    Sends full HITL simulator data + RC at 50Hz in background thread.
    This makes the FC think it's flying at the specified altitude.
    """
    def __init__(self, fc: FC):
        self._fc = fc
        self.throttle = RC_LOW
        self.aux1 = RC_LOW
        self.aux2 = RC_LOW
        self.alt_m = SIM_ALT_M
        self.vel_d_ms = 0.0   # cm/s downward (0=stationary)
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def set(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def _loop(self):
        flags = HITL_ENABLE | HITL_HAS_NEW_GPS_DATA
        while self._running:
            with self._lock:
                t, a1, a2 = self.throttle, self.aux1, self.aux2
                alt, vel = self.alt_m, self.vel_d_ms

            try:
                # Send HITL simulator data (GPS + attitude + IMU + baro)
                hitl_pkt = build_hitl_packet(flags, alt_m=alt, vel_d_ms=vel)
                self._fc.send(hitl_pkt)
                self._fc.recv(timeout=0.01)  # consume response

                # Send RC
                self._fc.send(build_rc(t, a1, a2))
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
# Test logic
# ---------------------------------------------------------------------------

def sample_variometer(fc: FC, duration: float, label: str):
    """Sample altitude+variometer for duration seconds. Returns list of (t, alt_cm, vario_cms)."""
    samples = []
    count = 0
    start = time.time()
    print(f"  Sampling {duration:.0f}s: {label}")
    while time.time() - start < duration:
        alt, vario = read_altitude(fc)
        t = time.time() - start
        if alt is not None:
            samples.append((t, alt, vario))
            count += 1
            if count % 5 == 1:
                print(f"    t={t:.1f}s  alt={alt/100:.1f}m  vario={vario:+d} cm/s")
        time.sleep(0.1)
    print(f"  Collected {len(samples)} samples")
    return samples


def classify(samples, label: str):
    """Returns (direction, avg_vario). direction: 'DESCENT', 'CLIMB', 'HOLD', 'UNKNOWN'."""
    if not samples:
        return "UNKNOWN", 0.0
    varios = [v for (_, _, v) in samples]
    avg = sum(varios) / len(varios)
    alts = [a for (_, a, _) in samples]
    delta = (alts[-1] - alts[0]) / 100.0 if len(alts) >= 2 else 0.0
    print(f"  {label}: avg_vario={avg:+.1f} cm/s, alt_delta={delta:+.2f}m")
    if avg < -20:
        return "DESCENT", avg
    elif avg > 20:
        return "CLIMB", avg
    else:
        return "HOLD", avg


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_test(host: str, port: int) -> int:
    print("=" * 65)
    print("ALTHOLD DESCENT BEHAVIOR TEST (with full HITL)")
    print("=" * 65)
    print(f"Target: {host}:{port}")
    print(f"Simulated altitude: {SIM_ALT_M}m")
    print("Note: Run with dangerouslyDisableSandbox in Claude sandbox")
    print()

    # ---- Connect ----
    try:
        fc = FC(host, port)
    except Exception as e:
        print(f"ERROR: Cannot connect to {host}:{port}: {e}")
        print("  Check: Is SITL running? ss -tln | grep 576")
        print("  In sandbox: retry with dangerouslyDisableSandbox: true")
        return 1

    if not ping(fc):
        print("ERROR: FC not responding to MSP")
        fc.close()
        return 1

    print("[OK] FC responding to MSP")

    try:
        # ---- Phase 1: Configure ----
        print("\n--- Phase 1: Configure (pre-reboot) ---")

        print("[1.1] Setting receiver type to MSP...")
        set_rx_msp(fc)

        print("[1.2] Setting up mode ranges...")
        setup_modes(fc)

        print("[1.3] Save + reboot...")
        save_and_reboot(fc)
        fc.close()

        print("\n  Waiting 18s for SITL to reboot + init sensors...")
        time.sleep(18)

        # ---- Phase 2: Post-reboot ----
        print("\n--- Phase 2: Post-reboot setup ---")
        try:
            fc = FC(host, port)
        except Exception as e:
            print(f"ERROR reconnecting: {e}")
            return 1

        if not ping(fc):
            print("ERROR: FC not responding after reboot")
            return 1
        print("[OK] Reconnected")

        # ---- Start HITL sender ----
        print("\n[2.1] Starting HITL data sender at 50Hz...")
        print(f"  GPS altitude: {SIM_ALT_M}m | attitude: level | baro: {SIM_BARO_PA:.0f} Pa")
        hitl = HITLSender(fc)
        hitl.set(throttle=RC_LOW, aux1=RC_LOW, aux2=RC_LOW, alt_m=SIM_ALT_M)
        hitl.start()

        # Wait 3s for HITL to initialize sensors
        time.sleep(3.0)
        print("  HITL running for 3s - sensors should be initializing")

        # ---- Check arming status ----
        print("\n[2.2] Checking arming status...")
        af, _ = read_arming_status(fc)
        ad, mf = read_flight_mode(fc)
        print(f"  armingFlags=0x{(af or 0):08X}")
        print(f"  armingDisable=0x{(ad or 0):08X}  flightMode=0x{(mf or 0):08X}")
        if af:
            bl = decode_blockers(af)
            if bl:
                print(f"  Blockers: {bl}")

        # ---- Arm ----
        print("\n[3] Arming (AUX1 high, throttle low)...")
        hitl.set(aux1=RC_HIGH, throttle=RC_LOW)
        time.sleep(0.5)  # brief delay for arm switch

        armed = False
        for i in range(80):
            time.sleep(0.1)
            af, _ = read_arming_status(fc)
            if af is not None and is_armed(af):
                armed = True
                print(f"  Armed after {(i+1)*0.1:.1f}s!")
                break
            if i % 20 == 19 and af:
                print(f"  t={i*0.1:.0f}s: flags=0x{af:08X} blockers={decode_blockers(af)}")

        if not armed:
            af, _ = read_arming_status(fc)
            blockers = decode_blockers(af or 0)
            print(f"  FAILED to arm. Blockers: {blockers}")
            log_result("ARM", FAIL, f"Blockers: {blockers}")
            hitl.stop()
            fc.close()
            return 1

        log_result("ARM", PASS, "Armed successfully")

        # ---- Apply mid throttle and check altitude ----
        print("\n[4] Setting throttle mid, GPS at 50m for stable hover...")
        hitl.set(throttle=RC_MID, aux1=RC_HIGH, aux2=RC_LOW, alt_m=SIM_ALT_M)
        time.sleep(2.0)

        alt, vario = read_altitude(fc)
        print(f"  Altitude reading: {alt/100 if alt else '?'}m, vario={vario} cm/s")

        # ---- Enable NAV_ALTHOLD ----
        print("\n[5] Enabling NAV_ALTHOLD (AUX2 high)...")
        hitl.set(aux2=RC_HIGH, throttle=RC_MID)
        time.sleep(2.5)

        # Check mode
        ad, mf = read_flight_mode(fc)
        althold_on = althold_active(mf or 0)
        print(f"  flightModeFlags=0x{(mf or 0):08X}, NAV_ALTHOLD_MODE: {althold_on}")

        if not althold_on:
            print("  WARNING: NAV_ALTHOLD not active in mode flags!")
            print("  Possible reasons:")
            print("    - FC may require GPS fix (check: is GPS data being accepted?)")
            print("    - Navigation safety checks not passed")
            print("    - ANGLE mode or other mode prerequisite")

            # Check nav status
            cmd, data = fc.exchange(build_v1(0x79), timeout=1.0)  # MSP_NAV_STATUS=121=0x79
            if data:
                print(f"  NAV_STATUS raw: navMode={data[0]} navState={data[1] if len(data)>1 else '?'}")

        log_result("ALTHOLD_MODE_ACTIVE", PASS if althold_on else FAIL,
                   "active" if althold_on else "NOT active - may affect test results")

        alt, vario = read_altitude(fc)
        print(f"  Altitude before tests: {alt/100 if alt else '?'}m, vario={vario} cm/s")

        # ====================================================================
        # TEST 1: Throttle LOW -> should DESCEND
        # ====================================================================
        print(f"\n[T1] Throttle LOW ({THROTTLE_LOW}) -> expected: DESCENT (vario < -20)")
        hitl.set(throttle=THROTTLE_LOW)
        time.sleep(2.0)  # let controller respond
        low_s = sample_variometer(fc, 7.0, f"throttle={THROTTLE_LOW}")
        low_dir, low_avg = classify(low_s, "LOW throttle")

        if low_dir == "DESCENT":
            log_result("TEST1_LOW_STICK_DESCENT", PASS,
                       f"vario={low_avg:+.1f} cm/s (NEGATIVE=descent, CORRECT)")
        elif low_dir == "CLIMB":
            log_result("TEST1_LOW_STICK_DESCENT", FAIL,
                       f"BUG! vario={low_avg:+.1f} cm/s (POSITIVE=CLIMBS when stick is LOW!)")
        else:
            log_result("TEST1_LOW_STICK_DESCENT", FAIL,
                       f"Inconclusive: vario={low_avg:+.1f} cm/s, dir={low_dir}")

        # Return to mid
        hitl.set(throttle=THROTTLE_MID)
        time.sleep(2.0)

        # ====================================================================
        # TEST 2: Throttle HIGH -> should CLIMB
        # ====================================================================
        print(f"\n[T2] Throttle HIGH ({THROTTLE_HIGH}) -> expected: CLIMB (vario > +20)")
        hitl.set(throttle=THROTTLE_HIGH)
        time.sleep(2.0)
        high_s = sample_variometer(fc, 7.0, f"throttle={THROTTLE_HIGH}")
        high_dir, high_avg = classify(high_s, "HIGH throttle")

        if high_dir == "CLIMB":
            log_result("TEST2_HIGH_STICK_CLIMB", PASS,
                       f"vario={high_avg:+.1f} cm/s (POSITIVE=climb, CORRECT)")
        elif high_dir == "DESCENT":
            log_result("TEST2_HIGH_STICK_CLIMB", FAIL,
                       f"BUG! vario={high_avg:+.1f} cm/s (NEGATIVE=DESCENDS when stick is HIGH!)")
        else:
            log_result("TEST2_HIGH_STICK_CLIMB", FAIL,
                       f"Inconclusive: vario={high_avg:+.1f} cm/s, dir={high_dir}")

        # Return to mid
        hitl.set(throttle=THROTTLE_MID)
        time.sleep(2.0)

        # ====================================================================
        # TEST 3: Throttle MID -> should HOLD
        # ====================================================================
        print(f"\n[T3] Throttle MID ({THROTTLE_MID}) -> expected: HOLD (|vario| < 20)")
        mid_s = sample_variometer(fc, 5.0, f"throttle={THROTTLE_MID}")
        mid_dir, mid_avg = classify(mid_s, "MID throttle")

        if mid_dir == "HOLD":
            log_result("TEST3_MID_STICK_HOLD", PASS,
                       f"vario={mid_avg:+.1f} cm/s (near-zero=hold, CORRECT)")
        else:
            log_result("TEST3_MID_STICK_HOLD", FAIL,
                       f"vario={mid_avg:+.1f} cm/s, dir={mid_dir} (expected HOLD)")

        # ====================================================================
        # Results
        # ====================================================================
        print("\n" + "=" * 65)
        print("FINAL TEST RESULTS")
        print("=" * 65)
        passed = failed = 0
        for label, status, detail in RESULTS:
            icon = "+" if status == PASS else "x"
            print(f"  [{icon}] {label}: {status}")
            if detail:
                print(f"        {detail}")
            passed += (1 if status == PASS else 0)
            failed += (0 if status == PASS else 1)
        print(f"\n  Passed: {passed}, Failed: {failed}")
        print("=" * 65)

        print("\nDIAGNOSIS:")
        t1 = next((r for r in RESULTS if "TEST1" in r[0]), None)
        t2 = next((r for r in RESULTS if "TEST2" in r[0]), None)
        if t1 and t2:
            if t1[1] == PASS and t2[1] == PASS:
                print("  VERDICT: CORRECT BEHAVIOR")
                print("  - Low throttle -> descent (correct)")
                print("  - High throttle -> climb (correct)")
            elif t1[1] == FAIL and "BUG" in (t1[2] or "") and t2[1] == FAIL and "BUG" in (t2[2] or ""):
                print("  VERDICT: BUG - DIRECTION INVERTED")
                print(f"  - Low throttle vario:  {low_avg:+.1f} cm/s (should be < -20)")
                print(f"  - High throttle vario: {high_avg:+.1f} cm/s (should be > +20)")
            elif t1[1] == FAIL:
                print(f"  VERDICT: BUG - Low stick causes climb ({low_avg:+.1f} cm/s, should be negative)")
            elif t2[1] == FAIL:
                print(f"  VERDICT: BUG - High stick causes descent ({high_avg:+.1f} cm/s, should be positive)")

        print("\nRAW VARIOMETER DATA:")
        print(f"  Low throttle ({THROTTLE_LOW}):  {low_avg:+.1f} cm/s")
        print(f"  High throttle ({THROTTLE_HIGH}): {high_avg:+.1f} cm/s")
        print(f"  Mid throttle ({THROTTLE_MID}):  {mid_avg:+.1f} cm/s")

        hitl.stop()
        fc.close()
        return 0 if failed == 0 else 1

    except Exception as e:
        import traceback
        print(f"\nERROR: {e}")
        traceback.print_exc()
        return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs="?", default="5761")
    parser.add_argument("--host", default="localhost")
    args = parser.parse_args()
    return run_test(args.host, int(args.port))


if __name__ == "__main__":
    sys.exit(main())
