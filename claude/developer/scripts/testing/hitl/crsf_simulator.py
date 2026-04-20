#!/usr/bin/env python3
"""
CRSF Frame Simulator.

Simulates a CRSF receiver by sending RC channel frames at 150Hz
to a serial port. This can be used to test FC behavior with CRSF
input without needing actual CRSF hardware.

CRSF Protocol:
- 420000 baud, 8N1
- Frame: DEVICE_ADDRESS LENGTH TYPE PAYLOAD... CRC
- RC Channels frame: 0xC8 0x16 0x14 [16 channels x 2 bytes] CRC
"""

import serial
import time
import struct
import threading
import argparse
from typing import List, Optional


# CRSF frame types
CRSF_ADDRESS_CRSF = 0xC8
CRSF_ADDRESS_FLIGHT_CONTROLLER = 0x00

CRSF_FRAME_TYPE_RC_CHANNELS_PACKED = 0x16
CRSF_FRAME_TYPE_LINK_STATISTICS = 0x14
CRSF_FRAME_TYPE_MSP_REQ = 0x7A
CRSF_FRAME_TYPE_MSP_WRITE = 0x7B

CRSF_FRAME_LENGTH_RC_CHANNELS = 22  # 2 + 16 channels * 2 bytes + 1 CRC
CRSF_FRAME_LENGTH_LINK_STATISTICS = 10


def crc8(data: bytes) -> int:
    """Calculate CRC8 for CRSF frame."""
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
            crc &= 0xFF
    return crc


def build_rc_channels_frame(channels: List[int], channel_count: int = 16) -> bytes:
    """
    Build a CRSF RC channels packed frame.
    
    Args:
        channels: List of channel values (typically 988-2012)
        channel_count: Number of channels (default 16)
    
    Returns:
        Complete CRSF frame bytes
    """
    if len(channels) < channel_count:
        channels = channels + [1500] * (channel_count - len(channels))
    
    # Build payload: 16 channels x 2 bytes = 32 bytes
    payload = b''
    for i in range(channel_count):
        ch = channels[i]
        # CRSF uses 11-bit channel data packed into 16 bits
        # Channel value: 0-2047 maps to 988us-2012us
        payload += struct.pack('<H', ch & 0x7FF)
    
    # Build frame: address + length (includes type + payload + crc) + type + payload
    frame = bytes([
        CRSF_ADDRESS_FLIGHT_CONTROLLER,
        CRSF_FRAME_LENGTH_RC_CHANNELS,  # length (type + payload + crc)
        CRSF_FRAME_TYPE_RC_CHANNELS_PACKED,
    ]) + payload
    
    # Calculate CRC (excludes address and length)
    crc = crc8(frame[2:])  # CRC from type to end
    
    return frame + bytes([crc])


def build_link_statistics_frame(
    uplink_rssi: int = -30,
    uplink_link_quality: int = 100,
    uplink_snr: int = 10,
    uplink_rf_power: int = 100,
    downlink_rssi: int = -40,
    downlink_link_quality: int = 100,
    downlink_snr: int = 15
) -> bytes:
    """
    Build a CRSF link statistics frame.
    
    Args:
        uplink_rssi: RSSI (negative dBm)
        uplink_link_quality: Link quality (0-100%)
        uplink_snr: SNR (dB)
        uplink_rf_power: RF power (mW)
        downlink_rssi: Downlink RSSI
        downlink_link_quality: Downlink link quality
        downlink_snr: Downlink SNR
    
    Returns:
        Complete CRSF frame bytes
    """
    payload = bytes([
        uplink_rssi & 0xFF,  # uplink RSSI
        uplink_link_quality & 0xFF,  # uplink link quality
        uplink_snr & 0xFF,  # uplink SNR (signed)
        uplink_rf_power & 0xFF,  # uplink RF power
        0,  # downlink RSSI (2 bytes)
        downlink_rssi & 0xFF,
        downlink_link_quality & 0xFF,  # downlink link quality
        downlink_snr & 0xFF,  # downlink SNR (signed)
    ])
    
    frame = bytes([
        CRSF_ADDRESS_FLIGHT_CONTROLLER,
        CRSF_FRAME_LENGTH_LINK_STATISTICS,
        CRSF_FRAME_TYPE_LINK_STATISTICS,
    ]) + payload
    
    crc = crc8(frame[2:])
    return frame + bytes([crc])


class CRSFSimulator:
    """
    CRSF receiver simulator.
    
    Sends RC channel frames at configurable rate to simulate
    a CRSF receiver connected to a UART.
    """
    
    def __init__(self, port: str, baudrate: int = 420000,
                 channels: Optional[List[int]] = None,
                 frame_rate_hz: float = 150.0):
        self.port = port
        self.baudrate = baudrate
        self.frame_rate_hz = frame_rate_hz
        self.frame_interval = 1.0 / frame_rate_hz
        
        # Default channels: throttle low, arm off
        self.channels = channels or [1500] * 16
        self.channels[2] = 988   # Throttle low
        self.channels[4] = 988   # Arm off
        
        self.serial: Optional[serial.Serial] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Stats
        self.frames_sent = 0
        self.errors = 0
    
    def set_channels(self, channels: List[int]):
        """Update channel values."""
        if len(channels) < 16:
            channels = channels + [1500] * (16 - len(channels))
        self.channels = channels[:16]
    
    def set_throttle(self, value: int):
        """Set throttle channel (channel 3)."""
        self.channels[2] = max(988, min(2012, value))
    
    def set_armed(self, armed: bool):
        """Set arm state via channel 5."""
        self.channels[4] = 2000 if armed else 988
    
    def connect(self) -> bool:
        """Open serial port."""
        try:
            self.serial = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1.0,
                write_timeout=1.0
            )
            return True
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Close serial port."""
        if self.serial:
            self.serial.close()
            self.serial = None
    
    def start(self):
        """Start sending frames."""
        if self.running:
            return
        
        if not self.serial or not self.serial.is_open:
            if not self.connect():
                return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"CRSF simulator started on {self.port} at {self.baudrate} baud, {self.frame_rate_hz}Hz")
    
    def stop(self):
        """Stop sending frames."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print(f"CRSF simulator stopped. Frames sent: {self.frames_sent}")
    
    def _run_loop(self):
        """Main sending loop."""
        last_send = time.monotonic()
        
        while self.running:
            now = time.monotonic()
            elapsed = now - last_send
            
            if elapsed >= self.frame_interval:
                # Build and send RC channels frame
                frame = build_rc_channels_frame(self.channels)
                
                try:
                    self.serial.write(frame)
                    self.frames_sent += 1
                except Exception as e:
                    self.errors += 1
                    if self.errors < 10:
                        print(f"Write error: {e}")
                
                last_send = now
            
            # Small sleep to avoid busy waiting
            time.sleep(0.0001)
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.disconnect()
        return False


def test_crsf():
    """Test CRSF frame generation."""
    print("Testing CRSF frame generation...")
    
    # Test channel frame
    channels = [1500] * 16
    channels[2] = 1000  # Throttle
    channels[4] = 2000  # Arm
    
    frame = build_rc_channels_frame(channels)
    print(f"RC Channels frame ({len(frame)} bytes): {frame.hex()}")
    print(f"  Address: 0x{frame[0]:02X}")
    print(f"  Length: {frame[1]}")
    print(f"  Type: 0x{frame[2]:02X}")
    print(f"  Channels: {channels[:4]}...")
    print(f"  CRC: 0x{frame[-1]:02X}")
    
    # Test link statistics frame
    ls_frame = build_link_statistics_frame(
        uplink_rssi=-30,
        uplink_link_quality=100,
        uplink_snr=10
    )
    print(f"\nLink Stats frame ({len(ls_frame)} bytes): {ls_frame.hex()}")
    
    print("\nFrame generation OK!")


def main():
    parser = argparse.ArgumentParser(description="CRSF Receiver Simulator")
    parser.add_argument("port", help="Serial port (e.g., /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=420000, help="Baud rate (default: 420000)")
    parser.add_argument("--rate", type=float, default=150.0, help="Frame rate Hz (default: 150)")
    parser.add_argument("--throttle", type=int, default=1000, help="Initial throttle (default: 1000)")
    parser.add_argument("--armed", action="store_true", help="Start in armed state")
    parser.add_argument("--test", action="store_true", help="Test frame generation only")
    args = parser.parse_args()
    
    if args.test:
        test_crsf()
        return
    
    print(f"Starting CRSF simulator on {args.port} at {args.baud} baud")
    
    with CRSFSimulator(args.port, args.baud, frame_rate_hz=args.rate) as crsf:
        crsf.set_throttle(args.throttle)
        crsf.set_armed(args.armed)
        
        print(f"Channels: {crsf.channels}")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped by user")


if __name__ == '__main__':
    main()
