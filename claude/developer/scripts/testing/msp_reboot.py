#!/usr/bin/env python3
"""
MSP_REBOOT utility script - Send reboot commands to INAV flight controller

Usage:
    msp_reboot.py [device] [mode]

Arguments:
    device  - Serial device path (default: /dev/ttyACM0)
    mode    - Reboot mode: normal | dfu (default: normal)

Examples:
    msp_reboot.py                    # Normal reboot on /dev/ttyACM0
    msp_reboot.py /dev/ttyACM0 dfu   # DFU mode reboot
    msp_reboot.py /dev/ttyACM1       # Normal reboot on different port
"""

import sys
import time
sys.path.insert(0, '/home/raymorris/Documents/planes/inavflight/mspapi2')

from mspapi2 import MSPSerial

def msp_reboot(device='/dev/ttyACM0', mode='normal'):
    """
    Send MSP_REBOOT command to flight controller

    Args:
        device: Serial port path
        mode: 'normal' or 'dfu'
    """
    # MSP_REBOOT command code
    MSP_REBOOT = 68

    # Determine payload based on mode
    if mode.lower() == 'dfu':
        payload = b'\x01'  # DFU mode
        print(f"Rebooting {device} to DFU mode...")
    elif mode.lower() == 'normal':
        payload = b'\x00'  # Normal reboot (can also use empty b'')
        print(f"Rebooting {device} to normal mode...")
    else:
        raise ValueError(f"Invalid mode: {mode}. Use 'normal' or 'dfu'")

    try:
        # Connect to flight controller
        msp = MSPSerial(device, baudrate=115200)
        msp.open()

        # Send reboot command
        msp.send(MSP_REBOOT, payload)

        # Close connection
        msp.close()

        print("✓ Reboot command sent successfully")

        if mode.lower() == 'dfu':
            print("\nWaiting for device to enter DFU mode...")
            time.sleep(2)
            print("Run 'dfu-util -l' to verify DFU mode")
        else:
            print("\nDevice is rebooting...")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    # Parse command line arguments
    device = '/dev/ttyACM0'
    mode = 'normal'

    if len(sys.argv) > 1:
        device = sys.argv[1]

    if len(sys.argv) > 2:
        mode = sys.argv[2]

    # Execute reboot
    success = msp_reboot(device, mode)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
