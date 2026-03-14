"""
Data models for SD Card testing.

All dataclasses used throughout the test framework.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, Optional


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
        disable_mask = 0x7FFFFFC0
        return (self.arming_flags & disable_mask) == 0


@dataclass
class TestResult:
    """Result of a single test"""
    test_num: int
    test_name: str
    passed: bool
    duration_sec: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
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
    download_method: str = "unknown"
    frame_count: int = 0
    i_frame_count: int = 0
    p_frame_count: int = 0
    header_fields: Dict[str, Any] = field(default_factory=dict)
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


@dataclass
class ArmedContext:
    """Result of arming context"""
    success: bool
    error: Optional[str] = None
    duration: float = 0.0
    
    def __bool__(self) -> bool:
        return self.success


@dataclass
class MSCContext:
    """Result of MSC context"""
    success: bool
    mount_point: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ServoStressResult:
    """Result of servo stress test"""
    success: bool
    updates_sent: int = 0
    errors: int = 0
    pattern: str = "unknown"
    duration: float = 0.0
