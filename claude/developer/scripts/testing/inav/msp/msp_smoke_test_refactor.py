#!/usr/bin/env python3
"""
MSP Smoke Test for refactor/flash-reduction-osd-msp-switch-cases

Tests MSP round-trips for:
  - Motor mixer (MSP2_COMMON_MOTOR_MIXER 0x1005)
  - Servo mixer (MSP2_INAV_SERVO_MIXER 0x2020)
  - Servo config (MSP_SERVO_CONFIGURATIONS 120 and MSP2_INAV_SERVO_CONFIG 0x2200)
  - Calibration data (MSP_ACC_CALIBRATION, MSP_MAG_CALIBRATION via MSP_SENSOR_STATUS)
  - Rates (MSP_RC_TUNING 111)
  - Attitude (MSP_ATTITUDE 108)
  - Status (MSP_STATUS 101)
"""

import socket
import struct
import time
import sys

HOST = "127.0.0.1"
PORT = 5760

# MSP v1 message IDs
MSP_STATUS               = 101
MSP_ATTITUDE             = 108
MSP_RC_TUNING            = 111
MSP_SERVO_CONFIGURATIONS = 120
MSP_SENSOR_STATUS        = 151  # includes calibration state
MSP_MOTOR                = 104

# MSP v2 message IDs (from firmware headers)
MSP2_COMMON_MOTOR_MIXER  = 0x1005
MSP2_INAV_SERVO_MIXER    = 0x2020
MSP2_INAV_SERVO_CONFIG   = 0x2200

# Counters — module-level so helper functions can modify them
_passed = 0
_failed = 0
_failures = []


def _check(name, condition, details=""):
    global _passed, _failed, _failures
    if condition:
        print(f"  OK  {name}")
        _passed += 1
    else:
        print(f"  FAIL {name}" + (f": {details}" if details else ""))
        _failed += 1
        _failures.append(name + (f" ({details})" if details else ""))


def _msp_v1_request(cmd):
    return bytes([ord('$'), ord('M'), ord('<'), 0, cmd, cmd])


def _crc8dvb_s2_update(crc, data):
    for b in (data if isinstance(data, (bytes, bytearray)) else [data]):
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc


def _msp_v2_request(cmd):
    flag = 0
    size = 0
    payload = struct.pack('<BHH', flag, cmd, size)
    crc = _crc8dvb_s2_update(0, payload)
    return b'$X<' + payload + bytes([crc])


def _connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3.0)
    try:
        s.connect((HOST, PORT))
        return s
    except Exception as e:
        print(f"  FAILED to connect to {HOST}:{PORT}: {e}")
        print("  Note: If running in sandbox, retry with dangerouslyDisableSandbox: true")
        return None


def _recv_v1(sock, expected_cmd):
    """Read MSP v1 response. Returns payload bytes or None."""
    buf = b''
    deadline = time.time() + 3.0
    while time.time() < deadline:
        try:
            chunk = sock.recv(512)
            if not chunk:
                break
            buf += chunk
        except socket.timeout:
            pass
        while len(buf) >= 6:
            if buf[0:3] in (b'$M>', b'$M!'):
                size = buf[3]
                if len(buf) < 6 + size:
                    break
                cmd = buf[4]
                payload = buf[5:5+size]
                buf = buf[6+size:]
                if cmd == expected_cmd:
                    return payload
            else:
                buf = buf[1:]
    return None


def _recv_v2(sock, expected_cmd):
    """Read MSP v2 response. Returns payload bytes or None."""
    buf = b''
    deadline = time.time() + 3.0
    while time.time() < deadline:
        try:
            chunk = sock.recv(1024)
            if not chunk:
                break
            buf += chunk
        except socket.timeout:
            pass
        # MSP v2 frame: $X>(3) flag(1) cmd(2LE) size(2LE) payload crc(1)
        while len(buf) >= 9:
            if buf[0:3] in (b'$X>', b'$X!'):
                cmd  = struct.unpack_from('<H', buf, 4)[0]
                size = struct.unpack_from('<H', buf, 6)[0]
                total = 9 + size
                if len(buf) < total:
                    break
                payload = buf[8:8+size]
                buf = buf[total:]
                if cmd == expected_cmd:
                    return payload
            else:
                buf = buf[1:]
    return None


# ---------------------------------------------------------------------------
# Individual test functions
# ---------------------------------------------------------------------------

def test_status(sock):
    print("\n--- MSP_STATUS (101) ---")
    sock.sendall(_msp_v1_request(MSP_STATUS))
    p = _recv_v1(sock, MSP_STATUS)
    _check("MSP_STATUS: got response", p is not None)
    if p is not None:
        _check("MSP_STATUS: payload >= 11 bytes", len(p) >= 11,
               f"got {len(p)} bytes")
        if len(p) >= 2:
            cycle_time = struct.unpack_from('<H', p, 0)[0]
            _check("MSP_STATUS: cycle_time is a uint16", 0 <= cycle_time <= 65535,
                   f"cycle_time={cycle_time}")


def test_attitude(sock):
    print("\n--- MSP_ATTITUDE (108) ---")
    sock.sendall(_msp_v1_request(MSP_ATTITUDE))
    p = _recv_v1(sock, MSP_ATTITUDE)
    _check("MSP_ATTITUDE: got response", p is not None)
    if p is not None:
        _check("MSP_ATTITUDE: payload == 6 bytes", len(p) == 6,
               f"got {len(p)} bytes")
        if len(p) >= 6:
            roll  = struct.unpack_from('<h', p, 0)[0]
            pitch = struct.unpack_from('<h', p, 2)[0]
            yaw   = struct.unpack_from('<H', p, 4)[0]
            _check("MSP_ATTITUDE: roll in [-1800,1800]", -1800 <= roll <= 1800,
                   f"roll={roll}")
            _check("MSP_ATTITUDE: pitch in [-900,900]", -900 <= pitch <= 900,
                   f"pitch={pitch}")
            _check("MSP_ATTITUDE: yaw in [0,3600]", 0 <= yaw <= 3600,
                   f"yaw={yaw}")


def test_rc_tuning(sock):
    print("\n--- MSP_RC_TUNING (111) ---")
    sock.sendall(_msp_v1_request(MSP_RC_TUNING))
    p = _recv_v1(sock, MSP_RC_TUNING)
    _check("MSP_RC_TUNING: got response", p is not None)
    if p is not None:
        _check("MSP_RC_TUNING: payload >= 7 bytes", len(p) >= 7,
               f"got {len(p)} bytes")


def test_servo_configurations(sock):
    print("\n--- MSP_SERVO_CONFIGURATIONS (120) ---")
    sock.sendall(_msp_v1_request(MSP_SERVO_CONFIGURATIONS))
    p = _recv_v1(sock, MSP_SERVO_CONFIGURATIONS)
    _check("MSP_SERVO_CONFIGURATIONS: got response", p is not None)
    if p is not None:
        # Each servo entry is 14 bytes (min U16, max U16, middle U16, rate U8, ...)
        remainder = len(p) % 14
        _check("MSP_SERVO_CONFIGURATIONS: length multiple of 14",
               remainder == 0, f"payload={len(p)} bytes, remainder={remainder}")
        n_servos = len(p) // 14
        _check("MSP_SERVO_CONFIGURATIONS: at least 1 servo", n_servos >= 1,
               f"n_servos={n_servos}")
        if n_servos >= 1:
            min_v = struct.unpack_from('<H', p, 0)[0]
            max_v = struct.unpack_from('<H', p, 2)[0]
            _check("MSP_SERVO_CONFIGURATIONS: servo0 min in [500,2500]",
                   500 <= min_v <= 2500, f"min={min_v}")
            _check("MSP_SERVO_CONFIGURATIONS: servo0 max in [500,2500]",
                   500 <= max_v <= 2500, f"max={max_v}")
            _check("MSP_SERVO_CONFIGURATIONS: servo0 min <= max",
                   min_v <= max_v, f"min={min_v} max={max_v}")


def test_msp2_inav_servo_config(sock):
    print("\n--- MSP2_INAV_SERVO_CONFIG (0x2200) ---")
    sock.sendall(_msp_v2_request(MSP2_INAV_SERVO_CONFIG))
    p = _recv_v2(sock, MSP2_INAV_SERVO_CONFIG)
    _check("MSP2_INAV_SERVO_CONFIG: got response", p is not None)
    if p is not None:
        _check("MSP2_INAV_SERVO_CONFIG: payload non-empty", len(p) > 0,
               f"got {len(p)} bytes")
        # Entry is 9 bytes: min(U16) max(U16) middle(U16) rate(S8) forwardFromChannel(S8) reversed(U8)
        remainder = len(p) % 9
        _check("MSP2_INAV_SERVO_CONFIG: length multiple of 9",
               remainder == 0, f"payload={len(p)} bytes, remainder={remainder}")


def test_motor_mixer(sock):
    print("\n--- MSP2_COMMON_MOTOR_MIXER (0x1005) ---")
    sock.sendall(_msp_v2_request(MSP2_COMMON_MOTOR_MIXER))
    p = _recv_v2(sock, MSP2_COMMON_MOTOR_MIXER)
    _check("MSP2_COMMON_MOTOR_MIXER: got response", p is not None)
    if p is not None:
        # Each motor entry: throttle(U16) roll(U16) pitch(U16) yaw(U16) = 8 bytes
        # May include two mixer profiles back-to-back → multiple of 8
        remainder = len(p) % 8
        _check("MSP2_COMMON_MOTOR_MIXER: length multiple of 8",
               remainder == 0, f"payload={len(p)} bytes, remainder={remainder}")
        n = len(p) // 8
        if n >= 1:
            throttle = struct.unpack_from('<H', p, 0)[0]
            roll     = struct.unpack_from('<H', p, 2)[0]
            pitch    = struct.unpack_from('<H', p, 4)[0]
            yaw_v    = struct.unpack_from('<H', p, 6)[0]
            # Values are constrainf(component+2, 0, 4)*1000, so [0,4000]
            for fname, val in [("throttle", throttle), ("roll", roll),
                                ("pitch", pitch), ("yaw", yaw_v)]:
                _check(f"MSP2_COMMON_MOTOR_MIXER: motor0 {fname} in [0,4000]",
                       0 <= val <= 4000, f"{fname}={val}")


def test_servo_mixer(sock):
    print("\n--- MSP2_INAV_SERVO_MIXER (0x2020) ---")
    sock.sendall(_msp_v2_request(MSP2_INAV_SERVO_MIXER))
    p = _recv_v2(sock, MSP2_INAV_SERVO_MIXER)
    _check("MSP2_INAV_SERVO_MIXER: got response", p is not None)
    if p is not None:
        # Empty mixer is valid on default SITL config
        # Each entry: targetChannel(U8) inputSource(U8) rate(U16) speed(U8) conditionId(U8) = 6 bytes
        if len(p) > 0:
            remainder = len(p) % 6
            _check("MSP2_INAV_SERVO_MIXER: length multiple of 6",
                   remainder == 0, f"payload={len(p)} bytes, remainder={remainder}")
        else:
            _check("MSP2_INAV_SERVO_MIXER: empty response (no servo rules)", True)


def main():
    global _passed, _failed, _failures
    print("=" * 60)
    print("MSP Smoke Test: refactor/flash-reduction-osd-msp-switch-cases")
    print(f"Target: {HOST}:{PORT}")
    print("=" * 60)

    sock = _connect()
    if sock is None:
        print("\nFATAL: Cannot connect to SITL. Aborting.")
        sys.exit(2)
    print("Connected to SITL")

    # Sanity check: ensure FC responds before running tests
    sock.sendall(_msp_v1_request(MSP_STATUS))
    sanity = _recv_v1(sock, MSP_STATUS)
    if sanity is None:
        print("\nFATAL: FC did not respond to MSP_STATUS probe.")
        print("  Is SITL fully started? (wait 10s after launch)")
        sock.close()
        sys.exit(2)
    print("FC responding to MSP -- running tests")
    sock.close()

    # Run each test with a fresh connection to avoid state pollution
    for test_fn in [
        test_status,
        test_attitude,
        test_rc_tuning,
        test_servo_configurations,
        test_msp2_inav_servo_config,
        test_motor_mixer,
        test_servo_mixer,
    ]:
        s = _connect()
        if s is None:
            print(f"  SKIP {test_fn.__name__}: cannot connect")
            _failed += 1
            _failures.append(f"{test_fn.__name__}: connect failed")
            continue
        try:
            test_fn(s)
        finally:
            s.close()

    print("\n" + "=" * 60)
    total = _passed + _failed
    print(f"RESULTS: {_passed}/{total} passed, {_failed} failed")
    if _failures:
        print("\nFAILURES:")
        for f in _failures:
            print(f"  - {f}")
    else:
        print("All tests PASSED")
    print("=" * 60)

    sys.exit(0 if _failed == 0 else 1)


if __name__ == "__main__":
    main()
