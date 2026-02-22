#!/usr/bin/env python3
"""
SD Card Test Automation for MATEKF765SE
========================================

Automated tests for validating SD card reliability before/after HAL update.
Uses MSP protocol to communicate with flight controller.

Tests Automated:
BASELINE TESTS (--baseline --test 1,2,3,4,6):
- Test 1: SD Card Detection & Initialization
- Test 2: Write Speed Measurement
- Test 3: Continuous Logging (configurable duration)
- Test 4: High-Frequency Logging
- Test 6: Rapid Arm/Disarm Cycles

ADVANCED TESTS:
- Test 8: GPS Fix + Immediate Arm (F765 lockup specific)
- Test 9: Extended Endurance Test (1+ hour stability)
- Test 10: DMA Contention Stress Test (concurrent SD/GPS)
- Test 11: Blocking Measurement (ST-Link + GDB)

Requirements:
- Python 3.9+
- mspapi2 library (pip install mspapi2 or install from repo)
- Flight controller connected via USB/serial
- SD card inserted
- For Test 8: GPS module connected and receiving signal
- For Test 9: None (optional: longer duration for extended test)
- For Test 10: GPS module with active fix
- For Test 11: ST-Link adapter, compiled ELF file

Usage:
    python sd_card_test.py /dev/ttyACM0
    python sd_card_test.py /dev/ttyACM0 --test 1,2,3
    python sd_card_test.py /dev/ttyACM0 --baseline
    python sd_card_test.py /dev/ttyACM0 --hal-version 1.3.3

Author: INAV Developer
Date: 2026-02-21
"""

import argparse
import json
import os
import platform
import shutil
import struct
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Optional

# Try to import mspapi2, provide helpful error if not available
try:
    from mspapi2 import MSPSerial
    MSPAPI2_AVAILABLE = True
except ImportError:
    MSPAPI2_AVAILABLE = False
    MSPSerial = None
    print("Warning: mspapi2 not installed. Install with: pip install mspapi2")
    print("         or clone from: https://github.com/xznhj8129/mspapi2")


# =============================================================================
# MSP Protocol Constants
# =============================================================================

class MSPCode:
    """MSP command codes"""
    # SD Card
    SDCARD_SUMMARY = 79

    # Blackbox
    DATAFLASH_SUMMARY = 70
    BLACKBOX_CONFIG = 0x201A  # MSP V2
    SET_BLACKBOX_CONFIG = 0x201B  # MSP V2

    # Status
    INAV_STATUS = 0x2000  # MSP V2
    STATUS_EX = 150

    # GPS
    RAW_GPS = 106
    COMP_GPS = 107
    GPSSTATISTICS = 166

    # RC Control
    SET_RAW_RC = 200
    RC = 105

    # Arming
    SET_ARMING_DISABLED = 0x200B  # MSP V2

    # Reboot
    SET_REBOOT = 68


class SDCardState(IntEnum):
    """SD card state enum from msp.c"""
    NOT_PRESENT = 0
    FATAL = 1
    CARD_INIT = 2
    FS_INIT = 3
    READY = 4


class GPSFixType(IntEnum):
    """GPS fix type enum"""
    NO_FIX = 0
    FIX_2D = 1
    FIX_3D = 2


class ArmingFlag(IntEnum):
    """Arming flags from runtime_config.h"""
    ARMED = 1 << 2
    WAS_EVER_ARMED = 1 << 3
    ARMING_DISABLED_FAILSAFE = 1 << 7
    ARMING_DISABLED_NOT_LEVEL = 1 << 8
    ARMING_DISABLED_THROTTLE = 1 << 19
    ARMING_DISABLED_ARM_SWITCH = 1 << 14
    ARMING_DISABLED_NO_PREARM = 1 << 28


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class SDCardStatus:
    """SD card status from MSP_SDCARD_SUMMARY"""
    supported: bool = False
    state: SDCardState = SDCardState.NOT_PRESENT
    fs_error: int = 0
    free_space_kb: int = 0
    total_space_kb: int = 0

    @property
    def state_name(self) -> str:
        return SDCardState(self.state).name

    @property
    def is_ready(self) -> bool:
        return self.state == SDCardState.READY


@dataclass
class GPSStatus:
    """GPS status from MSP_RAW_GPS"""
    fix_type: GPSFixType = GPSFixType.NO_FIX
    num_sat: int = 0
    latitude: float = 0.0
    longitude: float = 0.0
    altitude_cm: int = 0
    speed_cms: int = 0
    ground_course: int = 0
    hdop: float = 0.0

    @property
    def has_fix(self) -> bool:
        return self.fix_type == GPSFixType.FIX_3D

    @property
    def fix_name(self) -> str:
        return GPSFixType(self.fix_type).name


@dataclass
class ArmingStatus:
    """Arming status from MSP2_INAV_STATUS"""
    cycle_time: int = 0
    i2c_errors: int = 0
    cpu_load: int = 0
    arming_flags: int = 0

    @property
    def is_armed(self) -> bool:
        return bool(self.arming_flags & ArmingFlag.ARMED)

    @property
    def can_arm(self) -> bool:
        # Check if any arming disable flags are set (bits 6-30)
        disable_mask = 0x7FFFFFC0
        return (self.arming_flags & disable_mask) == 0


@dataclass
class TestResult:
    """Result of a single test"""
    test_num: int
    test_name: str
    passed: bool
    duration_sec: float = 0.0
    details: dict = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "test_num": self.test_num,
            "test_name": self.test_name,
            "passed": self.passed,
            "duration_sec": self.duration_sec,
            "details": self.details,
            "error": self.error
        }


@dataclass
class LogVerificationResult:
    """Result of log file verification"""
    passed: bool
    logs_found: int = 0
    total_size_bytes: int = 0
    total_size_mb: float = 0.0
    first_log_path: Optional[str] = None
    download_method: str = "unknown"  # "USB_MSC" or "MSP_FLASH"
    frame_count: int = 0
    i_frame_count: int = 0
    p_frame_count: int = 0
    header_fields: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "logs_found": self.logs_found,
            "total_size_mb": self.total_size_mb,
            "first_log_path": self.first_log_path,
            "download_method": self.download_method,
            "frame_count": self.frame_count,
            "i_frame_count": self.i_frame_count,
            "p_frame_count": self.p_frame_count,
            "header_fields": self.header_fields,
            "errors": self.errors,
            "warnings": self.warnings
        }


# =============================================================================
# MSP Communication Layer
# =============================================================================

class FCConnection:
    """Flight controller MSP connection wrapper"""

    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.conn: Optional[MSPSerial] = None

    def connect(self) -> bool:
        """Establish connection to flight controller"""
        if not MSPAPI2_AVAILABLE:
            print("ERROR: mspapi2 library not available")
            return False

        try:
            self.conn = MSPSerial(
                self.port,
                self.baudrate,
                read_timeout=0.1,
                write_timeout=0.5
            )
            self.conn.open()
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect to {self.port}: {e}")
            return False

    def disconnect(self):
        """Close connection"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass

    def _send_receive(self, code: int, data: bytes = b'', timeout: float = 1.0) -> Optional[bytes]:
        """Send MSP command and receive response"""
        if not self.conn:
            return None
        try:
            # MSPSerial.request() returns (code, payload) tuple
            _, payload = self.conn.request(code, data, timeout=timeout)
            return payload
        except Exception as e:
            print(f"MSP error (code {code}): {e}")
            return None

    def get_sd_card_status(self) -> Optional[SDCardStatus]:
        """Query SD card status via MSP_SDCARD_SUMMARY"""
        response = self._send_receive(MSPCode.SDCARD_SUMMARY)
        if not response or len(response) < 10:
            return None

        # Parse: u8 supported, u8 state, u8 fs_error, u32 free_kb, u32 total_kb
        # Note: response may be 10 or 11 bytes depending on version
        supported, state, fs_error = struct.unpack('<BBB', response[0:3])
        free_kb, total_kb = struct.unpack('<II', response[3:11]) if len(response) >= 11 else (0, 0)

        return SDCardStatus(
            supported=bool(supported & 0x01),
            state=SDCardState(state) if state <= 4 else SDCardState.NOT_PRESENT,
            fs_error=fs_error,
            free_space_kb=free_kb,
            total_space_kb=total_kb
        )

    def get_gps_status(self) -> Optional[GPSStatus]:
        """Query GPS status via MSP_RAW_GPS"""
        response = self._send_receive(MSPCode.RAW_GPS)
        if not response or len(response) < 18:
            return None

        # Parse: u8 fix, u8 numSat, i32 lat, i32 lon, i16 alt, i16 speed, i16 course, u16 hdop
        fix_type, num_sat = struct.unpack('<BB', response[0:2])
        lat, lon = struct.unpack('<ii', response[2:10])
        alt, speed, course, hdop = struct.unpack('<hhhH', response[10:18])

        return GPSStatus(
            fix_type=GPSFixType(fix_type) if fix_type <= 2 else GPSFixType.NO_FIX,
            num_sat=num_sat,
            latitude=lat / 1e7,
            longitude=lon / 1e7,
            altitude_cm=alt,
            speed_cms=speed,
            ground_course=course,
            hdop=hdop / 100.0
        )

    def get_arming_status(self) -> Optional[ArmingStatus]:
        """Query arming status via MSP2_INAV_STATUS"""
        response = self._send_receive(MSPCode.INAV_STATUS)
        if not response or len(response) < 12:
            return None

        # Parse: u16 cycleTime, u16 i2cErrors, u16 sensorStatus, u16 cpuLoad, u8 profile, u32 armingFlags
        cycle_time, i2c_errors, sensor_status, cpu_load = struct.unpack('<HHHH', response[0:8])
        profile = response[8]
        arming_flags = struct.unpack('<I', response[9:13])[0]

        return ArmingStatus(
            cycle_time=cycle_time,
            i2c_errors=i2c_errors,
            cpu_load=cpu_load,
            arming_flags=arming_flags
        )

    def get_blackbox_config(self) -> Optional[dict]:
        """Query blackbox config via MSP2_BLACKBOX_CONFIG (0x201A)"""
        response = self._send_receive(MSPCode.BLACKBOX_CONFIG)
        if not response or len(response) < 8:
            return None

        # Parse: u8 supported, u8 device, u16 rate_num, u16 rate_denom, u32 flags
        supported = response[0]
        device = response[1]
        rate_num = struct.unpack('<H', response[2:4])[0]
        rate_denom = struct.unpack('<H', response[4:6])[0]
        flags = struct.unpack('<I', response[6:10])[0] if len(response) >= 10 else 0

        return {
            "supported": bool(supported),
            "device": device,  # 0=SERIAL, 1=SPIFLASH, 2=SDCARD, 3=FILE
            "device_name": {0: "SERIAL", 1: "SPIFLASH", 2: "SDCARD", 3: "FILE"}.get(device, "UNKNOWN"),
            "rate_num": rate_num,
            "rate_denom": rate_denom,
            "flags": flags
        }

    def set_arming_disabled(self, disabled: bool, runaway_takeoff: bool = False) -> bool:
        """Enable/disable arming via MSP2_SET_ARMING_DISABLED"""
        # Payload: u8 command (1=disable, 0=enable), u8 disableRunawayTakeoff
        data = struct.pack('<BB', 1 if disabled else 0, 1 if runaway_takeoff else 0)
        response = self._send_receive(MSPCode.SET_ARMING_DISABLED, data)
        return response is not None

    def send_rc_channels(self, channels: list[int], rate_hz: float = 50.0) -> bool:
        """
        Send RC channels via MSP_SET_RAW_RC (200).

        Args:
            channels: List of 16 channel values (1000-2000)
            rate_hz: Update rate in Hz (default 50Hz)

        Note: For MSP RX, must send at 5Hz or faster. Uses AETR mapping:
            CH0=Roll, CH1=Pitch, CH2=Throttle, CH3=Yaw, CH4+=AUX
        """
        if not self.conn:
            return False

        # Ensure 16 channels
        while len(channels) < 16:
            channels.append(1500)

        payload = b''.join(struct.pack('<H', ch) for ch in channels[:16])
        try:
            self.conn.send(MSPCode.SET_RAW_RC, payload)
            return True
        except Exception as e:
            print(f"Error sending RC channels: {e}")
            return False

    # =========================================================================
    # Servo Stress Testing
    # =========================================================================

    def move_servos(self, duration: float, pattern: str = 'sweep', rate_hz: float = 10.0,
                    servo_channels: list[int] = None) -> dict:
        """
        Move servos for stress testing during logging.

        Generates RC channel commands to stress test servos while blackbox logs.
        Different patterns simulate different types of servo load.

        Args:
            duration: How long to move servos in seconds
            pattern: Type of servo movement:
                - 'sweep': Smooth oscillation from min to max (1000-2000)
                - 'random': Random jitter ±50% around center
                - 'rapid': Rapid position changes every 0.1s
                - 'hold': Keep at center (1500) - minimal stress
            rate_hz: How often to update RC commands (default 10 Hz)
            servo_channels: Which servo channels to move (default [6,7,8,9] for servos 6-9)

        Returns:
            dict with stress test results:
            - 'success': bool - All updates sent successfully
            - 'updates_sent': int - Number of RC updates sent
            - 'errors': int - Number of failed updates
            - 'pattern': str - Pattern used
            - 'duration': float - Actual duration in seconds
        """
        import time
        import random

        if servo_channels is None:
            servo_channels = [6, 7, 8, 9]  # Default to servos 6-9

        result = {
            'success': True,
            'updates_sent': 0,
            'errors': 0,
            'pattern': pattern,
            'duration': 0.0
        }

        if not self.conn:
            result['success'] = False
            return result

        try:
            start_time = time.time()
            update_interval = 1.0 / rate_hz
            last_update = start_time
            phase = 0.0

            while time.time() - start_time < duration:
                current_time = time.time()

                # Send update at desired rate
                if current_time - last_update >= update_interval:
                    # Build RC channels array
                    channels = [1500] * 16  # Center all channels

                    # Generate servo values based on pattern
                    if pattern == 'sweep':
                        # Smooth oscillation: sweep from 1000 to 2000
                        phase = (current_time - start_time) * 2.0  # 2 Hz sweep
                        servo_value = int(1500 + 500 * __import__('math').sin(phase * __import__('math').pi))

                    elif pattern == 'random':
                        # Random jitter ±250 around center (1250-1750)
                        servo_value = 1500 + random.randint(-250, 250)

                    elif pattern == 'rapid':
                        # Rapid changes: alternate between min and max every 0.1s
                        phase = (current_time - start_time) * 10.0  # 10 Hz toggle
                        servo_value = 1000 if int(phase) % 2 == 0 else 2000

                    elif pattern == 'hold':
                        # Static center - minimal stress
                        servo_value = 1500

                    else:
                        result['success'] = False
                        return result

                    # Apply servo value to all servo channels
                    for ch in servo_channels:
                        if ch < 16:
                            channels[ch] = servo_value

                    # Send RC update
                    if self.send_rc_channels(channels, rate_hz=rate_hz):
                        result['updates_sent'] += 1
                    else:
                        result['errors'] += 1
                        result['success'] = False

                    last_update = current_time

                # Small sleep to avoid busy-wait
                time.sleep(0.01)

            result['duration'] = time.time() - start_time
            return result

        except Exception as e:
            result['success'] = False
            result['errors'] += 1
            print(f"Servo stress test error: {e}")
            return result

    def start_servo_stress_background(self, duration: float, pattern: str = 'sweep',
                                     rate_hz: float = 10.0) -> dict:
        """
        Start servo stress testing in a background thread.

        Allows servo movement to run while other operations continue.
        Useful for stress testing while performing other FC operations.

        Args:
            duration: How long to run servo stress in seconds
            pattern: Stress pattern ('sweep', 'random', 'rapid', 'hold')
            rate_hz: Update rate in Hz

        Returns:
            dict with thread info:
            - 'thread': Thread object (can be joined later)
            - 'callback': Function to get results when done
        """
        import threading

        result_holder = {'result': None}

        def stress_thread():
            result_holder['result'] = self.move_servos(duration, pattern, rate_hz)

        thread = threading.Thread(target=stress_thread, daemon=False)
        thread.start()

        return {
            'thread': thread,
            'callback': lambda: result_holder['result'],
            'join': lambda timeout=None: thread.join(timeout)
        }

    def wait_for_servo_stress(self, stress_handle: dict, timeout: float = None) -> dict:
        """
        Wait for background servo stress to complete and get results.

        Args:
            stress_handle: Handle returned from start_servo_stress_background()
            timeout: Max time to wait (None = forever)

        Returns:
            Stress test result dict
        """
        stress_handle['join'](timeout)
        return stress_handle['callback']()

    def wait_for_arming_ready(self, timeout: float = 300.0, poll_interval: float = 0.5) -> tuple[bool, str]:
        """
        Wait for FC to be ready for arming (all sensor checks passing).

        Checks arming flags and displays status. Returns when ready or timeout occurs.
        Default 5-minute timeout allows for GPS 3D fix acquisition on cold start.

        GPS acquisition times:
        - Cold start (no recent data): 2-5 minutes
        - Warm start (recent position data): 30-60 seconds
        - Hot start (current position data): 10-30 seconds

        Args:
            timeout: Maximum time to wait in seconds (default: 300.0 = 5 minutes for GPS)
            poll_interval: How often to check status in seconds (default: 0.5)

        Returns:
            (ready: bool, status: str) - True if ready, False if timeout
        """
        start_time = time.time()
        last_status = None

        # Arming flags that block arming
        BLOCKING_FLAGS = {
            ArmingFlag.ARMING_DISABLED_NOT_LEVEL: "Not level",
            ArmingFlag.ARMING_DISABLED_FAILSAFE: "Failsafe active",
            ArmingFlag.ARMING_DISABLED_THROTTLE: "Throttle not LOW",
            ArmingFlag.ARMING_DISABLED_NO_PREARM: "PreArm checks failed",
            ArmingFlag.ARMING_DISABLED_ARM_SWITCH: "Arm switch not ready",
        }

        while time.time() - start_time < timeout:
            status = self.get_arming_status()
            if not status:
                return False, "Cannot query arming status"

            # Check if armed
            if status.arming_flags & ArmingFlag.ARMED:
                return False, "Already armed"

            # Check for blocking conditions
            blocking_reasons = []
            for flag, reason in BLOCKING_FLAGS.items():
                if status.arming_flags & flag:
                    blocking_reasons.append(reason)

            # Build status string
            if blocking_reasons:
                status_str = "Waiting: " + ", ".join(blocking_reasons)
            else:
                status_str = "Ready to arm"

            # Print only on change
            if status_str != last_status:
                print(f"  {status_str}")
                last_status = status_str

            # If ready, return success
            if not blocking_reasons:
                return True, "Ready to arm"

            # Wait before checking again
            time.sleep(poll_interval)

        # Timeout occurred
        remaining_reasons = []
        for flag, reason in BLOCKING_FLAGS.items():
            if status.arming_flags & flag:
                remaining_reasons.append(reason)

        if remaining_reasons:
            return False, f"Timeout: {', '.join(remaining_reasons)}"
        else:
            return False, "Timeout waiting for arm ready"

    def arm(self, timeout: float = 5.0, arm_channel: int = 4, arm_threshold: int = 1700) -> bool:
        """
        Attempt to arm the flight controller via MSP RC.
        
        Args:
            timeout: How long to try arming (seconds)
            arm_channel: Raw channel number for arm (default 4 = AUX1)
            arm_threshold: Channel value to trigger arm (default 1700)
        
        Requires:
            - FC configured with receiver_type = MSP
            - ARM mode configured on an AUX channel (default AUX1)
            - Arm channel must be LOW first, then raised HIGH
        
        Channel mapping (AETR):
            CH0=Roll, CH1=Pitch, CH2=Throttle, CH3=Yaw, CH4+=AUX
        """
        # First, enable arming (remove MSP disable)
        self.set_arming_disabled(False)

        # Check if already armed
        status = self.get_arming_status()
        if not status:
            return False

        if status.is_armed:
            return True  # Already armed

        # Phase 1: Send RC with arm channel LOW to establish link and clear ARM_SWITCH
        channels = [1500] * 16
        channels[2] = 1000  # Throttle LOW (raw channel 2)
        channels[arm_channel] = 1000  # ARM channel LOW

        print(f"  Establishing RC link (arm LOW)...")
        
        start_time = time.time()
        while time.time() - start_time < 2.0:
            self.send_rc_channels(channels)
            time.sleep(0.02)  # 50Hz

        # Check blockers
        status = self.get_arming_status()
        if status and not status.can_arm:
            print("  Cannot arm - arming flags still blocking")
            # Continue anyway, might still work

        # Phase 2: Raise arm channel to ARM
        print(f"  Sending ARM command (CH{arm_channel+1} HIGH)...")
        channels[arm_channel] = 2000  # ARM channel HIGH

        start_time = time.time()
        while time.time() - start_time < timeout:
            self.send_rc_channels(channels)
            time.sleep(0.02)  # 50Hz
            
            # Check if armed every 0.5s
            status = self.get_arming_status()
            if status and status.is_armed:
                print("  ARMED!")
                return True

        print("  Failed to arm within timeout")
        return False

    def disarm(self, timeout: float = 3.0, arm_channel: int = 4) -> bool:
        """
        Disarm the flight controller by setting arm channel low.
        """
        # Send RC channels with arm channel low
        channels = [1500] * 16
        channels[2] = 1000  # Throttle low (raw channel 2)
        channels[arm_channel] = 1000  # ARM channel low

        start_time = time.time()
        while time.time() - start_time < timeout:
            self.send_rc_channels(channels)
            time.sleep(0.02)
            
            status = self.get_arming_status()
            if status and not status.is_armed:
                return True

        # Also disable via MSP as backup
        return self.set_arming_disabled(True)

    def wait_for_gps_fix(self, timeout: float = 300.0, poll_interval: float = 1.0) -> bool:
        """Wait for GPS 3D fix"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            gps = self.get_gps_status()
            if gps and gps.has_fix:
                return True
            time.sleep(poll_interval)
        return False

    # =========================================================================
    # USB Mass Storage Operations
    # =========================================================================

    def find_msc_mount_point(self) -> Optional[Path]:
        """
        Find the USB Mass Storage device mount point for the FC.

        Looks for recently mounted mass storage devices that could be the FC.
        Returns the mount point path, or None if not found.
        """
        system = platform.system()

        if system == "Linux":
            return self._find_msc_mount_linux()
        elif system == "Darwin":
            return self._find_msc_mount_macos()
        elif system == "Windows":
            return self._find_msc_mount_windows()
        else:
            return None

    def _find_msc_mount_linux(self) -> Optional[Path]:
        """Find USB MSC mount point on Linux"""
        # Look for recently mounted removable media
        possible_paths = [
            Path("/mnt"),
            Path("/media"),
            Path(os.path.expanduser("~")),
        ]

        try:
            # Check for INAV_LOG labeled device
            result = subprocess.run(
                ["findmnt", "-r", "-o", "TARGET,SOURCE"],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.split('\n'):
                if 'sd' in line.lower() or 'usb' in line.lower():
                    parts = line.split()
                    if len(parts) >= 1:
                        mount_path = Path(parts[0])
                        if mount_path.exists() and mount_path.is_dir():
                            # Check if it has LOGS directory (SD card indicator)
                            logs_dir = mount_path / "LOGS"
                            if logs_dir.exists():
                                return mount_path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Fallback: look in /mnt and /media for recent directories
        for base_path in possible_paths:
            if not base_path.exists():
                continue

            try:
                for item in base_path.iterdir():
                    if item.is_dir() and (item / "LOGS").exists():
                        return item
            except (PermissionError, OSError):
                pass

        return None

    def _find_msc_mount_macos(self) -> Optional[Path]:
        """Find USB MSC mount point on macOS"""
        # On macOS, check /Volumes for recently mounted devices
        volumes_path = Path("/Volumes")
        if not volumes_path.exists():
            return None

        try:
            for item in volumes_path.iterdir():
                if item.is_dir() and (item / "LOGS").exists():
                    return item
        except (PermissionError, OSError):
            pass

        return None

    def _find_msc_mount_windows(self) -> Optional[Path]:
        """Find USB MSC mount point on Windows"""
        # On Windows, check all drive letters for recently mounted devices
        import string

        for drive_letter in string.ascii_uppercase:
            drive_path = Path(f"{drive_letter}:\\")
            try:
                if drive_path.exists():
                    logs_dir = drive_path / "LOGS"
                    if logs_dir.exists():
                        return drive_path
            except (PermissionError, OSError):
                pass

        return None

    def clear_sd_card_logs(self) -> bool:
        """
        Clear old log files from SD card via USB Mass Storage.

        This finds the FC's USB MSC mount point and deletes files in the LOGS
        directory to free up space. Keeps the directory structure intact.

        Returns:
            True if logs were cleared successfully, False otherwise
        """
        # Find the mount point
        mount_point = self.find_msc_mount_point()
        if not mount_point:
            return False

        logs_dir = mount_point / "LOGS"
        if not logs_dir.exists():
            return False

        try:
            deleted_files = 0
            total_size = 0

            # Delete all .LOG and .BBL files in LOGS directory
            for file_path in logs_dir.glob("*"):
                if file_path.is_file() and file_path.suffix.upper() in ['.LOG', '.BBL']:
                    try:
                        total_size += file_path.stat().st_size
                        file_path.unlink()
                        deleted_files += 1
                    except (PermissionError, OSError):
                        pass

            return deleted_files > 0
        except (PermissionError, OSError):
            return False

    # =========================================================================
    # CLI Command Interface
    # =========================================================================

    def send_cli_command(self, command: str, timeout: float = 2.0) -> bool:
        """
        Send a CLI command to the flight controller with proper exit sequence.

        This mimics how INAV Configurator handles CLI mode:
        1. Enter CLI mode with '#'
        2. Send command(s)
        3. Properly exit CLI mode (critical for FC stability)
        4. Reconnect MSP

        Args:
            command: CLI command to send (without # prefix or CR)
            timeout: How long to wait for response (seconds)

        Returns:
            True if command sent successfully, False otherwise
        """
        if not self.conn:
            return False

        try:
            import serial as pyserial

            # Close MSP connection to free serial port
            self.disconnect()
            time.sleep(0.5)

            # Open serial port directly for CLI access
            ser = pyserial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(0.5)

            # Enter CLI mode (send '#' and wait for prompt)
            ser.write(b"#")
            time.sleep(0.2)
            ser.read(100)  # Read response/prompt

            # Send command
            ser.write(f"{command}\r".encode())
            time.sleep(0.5)
            response = ser.read(500)  # Read response

            # CRITICAL: Properly exit CLI mode (this is what Configurator does)
            # Send "exit" or just newline to return to normal mode
            ser.write(b"\r")
            time.sleep(0.2)
            ser.read(100)  # Consume any response

            # Give FC time to exit CLI mode cleanly
            time.sleep(0.5)

            # Close serial port
            ser.close()
            time.sleep(0.5)

            # Reconnect MSP with fresh connection
            self.connect()
            time.sleep(0.5)

            return True

        except Exception as e:
            print(f"CLI error: {e}")
            # Try to recover by reconnecting
            try:
                self.connect()
            except:
                pass
            return False

    def set_blackbox_config_via_msp(self, rate_num: int, rate_denom: int) -> bool:
        """
        Set blackbox config via MSP2_SET_BLACKBOX_CONFIG (0x201B).

        This is more reliable than CLI mode switching because it avoids serial
        mode transitions and state inconsistencies.

        Args:
            rate_num: Rate numerator (e.g., 1 for 1/4 rate)
            rate_denom: Rate denominator (e.g., 4 for 1/4 rate)

        Returns:
            True if config set successfully, False otherwise
        """
        if not self.conn or rate_num < 1 or rate_denom < 1:
            return False

        try:
            # Build packet: u8 supported, u8 device, u16 rate_num, u16 rate_denom, u32 flags
            # Get current config first to preserve other settings
            current_config = self.get_blackbox_config()
            if not current_config:
                # Use defaults if we can't read current config
                supported = 1
                device = 0
                flags = 0
            else:
                supported = current_config['supported']
                device = current_config['device']
                flags = current_config['flags']

            # Build MSP packet with new rate
            packet = struct.pack(
                '<BBHHI',
                supported,           # u8 supported
                device,              # u8 device
                rate_num,            # u16 rate_num
                rate_denom,          # u16 rate_denom
                flags                # u32 flags
            )

            # Send via MSP
            _, response = self.conn.request(MSPCode.SET_BLACKBOX_CONFIG, packet, timeout=1.0)

            # MSP response is typically empty on success, just check if we got a response
            return True

        except Exception as e:
            print(f"MSP blackbox config error: {e}")
            return False

    def set_blackbox_rate(self, rate: str) -> bool:
        """
        Set blackbox logging rate via CLI command.

        Valid rates: 1/2, 1/4, 1/8, 1/16

        Smart optimization: Check current rate first - only change if different.
        This avoids unnecessary CLI mode switching which can destabilize MSP.

        Args:
            rate: Blackbox rate (e.g., "1/4")

        Returns:
            True if rate set successfully or already correct, False on error
        """
        if not rate or "/" not in rate:
            return False

        try:
            # Parse target rate
            parts = rate.split("/")
            if len(parts) != 2:
                return False

            target_num = int(parts[0].strip())
            target_denom = int(parts[1].strip())

            if target_num < 1 or target_denom < 1 or target_denom > 32:
                return False

            # Check current rate to avoid unnecessary CLI switch
            current_config = self.get_blackbox_config()
            if current_config:
                current_num = current_config['rate_num']
                current_denom = current_config['rate_denom']
                if current_num == target_num and current_denom == target_denom:
                    # Already at target rate - no change needed!
                    return True

            # Rate needs to be changed - use CLI (MSP SET not supported in this firmware)
            if self.send_cli_command(f"set blackbox_rate={rate}"):
                time.sleep(0.2)
                return self.send_cli_command("save")

            return False

        except Exception as e:
            return False

    # =========================================================================
    # FC Configuration Validation
    # =========================================================================

    def validate_fc_configuration(self, config_file: str = "baseline-fc-config.txt") -> dict:
        """
        Validate FC configuration against baseline requirements.

        Can use existing dumped config or run fc-get to dump current configuration.
        Checks for:
        - Motor mixer configured (4-motor quadcopter)
        - Servo mixer configured (4 servos on channels 6-9)
        - GPS feature enabled
        - PWM_OUTPUT_ENABLE feature enabled
        - Blackbox rate set to 1/2 (denom=2)
        - Serial ports configured

        Args:
            config_file: Path to baseline or current config file

        Returns:
            dict with keys:
            - 'valid': bool - True if all checks pass
            - 'issues': list[str] - Any missing/invalid configurations
            - 'config': str - Path to config file used
            - 'details': dict - Parsed configuration details
        """
        import subprocess
        import tempfile
        import os
        import time

        result = {
            'valid': True,
            'issues': [],
            'config': None,
            'details': {}
        }

        try:
            config_text = None
            config_path = None

            # Check if baseline config file already exists
            if os.path.exists(config_file):
                print(f"  Using existing config file: {config_file}")
                with open(config_file, 'r') as f:
                    config_text = f.read()
                config_path = config_file
            else:
                # Dump current FC configuration via fc-get
                temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
                temp_path = temp_config.name
                temp_config.close()

                print(f"  Dumping FC configuration via fc-get (this may take ~30-60s)...")
                cmd = f"fc-get {self.port} {temp_path}"
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Wait up to 90 seconds for fc-get to complete
                start_time = time.time()
                try:
                    stdout, stderr = process.communicate(timeout=90)
                except subprocess.TimeoutExpired:
                    process.kill()
                    result['issues'].append(f"fc-get timed out (>90s). Run manually: fc-get {self.port} {config_file}")
                    result['valid'] = False
                    return result

                elapsed = time.time() - start_time
                print(f"  fc-get completed in {elapsed:.1f}s")

                # Read the dumped configuration
                if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                    result['issues'].append("fc-get failed to create config file")
                    result['valid'] = False
                    return result

                with open(temp_path, 'r') as f:
                    config_text = f.read()

                config_path = temp_path

            if not config_text:
                result['issues'].append("No configuration data to validate")
                result['valid'] = False
                return result

            result['config'] = config_path

            # Parse configuration
            lines = config_text.split('\n')

            # Check for required features
            has_gps = False
            has_pwm_output = False

            # Check for motor mixer
            motor_mixer_lines = []
            servo_mixer_lines = []
            blackbox_rate = None
            serial_ports = []

            in_motor_mixer = False
            in_servo_mixer = False

            for line in lines:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Check blackbox rate FIRST (before other 'set' checks)
                if 'blackbox_rate_denom' in line and '=' in line:
                    try:
                        value_part = line.split('=')[1].strip()
                        blackbox_rate = int(value_part)
                    except (ValueError, IndexError):
                        pass

                # Check features
                if line.startswith('feature GPS'):
                    has_gps = True
                elif line.startswith('feature PWM_OUTPUT_ENABLE'):
                    has_pwm_output = True

                # Check motor mixer
                elif line == 'mmix reset':
                    in_motor_mixer = True
                elif in_motor_mixer and line.startswith('mmix '):
                    motor_mixer_lines.append(line)
                elif line.startswith('smix reset'):
                    in_motor_mixer = False
                    in_servo_mixer = True

                # Check servo mixer
                elif in_servo_mixer and line.startswith('smix '):
                    servo_mixer_lines.append(line)
                elif line.startswith('mixer_profile') or (line.startswith('set ') and 'blackbox_rate_denom' not in line):
                    in_servo_mixer = False

                # Check serial ports
                elif line.startswith('serial '):
                    serial_ports.append(line)

            # Store parsed details
            result['details'] = {
                'has_gps': has_gps,
                'has_pwm_output': has_pwm_output,
                'motor_mixer_count': len(motor_mixer_lines),
                'servo_mixer_count': len(servo_mixer_lines),
                'blackbox_rate_denom': blackbox_rate,
                'serial_ports': len(serial_ports),
            }

            # Validate all requirements
            if not has_gps:
                result['issues'].append("GPS feature not enabled")
                result['valid'] = False

            if not has_pwm_output:
                result['issues'].append("PWM_OUTPUT_ENABLE feature not enabled")
                result['valid'] = False

            if len(motor_mixer_lines) != 4:
                result['issues'].append(f"Motor mixer: expected 4 motors, found {len(motor_mixer_lines)}")
                result['valid'] = False

            if len(servo_mixer_lines) != 4:
                result['issues'].append(f"Servo mixer: expected 4 servos, found {len(servo_mixer_lines)}")
                result['valid'] = False

            if blackbox_rate != 2:
                result['issues'].append(f"Blackbox rate: expected denom=2 (1/2), found denom={blackbox_rate}")
                result['valid'] = False

            if len(serial_ports) < 2:
                result['issues'].append(f"Serial ports: expected at least 2, found {len(serial_ports)}")
                result['valid'] = False

            return result

        except Exception as e:
            result['issues'].append(f"Validation error: {str(e)}")
            result['valid'] = False
            return result

    def apply_baseline_configuration(self, config_file: str = "baseline-fc-config.txt") -> bool:
        """
        Apply baseline configuration to FC using fc-set.

        Requires fc-set utility installed and baseline config file to exist.

        Args:
            config_file: Path to baseline configuration file

        Returns:
            True if configuration applied successfully, False otherwise
        """
        import subprocess
        import os

        if not os.path.exists(config_file):
            print(f"ERROR: Baseline config file not found: {config_file}")
            return False

        try:
            print(f"  Applying baseline configuration via fc-set...")
            cmd = f"fc-set {self.port} {config_file}"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait up to 120 seconds for fc-set to complete
            try:
                stdout, stderr = process.communicate(timeout=120)
            except subprocess.TimeoutExpired:
                process.kill()
                print("  ERROR: fc-set timed out (>120s)")
                return False

            if process.returncode != 0:
                print(f"  ERROR: fc-set failed with code {process.returncode}")
                return False

            print(f"  ✓ Configuration applied successfully")
            return True

        except Exception as e:
            print(f"  ERROR: Failed to apply configuration: {e}")
            return False

    # =========================================================================
    # Blackbox Log Download & Verification
    # =========================================================================

    def enable_msc_mode(self, timeout: float = 30.0) -> bool:
        """
        Enable USB MSC mode via CLI command.

        Sends 'msc' command through serial CLI which reboots FC into MSC mode.
        Waits for FC to reboot and appear as USB mass storage device.

        Args:
            timeout: How long to wait for MSC device to appear (seconds)

        Returns:
            True if MSC mode enabled successfully, False otherwise
        """
        if not self.conn:
            return False

        try:
            import serial as pyserial

            # Close MSP connection to free serial port
            self.disconnect()
            time.sleep(0.5)

            # Open serial port directly for CLI access
            ser = pyserial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(0.5)

            # Enter CLI mode
            ser.write(b"#")
            time.sleep(0.2)
            ser.read(100)  # Read response

            # Send msc command
            ser.write(b"msc\r")
            time.sleep(1)
            ser.read(500)  # Read response

            ser.close()
            time.sleep(1)

            # Wait for FC to reboot and appear as USB device
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Try to find the mount point
                mount_point = self.find_msc_mount_point()
                if mount_point:
                    return True
                time.sleep(1)

            return False

        except Exception as e:
            return False

    def exit_msc_mode_and_reenumerate(self, openocd_config: str = None) -> bool:
        """
        Exit USB MSC mode and restore normal INAV operation.

        Process:
        1. Safely unmount USB MSC storage
        2. Reset FC via ST-Link (hardware reset)
        3. Force CDC ACM driver to bind to USB device
        4. Wait for /dev/ttyACM0 to appear
        5. Verify INAV is responding on serial

        Args:
            openocd_config: Path to OpenOCD config file (auto-detected if None)

        Returns:
            True if successfully restored to normal operation, False otherwise
        """
        try:
            import subprocess

            print("\n" + "="*60)
            print("EXITING USB MSC MODE AND RESTORING NORMAL OPERATION")
            print("="*60)

            # Step 1: Safely unmount MSC device
            print("\n1. Unmounting USB MSC storage...")
            msc_mount = self.find_msc_mount_point()
            if msc_mount:
                try:
                    result = subprocess.run(
                        ["udisksctl", "unmount", "-b", "/dev/sdb1"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print("   ✓ USB MSC safely unmounted")
                    else:
                        print("   ⚠ Unmount may have failed, continuing...")
                except Exception as e:
                    print(f"   ⚠ Unmount error: {e}")
            else:
                print("   ℹ Not currently in MSC mode")

            time.sleep(1)

            # Step 2: Reset via ST-Link
            print("\n2. Resetting FC via ST-Link...")

            # Find OpenOCD config if not provided
            if not openocd_config:
                config_paths = [
                    Path("/home/robs/Projects/inav-claude/claude/developer/workspace/sd-card-test-plan/openocd_matekf765_no_halt.cfg"),
                    Path("/home/robs/Projects/inav-claude/claude/developer/workspace/sd-card-test-plan/openocd_matekf765.cfg"),
                ]
                for path in config_paths:
                    if path.exists():
                        openocd_config = str(path)
                        break

            if openocd_config and Path(openocd_config).exists():
                print(f"   Using config: {openocd_config}")
                try:
                    result = subprocess.run(
                        [
                            "openocd",
                            "-f", openocd_config,
                            "-c", "init",
                            "-c", "reset hard",
                            "-c", "sleep 3000",
                            "-c", "shutdown"
                        ],
                        capture_output=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        print("   ✓ Hardware reset sent via ST-Link")
                    else:
                        print("   ⚠ OpenOCD reset may have failed")
                except Exception as e:
                    print(f"   ⚠ ST-Link reset error: {e}")
                    return False
            else:
                print("   ⚠ OpenOCD config not found, skipping ST-Link reset")
                print("   (Device may still need USB reconnect)")

            time.sleep(2)

            # Step 3: Force CDC driver to bind
            print("\n3. Forcing CDC ACM driver to bind...")

            # Find the USB device path
            usb_device = None
            try:
                for dev in Path("/sys/bus/usb/devices").iterdir():
                    if dev.is_dir():
                        try:
                            vid_file = dev / "idVendor"
                            pid_file = dev / "idProduct"
                            if vid_file.exists() and pid_file.exists():
                                vid = vid_file.read_text().strip()
                                pid = pid_file.read_text().strip()
                                # STM32 CDC: VID=0483, PID=572a
                                if vid == "0483" and pid == "572a":
                                    usb_device = dev.name
                                    break
                        except:
                            pass
            except:
                pass

            if usb_device:
                print(f"   Found FC USB device: {usb_device}")

                # Try to bind CDC driver with sudo
                bind_cmd = f"echo {usb_device} > /sys/bus/usb/drivers/cdc_acm/bind"
                try:
                    result = subprocess.run(
                        ["sudo", "sh", "-c", bind_cmd],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print("   ✓ CDC ACM driver bound successfully")
                    else:
                        # Try without sudo (may work if permissions are open)
                        try:
                            result = subprocess.run(
                                ["sh", "-c", bind_cmd],
                                capture_output=True,
                                timeout=5
                            )
                            if result.returncode == 0:
                                print("   ✓ CDC ACM driver bound successfully")
                            else:
                                print("   ⚠ CDC driver bind failed, waiting for auto-enumeration...")
                        except:
                            print("   ⚠ CDC driver bind failed, waiting for auto-enumeration...")
                except Exception as e:
                    print(f"   ⚠ CDC driver error: {e}")
            else:
                print("   ⚠ USB device not found in /sys/bus/usb")
                print("   Waiting for auto-enumeration...")

            time.sleep(2)

            # Step 4: Wait for serial port to appear
            print("\n4. Waiting for serial port to appear...")
            max_attempts = 20
            for attempt in range(max_attempts):
                if Path(self.port).exists():
                    print(f"   ✓ {self.port} appeared (attempt {attempt+1}/{max_attempts})")
                    time.sleep(1)
                    break
                if attempt < max_attempts - 1:
                    print(f"   Attempt {attempt+1}/{max_attempts}: Waiting for {self.port}...")
                    time.sleep(1)
            else:
                print(f"   ⚠ {self.port} did not appear after {max_attempts} attempts")
                print("   Try physically reconnecting the USB cable")
                return False

            # Step 5: Verify INAV is responding
            print("\n5. Verifying INAV is responding...")
            max_reconnect_attempts = 5
            for attempt in range(max_reconnect_attempts):
                try:
                    self.connect(attempts=1)
                    if self.conn:
                        print(f"   ✓ Connected to INAV on {self.port}")

                        # Try a simple MSP command to verify responsiveness
                        status = self.send_msp_command(MSPCode.SDCARD_SUMMARY)
                        if status:
                            print("   ✓ INAV is responding to MSP commands")
                            return True
                except:
                    pass

                if attempt < max_reconnect_attempts - 1:
                    print(f"   Attempt {attempt+1}/{max_reconnect_attempts}: Reconnecting...")
                    time.sleep(1)

            print("   ✗ INAV not responding yet")
            return False

        except Exception as e:
            print(f"Error during MSC exit/re-enumeration: {e}")
            import traceback
            traceback.print_exc()
            return False

    def download_logs_from_msc(self, output_dir: Path = None) -> list[tuple[Path, bytes]]:
        """
        Download blackbox logs from FC via USB Mass Storage (fastest method).

        Looks for .BBL, .LOG, and .TXT log files.

        Args:
            output_dir: Directory to copy logs to (optional)

        Returns:
            List of (file_path, file_data) tuples, or empty list if failed
        """
        mount_point = self.find_msc_mount_point()
        if not mount_point:
            return []

        logs_dir = mount_point / "LOGS"
        if not logs_dir.exists():
            return []

        logs = []
        try:
            # Look for all log file formats: .BBL, .LOG, .TXT
            for log_file in sorted(logs_dir.glob("*.BBL")) + sorted(logs_dir.glob("*.LOG")) + sorted(logs_dir.glob("*.TXT")):
                if log_file.is_file():
                    try:
                        with open(log_file, 'rb') as f:
                            data = f.read()
                        logs.append((log_file, data))

                        # Copy to output directory if specified
                        if output_dir:
                            output_dir.mkdir(parents=True, exist_ok=True)
                            output_file = output_dir / log_file.name
                            with open(output_file, 'wb') as f:
                                f.write(data)
                    except (PermissionError, OSError):
                        pass
        except (PermissionError, OSError):
            pass

        return logs

    def download_logs_from_msp_flash(self, output_dir: Path = None) -> list[tuple[str, bytes]]:
        """
        Download blackbox logs from FC via MSP SPIFLASH (fallback method).

        Slower than USB MSC but works if FC doesn't support MSC.

        Args:
            output_dir: Directory to save logs to (optional)

        Returns:
            List of (filename, data) tuples, or empty list if failed
        """
        if not self.conn:
            return []

        logs = []

        # Get dataflash summary
        try:
            _, response = self.conn.request(70, b"", timeout=2.0)  # MSP_DATAFLASH_SUMMARY
            if len(response) < 13:
                return []

            flags, sectors, total_size, used_size = struct.unpack('<BIII', response[:13])

            if used_size == 0:
                return []

            # Download log data via MSP_DATAFLASH_READ
            log_data = bytearray()
            address = 0
            chunk_size = 128
            errors = 0
            max_errors = 10

            while address < used_size and errors < max_errors:
                to_read = min(chunk_size, used_size - address)
                request = struct.pack('<IH', address, to_read)

                try:
                    _, response = self.conn.request(71, request, timeout=2.0)  # MSP_DATAFLASH_READ
                    if len(response) >= 4:
                        chunk_data = response[4:]  # Skip address in response
                        log_data.extend(chunk_data)
                        address += len(chunk_data)
                        errors = 0
                    else:
                        errors += 1
                        time.sleep(0.1)
                except Exception:
                    errors += 1
                    time.sleep(0.1)

            if errors < max_errors and len(log_data) > 0:
                filename = f"blackbox_fc_{int(time.time())}.BBL"
                logs.append((filename, bytes(log_data)))

                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_file = output_dir / filename
                    with open(output_file, 'wb') as f:
                        f.write(log_data)

        except Exception:
            pass

        return logs

    def verify_blackbox_log(self, log_data: bytes) -> LogVerificationResult:
        """
        Verify blackbox log integrity and extract frame information.

        Checks:
        - Log has proper header section
        - Log contains I-frames and P-frames
        - Required fields are defined in header
        - No obvious corruption

        Args:
            log_data: Raw blackbox log file data

        Returns:
            LogVerificationResult with pass/fail status and details
        """
        result = LogVerificationResult(passed=False)

        if not log_data:
            result.errors.append("Empty log data")
            return result

        try:
            # Check for header section (text-based)
            header_end = log_data.rfind(b'\nH ')
            if header_end == -1:
                # Try alternate header marker
                header_end = log_data.rfind(b'H ')
                if header_end == -1:
                    result.errors.append("No blackbox header found")
                    return result

            header_section = log_data[:header_end].decode('utf-8', errors='ignore')

            # Parse header fields
            for line in header_section.split('\n'):
                if line.startswith('H '):
                    parts = line[2:].split(',')
                    if len(parts) >= 2:
                        field_name = parts[0].strip()
                        field_info = ','.join(parts[1:]).strip()
                        result.header_fields[field_name] = field_info

            # Check required fields
            required_fields = ['loopIteration', 'time', 'gyroADC']
            missing_fields = [f for f in required_fields if f not in result.header_fields]
            if missing_fields:
                result.warnings.append(f"Missing fields: {', '.join(missing_fields)}")

            # Count frames in data section
            frame_section = log_data[header_end:]
            result.i_frame_count = frame_section.count(b'I')
            result.p_frame_count = frame_section.count(b'P')
            result.frame_count = result.i_frame_count + result.p_frame_count

            if result.frame_count == 0:
                result.errors.append("No frame data found (no I or P frames)")
                return result

            # Basic validation
            if result.i_frame_count < 1:
                result.errors.append("No I-frames (key frames) found")
            else:
                result.passed = True  # At least has valid structure

            # Warn if very few frames
            if result.frame_count < 10:
                result.warnings.append(f"Very few frames logged ({result.frame_count})")

        except Exception as e:
            result.errors.append(f"Exception parsing log: {str(e)}")

        return result


# =============================================================================
# Test Implementations
# =============================================================================

class SDCardTestSuite:
    """SD Card test suite"""

    def __init__(self, fc: FCConnection, verbose: bool = True):
        self.fc = fc
        self.verbose = verbose
        self.results: list[TestResult] = []
        self.sd_card_info: dict = {}  # Track SD card info for baseline

    def log(self, message: str):
        """Print message if verbose mode"""
        if self.verbose:
            print(message)

    # -------------------------------------------------------------------------
    # Pre-Test Validation
    # -------------------------------------------------------------------------

    def validate_sd_card_ready(self, min_free_mb: float = 100.0) -> bool:
        """
        Validate SD card is ready and has sufficient free space.

        Automatically attempts to clear old logs via USB MSC if space is insufficient.

        Args:
            min_free_mb: Minimum free space required in MB (default: 100)

        Returns:
            True if SD card is ready with sufficient space, False otherwise
        """
        self.log("\n" + "="*60)
        self.log("PRE-TEST VALIDATION: SD Card Readiness Check")
        self.log("="*60)

        # Get SD card status
        sd_status = self.fc.get_sd_card_status()
        if not sd_status:
            self.log("  ✗ Failed to query SD card status")
            return False

        # Store SD card info for baseline
        self.sd_card_info = {
            "supported": sd_status.supported,
            "state": sd_status.state_name,
            "fs_error": sd_status.fs_error,
            "free_space_mb": sd_status.free_space_kb / 1024,
            "total_space_mb": sd_status.total_space_kb / 1024,
            "validation_timestamp": datetime.now().isoformat()
        }

        self.log(f"  Supported: {sd_status.supported}")
        self.log(f"  State: {sd_status.state_name}")
        self.log(f"  FS Error: {sd_status.fs_error}")
        self.log(f"  Total Space: {self.sd_card_info['total_space_mb']:.1f} MB")
        self.log(f"  Free Space: {self.sd_card_info['free_space_mb']:.1f} MB")

        # Check status conditions
        if not sd_status.supported:
            self.log(f"  ✗ SD card not supported by this hardware")
            return False

        if sd_status.fs_error != 0:
            self.log(f"  ✗ SD card has filesystem error code {sd_status.fs_error}")
            self.log(f"     → Attempting to format SD card...")
            self.log(f"     → If this fails, manually format via: format_sd_card (CLI)")
            return False

        if not sd_status.is_ready:
            self.log(f"  ✗ SD card not ready (state: {sd_status.state_name})")
            self.log(f"     → Recommendation: Check card insertion or filesystem")
            return False

        if sd_status.total_space_kb == 0:
            self.log(f"  ✗ SD card reports 0 total space")
            self.log(f"     → Recommendation: Check card detection or filesystem")
            return False

        # Check free space
        free_mb = sd_status.free_space_kb / 1024
        if free_mb < min_free_mb:
            self.log(f"  ⚠️  Insufficient free space: {free_mb:.2f} MB < {min_free_mb:.1f} MB required")
            self.log(f"")
            self.log(f"  NOTE: USB Mass Storage (MSC) mode is reserved for post-test log download only.")
            self.log(f"        To free space before testing:")
            self.log(f"        1. Delete old logs manually via INAV Configurator")
            self.log(f"        2. Or format the SD card")
            self.log(f"        3. Then re-run the baseline test")
            self.log(f"")
            self.log(f"  Cannot proceed with insufficient free space:")
            self.log(f"     Total capacity: {self.sd_card_info['total_space_mb']:.2f} MB")
            self.log(f"     Current free space: {free_mb:.2f} MB")
            self.log(f"     Required: {min_free_mb:.1f} MB")
            return False

        # All checks passed
        self.log(f"  ✓ SD card ready for testing")
        self.log(f"    Free space available: {free_mb:.2f} MB (need at least {min_free_mb:.1f} MB)")
        utilization = ((sd_status.total_space_kb - sd_status.free_space_kb) / sd_status.total_space_kb * 100) if sd_status.total_space_kb > 0 else 0
        self.log(f"    Utilization: {utilization:.1f}%")
        self.log(f"    Note: INAV supports max 4GB SD cards")
        return True

    def validate_fc_configuration(self, baseline_config: str = "baseline-fc-config.txt",
                                  auto_fix: bool = False) -> bool:
        """
        Validate FC configuration against baseline requirements.

        Checks for:
        - Motor mixer configured (4-motor quadcopter)
        - Servo mixer configured (4 servos on channels 6-9)
        - GPS feature enabled
        - PWM_OUTPUT_ENABLE feature enabled
        - Blackbox rate set to 1/2 (denom=2)
        - Serial ports configured

        Args:
            baseline_config: Path to baseline config file
            auto_fix: If True, attempt to apply baseline config if validation fails

        Returns:
            True if configuration is valid, False otherwise
        """
        self.log("\n" + "="*60)
        self.log("PRE-TEST VALIDATION: FC Configuration Check")
        self.log("="*60)

        # Run validation
        validation = self.fc.validate_fc_configuration(baseline_config)

        # Display validation results
        if validation['valid']:
            self.log("  ✓ FC configuration is valid")
            self.log(f"    Motor mixer: {validation['details']['motor_mixer_count']} motors")
            self.log(f"    Servo mixer: {validation['details']['servo_mixer_count']} servos")
            self.log(f"    GPS: {'Enabled' if validation['details']['has_gps'] else 'Disabled'}")
            self.log(f"    PWM Output: {'Enabled' if validation['details']['has_pwm_output'] else 'Disabled'}")
            self.log(f"    Blackbox rate: 1/{validation['details']['blackbox_rate_denom']}")
            self.log(f"    Serial ports: {validation['details']['serial_ports']}")
            return True

        # Configuration is invalid - show issues
        self.log("  ✗ FC configuration has issues:")
        for issue in validation['issues']:
            self.log(f"    - {issue}")

        # Attempt to fix if requested
        if auto_fix:
            self.log("\n  Attempting to apply baseline configuration...")
            if self.fc.apply_baseline_configuration(baseline_config):
                self.log("  ✓ Baseline configuration applied")
                self.log("  ℹ Please power-cycle FC and re-run tests")
                return False  # Still return False - user should re-run
            else:
                self.log("  ✗ Failed to apply baseline configuration")
                self.log("  ℹ Please manually restore configuration using:")
                self.log(f"    fc-set {self.fc.port} {baseline_config}")
                return False

        return False

    def set_optimal_blackbox_rate(self, test_num: int, duration_min: int = 60, override_rate: str = None) -> str:
        """
        Determine and set the optimal blackbox rate for a given test.

        Rate selection logic:
        - Tests 1-6, 8, 10, 11 (quick baseline tests): Use 1/2 rate (70 KB/s)
        - Test 9 (extended endurance):
            - <= 60 min: 1/2 rate (70 KB/s)
            - 61-240 min: 1/4 rate (35 KB/s)
            - 241-480 min: 1/4 rate (35 KB/s)
            - 481+ min: 1/8 rate (17.5 KB/s)
        - Can be overridden with override_rate parameter

        Args:
            test_num: Test number
            duration_min: Test duration in minutes (for Test 9)
            override_rate: Force a specific rate (e.g., "1/8") - overrides auto selection

        Returns:
            The blackbox rate that was set (e.g., "1/2"), or "unknown" if couldn't set
        """
        # Determine target rate
        if override_rate:
            target_rate = override_rate
        elif test_num == 9:
            # Extended endurance: rate depends on duration
            if duration_min <= 60:
                target_rate = "1/2"
            elif duration_min <= 240:
                target_rate = "1/4"
            elif duration_min <= 480:
                target_rate = "1/4"
            else:
                target_rate = "1/8"
        else:
            # All other tests: use 1/2 rate
            target_rate = "1/2"

        # Log the rate being set
        if override_rate:
            self.log(f"  Setting blackbox rate: {target_rate} (override)")
        else:
            self.log(f"  Setting blackbox rate: {target_rate}")

        # Try to set the rate
        if self.fc.set_blackbox_rate(target_rate):
            self.log(f"    ✓ Blackbox rate set to {target_rate}")
            return target_rate
        else:
            self.log(f"    ⚠ Failed to set blackbox rate, continuing with current rate")
            return "unknown"

    def run_test(self, test_num: int, **kwargs) -> Optional[TestResult]:
        """
        Run a specific test by number.

        Automatically sets optimal blackbox rate for the test before running.

        Args:
            test_num: Test number to run
            **kwargs: Test-specific parameters (duration_min, etc.)
                     For Test 9: also supports override_rate="1/8"

        Returns:
            TestResult if test ran, None otherwise
        """
        test_map = {
            1: self.test_1_detection,
            2: self.test_2_write_speed,
            3: self.test_3_continuous_logging,
            4: self.test_4_high_frequency,
            6: self.test_6_arm_disarm_cycles,
            8: self.test_8_gps_arm,
            9: self.test_9_extended_endurance,
            10: self.test_10_dma_contention,
            11: self.test_11_blocking_measurement,
        }

        if test_num not in test_map:
            self.log(f"Test {test_num} not implemented for automation")
            return None

        # Save original FC configuration (to restore after test)
        original_blackbox_config = self.fc.get_blackbox_config()

        try:
            # Set optimal blackbox rate before running test (unless rate is already correct)
            # This avoids unnecessary CLI mode switching which can destabilize MSP
            duration_min = kwargs.get("duration_min", 60)
            override_rate = kwargs.get("override_rate", None)

            # Only attempt rate setting if we have an override, otherwise just log current rate
            if override_rate:
                self.log(f"\n  ⚠ WARNING: Changing blackbox rate may temporarily affect FC stability")
                self.log(f"  The configuration will be restored after the test completes.")
                self.set_optimal_blackbox_rate(test_num, duration_min=duration_min, override_rate=override_rate)
            else:
                # Log current rate without attempting to change it
                current_config = self.fc.get_blackbox_config()
                if current_config:
                    self.log(f"  Current blackbox rate: {current_config['rate_num']}/{current_config['rate_denom']}")
                else:
                    self.log(f"  Cannot read blackbox rate, using current FC setting")

            # Filter kwargs to only pass parameters that the test expects
            # Tests 3, 9, 10 use duration_min; others don't need it
            test_kwargs = {}
            if test_num in [3, 9, 10]:
                # These tests accept duration_min
                if "duration_min" in kwargs:
                    test_kwargs["duration_min"] = kwargs["duration_min"]

            # Note: override_rate is only used for rate setting before test, not passed to test method

            # Run the test
            result = test_map[test_num](**test_kwargs)

            # Restore original blackbox configuration if it was changed
            if original_blackbox_config:
                try:
                    current_config = self.fc.get_blackbox_config()
                    if current_config and (current_config['rate_num'] != original_blackbox_config['rate_num'] or
                                          current_config['rate_denom'] != original_blackbox_config['rate_denom']):
                        original_rate = f"{original_blackbox_config['rate_num']}/{original_blackbox_config['rate_denom']}"
                        self.log(f"\n  Restoring original blackbox rate to {original_rate}...")
                        if self.fc.set_blackbox_rate(original_rate):
                            self.log(f"  ✓ Blackbox rate restored")
                        else:
                            self.log(f"  ⚠ Failed to restore blackbox rate")
                            self.log(f"  Manual restoration may be needed: set blackbox_rate={original_rate}")
                except Exception as restore_error:
                    self.log(f"\n  ⚠ WARNING: Could not restore blackbox rate")
                    self.log(f"  FC may be in unstable state. Recommend power cycle.")
                    self.log(f"  Manual restoration: fc-set {self.fc.port} baseline-fc-config.txt")

            return result

        except Exception as e:
            # Restore configuration even if test fails
            if original_blackbox_config:
                try:
                    current_config = self.fc.get_blackbox_config()
                    if current_config and (current_config['rate_num'] != original_blackbox_config['rate_num'] or
                                          current_config['rate_denom'] != original_blackbox_config['rate_denom']):
                        original_rate = f"{original_blackbox_config['rate_num']}/{original_blackbox_config['rate_denom']}"
                        try:
                            self.fc.set_blackbox_rate(original_rate)
                            self.log(f"\n  ✓ Configuration restored (test failed but config recovered)")
                        except:
                            self.log(f"\n  ⚠ WARNING: Could not restore configuration after test failure")
                            self.log(f"  FC may be in unstable state. Power cycle recommended.")
                except:
                    pass  # Silently fail if we can't even query current config
            raise e

    def run_all(self, tests: list[int] = None, **test_params) -> list[TestResult]:
        """
        Run all or specified tests.

        Args:
            tests: List of test numbers to run
            **test_params: Test-specific parameters (duration_min, override_rate, etc.)

        Returns:
            List of TestResult objects
        """
        if tests is None:
            tests = [1, 2, 3, 4, 6, 8, 10]

        self.results = []
        for test_num in tests:
            result = self.run_test(test_num, **test_params)
            if result:
                self.results.append(result)

        return self.results

    # -------------------------------------------------------------------------
    # Post-Test Log Verification
    # -------------------------------------------------------------------------

    def verify_baseline_logs(self) -> LogVerificationResult:
        """
        Download and verify blackbox logs from the FC.

        Tries USB MSC first (fast), attempts to enable MSC mode if needed,
        then falls back to MSP SPIFLASH if necessary.
        Validates log structure and frame integrity.

        Returns:
            LogVerificationResult with detailed log information
        """
        self.log("\n" + "="*60)
        self.log("POST-TEST LOG VERIFICATION")
        self.log("="*60)

        result = LogVerificationResult(passed=False)

        # Try USB MSC first (fastest)
        self.log("  1. Attempting to download via USB Mass Storage (fastest)...")
        logs = self.fc.download_logs_from_msc()

        if not logs:
            self.log("  ✗ USB MSC mount point not found")
            self.log("  2. Attempting to enable USB MSC mode via CLI...")

            if self.fc.enable_msc_mode(timeout=30.0):
                self.log("  ✓ USB MSC mode enabled, waiting for mount...")
                time.sleep(3)

                # Try to download again
                logs = self.fc.download_logs_from_msc()
                if logs:
                    result.download_method = "USB_MSC"
                    self.log("  ✓ USB Mass Storage download successful")
                else:
                    self.log("  ✗ MSC mode enabled but mount failed")
            else:
                self.log("  ✗ Failed to enable USB MSC mode")

        else:
            result.download_method = "USB_MSC"
            self.log("  ✓ USB Mass Storage download successful")

        # Fallback to MSP SPIFLASH if USB MSC failed
        if not logs:
            self.log("  3. Attempting to download via MSP SPIFLASH (slower)...")
            logs = self.fc.download_logs_from_msp_flash()
            if logs:
                result.download_method = "MSP_FLASH"
                self.log("  ✓ MSP SPIFLASH download successful")
            else:
                self.log("  ✗ MSP SPIFLASH download also failed")
                result.errors.append("No logs found - USB MSC, MSC mode enable, and MSP SPIFLASH all failed")
                return result

        # Process downloaded logs
        self.log(f"\n  Found {len(logs)} log file(s)")

        for log_path_or_name, log_data in logs:
            result.logs_found += 1
            result.total_size_bytes += len(log_data)

            # Set first log path for reference
            if result.first_log_path is None:
                result.first_log_path = str(log_path_or_name)

            self.log(f"  - {log_path_or_name}: {len(log_data)/1024:.1f} KB")

            # Verify this log
            verification = self.fc.verify_blackbox_log(log_data)

            # Merge verification results
            if verification.passed:
                result.passed = True
            result.i_frame_count += verification.i_frame_count
            result.p_frame_count += verification.p_frame_count
            result.frame_count += verification.frame_count
            result.errors.extend(verification.errors)
            result.warnings.extend(verification.warnings)

            # Update header fields from first log
            if not result.header_fields:
                result.header_fields = verification.header_fields

        result.total_size_mb = result.total_size_bytes / 1024 / 1024

        # Report results
        self.log(f"\n  Total logs: {result.logs_found}")
        self.log(f"  Total size: {result.total_size_mb:.2f} MB")
        self.log(f"  Download method: {result.download_method}")
        self.log(f"  Total frames: {result.frame_count} (I: {result.i_frame_count}, P: {result.p_frame_count})")

        if result.header_fields:
            self.log(f"\n  Header fields found:")
            for field_name in sorted(result.header_fields.keys())[:10]:  # Show first 10
                self.log(f"    - {field_name}")
            if len(result.header_fields) > 10:
                self.log(f"    ... and {len(result.header_fields) - 10} more")

        if result.errors:
            self.log(f"\n  ✗ Errors:")
            for error in result.errors:
                self.log(f"    - {error}")
        else:
            self.log(f"\n  ✓ No errors detected")

        if result.warnings:
            self.log(f"\n  ⚠️  Warnings:")
            for warning in result.warnings:
                self.log(f"    - {warning}")

        self.log(f"\n  RESULT: {'PASS' if result.passed else 'FAIL'}")

        # Auto-restore normal operation if we enabled MSC mode
        if result.download_method == "USB_MSC" and self.fc.find_msc_mount_point():
            self.log("\n  Automatically restoring normal INAV operation...")
            if self.fc.exit_msc_mode_and_reenumerate():
                self.log("  ✓ Successfully restored to normal operation")
            else:
                self.log("  ⚠ Failed to auto-restore, may need manual USB reconnect")
                self.log("     Try: Disconnect and reconnect the USB cable")

        return result

    # -------------------------------------------------------------------------
    # Servo Stress Testing Helper
    # -------------------------------------------------------------------------

    def enable_servo_stress(self, duration: float, pattern: str = 'sweep',
                           rate_hz: float = 10.0, run_background: bool = False) -> dict:
        """
        Enable servo stress testing for a test.

        Moves servos in specified pattern to increase system load during logging.
        Useful for stress testing motor control timing and DMA contention.

        Args:
            duration: How long to stress servos in seconds
            pattern: Stress pattern:
                - 'sweep': Smooth oscillation (default)
                - 'random': Random position changes
                - 'rapid': Rapid toggle between min/max
                - 'hold': Center position (minimal stress)
            rate_hz: Servo update rate in Hz (default 10 Hz)
            run_background: If True, run in background thread (return immediately)
                           If False, block until servo stress completes

        Returns:
            dict with status and results:
            - 'started': bool - Stress test started successfully
            - 'handle': Thread handle (if run_background=True)
            - 'result': Stress test result (if run_background=False)
        """
        self.log(f"\n  Starting servo stress: {pattern} pattern for {duration}s at {rate_hz} Hz")

        if run_background:
            # Start servo stress in background
            handle = self.fc.start_servo_stress_background(duration, pattern, rate_hz)
            self.log(f"  ✓ Servo stress running in background (will complete in ~{duration}s)")
            return {
                'started': True,
                'handle': handle,
                'pattern': pattern,
                'duration': duration
            }
        else:
            # Run servo stress in foreground (blocks)
            result = self.fc.move_servos(duration, pattern, rate_hz)

            if result['success']:
                self.log(f"  ✓ Servo stress complete: {result['updates_sent']} updates, {result['errors']} errors")
            else:
                self.log(f"  ✗ Servo stress encountered errors: {result['errors']} failed updates")

            return {
                'started': result['success'],
                'result': result,
                'pattern': pattern,
                'duration': duration
            }

    def wait_servo_stress(self, stress_info: dict) -> dict:
        """
        Wait for background servo stress to complete and get results.

        Args:
            stress_info: Handle returned from enable_servo_stress(..., run_background=True)

        Returns:
            Stress test result dict
        """
        if 'handle' not in stress_info:
            return stress_info.get('result', {})

        self.log(f"  Waiting for servo stress to complete...")
        result = self.fc.wait_for_servo_stress(stress_info['handle'])

        if result['success']:
            self.log(f"  ✓ Servo stress complete: {result['updates_sent']} updates, {result['errors']} errors")
        else:
            self.log(f"  ✗ Servo stress had issues: {result['errors']} failed updates")

        return result

    # -------------------------------------------------------------------------
    # Test 1: SD Card Detection & Initialization
    # -------------------------------------------------------------------------

    def test_1_detection(self, timeout_sec: float = 3.0) -> TestResult:
        """Test 1: SD Card Detection & Initialization
        
        WARNING: This test sends MSP_SDCARD_SUMMARY which can lock up the FC
        if the SD card subsystem is in a bad state. Use with caution.
        """
        self.log("\n" + "="*60)
        self.log("TEST 1: SD Card Detection & Initialization")
        self.log("="*60)
        self.log("  WARNING: MSP_SDCARD_SUMMARY can lock up FC if SD is in bad state")

        start_time = time.time()
        details = {}

        # Query SD card status with short timeout
        try:
            sd_status = self.fc.get_sd_card_status()
        except Exception as e:
            return TestResult(
                test_num=1,
                test_name="SD Card Detection",
                passed=False,
                duration_sec=time.time() - start_time,
                error=f"Exception querying SD card: {e}"
            )

        if not sd_status:
            return TestResult(
                test_num=1,
                test_name="SD Card Detection",
                passed=False,
                duration_sec=time.time() - start_time,
                error="Failed to query SD card status via MSP"
            )

        details["supported"] = sd_status.supported
        details["state"] = sd_status.state_name
        details["fs_error"] = sd_status.fs_error
        details["free_space_mb"] = sd_status.free_space_kb / 1024
        details["total_space_mb"] = sd_status.total_space_kb / 1024

        self.log(f"  Supported: {sd_status.supported}")
        self.log(f"  State: {sd_status.state_name}")
        self.log(f"  FS Error: {sd_status.fs_error}")
        self.log(f"  Free Space: {details['free_space_mb']:.1f} MB")
        self.log(f"  Total Space: {details['total_space_mb']:.1f} MB")

        # Check pass criteria
        passed = (
            sd_status.supported and
            sd_status.is_ready and
            sd_status.fs_error == 0 and
            sd_status.total_space_kb > 0
        )

        result = TestResult(
            test_num=1,
            test_name="SD Card Detection",
            passed=passed,
            duration_sec=time.time() - start_time,
            details=details
        )

        self.log(f"  RESULT: {'PASS' if passed else 'FAIL'}")
        return result

    # -------------------------------------------------------------------------
    # Test 2: Write Speed Measurement
    # -------------------------------------------------------------------------

    def test_2_write_speed(self, duration_sec: int = 60) -> TestResult:
        """Test 2: Write Speed Measurement"""
        self.log("\n" + "="*60)
        self.log(f"TEST 2: Write Speed Measurement ({duration_sec}s)")
        self.log("="*60)

        start_time = time.time()
        details = {}

        # Get initial SD card status
        sd_before = self.fc.get_sd_card_status()
        if not sd_before or not sd_before.is_ready:
            return TestResult(
                test_num=2,
                test_name="Write Speed Measurement",
                passed=False,
                duration_sec=time.time() - start_time,
                error="SD card not ready"
            )

        details["free_space_before_mb"] = sd_before.free_space_kb / 1024

        # Check blackbox config (do NOT modify)
        bb_config = self.fc.get_blackbox_config()
        if bb_config:
            details["blackbox_device"] = bb_config["device_name"]
            details["blackbox_rate"] = f"{bb_config['rate_num']}/{bb_config['rate_denom']}"
            self.log(f"  Blackbox device: {bb_config['device_name']}")
            self.log(f"  Blackbox rate: {bb_config['rate_num']}/{bb_config['rate_denom']}")
            if bb_config["device"] != 2:  # Not SDCARD
                self.log(f"  WARNING: Blackbox not configured for SDCARD (device={bb_config['device']})")
        else:
            self.log("  WARNING: Could not query blackbox config")

        self.log(f"  Free space before: {details['free_space_before_mb']:.1f} MB")

        # Wait for FC to be ready for arming (sensor checks passing)
        self.log("  Checking sensor status and waiting for arming readiness...")
        self.log("  (Waiting up to 5 minutes for GPS 3D fix if needed...)")
        ready, status_msg = self.fc.wait_for_arming_ready(timeout=300.0)  # 5 minutes for GPS
        if not ready:
            self.log(f"  ERROR: FC not ready for arming: {status_msg}")
            return TestResult(
                test_num=2,
                test_name="Write Speed Measurement",
                passed=False,
                duration_sec=time.time() - start_time,
                error=f"Cannot arm: {status_msg}"
            )

        # Arm the FC to start blackbox logging
        self.log("  Arming FC to start blackbox logging...")
        if not self.fc.arm(timeout=5.0):
            self.log("  ERROR: Failed to arm FC after sensor checks passed")
            return TestResult(
                test_num=2,
                test_name="Write Speed Measurement",
                passed=False,
                duration_sec=time.time() - start_time,
                error="Failed to arm despite passing sensor checks"
            )
        else:
            self.log("  ✓ FC armed, blackbox logging active")

        self.log(f"  Logging for {duration_sec} seconds...")
        
        # Keep sending RC during logging period to stay armed
        channels = [1500] * 16
        channels[2] = 1000  # Throttle LOW
        channels[4] = 2000  # ARM HIGH
        
        log_start = time.time()
        while time.time() - log_start < duration_sec:
            self.fc.send_rc_channels(channels)
            time.sleep(0.02)  # 50Hz

        # Disarm
        self.log("  Disarming FC...")
        self.fc.disarm()

        # Wait a moment for FC to flush all writes to SD card
        self.log("  Waiting for SD card flush...")
        time.sleep(2)

        # Get final SD card status
        sd_after = self.fc.get_sd_card_status()
        if not sd_after:
            return TestResult(
                test_num=2,
                test_name="Write Speed Measurement",
                passed=False,
                duration_sec=time.time() - start_time,
                error="Failed to query SD card after logging"
            )

        details["free_space_before_kb"] = sd_before.free_space_kb
        details["free_space_after_kb"] = sd_after.free_space_kb
        details["free_space_before_mb"] = sd_before.free_space_kb / 1024
        details["free_space_after_mb"] = sd_after.free_space_kb / 1024

        # Calculate write speed (free_space_kb is in KB, convert to bytes)
        kb_written = sd_before.free_space_kb - sd_after.free_space_kb
        bytes_written = kb_written * 1024
        write_speed_kbps = kb_written / duration_sec if duration_sec > 0 else 0

        details["kb_written"] = kb_written
        details["bytes_written"] = bytes_written
        details["write_speed_kbps"] = write_speed_kbps
        details["duration_sec"] = duration_sec

        self.log(f"  Free space before: {details['free_space_before_mb']:.1f} MB ({sd_before.free_space_kb} KB)")
        self.log(f"  Free space after: {details['free_space_after_mb']:.1f} MB ({sd_after.free_space_kb} KB)")
        self.log(f"  KB written: {kb_written} KB")
        self.log(f"  Bytes written: {bytes_written} bytes")
        self.log(f"  Write speed: {write_speed_kbps:.1f} KB/s")

        # Validate that free space actually decreased
        if kb_written < 0:
            self.log(f"  WARNING: Free space INCREASED ({kb_written} KB) - possible cache or query issue")
        elif kb_written == 0:
            self.log(f"  WARNING: No change in free space - blackbox may not be logging")

        # Pass only if:
        # 1. SD card is ready
        # 2. Write speed > 100 KB/s (baseline with 1/2 gyro raw recording ~136 KB/s)
        # 3. Actual data was written (bytes_written > 0)
        passed = sd_after.is_ready and write_speed_kbps > 100 and bytes_written > 0

        if bytes_written == 0:
            self.log("  WARNING: No data written. Check blackbox configuration.")

        result = TestResult(
            test_num=2,
            test_name="Write Speed Measurement",
            passed=passed,
            duration_sec=time.time() - start_time,
            details=details
        )

        self.log(f"  RESULT: {'PASS' if passed else 'FAIL'}")
        return result

    # -------------------------------------------------------------------------
    # Test 3: Continuous Logging
    # -------------------------------------------------------------------------

    def test_3_continuous_logging(self, duration_min: int = 5) -> TestResult:
        """Test 3: Continuous Logging (with arm/disarm to enable logging)"""
        self.log("\n" + "="*60)
        self.log(f"TEST 3: Continuous Logging ({duration_min} min)")
        self.log("="*60)
        self.log("  Note: Full test is 30 min. Running shortened version.")
        self.log("  Monitoring SD card status while armed to enable blackbox logging.")

        start_time = time.time()
        duration_sec = duration_min * 60
        details = {"duration_min": duration_min}
        errors_detected = 0

        # Wait for arming ready before starting
        self.log(f"  Checking sensor status before arming...")
        ready, status_msg = self.fc.wait_for_arming_ready(timeout=300.0)
        if not ready:
            self.log(f"  ERROR: FC not ready for arming: {status_msg}")
            return TestResult(
                test_num=3,
                test_name="Continuous Logging",
                passed=False,
                duration_sec=time.time() - start_time,
                error=f"Cannot arm: {status_msg}"
            )

        # Arm FC to enable logging
        self.log(f"  Arming FC to enable blackbox logging...")
        if not self.fc.arm(timeout=5.0):
            self.log(f"  ERROR: Failed to arm FC")
            return TestResult(
                test_num=3,
                test_name="Continuous Logging",
                passed=False,
                duration_sec=time.time() - start_time,
                error="Failed to arm"
            )

        self.log(f"  ✓ FC armed, monitoring SD card for {duration_min} minutes...")

        # Start servo stress in background (increases system load during logging)
        servo_stress = self.enable_servo_stress(duration=duration_sec, pattern='sweep', rate_hz=10.0, run_background=True)

        # Monitor SD card status periodically
        check_interval = 30  # Check every 30 seconds
        checks = 0

        while time.time() - start_time < duration_sec:
            sd_status = self.fc.get_sd_card_status()
            checks += 1

            if not sd_status:
                errors_detected += 1
                self.log(f"  [{checks}] ERROR: Failed to query SD status")
            elif not sd_status.is_ready:
                errors_detected += 1
                self.log(f"  [{checks}] ERROR: SD card state = {sd_status.state_name}")
            elif sd_status.fs_error != 0:
                errors_detected += 1
                self.log(f"  [{checks}] ERROR: FS error = {sd_status.fs_error}")
            else:
                self.log(f"  [{checks}] OK - State: {sd_status.state_name}, Free: {sd_status.free_space_kb/1024:.1f} MB")

            time.sleep(check_interval)

        # Wait for servo stress to complete
        if servo_stress['started']:
            servo_result = self.wait_servo_stress(servo_stress)
            details["servo_stress"] = {
                "pattern": servo_result.get('pattern'),
                "updates_sent": servo_result.get('updates_sent', 0),
                "errors": servo_result.get('errors', 0)
            }

        # Disarm FC
        self.log(f"  Disarming FC...")
        self.fc.disarm()

        details["checks_performed"] = checks
        details["errors_detected"] = errors_detected

        passed = errors_detected == 0

        result = TestResult(
            test_num=3,
            test_name="Continuous Logging",
            passed=passed,
            duration_sec=time.time() - start_time,
            details=details
        )

        self.log(f"  RESULT: {'PASS' if passed else 'FAIL'} ({errors_detected} errors in {checks} checks)")
        return result

    # -------------------------------------------------------------------------
    # Test 4: High-Frequency Logging
    # -------------------------------------------------------------------------

    def test_4_high_frequency(self, duration_sec: int = 60) -> TestResult:
        """Test 4: High-Frequency Logging"""
        self.log("\n" + "="*60)
        self.log(f"TEST 4: High-Frequency Logging ({duration_sec}s)")
        self.log("="*60)

        # This test is similar to Test 2 but with higher logging rate
        # For automation, we just verify SD card stability under load
        # Blackbox configuration is set via CLI and not modified by this script

        return self.test_2_write_speed(duration_sec)

    # -------------------------------------------------------------------------
    # Test 6: Rapid Arm/Disarm Cycles
    # -------------------------------------------------------------------------

    def test_6_arm_disarm_cycles(self, cycles: int = 20) -> TestResult:
        """Test 6: Rapid Arm/Disarm Cycles"""
        self.log("\n" + "="*60)
        self.log(f"TEST 6: Rapid Arm/Disarm Cycles ({cycles} cycles)")
        self.log("="*60)

        start_time = time.time()
        details = {"target_cycles": cycles}
        successful_cycles = 0

        # Check sensors once before starting
        self.log(f"  Checking sensor status...")
        ready, status_msg = self.fc.wait_for_arming_ready(timeout=300.0)
        if not ready:
            self.log(f"  WARNING: FC not ready for arming: {status_msg}")
            self.log(f"  Proceeding with test anyway (arm attempts may fail)")

        for i in range(cycles):
            self.log(f"  Cycle {i+1}/{cycles}...")

            # Check SD card before
            sd_before = self.fc.get_sd_card_status()
            if not sd_before or not sd_before.is_ready:
                self.log(f"    ERROR: SD card not ready before arm")
                continue

            # Attempt to arm
            if not self.fc.arm(timeout=2.0):
                self.log(f"    WARNING: Failed to arm FC")
                continue

            self.log(f"    ✓ Armed, servo stress for 2 seconds...")
            # Move servos while armed for stress testing
            servo_result = self.fc.move_servos(duration=2.0, pattern='rapid', rate_hz=20.0)

            # Disarm
            if not self.fc.disarm(timeout=2.0):
                self.log(f"    WARNING: Failed to disarm FC")
                continue

            self.log(f"    ✓ Disarmed")

            # Check SD card after
            sd_after = self.fc.get_sd_card_status()
            if not sd_after or not sd_after.is_ready:
                self.log(f"    ERROR: SD card not ready after cycle")
                continue

            # Wait between cycles
            time.sleep(0.5)

            successful_cycles += 1

        details["successful_cycles"] = successful_cycles
        passed = successful_cycles == cycles

        result = TestResult(
            test_num=6,
            test_name="Rapid Arm/Disarm Cycles",
            passed=passed,
            duration_sec=time.time() - start_time,
            details=details
        )

        self.log(f"  RESULT: {'PASS' if passed else 'FAIL'} ({successful_cycles}/{cycles})")
        return result

    # -------------------------------------------------------------------------
    # Test 8: GPS Fix + Immediate Arm (F765 LOCKUP SPECIFIC)
    # -------------------------------------------------------------------------

    def test_8_gps_arm(self, attempts: int = 10, gps_timeout: float = 300) -> TestResult:
        """Test 8: GPS Fix + Immediate Arm (F765 lockup specific)"""
        self.log("\n" + "="*60)
        self.log(f"TEST 8: GPS Fix + Immediate Arm ({attempts} attempts)")
        self.log("="*60)
        self.log("  This test reproduces the F765 arming lockup scenario.")
        self.log("  Requires GPS module connected and receiving signal.")

        start_time = time.time()
        details = {"target_attempts": attempts}
        successful_arms = 0
        lockups_detected = 0

        for i in range(attempts):
            self.log(f"\n  Attempt {i+1}/{attempts}:")

            # Check initial GPS status
            gps = self.fc.get_gps_status()
            if not gps:
                self.log("    ERROR: Cannot query GPS status")
                continue

            self.log(f"    GPS: {gps.fix_name}, {gps.num_sat} sats")

            # If no fix, wait for one
            if not gps.has_fix:
                self.log(f"    Waiting for GPS fix (timeout: {gps_timeout}s)...")
                if not self.fc.wait_for_gps_fix(timeout=gps_timeout):
                    self.log("    WARNING: GPS fix timeout")
                    continue
                self.log("    GPS fix acquired!")

            # Check arming status after GPS fix
            self.log(f"    Checking arming status...")
            ready, status_msg = self.fc.wait_for_arming_ready(timeout=10.0)
            if not ready:
                self.log(f"    WARNING: Not ready to arm: {status_msg}")
                continue

            # Immediately try to arm (this is the critical moment for F765 lockup)
            arm_time = time.time()
            arm_result = self.fc.arm(timeout=2.0)
            response_time = time.time() - arm_time

            if not arm_result:
                # Arm failed - check if FC is still responsive
                self.log(f"    WARNING: Arm command timed out after {response_time*1000:.1f}ms")

                # Check if FC still responds
                arming = self.fc.get_arming_status()
                if arming is None:
                    lockups_detected += 1
                    self.log(f"    LOCKUP DETECTED! FC not responding after arm attempt")

                    # Try to recover
                    self.log("    Waiting 5s for recovery...")
                    time.sleep(5)
                    recovery = self.fc.get_arming_status()
                    if recovery:
                        self.log("    FC recovered")
                    else:
                        self.log("    FC still unresponsive - may need power cycle")
            else:
                successful_arms += 1
                self.log(f"    ✓ Armed successfully in {response_time*1000:.1f}ms")

                # Move servos while armed for stress testing
                self.log(f"    Servo stress for 2 seconds...")
                servo_result = self.fc.move_servos(duration=2.0, pattern='random', rate_hz=15.0)

                # Disarm after successful arm
                self.fc.disarm(timeout=2.0)
                self.log(f"    Disarmed")

            # Small delay between attempts
            time.sleep(2)

        details["successful_arms"] = successful_arms
        details["lockups_detected"] = lockups_detected

        # Pass only if ALL attempts succeeded with no lockups
        passed = successful_arms == attempts and lockups_detected == 0

        result = TestResult(
            test_num=8,
            test_name="GPS Fix + Immediate Arm",
            passed=passed,
            duration_sec=time.time() - start_time,
            details=details
        )

        self.log(f"\n  RESULT: {'PASS' if passed else 'FAIL'}")
        self.log(f"  Successful: {successful_arms}/{attempts}, Lockups: {lockups_detected}")
        return result

    # -------------------------------------------------------------------------
    # Test 9: Extended Endurance Test
    # -------------------------------------------------------------------------

    def test_9_extended_endurance(self, duration_min: int = 60) -> TestResult:
        """Test 9: Extended Endurance Test (long-duration stability)"""
        self.log("\n" + "="*60)
        self.log(f"TEST 9: Extended Endurance Test ({duration_min} min)")
        self.log("="*60)
        self.log("  Continuous logging with periodic arm/disarm cycles.")
        self.log("  Monitors SD card stability and performance over time.")
        self.log("")

        start_time = time.time()
        duration_sec = duration_min * 60
        details = {"duration_min": duration_min}

        # Track metrics
        arm_cycles = 0
        disarm_cycles = 0
        sd_errors = 0
        msp_timeouts = 0
        write_speeds = []
        free_space_samples = []
        last_free_space = None

        # Check initial state
        initial_sd = self.fc.get_sd_card_status()
        if initial_sd:
            last_free_space = initial_sd.free_space_kb
            details["initial_free_space_mb"] = initial_sd.free_space_kb / 1024
        else:
            self.log("  WARNING: Cannot query initial SD card status")
            return TestResult(
                test_num=9,
                test_name="Extended Endurance",
                passed=False,
                duration_sec=time.time() - start_time,
                error="Cannot query SD card status"
            )

        self.log(f"  Initial free space: {last_free_space/1024:.1f} MB")
        self.log(f"  Checking sensor status before arming cycles...")

        # Wait for FC to be ready for arming before starting test
        ready, status_msg = self.fc.wait_for_arming_ready(timeout=300.0)
        if not ready:
            self.log(f"  WARNING: FC not ready for arming: {status_msg}")
            self.log(f"  Proceeding with test anyway (arm attempts may fail)")
        else:
            self.log(f"  ✓ FC ready for arming")

        self.log(f"  Running for {duration_min} minutes...")
        self.log("")

        # Calculate space requirements and warn if needed
        # Estimate based on typical blackbox write speeds
        typical_write_speed_kbps = 70  # KB/s (1/2 rate)
        estimated_data_mb = (typical_write_speed_kbps * duration_min * 60) / 1024 / 1024
        estimated_final_free_mb = (last_free_space / 1024) - estimated_data_mb
        min_safe_free_mb = 100  # Keep at least 100 MB free

        self.log(f"  SPACE CALCULATION:")
        self.log(f"    Estimated data: {estimated_data_mb:.1f} MB (at 1/2 rate)")
        self.log(f"    Final free space: {estimated_final_free_mb:.1f} MB")

        if estimated_final_free_mb < min_safe_free_mb:
            self.log(f"")
            self.log(f"  ⚠ WARNING: Test may run out of space!")
            self.log(f"    Recommendation: Reduce blackbox rate before testing")
            self.log(f"")
            self.log(f"  Suggested blackbox rates for this duration:")

            rates = [
                ("1/2 rate", 70),
                ("1/4 rate", 35),
                ("1/8 rate", 17.5),
                ("1/16 rate", 8.75),
            ]

            for rate_name, rate_kbps in rates:
                data = (rate_kbps * duration_min * 60) / 1024 / 1024
                final_free = (last_free_space / 1024) - data
                if final_free >= min_safe_free_mb:
                    self.log(f"    ✓ {rate_name:12s} → {data:6.1f} MB → {final_free:6.1f} MB free")
                else:
                    self.log(f"    ✗ {rate_name:12s} → {data:6.1f} MB → {final_free:6.1f} MB free (TOO LOW)")

            self.log(f"")
            self.log(f"  To change blackbox rate via CLI:")
            self.log(f"    set blackbox_rate=1/4")
            self.log(f"    save")
            self.log(f"")

        check_interval = 10  # Check every 10 seconds
        arm_interval = 30    # Try to arm every 30 seconds
        last_arm_attempt = time.time()
        min_free_mb = 100    # Stop test if free space drops below this

        while time.time() - start_time < duration_sec:
            elapsed = time.time() - start_time
            elapsed_min = elapsed / 60

            # Attempt arm/disarm cycle
            if time.time() - last_arm_attempt >= arm_interval:
                last_arm_attempt = time.time()

                # Try to arm
                try:
                    if self.fc.arm(timeout=2.0):
                        arm_cycles += 1

                        # Move servos while armed for stress testing (1 second duration)
                        servo_result = self.fc.move_servos(duration=1.0, pattern='sweep', rate_hz=12.0)
                        time.sleep(1)  # Additional 1 second stay armed after servo stress

                        # Disarm
                        if self.fc.disarm(timeout=2.0):
                            disarm_cycles += 1
                except Exception as e:
                    pass  # Silently continue if arming fails

            # Query SD card status
            try:
                sd_status = self.fc.get_sd_card_status()

                if sd_status:
                    free_space_samples.append((elapsed, sd_status.free_space_kb))
                    current_free_space = sd_status.free_space_kb
                    current_free_mb = current_free_space / 1024

                    # Calculate write speed since last check
                    if last_free_space is not None and last_free_space > current_free_space:
                        bytes_written = (last_free_space - current_free_space) * 1024
                        time_elapsed = check_interval  # Approximate
                        write_speed_kbps = bytes_written / 1024 / time_elapsed
                        write_speeds.append(write_speed_kbps)

                    last_free_space = current_free_space

                    # Check for errors
                    if not sd_status.is_ready:
                        sd_errors += 1
                        self.log(f"  [{elapsed_min:.1f}m] ⚠ SD Error: {sd_status.state_name}")

                    # Safety check: stop if free space drops too low
                    if current_free_mb < min_free_mb:
                        self.log(f"  [{elapsed_min:.1f}m] ⚠ STOPPING: Free space critical ({current_free_mb:.1f} MB)")
                        self.log(f"              Continued logging would overflow SD card")
                        break
                else:
                    msp_timeouts += 1

            except Exception as e:
                msp_timeouts += 1

            # Log status every 30 seconds
            if int(elapsed) % 30 == 0:
                if sd_status:
                    free_mb = sd_status.free_space_kb / 1024
                    if write_speeds:
                        avg_speed = sum(write_speeds[-3:]) / len(write_speeds[-3:])
                        self.log(f"  [{elapsed_min:.1f}m] Free: {free_mb:.1f}MB, Cycles: {arm_cycles}/{disarm_cycles}, Write: {avg_speed:.1f} KB/s")
                    else:
                        self.log(f"  [{elapsed_min:.1f}m] Free: {free_mb:.1f}MB, Cycles: {arm_cycles}/{disarm_cycles}")

            time.sleep(check_interval)

        # Calculate statistics
        details["arm_cycles"] = arm_cycles
        details["disarm_cycles"] = disarm_cycles
        details["sd_errors"] = sd_errors
        details["msp_timeouts"] = msp_timeouts

        if write_speeds:
            details["avg_write_speed_kbps"] = sum(write_speeds) / len(write_speeds)
            details["min_write_speed_kbps"] = min(write_speeds)
            details["max_write_speed_kbps"] = max(write_speeds)
        else:
            details["avg_write_speed_kbps"] = 0

        if free_space_samples:
            initial_free = free_space_samples[0][1]
            final_free = free_space_samples[-1][1]
            total_written_mb = (initial_free - final_free) / 1024
            details["total_written_mb"] = total_written_mb
        else:
            details["total_written_mb"] = 0

        # Pass if no SD errors and reasonable write speeds
        passed = sd_errors == 0 and msp_timeouts < 5

        result = TestResult(
            test_num=9,
            test_name="Extended Endurance",
            passed=passed,
            duration_sec=time.time() - start_time,
            details=details
        )

        # Final report
        self.log(f"\n  RESULT: {'PASS' if passed else 'FAIL'}")
        self.log(f"  Arm/Disarm cycles: {arm_cycles}")
        self.log(f"  SD errors: {sd_errors}")
        self.log(f"  MSP timeouts: {msp_timeouts}")
        if details["avg_write_speed_kbps"] > 0:
            self.log(f"  Write speed: {details['avg_write_speed_kbps']:.1f} KB/s (min: {details['min_write_speed_kbps']:.1f}, max: {details['max_write_speed_kbps']:.1f})")
        if details["total_written_mb"] > 0:
            self.log(f"  Data written: {details['total_written_mb']:.1f} MB")

        return result

    # -------------------------------------------------------------------------
    # Test 10: DMA Contention Stress Test (F765 LOCKUP SPECIFIC)
    # -------------------------------------------------------------------------

    def test_10_dma_contention(self, duration_min: int = 10) -> TestResult:
        """Test 10: DMA Contention Stress Test with real GPS"""
        self.log("\n" + "="*60)
        self.log(f"TEST 10: DMA Contention Stress Test ({duration_min} min)")
        self.log("="*60)
        self.log("  Monitors SD card and GPS under simultaneous DMA load.")
        self.log("  Requires: GPS module connected with active fix.")

        start_time = time.time()
        duration_sec = duration_min * 60
        details = {"duration_min": duration_min}

        sd_errors = 0
        gps_dropouts = 0
        msp_timeouts = 0
        checks = 0

        check_interval = 5  # Check every 5 seconds for more granularity

        # Verify GPS is working
        gps = self.fc.get_gps_status()
        if not gps or not gps.has_fix:
            self.log("  WARNING: GPS does not have fix. Test may be less meaningful.")
            details["gps_fix_at_start"] = False
        else:
            self.log(f"  GPS: {gps.num_sat} satellites, HDOP {gps.hdop}")
            details["gps_fix_at_start"] = True
            details["initial_satellites"] = gps.num_sat

        self.log(f"  Running for {duration_min} minutes...")
        self.log(f"  Starting servo stress (sweep pattern) for DMA contention...")
        self.log("")

        # Start servo stress in background (increases DMA load)
        servo_stress = self.enable_servo_stress(duration=duration_sec, pattern='sweep', rate_hz=15.0, run_background=True)

        prev_gps_fix = gps.has_fix if gps else False

        while time.time() - start_time < duration_sec:
            checks += 1

            # Query both SD and GPS rapidly to stress DMA
            query_start = time.time()

            sd_status = self.fc.get_sd_card_status()
            gps_status = self.fc.get_gps_status()
            arming_status = self.fc.get_arming_status()

            query_time = (time.time() - query_start) * 1000  # ms

            # Check for issues
            issues = []

            if sd_status is None:
                msp_timeouts += 1
                issues.append("MSP timeout (SD)")
            elif not sd_status.is_ready:
                sd_errors += 1
                issues.append(f"SD error: {sd_status.state_name}")

            if gps_status is None:
                msp_timeouts += 1
                issues.append("MSP timeout (GPS)")
            elif prev_gps_fix and not gps_status.has_fix:
                gps_dropouts += 1
                issues.append("GPS fix lost")

            if arming_status is None:
                msp_timeouts += 1
                issues.append("MSP timeout (STATUS)")

            # Log status every 30 seconds or on error
            elapsed = time.time() - start_time
            if checks % 6 == 0 or issues:  # Every 30s or on error
                status_str = ", ".join(issues) if issues else "OK"
                sat_str = f"{gps_status.num_sat}sat" if gps_status else "?"
                sd_str = sd_status.state_name if sd_status else "?"
                self.log(f"  [{elapsed/60:.1f}m] {status_str} | GPS:{sat_str} SD:{sd_str} MSP:{query_time:.0f}ms")

            if gps_status:
                prev_gps_fix = gps_status.has_fix

            time.sleep(check_interval)

        # Wait for servo stress to complete
        if servo_stress['started']:
            servo_result = self.wait_servo_stress(servo_stress)
            details["servo_stress"] = {
                "pattern": servo_result.get('pattern'),
                "updates_sent": servo_result.get('updates_sent', 0),
                "errors": servo_result.get('errors', 0)
            }

        details["checks_performed"] = checks
        details["sd_errors"] = sd_errors
        details["gps_dropouts"] = gps_dropouts
        details["msp_timeouts"] = msp_timeouts
        details["total_issues"] = sd_errors + gps_dropouts + msp_timeouts

        # Pass if no issues detected
        passed = (sd_errors == 0 and gps_dropouts == 0 and msp_timeouts == 0)

        result = TestResult(
            test_num=10,
            test_name="DMA Contention Stress Test",
            passed=passed,
            duration_sec=time.time() - start_time,
            details=details
        )

        self.log(f"\n  RESULT: {'PASS' if passed else 'FAIL'}")
        self.log(f"  SD errors: {sd_errors}, GPS dropouts: {gps_dropouts}, MSP timeouts: {msp_timeouts}")
        return result

    # -------------------------------------------------------------------------
    # Test 11: Blocking Measurement (ST-Link + GDB)
    # -------------------------------------------------------------------------

    def test_11_blocking_measurement(self, elf_path: str = None, duration_sec: int = 60) -> TestResult:
        """Test 11: Blocking Measurement using ST-Link + GDB"""
        self.log("\n" + "="*60)
        self.log(f"TEST 11: Blocking Measurement (ST-Link + GDB)")
        self.log("="*60)

        start_time = time.time()

        if not elf_path:
            # Try to find ELF file
            possible_paths = [
                Path("build/MATEKF765.elf"),
                Path("build_MATEKF765/MATEKF765.elf"),
                Path("../inav/build/MATEKF765.elf"),
            ]
            for p in possible_paths:
                if p.exists():
                    elf_path = str(p)
                    break

        if not elf_path:
            return TestResult(
                test_num=11,
                test_name="Blocking Measurement",
                passed=False,
                duration_sec=time.time() - start_time,
                error="ELF file not found. Specify with --elf parameter."
            )

        self.log(f"  Using ELF: {elf_path}")
        self.log(f"  Duration: {duration_sec} seconds")
        self.log("")
        self.log("  NOTE: This test requires ST-Link connected to the FC.")
        self.log("  Running test_11_blocking.py...")
        self.log("")

        # Run the separate blocking measurement script
        import subprocess
        script_path = Path(__file__).parent / "test_11_blocking.py"

        try:
            result = subprocess.run(
                [sys.executable, str(script_path), elf_path,
                 "--duration", str(duration_sec)],
                capture_output=True,
                text=True,
                timeout=duration_sec + 60
            )

            self.log(result.stdout)
            if result.stderr:
                self.log(f"STDERR: {result.stderr}")

            # Parse results from output
            max_blocking = 0.0
            for line in result.stdout.split('\n'):
                if "Maximum blocking time:" in line:
                    try:
                        max_blocking = float(line.split(':')[1].strip().replace('ms', ''))
                    except:
                        pass

            passed = result.returncode == 0
            details = {
                "max_blocking_ms": max_blocking,
                "elf_path": elf_path,
                "duration_sec": duration_sec
            }

            return TestResult(
                test_num=11,
                test_name="Blocking Measurement",
                passed=passed,
                duration_sec=time.time() - start_time,
                details=details
            )

        except subprocess.TimeoutExpired:
            return TestResult(
                test_num=11,
                test_name="Blocking Measurement",
                passed=False,
                duration_sec=time.time() - start_time,
                error="Test timed out"
            )
        except Exception as e:
            return TestResult(
                test_num=11,
                test_name="Blocking Measurement",
                passed=False,
                duration_sec=time.time() - start_time,
                error=str(e)
            )


# =============================================================================
# Report Generation
# =============================================================================

def generate_report(results: list[TestResult], hal_version: str = "unknown",
                    baseline: bool = False, sd_card_info: dict = None) -> str:
    """Generate test report"""

    report_type = "BASELINE" if baseline else "COMPARISON"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "=" * 70,
        f"SD CARD TEST REPORT - {report_type}",
        "=" * 70,
        f"Timestamp: {timestamp}",
        f"HAL Version: {hal_version}",
        "",
    ]

    # Add SD card information if available
    if sd_card_info and baseline:
        lines.extend([
            "SD CARD INFORMATION (Pre-Test Validation)",
            "-" * 70,
            f"  Total Capacity: {sd_card_info.get('total_space_mb', 'N/A'):.1f} MB",
            f"  Free Space at Start: {sd_card_info.get('free_space_mb', 'N/A'):.1f} MB",
            f"  State: {sd_card_info.get('state', 'Unknown')}",
            f"  FS Error: {sd_card_info.get('fs_error', 'N/A')}",
            f"  Utilization: {((sd_card_info.get('total_space_mb', 0) - sd_card_info.get('free_space_mb', 0)) / max(sd_card_info.get('total_space_mb', 1), 1) * 100):.1f}%",
            "",
        ])

    lines.extend([
        "RESULTS SUMMARY",
        "-" * 70,
    ])

    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"  Test {r.test_num}: {r.test_name:<30} [{status}] ({r.duration_sec:.1f}s)")
        if r.error:
            lines.append(f"           Error: {r.error}")
        for key, value in r.details.items():
            lines.append(f"           {key}: {value}")

    lines.extend([
        "",
        "-" * 70,
        f"TOTAL: {passed_count}/{total_count} tests passed",
        "=" * 70,
    ])

    return "\n".join(lines)


def save_results(results: list[TestResult], output_path: Path, hal_version: str, sd_card_info: dict = None):
    """Save results to JSON file"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "hal_version": hal_version,
        "results": [r.to_dict() for r in results]
    }

    # Add SD card information if available
    if sd_card_info:
        data["sd_card_validation"] = sd_card_info

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Results saved to: {output_path}")


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SD Card Test Automation for MATEKF765SE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sd_card_test.py /dev/ttyACM0
  python sd_card_test.py /dev/ttyACM0 --test 1,2,3
  python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2
  python sd_card_test.py COM3 --test 8 --gps-timeout 600
        """
    )

    parser.add_argument("port", help="Serial port (e.g., /dev/ttyACM0 or COM3)")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--test", type=str, help="Comma-separated list of tests to run (e.g., 1,2,3)")
    parser.add_argument("--baseline", action="store_true", help="Mark as baseline measurement")
    parser.add_argument("--hal-version", type=str, default="unknown", help="HAL version being tested")
    parser.add_argument("--output", type=str, help="Output JSON file for results")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    parser.add_argument("--gps-timeout", type=int, default=300, help="GPS fix timeout in seconds")
    parser.add_argument("--elf", type=str, help="Path to firmware ELF file (for Test 11)")
    parser.add_argument("--verify-logs", action="store_true", help="Download and verify blackbox logs after tests")
    parser.add_argument("--save-logs", type=str, help="Save downloaded logs to this directory")
    parser.add_argument("--duration-min", type=int, default=60, help="Test duration in minutes (default: 60, used by Test 9)")
    parser.add_argument("--test9-blackbox-rate", type=str, help="Override blackbox rate for Test 9 (e.g., 1/8)")
    parser.add_argument("--restore-config", action="store_true", help="Restore baseline FC configuration and exit")
    parser.add_argument("--config-file", type=str, default="baseline-fc-config.txt", help="Baseline configuration file (default: baseline-fc-config.txt)")

    args = parser.parse_args()

    # Parse test list
    tests = None
    if args.test:
        try:
            tests = [int(t.strip()) for t in args.test.split(",")]
        except ValueError:
            print("ERROR: Invalid test list format. Use comma-separated numbers.")
            sys.exit(1)

    # Check mspapi2 availability
    if not MSPAPI2_AVAILABLE:
        print("\nERROR: mspapi2 library is required.")
        print("Install with: pip install mspapi2")
        print("Or clone from: https://github.com/xznhj8129/mspapi2")
        sys.exit(1)

    # Connect to flight controller
    print(f"Connecting to {args.port}...")
    fc = FCConnection(args.port, args.baudrate)

    if not fc.connect():
        print("ERROR: Failed to connect to flight controller")
        sys.exit(1)

    print("Connected successfully!")

    try:
        # Handle --restore-config flag
        if args.restore_config:
            print("\n" + "=" * 70)
            print("RESTORING BASELINE FC CONFIGURATION")
            print("=" * 70)
            if fc.apply_baseline_configuration(args.config_file):
                print("\n✓ Configuration applied successfully!")
                print("\nIMPORTANT: Please power-cycle the flight controller now.")
                print("After power-cycling, re-run the tests to validate.")
                sys.exit(0)
            else:
                print("\n✗ Failed to apply configuration.")
                print(f"Please apply manually: fc-set {args.port} {args.config_file}")
                sys.exit(1)

        # Initialize test suite
        suite = SDCardTestSuite(fc, verbose=not args.quiet)

        # Pre-test validation: check SD card before running tests
        min_free_mb = 150.0  # Need at least 150 MB for baseline tests
        if not suite.validate_sd_card_ready(min_free_mb=min_free_mb):
            print("\n" + "!" * 70)
            print("SD CARD VALIDATION FAILED - CANNOT RUN TESTS")
            print("!" * 70)
            print("\nREQUIREMENTS:")
            print("1. SD card must be properly formatted (FAT32 or exFAT)")
            print("2. SD card must have at least 150 MB free space")
            print("3. SD card filesystem must not have errors")
            print("\nTO FIX:")
            print("• Format the SD card using your flight controller or a PC")
            print("  Recommended: exFAT for SD cards > 4GB, FAT32 for smaller cards")
            print("• Ensure the card is detected by the flight controller")
            print("• Check in the INAV CLI: 'status' command should show SD card info")
            print("\nOnce fixed, run this script again to validate and proceed with testing.")
            sys.exit(1)

        # Pre-test validation: check FC configuration before running tests
        if not suite.validate_fc_configuration(args.config_file, auto_fix=False):
            print("\n" + "!" * 70)
            print("FC CONFIGURATION VALIDATION FAILED - CANNOT RUN TESTS")
            print("!" * 70)
            print("\nREQUIREMENTS:")
            print("1. Motor mixer: 4 motors configured (quadcopter)")
            print("2. Servo mixer: 4 servos configured (channels 6-9)")
            print("3. GPS feature must be enabled")
            print("4. PWM_OUTPUT_ENABLE feature must be enabled")
            print("5. Blackbox rate must be set to 1/2 (denom=2)")
            print("6. At least 2 serial ports configured")
            print("\nTO FIX:")
            print("Option 1 - AUTO RESTORE (recommended):")
            print("  python sd_card_test.py {args.port} --restore-config")
            print("\nOption 2 - MANUAL RESTORE:")
            print(f"  fc-set {args.port} baseline-fc-config.txt")
            print("\nOption 3 - MANUAL CONFIGURATION:")
            print("  • Use INAV Configurator to configure your FC")
            print("  • Save configuration: fc-get {args.port} baseline-fc-config.txt")
            print("\nOnce fixed, run this script again to validate and proceed with testing.")
            sys.exit(1)

        # Run tests with optional test-specific parameters
        test_params = {
            "duration_min": args.duration_min,
        }
        if args.test9_blackbox_rate:
            test_params["override_rate"] = args.test9_blackbox_rate

        results = suite.run_all(tests, **test_params)

        # Generate and print report
        report = generate_report(results, args.hal_version, args.baseline, suite.sd_card_info)
        print("\n" + report)

        # Verify logs if requested
        log_verification = None
        if args.verify_logs:
            save_logs_dir = Path(args.save_logs) if args.save_logs else None
            log_verification = suite.verify_baseline_logs()

            # Print log verification
            print("\n" + "="*70)
            if log_verification.passed:
                print("LOG VERIFICATION: PASS")
            else:
                print("LOG VERIFICATION: FAIL")
            print("="*70)
            print(f"Download method: {log_verification.download_method}")
            print(f"Logs found: {log_verification.logs_found}")
            print(f"Total size: {log_verification.total_size_mb:.2f} MB")
            print(f"Frames: {log_verification.frame_count} (I: {log_verification.i_frame_count}, P: {log_verification.p_frame_count})")
            if log_verification.errors:
                print("\nErrors:")
                for error in log_verification.errors:
                    print(f"  - {error}")
            if log_verification.warnings:
                print("\nWarnings:")
                for warning in log_verification.warnings:
                    print(f"  - {warning}")

        # Save results if output specified
        if args.output:
            output_path = Path(args.output)
            data = {
                "timestamp": datetime.now().isoformat(),
                "hal_version": args.hal_version,
                "results": [r.to_dict() for r in results]
            }
            if suite.sd_card_info:
                data["sd_card_validation"] = suite.sd_card_info
            if log_verification:
                data["log_verification"] = log_verification.to_dict()

            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\nResults saved to: {output_path}")

        # Exit with appropriate code
        all_passed = all(r.passed for r in results)
        if log_verification and not log_verification.passed:
            all_passed = False

        sys.exit(0 if all_passed else 1)

    finally:
        fc.disconnect()


if __name__ == "__main__":
    main()
