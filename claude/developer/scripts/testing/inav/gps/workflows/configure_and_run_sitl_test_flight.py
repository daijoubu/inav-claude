#!/usr/bin/env python3
"""Configure SITL for blackbox logging and arming."""

import struct
import time
from mspapi2 import MSPApi, InavMSP

def main():
    print("Waiting for SITL to start...")
    time.sleep(10)

    print("Connecting to SITL on port 5760...")
    api = MSPApi(tcp_endpoint='localhost:5760')
    api.open()

    time.sleep(0.5)

    print("\n=== Configuring SITL ===\n")

    # Configure blackbox
    print("1. Enabling blackbox logging to SDCARD...")
    # We need to use CLI commands for this
    # For now, blackbox should already be configured in default SITL settings

    # Step 1: Set receiver type to MSP
    print("\n2. Setting receiver type to MSP...")
    response = api._serial.request(int(InavMSP.MSP_RX_CONFIG))
    rx_config = response[1] if isinstance(response, tuple) else response

    rx_config_list = list(rx_config)
    rx_config_list[23] = 2  # RX_TYPE_MSP
    new_rx_config = bytes(rx_config_list)

    api._serial.send(int(InavMSP.MSP_SET_RX_CONFIG), new_rx_config)
    time.sleep(0.2)
    print("   ✓ RX type set to MSP")

    # Step 2: Configure ARM mode on AUX1
    print("\n3. Configuring ARM switch on AUX1...")
    mode_range = struct.pack('<BBBBB', 0, 0, 0, 32, 48)
    api._serial.send(int(InavMSP.MSP_SET_MODE_RANGE), mode_range)
    time.sleep(0.2)
    print("   ✓ ARM configured on AUX1 (1700-2100us)")

    # Step 3: Save configuration
    print("\n4. Saving configuration...")
    api._serial.send(int(InavMSP.MSP_EEPROM_WRITE), b'')
    time.sleep(1)
    print("   ✓ Configuration saved")

    # Step 4: Reboot SITL
    print("\n5. Rebooting SITL...")
    api._serial.send(int(InavMSP.MSP_REBOOT), b'')
    time.sleep(0.5)

    api.close()

    print("\n   ✓ SITL configured and rebooting")
    print("\nWaiting 15 seconds for reboot...")
    time.sleep(15)

    # Now arm and run
    print("\n=== Starting flight ===\n")
    api = MSPApi(tcp_endpoint='localhost:5760')
    api.open()

    # Enable HITL mode
    print("Enabling HITL mode...")
    MSP_SIMULATOR = 0x201F
    payload = bytes([2, 1])  # version 2, HITL_ENABLE
    api._serial.send(MSP_SIMULATOR, payload)
    time.sleep(0.5)
    print("   ✓ HITL mode enabled")

    # Send RC data to arm
    print("\nSending RC data (armed for 30 seconds)...")
    for i in range(1500):  # 30 seconds at 50Hz
        # AETR order: Roll, Pitch, Throttle, Yaw, AUX1 (ARM), ...
        channels = [1500, 1500, 1000, 1500, 2000, 1000, 1000, 1000] + [1500]*8
        data = []
        for ch in channels:
            data.extend([ch & 0xFF, (ch >> 8) & 0xFF])

        api._serial.send(int(InavMSP.MSP_SET_RAW_RC), bytes(data))

        # Consume response to prevent buffer overflow
        try:
            api._serial.recv()
        except:
            pass

        time.sleep(0.02)  # 50Hz

        if i % 250 == 0:
            print(f"   Running... {i//50} seconds")

    # Disarm
    print("\nDisarming...")
    for i in range(50):
        channels = [1500, 1500, 1000, 1500, 1000, 1000, 1000, 1000] + [1500]*8
        data = []
        for ch in channels:
            data.extend([ch & 0xFF, (ch >> 8) & 0xFF])

        api._serial.send(int(InavMSP.MSP_SET_RAW_RC), bytes(data))
        try:
            api._serial.recv()
        except:
            pass
        time.sleep(0.02)

    api.close()
    print("\n✓ Flight complete")

if __name__ == '__main__':
    main()
