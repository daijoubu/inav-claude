#!/usr/bin/env python3
"""
Simplified blackbox capture - assumes SITL is already configured with:
- blackbox_device = SERIAL
- serial port 1 function = 129 (MSP + BLACKBOX)
- MSP receiver configured
- ARM mode on AUX1
"""

import socket
import struct
import time
import threading
from mspapi2 import MSPApi, InavMSP

blackbox_data = bytearray()
capture_active = False

def capture_blackbox_stream(port=5761, duration=40):
    """Capture blackbox data from UART2 (port 5761)."""
    global blackbox_data, capture_active

    print(f"[CAPTURE] Connecting to port {port}...")
    time.sleep(1)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        sock.connect(('localhost', port))
        print(f"[CAPTURE] Connected, waiting for blackbox data...")

        capture_active = True
        start_time = time.time()
        last_report = start_time

        while capture_active and (time.time() - start_time) < duration:
            try:
                chunk = sock.recv(4096)
                if chunk:
                    blackbox_data.extend(chunk)
                    # Report progress
                    now = time.time()
                    if now - last_report >= 5:
                        print(f"[CAPTURE] {len(blackbox_data)} bytes so far...")
                        last_report = now
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[CAPTURE] Error: {e}")
                break

        sock.close()
        print(f"[CAPTURE] Finished: {len(blackbox_data)} bytes captured")

    except Exception as e:
        print(f"[CAPTURE] Failed to connect: {e}")

def main():
    global capture_active

    print("=== Simplified SITL Blackbox Capture ===\n")

    # Start capture thread
    print("Starting blackbox capture thread on port 5761...")
    capture_thread = threading.Thread(target=capture_blackbox_stream, daemon=True)
    capture_thread.start()
    time.sleep(2)

    # Connect for arming
    print("\nConnecting to SITL on port 5760...")
    api = MSPApi(tcp_endpoint='localhost:5760')
    api.open()
    time.sleep(0.5)

    # Enable HITL mode
    print("Enabling HITL mode...")
    MSP_SIMULATOR = 0x201F
    payload = bytes([2, 1])
    api._serial.send(MSP_SIMULATOR, payload)
    time.sleep(0.5)

    # Arm and fly for 30 seconds
    print("\nFlying armed for 30 seconds...\n")
    for i in range(1500):
        # AETR order: Roll, Pitch, Throttle, Yaw, AUX1 (ARM)
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
            print(f"   {i//50} seconds...")

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

    # Stop capture
    print("\nStopping capture thread...")
    capture_active = False
    capture_thread.join(timeout=3)

    # Save data
    if len(blackbox_data) > 0:
        filename = f"blackbox_serial_{int(time.time())}.TXT"
        with open(filename, 'wb') as f:
            f.write(blackbox_data)
        print(f"\n✓ SUCCESS: Saved {len(blackbox_data)} bytes to {filename}")
        print(f"\nDecode with: blackbox_decode {filename}")
    else:
        print("\n✗ FAILED: No blackbox data captured!")
        print("\nDebugging tips:")
        print("1. Check: get blackbox_device (should be SERIAL)")
        print("2. Check: serial (port 1 function should be 129)")
        print("3. Check SITL log for blackbox messages")

if __name__ == '__main__':
    main()
