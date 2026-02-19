#!/usr/bin/env python3
"""
MSP Continuous Sender - sends MSP packets in a loop for SWD debugging sessions.

Sends MSP_API_VERSION (cmd=1) every 500ms for 60 seconds.
MSP v1 format: $M< + length(0) + cmd + checksum

Usage:
    python3 msp_continuous_sender.py [port] [--interval 0.5] [--duration 60]

Note: If running in a sandbox, retry with dangerouslyDisableSandbox: true
"""

import serial
import time
import sys
import argparse


def calc_checksum(data):
    """MSP v1 checksum: XOR of all bytes after the header."""
    chk = 0
    for b in data:
        chk ^= b
    return chk


def build_msp_v1(cmd, payload=b''):
    """Build MSP v1 packet: $M< + len + cmd + payload + checksum"""
    length = len(payload)
    # Checksum covers: length + cmd + payload
    chk_data = bytes([length, cmd]) + payload
    checksum = calc_checksum(chk_data)
    packet = b'$M<' + bytes([length, cmd]) + payload + bytes([checksum])
    return packet


def parse_msp_response(data):
    """Try to parse an MSP v1 response from raw bytes."""
    results = []
    i = 0
    while i < len(data) - 4:
        if data[i:i+3] == b'$M>':
            if i + 5 <= len(data):
                length = data[i+3]
                cmd = data[i+4]
                if i + 5 + length + 1 <= len(data):
                    payload = data[i+5:i+5+length]
                    checksum = data[i+5+length]
                    # Verify checksum
                    expected = calc_checksum(bytes([length, cmd]) + payload)
                    if checksum == expected:
                        results.append({
                            'cmd': cmd,
                            'payload': payload,
                            'valid': True
                        })
                    else:
                        results.append({
                            'cmd': cmd,
                            'payload': payload,
                            'valid': False,
                            'checksum_error': f'got {checksum:#x} expected {expected:#x}'
                        })
                    i += 5 + length + 1
                    continue
        elif data[i:i+3] == b'$M!':
            # MSP error response
            if i + 5 <= len(data):
                length = data[i+3]
                cmd = data[i+4]
                results.append({'cmd': cmd, 'error': True})
                i += 5 + length + 1
                continue
        i += 1
    return results


def main():
    parser = argparse.ArgumentParser(description='Send MSP packets continuously')
    parser.add_argument('port', nargs='?', default='/dev/ttyACM1',
                        help='Serial port (default: /dev/ttyACM1)')
    parser.add_argument('--interval', type=float, default=0.5,
                        help='Interval between packets in seconds (default: 0.5)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Total duration in seconds (default: 60)')
    parser.add_argument('--baud', type=int, default=115200,
                        help='Baud rate (default: 115200)')
    args = parser.parse_args()

    port = args.port
    interval = args.interval
    duration = args.duration
    baud = args.baud

    MSP_API_VERSION = 1

    print(f"MSP Continuous Sender")
    print(f"  Port:     {port}")
    print(f"  Baud:     {baud}")
    print(f"  Interval: {interval}s")
    print(f"  Duration: {duration}s")
    print(f"  Command:  MSP_API_VERSION (cmd={MSP_API_VERSION})")
    print()
    print("Waiting 3 seconds for USB enumeration...")
    time.sleep(3)

    # Open port
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baud,
            timeout=0.1,          # Non-blocking read
            write_timeout=1.0
        )
        print(f"[OK] Port opened: {port}")
    except serial.SerialException as e:
        print(f"[FAIL] Could not open {port}: {e}")
        print()
        print("Troubleshooting:")
        print("  - Is the RP2350 connected and enumerated? (check: ls /dev/ttyACM*)")
        print("  - Is another process using the port?")
        print("  - Note: If running in sandbox, retry with dangerouslyDisableSandbox: true")
        sys.exit(1)

    packet = build_msp_v1(MSP_API_VERSION)
    print(f"Packet bytes: {' '.join(f'{b:02x}' for b in packet)}")
    print()

    start_time = time.time()
    attempt = 0
    responses_received = 0
    send_errors = 0

    try:
        while time.time() - start_time < duration:
            attempt += 1
            elapsed = time.time() - start_time

            # Send packet
            try:
                written = ser.write(packet)
                ser.flush()
                if written == len(packet):
                    print(f"[{elapsed:6.1f}s] Attempt #{attempt:3d} - Sent {written} bytes: "
                          f"{' '.join(f'{b:02x}' for b in packet)}", end='')
                else:
                    print(f"[{elapsed:6.1f}s] Attempt #{attempt:3d} - PARTIAL WRITE: "
                          f"{written}/{len(packet)} bytes", end='')
                    send_errors += 1
            except serial.SerialException as e:
                print(f"[{elapsed:6.1f}s] Attempt #{attempt:3d} - SEND ERROR: {e}")
                send_errors += 1
                time.sleep(interval)
                continue

            # Read response (non-blocking, short wait)
            time.sleep(0.1)
            raw = b''
            try:
                if ser.in_waiting > 0:
                    raw = ser.read(ser.in_waiting)
            except serial.SerialException as e:
                print(f" | READ ERROR: {e}")
                send_errors += 1
                time.sleep(interval - 0.1)
                continue

            if raw:
                responses = parse_msp_response(raw)
                if responses:
                    for resp in responses:
                        responses_received += 1
                        if resp.get('error'):
                            print(f" | RESPONSE: MSP ERROR for cmd={resp['cmd']}")
                        elif resp['valid']:
                            payload_hex = ' '.join(f'{b:02x}' for b in resp['payload'])
                            print(f" | RESPONSE cmd={resp['cmd']} "
                                  f"len={len(resp['payload'])} payload=[{payload_hex}]")
                            # Parse API version response
                            if resp['cmd'] == MSP_API_VERSION and len(resp['payload']) >= 3:
                                proto = resp['payload'][0]
                                major = resp['payload'][1]
                                minor = resp['payload'][2]
                                print(f"    API Version: protocol={proto} v{major}.{minor}")
                        else:
                            print(f" | RESPONSE: BAD CHECKSUM cmd={resp['cmd']} "
                                  f"({resp.get('checksum_error', '')})")
                else:
                    # Got bytes but not a valid MSP response
                    raw_hex = ' '.join(f'{b:02x}' for b in raw[:32])
                    raw_ascii = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw[:32])
                    print(f" | RAW {len(raw)} bytes: [{raw_hex}] '{raw_ascii}'")
            else:
                print(f" | (no response)")

            # Wait for next interval
            next_send = start_time + attempt * interval
            sleep_time = next_send - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED by user]")
    finally:
        ser.close()

    elapsed_total = time.time() - start_time
    print()
    print("=" * 60)
    print(f"Session complete after {elapsed_total:.1f}s")
    print(f"  Attempts:          {attempt}")
    print(f"  Responses:         {responses_received}")
    print(f"  Send errors:       {send_errors}")
    print(f"  Response rate:     {responses_received/attempt*100:.1f}%" if attempt else "N/A")


if __name__ == '__main__':
    main()
