#!/usr/bin/env python3
"""Query MSP2_COMMON_SETTING_INFO (0x1007) for a named setting over raw MSPv2.

Useful for verifying a setting's firmware-reported min/max/type independent of
any UI (Configurator) - e.g. to prove a UI's displayed min/max actually reflects
what the FC reports, rather than a stale/static HTML value.

IMPORTANT: SITL (and most FC UART emulations) accept only ONE client connection
per port at a time. If the Configurator (or another script) is already connected
to the same TCP port (e.g. 5760), this script's connection will hang/timeout
silently at the OS level (TCP handshake succeeds but the FC's serial task never
services it). Disconnect other clients from that port first.

Usage:
    python3 query_setting_info.py [port] [setting_name ...]

Example:
    python3 query_setting_info.py 5760 dronecan_gps_node_id dronecan_battery_id
"""
import socket
import struct
import sys

MSP2_COMMON_SETTING_INFO = 0x1007


def crc8_dvb_s2(crc, a):
    crc ^= a
    for _ in range(8):
        if crc & 0x80:
            crc = ((crc << 1) ^ 0xD5) & 0xFF
        else:
            crc = (crc << 1) & 0xFF
    return crc


def build_mspv2_frame(code, payload: bytes) -> bytes:
    flag = 0
    body = struct.pack('<BHH', flag, code, len(payload)) + payload
    crc = 0
    for b in body:
        crc = crc8_dvb_s2(crc, b)
    return b'$X<' + body + bytes([crc])


def read_mspv2_reply(sock, timeout=3.0):
    sock.settimeout(timeout)
    buf = b''
    while len(buf) < 3:
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("Connection closed while reading header")
        buf += chunk
    if buf[0:1] != b'$' or buf[1:2] != b'X':
        raise ValueError(f"Bad preamble: {buf}")
    direction = buf[2:3]
    header = b''
    while len(header) < 5:
        chunk = sock.recv(5 - len(header))
        if not chunk:
            raise ConnectionError("Connection closed while reading msp header")
        header += chunk
    flag, code, size = struct.unpack('<BHH', header)
    payload = b''
    while len(payload) < size:
        chunk = sock.recv(size - len(payload))
        if not chunk:
            raise ConnectionError("Connection closed while reading payload")
        payload += chunk
    sock.recv(1)  # crc byte, unchecked
    return direction, code, payload


def query_setting(host, port, name, verbose=True):
    """Returns dict with type/min/max/etc, or None on failure (prints diagnostic)."""
    try:
        s = socket.create_connection((host, port), timeout=5)
    except OSError as e:
        print(f"FAILED to connect to {host}:{port}: {e}")
        print("  Note: if running in a sandbox, retry with dangerouslyDisableSandbox: true")
        return None

    try:
        payload = name.encode('ascii') + b'\x00'
        frame = build_mspv2_frame(MSP2_COMMON_SETTING_INFO, payload)
        sent = s.send(frame)
        if sent != len(frame):
            print(f"FAILED: only sent {sent}/{len(frame)} bytes")
            return None

        try:
            direction, code, reply_payload = read_mspv2_reply(s)
        except (socket.timeout, TimeoutError):
            print(f"TIMEOUT waiting for reply for setting '{name}'.")
            print("  Check: is another client (e.g. the Configurator) already connected")
            print(f"  to {host}:{port}? SITL/FC UARTs generally serve one client at a time.")
            return None

        if direction == b'!':
            print(f"FC returned MSP error for setting '{name}' (unknown setting name?)")
            return None
        if code != MSP2_COMMON_SETTING_INFO:
            print(f"Unexpected reply code {code:#x}, expected {MSP2_COMMON_SETTING_INFO:#x}")
            return None

        # Reply layout (matches MSPHelper.js self._getSetting parsing):
        # name (cstring), pgId (u16), type (u8), section (u8), mode (u8), min (i32), max (u32), ...
        idx = reply_payload.index(b'\x00')
        setting_name = reply_payload[:idx].decode('ascii', errors='replace')
        off = idx + 1
        pg_id = struct.unpack_from('<H', reply_payload, off)[0]; off += 2
        stype = reply_payload[off]; off += 1
        section = reply_payload[off]; off += 1
        mode = reply_payload[off]; off += 1
        minv = struct.unpack_from('<i', reply_payload, off)[0]; off += 4
        maxv = struct.unpack_from('<I', reply_payload, off)[0]; off += 4

        result = {
            'name': setting_name,
            'pg_id': pg_id,
            'type': stype,
            'section': section,
            'mode': mode,
            'min': minv,
            'max': maxv,
        }
        if verbose:
            print(f"Setting '{name}': type={stype} min={minv} max={maxv} (raw name field='{setting_name}')")
        return result
    finally:
        s.close()


if __name__ == '__main__':
    host = 'localhost'
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5760
    names = sys.argv[2:] if len(sys.argv) > 2 else ['dronecan_gps_node_id', 'dronecan_battery_id']
    ok = True
    for n in names:
        r = query_setting(host, port, n)
        if r is None:
            ok = False
    sys.exit(0 if ok else 1)
