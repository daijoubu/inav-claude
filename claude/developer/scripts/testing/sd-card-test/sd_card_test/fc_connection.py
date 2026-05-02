import struct
import threading
import time
from pathlib import Path
from typing import Optional, Tuple

try:
    from mspapi2 import MSPSerial
    MSPAPI2_AVAILABLE = True
except ImportError:
    MSPAPI2_AVAILABLE = False
    MSPSerial = None
    print("Warning: mspapi2 not installed. Install with: pip install mspapi2")

from .msp_types import (
    MSPCode, SDCardStatus, GPSStatus, ArmingStatus,
    SDCardState, GPSFixType, ArmingFlag
)


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
        """Query blackbox config via MSP2_BLACKBOX_CONFIG"""
        response = self._send_receive(MSPCode.BLACKBOX_CONFIG)
        if not response or len(response) < 8:
            return None

        supported = response[0]
        device = response[1]
        rate_num = struct.unpack('<H', response[2:4])[0]
        rate_denom = struct.unpack('<H', response[4:6])[0]
        flags = struct.unpack('<I', response[6:10])[0] if len(response) >= 10 else 0

        return {
            "supported": bool(supported),
            "device": device,
            "device_name": {0: "SERIAL", 1: "SPIFLASH", 2: "SDCARD", 3: "FILE"}.get(device, "UNKNOWN"),
            "rate_num": rate_num,
            "rate_denom": rate_denom,
            "flags": flags
        }

    def set_arming_disabled(self, disabled: bool, runaway_takeoff: bool = False) -> bool:
        """Enable/disable arming via MSP2_SET_ARMING_DISABLED"""
        data = struct.pack('<BB', 1 if disabled else 0, 1 if runaway_takeoff else 0)
        response = self._send_receive(MSPCode.SET_ARMING_DISABLED, data)
        return response is not None

    def send_rc_channels(self, channels: list[int], rate_hz: float = 50.0) -> bool:
        """Send RC channels via MSP_SET_RAW_RC (200)."""
        if not self.conn:
            return False

        while len(channels) < 16:
            channels.append(1500)

        payload = b''.join(struct.pack('<H', ch) for ch in channels[:16])
        try:
            self.conn.send(MSPCode.SET_RAW_RC, payload)
            return True
        except Exception as e:
            print(f"Error sending RC channels: {e}")
            return False

    def move_servos(self, duration: float, pattern: str = 'sweep', rate_hz: float = 10.0,
                    servo_channels: list[int] = None) -> dict:
        """Move servos for stress testing."""
        import random
        import math

        if servo_channels is None:
            servo_channels = [6, 7, 8, 9]

        result = {'success': True, 'updates_sent': 0, 'errors': 0, 'pattern': pattern, 'duration': 0.0}

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

                if current_time - last_update >= update_interval:
                    channels = [1500] * 16

                    if pattern == 'sweep':
                        phase = (current_time - start_time) * 2.0
                        servo_value = int(1500 + 500 * math.sin(phase * math.pi))
                    elif pattern == 'random':
                        servo_value = 1500 + random.randint(-250, 250)
                    elif pattern == 'rapid':
                        phase = (current_time - start_time) * 10.0
                        servo_value = 1000 if int(phase) % 2 == 0 else 2000
                    elif pattern == 'hold':
                        servo_value = 1500
                    else:
                        result['success'] = False
                        return result

                    for ch in servo_channels:
                        if ch < 16:
                            channels[ch] = servo_value

                    if self.send_rc_channels(channels, rate_hz=rate_hz):
                        result['updates_sent'] += 1
                    else:
                        result['errors'] += 1
                        result['success'] = False

                    last_update = current_time

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
        """Start servo stress testing in a background thread."""
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
        """Wait for background servo stress to complete."""
        stress_handle['join'](timeout)
        return stress_handle['callback']()

    def wait_for_arming_ready(self, timeout: float = 300.0, poll_interval: float = 0.5, 
                              rc_rate_hz: float = 50.0) -> Tuple[bool, str]:
        """Wait for FC to be ready for arming."""
        start_time = time.time()
        last_status = None
        rc_update_interval = 1.0 / rc_rate_hz
        last_rc_update = start_time

        BLOCKING_FLAGS = {
            ArmingFlag.ARMING_DISABLED_NOT_LEVEL: "Not level",
            ArmingFlag.ARMING_DISABLED_FAILSAFE: "Failsafe active",
            ArmingFlag.ARMING_DISABLED_THROTTLE: "Throttle not LOW",
            ArmingFlag.ARMING_DISABLED_NO_PREARM: "PreArm checks failed",
            ArmingFlag.ARMING_DISABLED_ARM_SWITCH: "Arm switch not ready",
        }

        rc_channels = [1500] * 16
        rc_channels[2] = 1000
        rc_channels[4] = 1000

        while time.time() - start_time < timeout:
            current_time = time.time()

            if current_time - last_rc_update >= rc_update_interval:
                self.send_rc_channels(rc_channels, rate_hz=rc_rate_hz)
                last_rc_update = current_time

            status = self.get_arming_status()
            if not status:
                return False, "Cannot query arming status"

            if status.arming_flags & ArmingFlag.ARMED:
                return False, "Already armed"

            blocking_reasons = []
            for flag, reason in BLOCKING_FLAGS.items():
                if status.arming_flags & flag:
                    blocking_reasons.append(reason)

            status_str = "Waiting: " + ", ".join(blocking_reasons) if blocking_reasons else "Ready to arm"

            if status_str != last_status:
                print(f"  {status_str}")
                last_status = status_str

            if not blocking_reasons:
                return True, "Ready to arm"

            time.sleep(poll_interval)

        return False, "Timeout waiting for arm ready"

    def arm(self, timeout: float = 5.0, arm_channel: int = 4) -> bool:
        """Attempt to arm the flight controller."""
        self.set_arming_disabled(False)

        status = self.get_arming_status()
        if not status:
            return False

        if status.is_armed:
            return True

        channels = [1500] * 16
        channels[2] = 1000
        channels[arm_channel] = 1000

        print(f"  Establishing RC link (arm LOW)...")
        
        start_time = time.time()
        while time.time() - start_time < 2.0:
            self.send_rc_channels(channels)
            time.sleep(0.02)

        status = self.get_arming_status()
        if status and not status.can_arm:
            print("  Cannot arm - arming flags still blocking")

        print(f"  Sending ARM command (CH{arm_channel+1} HIGH)...")
        channels[arm_channel] = 2000

        start_time = time.time()
        while time.time() - start_time < timeout:
            self.send_rc_channels(channels)
            time.sleep(0.02)
            
            status = self.get_arming_status()
            if status and status.is_armed:
                print("  ARMED!")
                return True

        print("  Failed to arm within timeout")
        return False

    def disarm(self, timeout: float = 3.0, arm_channel: int = 4) -> bool:
        """Disarm the flight controller."""
        channels = [1500] * 16
        channels[2] = 1000
        channels[arm_channel] = 1000

        start_time = time.time()
        while time.time() - start_time < timeout:
            self.send_rc_channels(channels)
            time.sleep(0.02)
            
            status = self.get_arming_status()
            if status and not status.is_armed:
                return True

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

    def reset_fc_state(self, timeout: float = 5.0) -> bool:
        """Reset FC to a clean state for test independence."""
        start_time = time.time()

        status = self.get_arming_status()
        if not status:
            return False

        was_armed = status.is_armed
        had_failsafe = bool(status.arming_flags & ArmingFlag.ARMING_DISABLED_FAILSAFE)

        if was_armed or had_failsafe:
            if was_armed:
                self.disarm(timeout=2.0)

            rc_channels = [1500] * 16
            rc_channels[2] = 1000
            rc_channels[4] = 1000

            while time.time() - start_time < timeout:
                self.send_rc_channels(rc_channels)
                time.sleep(0.02)

                status = self.get_arming_status()
                if status:
                    still_fs = bool(status.arming_flags & ArmingFlag.ARMING_DISABLED_FAILSAFE)
                    if not still_fs:
                        return True

            return False

        return True
