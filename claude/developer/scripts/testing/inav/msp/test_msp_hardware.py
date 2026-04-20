#!/usr/bin/env python3
"""
MSP Hardware Test Script
Tests MSP communication with a physical flight controller over serial.

Usage:
    python3 test_msp_hardware.py /dev/ttyACM1

Tests:
    - MSP_API_VERSION (cmd=1)
    - MSP_FC_VARIANT (cmd=2)  - expects "INAV"
    - MSP_BOARD_INFO (cmd=4)  - expects "RP2P" for RP2350

Tries both MSP v1 ($M<) and MSP v2 ($X<) formats.

Note: If running in sandbox, you may need dangerouslyDisableSandbox: true
      for serial port access.
"""

import sys
import time
import struct

try:
    import serial
except ImportError:
    print("ERROR: pyserial not installed. Run: pip install pyserial")
    sys.exit(1)


DEVICE = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM1"
BAUD = 115200
TIMEOUT = 1.0


def msp_v1_frame(cmd, data=b''):
    """Build an MSP v1 frame: $M< + size + cmd + data + crc"""
    size = len(data)
    crc = size ^ cmd
    for b in data:
        crc ^= b
    frame = b'$M<' + bytes([size, cmd]) + data + bytes([crc])
    return frame


def msp_v2_frame(cmd, data=b''):
    """Build an MSP v2 frame: $X< + flag + cmd(u16le) + size(u16le) + data + crc8"""
    flag = 0
    size = len(data)
    header = struct.pack('<BBHH', flag, 0, cmd, size)
    # CRC8/DVB-S2 over header[1:] + data
    payload = header[1:] + data
    crc = _crc8_dvb_s2(payload)
    frame = b'$X<' + bytes([flag]) + struct.pack('<HH', cmd, size) + data + bytes([crc])
    return frame


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


def hexdump(data, prefix='  '):
    """Print hex dump of bytes."""
    if not data:
        print(f"{prefix}(empty)")
        return
    hex_str = ' '.join(f'{b:02X}' for b in data)
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
    print(f"{prefix}{hex_str}  |{ascii_str}|")


def try_read_response(ser, timeout=1.0):
    """Read response bytes until timeout."""
    deadline = time.time() + timeout
    buf = b''
    while time.time() < deadline:
        if ser.in_waiting:
            buf += ser.read(ser.in_waiting)
            # Give more time if we have partial data
            deadline = max(deadline, time.time() + 0.2)
        else:
            time.sleep(0.01)
    return buf


def parse_msp_v1_response(data):
    """Try to parse MSP v1 response from buffer. Returns list of (cmd, payload) tuples."""
    results = []
    i = 0
    while i < len(data) - 5:
        if data[i:i+3] == b'$M>' or data[i:i+3] == b'$M!':
            direction = 'response' if data[i+2:i+3] == b'>' else 'error'
            size = data[i+3]
            cmd = data[i+4]
            if i + 5 + size + 1 <= len(data):
                payload = data[i+5:i+5+size]
                crc_recv = data[i+5+size]
                # Verify CRC
                crc_calc = size ^ cmd
                for b in payload:
                    crc_calc ^= b
                crc_ok = (crc_recv == crc_calc)
                results.append({
                    'version': 1,
                    'direction': direction,
                    'cmd': cmd,
                    'payload': payload,
                    'crc_ok': crc_ok,
                    'offset': i
                })
                i += 5 + size + 1
                continue
        i += 1
    return results


def parse_msp_v2_response(data):
    """Try to parse MSP v2 response from buffer."""
    results = []
    i = 0
    while i < len(data) - 8:
        if data[i:i+2] == b'$X' and data[i+2] in (ord('>'), ord('!')):
            direction = 'response' if data[i+2] == ord('>') else 'error'
            if i + 8 <= len(data):
                flag = data[i+3]
                cmd = struct.unpack_from('<H', data, i+4)[0]
                size = struct.unpack_from('<H', data, i+6)[0]
                if i + 8 + size + 1 <= len(data):
                    payload = data[i+8:i+8+size]
                    crc_recv = data[i+8+size]
                    # Verify CRC8/DVB-S2 over everything after '$X>' byte
                    crc_calc = _crc8_dvb_s2(data[i+3:i+8+size])
                    crc_ok = (crc_recv == crc_calc)
                    results.append({
                        'version': 2,
                        'direction': direction,
                        'cmd': cmd,
                        'payload': payload,
                        'crc_ok': crc_ok,
                        'offset': i
                    })
                    i += 8 + size + 1
                    continue
        i += 1
    return results


def decode_api_version(payload):
    if len(payload) >= 3:
        return f"MSP protocol {payload[0]}, API {payload[1]}.{payload[2]}"
    return f"(short payload: {payload.hex()})"


def decode_fc_variant(payload):
    if len(payload) >= 4:
        return payload[:4].decode('ascii', errors='replace')
    return f"(short payload: {payload.hex()})"


def decode_board_info(payload):
    if len(payload) >= 4:
        board_id = payload[:4].decode('ascii', errors='replace')
        result = f"Board ID: {board_id}"
        if len(payload) >= 6:
            hw_revision = struct.unpack_from('<H', payload, 4)[0]
            result += f", HW revision: {hw_revision}"
        return result
    return f"(short payload: {payload.hex()})"


COMMANDS = {
    1: ("MSP_API_VERSION", decode_api_version),
    2: ("MSP_FC_VARIANT", decode_fc_variant),
    4: ("MSP_BOARD_INFO", decode_board_info),
}


def run_test(ser, cmd_id, use_v2=False):
    cmd_name = COMMANDS[cmd_id][0]
    decoder = COMMANDS[cmd_id][1]
    version_label = "v2" if use_v2 else "v1"

    if use_v2:
        frame = msp_v2_frame(cmd_id)
    else:
        frame = msp_v1_frame(cmd_id)

    print(f"\n--- {cmd_name} (cmd={cmd_id}) via MSP {version_label} ---")
    print(f"  Sending ({len(frame)} bytes):")
    hexdump(frame)

    # Flush before sending
    ser.reset_input_buffer()

    try:
        written = ser.write(frame)
        ser.flush()
    except serial.SerialException as e:
        print(f"  FAILED to write: {e}")
        return None

    if written != len(frame):
        print(f"  WARNING: Only wrote {written}/{len(frame)} bytes")

    # Read response
    response = try_read_response(ser, timeout=1.0)

    if not response:
        print(f"  No response received (timeout)")
        return None

    print(f"  Received ({len(response)} bytes):")
    hexdump(response)

    # Try to parse
    parsed_v1 = parse_msp_v1_response(response)
    parsed_v2 = parse_msp_v2_response(response)
    all_parsed = parsed_v1 + parsed_v2

    if not all_parsed:
        print(f"  Could not parse any valid MSP frames from response")
        return None

    for msg in all_parsed:
        crc_status = "CRC OK" if msg['crc_ok'] else "CRC FAIL"
        print(f"  Parsed MSP v{msg['version']} {msg['direction']}: "
              f"cmd={msg['cmd']}, payload={len(msg['payload'])} bytes [{crc_status}]")
        if msg['cmd'] in COMMANDS and msg['payload']:
            decoded = COMMANDS[msg['cmd']][1](msg['payload'])
            print(f"  Decoded: {decoded}")
        elif msg['payload']:
            hexdump(msg['payload'], prefix='  Payload: ')

    return all_parsed


def main():
    print("=" * 60)
    print("MSP Hardware Communication Test")
    print(f"Device: {DEVICE}")
    print(f"Baud: {BAUD}")
    print("=" * 60)

    # Open port
    try:
        ser = serial.Serial(DEVICE, BAUD, timeout=TIMEOUT)
        print(f"\nConnected to {DEVICE}")
    except serial.SerialException as e:
        print(f"\nFAILED to open {DEVICE}: {e}")
        print("Check:")
        print("  - Is the FC plugged in?")
        print("  - Is the correct device path used?")
        print("  - Is the configurator or another tool using the port?")
        print("  - If in sandbox: retry with dangerouslyDisableSandbox=true")
        sys.exit(1)
    except PermissionError as e:
        print(f"\nPERMISSION DENIED on {DEVICE}: {e}")
        print("  If in sandbox: retry with dangerouslyDisableSandbox=true")
        print("  Otherwise: sudo usermod -aG dialout $USER")
        sys.exit(1)

    # Allow FC time to initialize (USB CDC can take a moment)
    print("Waiting 1s for FC to be ready...")
    time.sleep(1.0)

    # Sanity check: send a basic v1 command and see if ANYTHING comes back
    print("\n=== SANITY CHECK: MSP_API_VERSION via v1 ===")
    ser.reset_input_buffer()
    frame = msp_v1_frame(1)
    ser.write(frame)
    ser.flush()
    time.sleep(0.5)
    raw = b''
    if ser.in_waiting:
        raw = ser.read(ser.in_waiting)
        print(f"FC is responding: received {len(raw)} bytes")
        hexdump(raw)
    else:
        print("No response to sanity check. The FC may not be running MSP,")
        print("or may need more time to initialize.")
        print("Continuing with full tests anyway...")

    results = {}

    # Test each command with MSP v1 first, then v2
    for cmd_id in [1, 2, 4]:
        cmd_name = COMMANDS[cmd_id][0]

        # Try v1
        time.sleep(0.2)
        result_v1 = run_test(ser, cmd_id, use_v2=False)

        # Try v2
        time.sleep(0.2)
        result_v2 = run_test(ser, cmd_id, use_v2=True)

        results[cmd_id] = {
            'name': cmd_name,
            'v1': result_v1,
            'v2': result_v2,
        }

    ser.close()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_pass = True
    for cmd_id, result in results.items():
        name = result['name']
        v1_ok = result['v1'] is not None and len(result['v1']) > 0
        v2_ok = result['v2'] is not None and len(result['v2']) > 0
        status = "PASS" if (v1_ok or v2_ok) else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"  {name}: {status} (v1={'OK' if v1_ok else 'no response'}, v2={'OK' if v2_ok else 'no response'})")

    print()
    if all_pass:
        print("OVERALL: PASS - FC is responding to MSP commands")
    else:
        print("OVERALL: FAIL - One or more commands did not get a valid response")
        sys.exit(1)


if __name__ == '__main__':
    main()
