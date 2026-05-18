#!/usr/bin/env python3
"""
Query M10 GPS Clock Configuration

This script safely reads (does NOT write) the CPU clock configuration
from u-blox M10 GPS modules to determine if they have default or
high-performance clock settings.

Based on u-blox MAX-M10S Integration Manual (UBX-20053088-R04)
Section 2.1.7, Page 14

SAFETY: This script only performs READ operations. It does NOT
modify OTP memory or change any GPS configuration.
"""

import serial
import struct
import sys
import time
from typing import Optional, Tuple

# UBX protocol constants
UBX_SYNC1 = 0xB5
UBX_SYNC2 = 0x62
UBX_CLASS_CFG = 0x06
UBX_CLASS_ACK = 0x05
UBX_CLASS_MON = 0x0A

UBX_CFG_VALGET = 0x8B
UBX_ACK_ACK = 0x01
UBX_ACK_NAK = 0x00
UBX_MON_VER = 0x04

# Configuration key IDs for CPU clock query
# From Integration Manual Table 6 verification sequence
CFG_KEYS_TO_QUERY = [
    0x40A40001,  # CPU clock configuration key 1
    0x40A40003,  # CPU clock configuration key 3
    0x40A40005,  # CPU clock configuration key 5
    0x40A4000A,  # CPU clock configuration key 10
]

# Expected values for high-performance CPU clock
# From Integration Manual page 14
HIGH_PERF_VALUES = {
    0x40A40001: 0x0B71B000,
    0x40A40003: 0x0B71B000,
    0x40A40005: 0x0B71B000,
    0x40A4000A: 0x05B8D800,
}


class UBXMessage:
    """UBX protocol message builder and parser"""

    @staticmethod
    def calculate_checksum(msg_class: int, msg_id: int, payload: bytes) -> Tuple[int, int]:
        """Calculate UBX checksum"""
        ck_a = 0
        ck_b = 0

        for byte in [msg_class, msg_id] + list(struct.pack('<H', len(payload))) + list(payload):
            ck_a = (ck_a + byte) & 0xFF
            ck_b = (ck_b + ck_a) & 0xFF

        return ck_a, ck_b

    @staticmethod
    def build_message(msg_class: int, msg_id: int, payload: bytes = b'') -> bytes:
        """Build complete UBX message"""
        ck_a, ck_b = UBXMessage.calculate_checksum(msg_class, msg_id, payload)

        return struct.pack(
            '<BBBBH',
            UBX_SYNC1,
            UBX_SYNC2,
            msg_class,
            msg_id,
            len(payload)
        ) + payload + struct.pack('BB', ck_a, ck_b)


def read_ubx_message(port: serial.Serial, timeout: float = 2.0) -> Optional[Tuple[int, int, bytes]]:
    """Read a UBX message from serial port"""
    start_time = time.time()

    # Find sync characters
    while time.time() - start_time < timeout:
        byte = port.read(1)
        if not byte:
            continue

        if byte[0] == UBX_SYNC1:
            byte2 = port.read(1)
            if byte2 and byte2[0] == UBX_SYNC2:
                break
    else:
        return None  # Timeout

    # Read header
    header = port.read(4)
    if len(header) != 4:
        return None

    msg_class, msg_id, length = struct.unpack('<BBH', header)

    # Read payload
    payload = port.read(length) if length > 0 else b''
    if len(payload) != length:
        return None

    # Read checksum
    checksum = port.read(2)
    if len(checksum) != 2:
        return None

    # Verify checksum
    ck_a, ck_b = UBXMessage.calculate_checksum(msg_class, msg_id, payload)
    if checksum[0] != ck_a or checksum[1] != ck_b:
        print(f"Checksum mismatch: expected {ck_a:02X}{ck_b:02X}, got {checksum[0]:02X}{checksum[1]:02X}")
        return None

    return msg_class, msg_id, payload


def query_version(port: serial.Serial) -> Optional[str]:
    """Query GPS module version (UBX-MON-VER)"""
    # Build UBX-MON-VER message (poll)
    msg = UBXMessage.build_message(UBX_CLASS_MON, UBX_MON_VER)

    port.write(msg)
    port.flush()

    # Read response
    response = read_ubx_message(port)
    if response and response[0] == UBX_CLASS_MON and response[1] == UBX_MON_VER:
        payload = response[2]
        # Version string is at offset 0, 30 bytes
        sw_version = payload[0:30].decode('ascii', errors='ignore').strip('\x00')
        return sw_version

    return None


def query_clock_config(port: serial.Serial) -> Optional[dict]:
    """
    Query M10 CPU clock configuration using UBX-CFG-VALGET

    This is a READ-ONLY operation. Does NOT modify GPS configuration.

    Based on Integration Manual Section 2.1.7, Page 14:
    Send: B5 62 06 8B 14 00 00 04 00 00 01 00 A4 40 03 00 A4 40 05 00 A4 40 0A 00 A4 40 4C 15
    """
    # Build UBX-CFG-VALGET message
    # Version: 0, Layer: 0 (RAM), reserved: 0, then configuration keys
    payload = struct.pack('<BBBB', 0x00, 0x04, 0x00, 0x00)  # version, layer, reserved

    # Add configuration keys to query
    for key in CFG_KEYS_TO_QUERY:
        payload += struct.pack('<I', key)

    msg = UBXMessage.build_message(UBX_CLASS_CFG, UBX_CFG_VALGET, payload)

    port.write(msg)
    port.flush()

    # Read response
    response = read_ubx_message(port, timeout=5.0)
    if not response:
        print("No response to CFG-VALGET query")
        return None

    msg_class, msg_id, resp_payload = response

    if msg_class == UBX_CLASS_CFG and msg_id == UBX_CFG_VALGET:
        # Parse response
        # Format: version(1), layer(1), reserved(2), then key-value pairs
        if len(resp_payload) < 4:
            print(f"Response too short: {len(resp_payload)} bytes")
            return None

        version, layer = struct.unpack('<BB', resp_payload[0:2])

        # Parse key-value pairs
        offset = 4
        config_values = {}

        while offset + 8 <= len(resp_payload):  # key(4) + value(4) = 8 bytes minimum
            key = struct.unpack('<I', resp_payload[offset:offset+4])[0]
            value = struct.unpack('<I', resp_payload[offset+4:offset+8])[0]
            config_values[key] = value
            offset += 8

        return config_values

    elif msg_class == UBX_CLASS_ACK and msg_id == UBX_ACK_NAK:
        print("GPS module returned NAK - query not supported")
        return None

    else:
        print(f"Unexpected response: class={msg_class:02X}, id={msg_id:02X}")
        return None


def determine_clock_mode(config_values: dict) -> str:
    """Determine if GPS is in default or high-performance clock mode"""
    if not config_values:
        return "UNKNOWN"

    # Check if values match high-performance configuration
    matches_high_perf = all(
        config_values.get(key) == expected_value
        for key, expected_value in HIGH_PERF_VALUES.items()
    )

    if matches_high_perf:
        return "HIGH_PERFORMANCE"
    else:
        return "DEFAULT"


def main():
    """Main query function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Query M10 GPS CPU clock configuration (READ-ONLY)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /dev/ttyUSB0
  %(prog)s /dev/ttyACM0 --baud 115200
  %(prog)s COM3

SAFETY: This script only READS configuration. It does NOT write or modify
        anything in the GPS module. It is safe to run.
"""
    )

    parser.add_argument('port', help='Serial port (e.g., /dev/ttyUSB0, COM3)')
    parser.add_argument('--baud', type=int, default=9600,
                        help='Baud rate (default: 9600)')
    parser.add_argument('--timeout', type=float, default=2.0,
                        help='Serial timeout in seconds (default: 2.0)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    # Open serial port
    try:
        port = serial.Serial(
            args.port,
            baudrate=args.baud,
            timeout=args.timeout,
            write_timeout=args.timeout
        )
    except serial.SerialException as e:
        print(f"Error opening serial port {args.port}: {e}")
        return 1

    print(f"Querying M10 GPS on {args.port} at {args.baud} baud...")
    print("=" * 60)

    # Query version
    print("\n1. Querying GPS version...")
    version = query_version(port)
    if version:
        print(f"   GPS Version: {version}")

        # Check if it's an M10
        if 'M10' not in version.upper():
            print(f"   WARNING: This doesn't appear to be an M10 module")
            print(f"   This script is designed for M10 modules only")
    else:
        print("   ERROR: Could not read GPS version")
        print("   Make sure GPS is powered and connected correctly")
        return 1

    # Query clock configuration
    print("\n2. Querying CPU clock configuration...")
    print("   (This is a READ-ONLY operation)")

    config_values = query_clock_config(port)

    if config_values:
        print(f"   Successfully read {len(config_values)} configuration values")

        if args.verbose:
            print("\n   Configuration values:")
            for key, value in config_values.items():
                print(f"     Key 0x{key:08X}: 0x{value:08X}")

        # Determine clock mode
        clock_mode = determine_clock_mode(config_values)

        print("\n" + "=" * 60)
        print(f"RESULT: CPU Clock Mode = {clock_mode}")
        print("=" * 60)

        if clock_mode == "HIGH_PERFORMANCE":
            print("\nThis M10 module has been OTP-programmed for high-performance mode.")
            print("It can achieve higher navigation update rates.")
        elif clock_mode == "DEFAULT":
            print("\nThis M10 module is running in default (low-power) clock mode.")
            print("Update rates are limited based on constellation count.")
            print("\nSee u-blox Integration Manual for OTP programming instructions")
            print("if you want to enable high-performance mode (permanent change!).")
        else:
            print("\nCould not determine clock mode (unexpected configuration values).")

        return 0
    else:
        print("   ERROR: Could not read clock configuration")
        print("   This may not be an M10 module, or firmware doesn't support CFG-VALGET")
        return 1


if __name__ == '__main__':
    sys.exit(main())
