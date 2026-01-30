#!/usr/bin/env python3
"""Test basic MSP communication"""
import serial
import struct
import time
import sys

def build_msp_request(cmd: int) -> bytes:
    """Build MSPv1 request packet"""
    header = b'$M<'
    size = 0
    checksum = size ^ cmd
    return header + struct.pack('BB', size, cmd) + struct.pack('B', checksum)

port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM1'
baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

print(f"Connecting to {port} at {baudrate}...")
ser = serial.Serial(port, baudrate, timeout=2)
time.sleep(0.5)

print("Sending MSP_API_VERSION (1)...")
ser.reset_input_buffer()
ser.write(build_msp_request(1))
time.sleep(0.1)
response = ser.read(100)
print(f"Response: {response.hex() if response else 'NONE'} ({len(response)} bytes)")

print("\nSending MSP_FC_VARIANT (2)...")
ser.reset_input_buffer()
ser.write(build_msp_request(2))
time.sleep(0.1)
response = ser.read(100)
print(f"Response: {response.hex() if response else 'NONE'} ({len(response)} bytes)")

print("\nSending MSP_RAW_IMU (102)...")
ser.reset_input_buffer()
ser.write(build_msp_request(102))
time.sleep(0.1)
response = ser.read(100)
print(f"Response: {response.hex() if response else 'NONE'} ({len(response)} bytes)")

if response:
    print("\n✓ FC is responding to MSP commands")
else:
    print("\n✗ FC not responding - check connection/baud rate")

ser.close()
