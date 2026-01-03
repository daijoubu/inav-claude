#!/usr/bin/env python3
"""
Test blackbox logging via SERIAL device in SITL.
Captures blackbox data from UART2 (TCP port 5761) while SITL is armed.
"""

import socket
import struct
import time
import threading
from mspapi2 import MSPApi, InavMSP

blackbox_data = bytearray()
capture_active = False

def capture_blackbox_stream(port=5761, duration=35):
    """Capture blackbox data from UART2."""
    global blackbox_data, capture_active

    print(f"\n[CAPTURE] Connecting to port {port} for blackbox data...")
    time.sleep(2)  # Wait for SITL to reboot

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        sock.connect(('localhost', port))
        print(f"[CAPTURE] Connected to port {port}")

        capture_active = True
        start_time = time.time()

        while capture_active and (time.time() - start_time) < duration:
            try:
                chunk = sock.recv(4096)
                if chunk:
                    blackbox_data.extend(chunk)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[CAPTURE] Error: {e}")
                break

        sock.close()
        print(f"[CAPTURE] Captured {len(blackbox_data)} bytes")

    except Exception as e:
        print(f"[CAPTURE] Failed to connect: {e}")

def main():
    global capture_active

    print("=== SITL Blackbox via SERIAL Test ===\n")

    # Step 1: Configure SITL
    print("Step 1: Connecting to SITL for configuration...")
    api = MSPApi(tcp_endpoint='localhost:5760')
    api.open()
    time.sleep(0.5)

    # Configure via CLI
    print("\nStep 2: Configuring blackbox via CLI...")
    # Enter CLI mode
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5760))
    sock.settimeout(2.0)
    api.close()  # Close MSP connection before CLI

    time.sleep(0.5)

    # Enter CLI
    sock.send(b'#####')
    time.sleep(1)

    # Configure blackbox
    print("   Setting blackbox_device = SERIAL")
    sock.send(b'set blackbox_device = SERIAL\r\n')
    time.sleep(0.3)
    sock.recv(4096)

    print("   Setting serial_port_2_functions = BLACKBOX")
    sock.send(b'set serial_port_2_functions = BLACKBOX\r\n')
    time.sleep(0.3)
    sock.recv(4096)

    print("   Setting blackbox_rate_denom = 100")
    sock.send(b'set blackbox_rate_denom = 100\r\n')
    time.sleep(0.3)
    sock.recv(4096)

    # Save
    print("   Saving configuration...")
    sock.send(b'save\r\n')
    time.sleep(2)
    sock.close()

    print("\nStep 3: Waiting for SITL to reboot...")
    time.sleep(15)

    # Step 2: Reconnect and configure arming
    print("\nStep 4: Configuring MSP receiver and ARM mode...")
    api = MSPApi(tcp_endpoint='localhost:5760')
    api.open()
    time.sleep(0.5)

    # Set receiver type to MSP
    response = api._serial.request(int(InavMSP.MSP_RX_CONFIG))
    rx_config = response[1] if isinstance(response, tuple) else response
    rx_config_list = list(rx_config)
    rx_config_list[23] = 2  # RX_TYPE_MSP
    api._serial.send(int(InavMSP.MSP_SET_RX_CONFIG), bytes(rx_config_list))
    time.sleep(0.2)

    # Configure ARM on AUX1
    mode_range = struct.pack('<BBBBB', 0, 0, 0, 32, 48)
    api._serial.send(int(InavMSP.MSP_SET_MODE_RANGE), mode_range)
    time.sleep(0.2)

    # Save and reboot
    api._serial.send(int(InavMSP.MSP_EEPROM_WRITE), b'')
    time.sleep(1)
    api._serial.send(int(InavMSP.MSP_REBOOT), b'')
    time.sleep(0.5)
    api.close()

    print("   Waiting for reboot...")
    time.sleep(15)

    # Step 3: Start blackbox capture thread
    print("\nStep 5: Starting blackbox capture thread...")
    capture_thread = threading.Thread(target=capture_blackbox_stream, daemon=True)
    capture_thread.start()
    time.sleep(3)  # Give capture thread time to connect

    # Step 4: Arm and fly
    print("\nStep 6: Connecting for flight...")
    api = MSPApi(tcp_endpoint='localhost:5760')
    api.open()

    # Enable HITL mode
    print("   Enabling HITL mode...")
    MSP_SIMULATOR = 0x201F
    payload = bytes([2, 1])
    api._serial.send(MSP_SIMULATOR, payload)
    time.sleep(0.5)

    # Arm and fly for 30 seconds
    print("\n   Flying armed for 30 seconds...")
    for i in range(1500):
        channels = [1500, 1500, 1000, 1500, 2000, 1000, 1000, 1000] + [1500]*8
        data = []
        for ch in channels:
            data.extend([ch & 0xFF, (ch >> 8) & 0xFF])

        api._serial.send(int(InavMSP.MSP_SET_RAW_RC), bytes(data))
        try:
            api._serial.recv()
        except:
            pass

        time.sleep(0.02)

        if i % 250 == 0:
            print(f"      {i//50} seconds...")

    # Disarm
    print("\n   Disarming...")
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

    # Step 5: Stop capture and save data
    print("\n\nStep 7: Stopping capture...")
    capture_active = False
    capture_thread.join(timeout=2)

    if len(blackbox_data) > 0:
        filename = f"blackbox_serial_{int(time.time())}.TXT"
        with open(filename, 'wb') as f:
            f.write(blackbox_data)
        print(f"\n✓ Saved {len(blackbox_data)} bytes to {filename}")
        print(f"\nDecode with: blackbox_decode {filename}")
    else:
        print("\n✗ No blackbox data captured!")

if __name__ == '__main__':
    main()
