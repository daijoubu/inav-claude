"""
Example: Refactored Test Using Context Managers

Shows how test_2_write_speed can be simplified.
"""
import time
from dataclasses import dataclass
from typing import Optional

# From models.py
@dataclass
class TestResult:
    test_num: int
    test_name: str
    passed: bool
    duration_sec: float = 0.0
    details: dict = None
    error: Optional[str] = None


class SDCardTestBase:
    """Base class with common test patterns"""
    
    def __init__(self, fc, verbose: bool = True):
        self.fc = fc
        self.verbose = verbose
    
    def log(self, msg: str):
        if self.verbose:
            print(msg)
    
    def log_header(self, test_num: int, name: str):
        self.log("="*60)
        self.log(f"TEST {test_num}: {name}")
        self.log("="*60)
    
    def error_result(self, test_num: int, test_name: str, error: str) -> TestResult:
        return TestResult(
            test_num=test_num,
            test_name=test_name,
            passed=False,
            error=error
        )
    
    def calculate_write_speed(self, sd_before, sd_after, duration: float) -> dict:
        """Shared calculation for write speed tests"""
        kb_written = sd_before.free_space_kb - sd_after.free_space_kb
        return {
            "kb_written": kb_written,
            "bytes_written": kb_written * 1024,
            "write_speed_kbps": kb_written / duration if duration > 0 else 0,
            "free_space_before_mb": sd_before.free_space_kb / 1024,
            "free_space_after_mb": sd_after.free_space_kb / 1024,
        }


# BEFORE: test_2_write_speed (~150 lines)
# ========================================
def test_2_write_speed_BEFORE(self, duration_sec: int = 60) -> TestResult:
    """Test 2: Write Speed Measurement - ORIGINAL VERSION"""
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

    # Wait for FC to be ready for arming
    self.log("  Checking sensor status...")
    ready, status_msg = self.fc.wait_for_arming_ready(timeout=300.0)
    if not ready:
        return TestResult(
            test_num=2,
            test_name="Write Speed Measurement",
            passed=False,
            duration_sec=time.time() - start_time,
            error=f"Cannot arm: {status_msg}"
        )

    # Arm the FC
    self.log("  Arming FC...")
    if not self.fc.arm(timeout=5.0):
        return TestResult(
            test_num=2,
            test_name="Write Speed Measurement",
            passed=False,
            duration_sec=time.time() - start_time,
            error="Failed to arm"
        )
    
    try:
        self.log(f"  Logging for {duration_sec} seconds...")
        channels = [1500] * 16
        channels[2] = 1000  # Throttle LOW
        channels[4] = 2000  # ARM HIGH
        
        log_start = time.time()
        while time.time() - log_start < duration_sec:
            self.fc.send_rc_channels(channels)
            time.sleep(0.02)
    finally:
        self.log("  Disarming FC...")
        self.fc.disarm()

    # Get final status and calculate
    time.sleep(2)
    sd_after = self.fc.get_sd_card_status()
    
    details["kb_written"] = sd_before.free_space_kb - sd_after.free_space_kb
    details["write_speed_kbps"] = details["kb_written"] / duration_sec
    # ... more calculations ...

    return TestResult(
        test_num=2,
        test_name="Write Speed Measurement",
        passed=details["write_speed_kbps"] > 100,
        duration_sec=time.time() - start_time,
        details=details
    )


# AFTER: test_2_write_speed (~40 lines)
# ======================================
def test_2_write_speed_AFTER(self, duration_sec: int = 60) -> TestResult:
    """Test 2: Write Speed Measurement - REFACTORED"""
    from contexts import FCContextManager  # Our new context manager
    
    self.log_header(2, f"Write Speed Measurement ({duration_sec}s)")
    start_time = time.time()
    
    # Get baseline SD status
    sd_before = self.fc.get_sd_card_status()
    if not sd_before or not sd_before.is_ready:
        return self.error_result(2, "Write Speed Measurement", "SD card not ready")
    
    # Use context manager for arming - handles all the boilerplate
    ctx = FCContextManager(self.fc)
    with ctx.armed(timeout=300) as armed:
        if not armed:
            return self.error_result(2, "Write Speed Measurement", armed.error)
        
        self.log(f"  Logging for {duration_sec} seconds...")
        self.fc.run_rc_loop(duration_sec)  # Encapsulated RC loop
    
    # Calculate results
    time.sleep(2)  # Flush
    sd_after = self.fc.get_sd_card_status()
    details = self.calculate_write_speed(sd_before, sd_after, duration_sec)
    
    self.log(f"  Write speed: {details['write_speed_kbps']:.1f} KB/s")
    
    return TestResult(
        test_num=2,
        test_name="Write Speed Measurement",
        passed=details["write_speed_kbps"] > 100,
        duration_sec=time.time() - start_time,
        details=details
    )


# EVEN BETTER: Using run_armed_test helper
# =========================================
def test_2_write_speed_BEST(self, duration_sec: int = 60) -> TestResult:
    """Test 2: Write Speed Measurement - BEST VERSION"""
    self.log_header(2, f"Write Speed Measurement ({duration_sec}s)")
    
    sd_before = self.fc.get_sd_card_status()
    if not sd_before or not sd_before.is_ready:
        return self.error_result(2, "Write Speed Measurement", "SD card not ready")
    
    def measure():
        self.fc.run_rc_loop(duration_sec)
        time.sleep(2)
        sd_after = self.fc.get_sd_card_status()
        return self.calculate_write_speed(sd_before, sd_after, duration_sec)
    
    details = self.run_armed_test(measure, timeout=300)
    
    if isinstance(details, str):  # Error case
        return self.error_result(2, "Write Speed Measurement", details)
    
    return TestResult(
        test_num=2,
        test_name="Write Speed Measurement",
        passed=details["write_speed_kbps"] > 100,
        details=details
    )


# COMPARISON
# ==========
print("""
REFACTORING IMPACT:
===================

test_2_write_speed:
  BEFORE: ~150 lines with repeated patterns
  AFTER:  ~40 lines, context manager handles arming/RC/disarm
  
test_3_continuous_logging:
  BEFORE: ~120 lines
  AFTER:  ~30 lines (same pattern)
  
test_6_arm_disarm_cycles:
  BEFORE: ~80 lines of nested try/finally
  AFTER:  ~25 lines with armed context in loop

Total savings across all tests: ~400 lines of boilerplate removed
""")
