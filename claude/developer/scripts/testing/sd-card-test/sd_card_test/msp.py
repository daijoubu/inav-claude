"""
MSP Protocol Constants and Parsing.

MSP command codes and data parsing functions.
"""
import struct
from typing import Optional, Tuple


class MSPCode:
    """MSP command codes"""
    SDCARD_SUMMARY = 79
    DATAFLASH_SUMMARY = 70
    DATAFLASH_READ = 71
    BLACKBOX_CONFIG = 0x201A
    SET_BLACKBOX_CONFIG = 0x201B
    INAV_STATUS = 0x2000
    STATUS_EX = 150
    RAW_GPS = 106
    COMP_GPS = 107
    GPSSTATISTICS = 166
    SET_RAW_RC = 200
    RC = 105
    SET_ARMING_DISABLED = 0x200B
    SET_REBOOT = 68


class MSPParse:
    """MSP response parsing utilities"""
    
    @staticmethod
    def sd_card_status(data: bytes) -> Optional[dict]:
        """Parse MSP_SDCARD_SUMMARY response"""
        if not data or len(data) < 10:
            return None
        supported, state, fs_error = struct.unpack('<BBB', data[0:3])
        free_kb, total_kb = struct.unpack('<II', data[3:11]) if len(data) >= 11 else (0, 0)
        return {
            'supported': bool(supported & 0x01),
            'state': state,
            'fs_error': fs_error,
            'free_space_kb': free_kb,
            'total_space_kb': total_kb
        }
    
    @staticmethod
    def gps_status(data: bytes) -> Optional[dict]:
        """Parse MSP_RAW_GPS response"""
        if not data or len(data) < 18:
            return None
        fix_type, num_sat = struct.unpack('<BB', data[0:2])
        lat, lon = struct.unpack('<ii', data[2:10])
        alt, speed, course, hdop = struct.unpack('<hhhH', data[10:18])
        return {
            'fix_type': fix_type,
            'num_sat': num_sat,
            'latitude': lat / 1e7,
            'longitude': lon / 1e7,
            'altitude_cm': alt,
            'speed_cms': speed,
            'ground_course': course,
            'hdop': hdop / 100.0
        }
    
    @staticmethod
    def arming_status(data: bytes) -> Optional[dict]:
        """Parse MSP2_INAV_STATUS response"""
        if not data or len(data) < 12:
            return None
        cycle_time, i2c_errors, sensor_status, cpu_load = struct.unpack('<HHHH', data[0:8])
        profile = data[8]
        arming_flags = struct.unpack('<I', data[9:13])[0]
        return {
            'cycle_time': cycle_time,
            'i2c_errors': i2c_errors,
            'cpu_load': cpu_load,
            'arming_flags': arming_flags
        }
    
    @staticmethod
    def blackbox_config(data: bytes) -> Optional[dict]:
        """Parse MSP2_BLACKBOX_CONFIG response"""
        if not data or len(data) < 8:
            return None
        supported = data[0]
        device = data[1]
        rate_num = struct.unpack('<H', data[2:4])[0]
        rate_denom = struct.unpack('<H', data[4:6])[0]
        flags = struct.unpack('<I', data[6:10])[0] if len(data) >= 10 else 0
        device_names = {0: "SERIAL", 1: "SPIFLASH", 2: "SDCARD", 3: "FILE"}
        return {
            'supported': bool(supported),
            'device': device,
            'device_name': device_names.get(device, "UNKNOWN"),
            'rate_num': rate_num,
            'rate_denom': rate_denom,
            'flags': flags
        }
    
    @staticmethod
    def dataflash_summary(data: bytes) -> Optional[dict]:
        """Parse MSP_DATAFLASH_SUMMARY response"""
        if not data or len(data) < 13:
            return None
        flags, sectors, total_size, used_size = struct.unpack('<BIII', data[:13])
        return {
            'flags': flags,
            'sectors': sectors,
            'total_size': total_size,
            'used_size': used_size
        }


class MSPBuilder:
    """MSP request building utilities"""
    
    @staticmethod
    def set_arming_disabled(disabled: bool, runaway_takeoff: bool = False) -> bytes:
        """Build SET_ARMING_DISABLED payload"""
        return struct.pack('<BB', 1 if disabled else 0, 1 if runaway_takeoff else 0)
    
    @staticmethod
    def set_raw_rc(channels: list) -> bytes:
        """Build SET_RAW_RC payload from 16 channel values"""
        return b''.join(struct.pack('<H', ch) for ch in channels[:16])
    
    @staticmethod
    def set_blackbox_config(supported: int, device: int, rate_num: int, rate_denom: int, flags: int) -> bytes:
        """Build SET_BLACKBOX_CONFIG payload"""
        return struct.pack('<BBHHI', supported, device, rate_num, rate_denom, flags)
    
    @staticmethod
    def dataflash_read(address: int, size: int) -> bytes:
        """Build DATAFLASH_READ payload"""
        return struct.pack('<IH', address, size)
