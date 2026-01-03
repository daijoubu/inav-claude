#!/usr/bin/env python3
"""
Configure Blackbox via CLI (Reliable Method)

Uses CLI commands instead of MSP to ensure settings are applied.
"""

import sys
import time
import serial
import argparse


def send_cli_commands(port, commands, baud=115200):
    """Send CLI commands and wait for responses."""
    with serial.Serial(port, baud, timeout=3) as ser:
        # Enter CLI mode
        ser.write(b'####\r\n')
        time.sleep(0.5)

        # Read until we see CLI prompt
        start = time.time()
        cli_ready = False
        while time.time() - start < 3:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
                if 'CLI' in data or '#' in data:
                    cli_ready = True
                    break
            time.sleep(0.1)

        if not cli_ready:
            print("✗ ERROR: Failed to enter CLI mode")
            return False

        print("✓ Entered CLI mode")

        # Send each command
        for cmd in commands:
            ser.write(f"{cmd}\r\n".encode('ascii'))
            time.sleep(0.3)

            # Read response
            response = ""
            start = time.time()
            while time.time() - start < 1:
                if ser.in_waiting:
                    response += ser.read(ser.in_waiting).decode('ascii', errors='ignore')
                time.sleep(0.05)

            print(f"  {cmd}")
            if "invalid" in response.lower() or "unknown" in response.lower():
                print(f"    ✗ ERROR: {response.strip()}")
                return False

        print("✓ All commands sent")
        return True


def main():
    parser = argparse.ArgumentParser(description='Configure blackbox via CLI')
    parser.add_argument('--port', type=str, default='/dev/ttyACM0',
                        help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--rate-denom', type=int, default=100,
                        help='Blackbox rate denominator (default: 100)')

    args = parser.parse_args()

    print("=" * 70)
    print("Blackbox Configuration via CLI")
    print("=" * 70)
    print()

    commands = [
        "set blackbox_device = SPIFLASH",
        "set blackbox_rate_num = 1",
        f"set blackbox_rate_denom = {args.rate_denom}",
        "set debug_mode = POS_EST",
        "set blackbox_arm_control = 0",
        "save"
    ]

    print(f"Port: {args.port}")
    print(f"Rate: 1/{args.rate_denom}")
    print()

    if not send_cli_commands(args.port, commands):
        return 1

    print()
    print("Waiting for FC to reboot (10 seconds)...")
    time.sleep(10)

    print()
    print("=" * 70)
    print("Configuration Complete")
    print("=" * 70)
    print()
    print("Verify with CLI:")
    print(f"  get blackbox_rate_denom")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
