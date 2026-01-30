#!/usr/bin/env python3
"""
Debug MSP_BOARD_ALIGNMENT command
"""

import serial
import struct
import time
import sys

MSP_HEADER = b'$M<'
MSP_BOARD_ALIGNMENT = 242

def calculate_checksum(size, cmd, data=b''):
    checksum = size ^ cmd
    for byte in data:
        checksum ^= byte
    return checksum

def build_msp_request(cmd, data=b''):
    size = len(data)
    checksum = calculate_checksum(size, cmd, data)
    return MSP_HEADER + struct.pack('BB', size, cmd) + data + struct.pack('B', checksum)

port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'
baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

print(f"Connecting to {port} at {baudrate}...")
ser = serial.Serial(port, baudrate, timeout=2)
time.sleep(0.5)

print("Sending MSP_BOARD_ALIGNMENT (242)...")
request = build_msp_request(MSP_BOARD_ALIGNMENT)
print(f"Request bytes: {request.hex()}")

ser.reset_input_buffer()
ser.write(request)
time.sleep(0.2)

response = ser.read(100)
print(f"Response: {response.hex() if response else 'NONE'} ({len(response)} bytes)")

if response:
    print(f"Response ASCII: {response}")

    # Try to parse
    if b'$M>' in response:
        idx = response.find(b'$M>')
        print(f"Found response header at index {idx}")
        if len(response) >= idx + 5:
            size = response[idx + 3]
            cmd = response[idx + 4]
            print(f"Size: {size}, Command: {cmd}")
            if len(response) >= idx + 5 + size + 1:
                payload = response[idx + 5 : idx + 5 + size]
                print(f"Payload: {payload.hex()} ({len(payload)} bytes)")
                if len(payload) >= 6:
                    values = struct.unpack('<hhh', payload[:6])
                    print(f"Decoded: pitch={values[0]//10}°, roll={values[1]//10}°, yaw={values[2]//10}°")

ser.close()
