#!/usr/bin/env python3
"""
reboot-to-dfu.py - Reboot flight controller into DFU mode via serial CLI

Usage: ./reboot-to-dfu.py [serial_port]
  serial_port: defaults to /dev/ttyACM0

This script replicates the working DFU reboot logic from inav-configurator's stm32.js:
1. Send #### to enter CLI mode
2. Wait for "CLI" prompt in response (with timeout)
3. Send dfu command to trigger DFU bootloader
4. Disconnect and wait for DFU device
"""

import sys
import time
import serial

def reboot_to_dfu(port='/dev/ttyACM0', baudrate=115200, timeout=2.0):
    """
    Reboot flight controller to DFU mode using CLI commands.

    Args:
        port: Serial port device path
        baudrate: Serial baud rate (default 115200)
        timeout: Timeout in seconds waiting for CLI prompt

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Opening serial port: {port}")
        ser = serial.Serial(port, baudrate, timeout=0.5)
        time.sleep(0.1)  # Let port settle

        # Flush any existing data
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Step 1: Send #### to enter CLI mode
        print("Entering CLI mode...")
        ser.write(b'####\r\n')
        ser.flush()

        # Step 2: Wait for "CLI" prompt in response
        print("Waiting for CLI prompt...")
        start_time = time.time()
        received_data = b''

        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting)
                received_data += chunk

                # Check if we received the CLI prompt
                # INAV responds with either "CLI" or just "# " prompt
                if b'CLI' in received_data or b'# ' in received_data:
                    print("✓ CLI mode entered successfully")
                    break

            time.sleep(0.05)  # Small delay to avoid busy-waiting
        else:
            # Timeout occurred
            print(f"ERROR: Timeout waiting for CLI prompt")
            print(f"Received: {received_data.decode('ascii', errors='replace')}")
            ser.close()
            return False

        # Step 3: Send dfu command
        print("Sending DFU reboot command...")
        ser.write(b'dfu\r\n')
        ser.flush()

        # Step 4: Close connection
        time.sleep(0.2)
        ser.close()
        print("Serial connection closed")

        return True

    except serial.SerialException as e:
        print(f"ERROR: Serial port error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False


def main():
    # Parse command line arguments
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'

    # Attempt to reboot to DFU mode
    if reboot_to_dfu(port):
        print("\nWaiting for DFU device to appear (10 seconds)...")
        time.sleep(10)

        # Verify DFU device
        import subprocess
        try:
            result = subprocess.run(['dfu-util', '-l'],
                                    capture_output=True,
                                    text=True,
                                    timeout=5)

            if '0483:df11' in result.stdout:
                print("\n✓ SUCCESS: Flight controller is now in DFU mode\n")
                print(result.stdout)
                return 0
            else:
                print("\n⚠ WARNING: DFU device not detected. Check connection.")
                return 1

        except FileNotFoundError:
            print("\nNote: dfu-util not found, cannot verify DFU mode")
            print("Install with: sudo apt install dfu-util")
            return 0
        except Exception as e:
            print(f"\nNote: Could not verify DFU mode: {e}")
            return 0
    else:
        print("\n✗ FAILED: Could not reboot to DFU mode")
        return 1


if __name__ == '__main__':
    sys.exit(main())
