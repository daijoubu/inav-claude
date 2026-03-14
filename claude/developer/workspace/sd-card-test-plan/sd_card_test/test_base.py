"""
Base Test Class.

Provides common patterns and utilities for all SD card tests.
"""
import time
from typing import Optional

from .models import TestResult, SDCardStatus
from .contexts import FCContexts


class TestBase:
    """
    Base class for SD card tests.
    
    Provides:
    - Logging utilities
    - Common test patterns
    - Result creation helpers
    """
    
    test_num: int = 0
    test_name: str = "Base Test"
    
    def __init__(self, fc, msc=None, verbose=True):
        self.fc = fc
        self.msc = msc
        self.verbose = verbose
        self.contexts = FCContexts(fc, msc)
    
    def log(self, msg: str):
        """Print message if verbose mode."""
        if self.verbose:
            print(msg)
    
    def log_header(self):
        """Print test header."""
        self.log("")
        self.log("=" * 60)
        self.log(f"TEST {self.test_num}: {self.test_name}")
        self.log("=" * 60)
    
    def error_result(self, error: str, duration: float = 0.0) -> TestResult:
        """Create a failed test result."""
        return TestResult(
            test_num=self.test_num,
            test_name=self.test_name,
            passed=False,
            duration_sec=duration,
            error=error
        )
    
    def success_result(self, details: dict = None, duration: float = 0.0) -> TestResult:
        """Create a passed test result."""
        return TestResult(
            test_num=self.test_num,
            test_name=self.test_name,
            passed=True,
            duration_sec=duration,
            details=details or {}
        )
    
    def validate_sd_ready(self) -> Optional[SDCardStatus]:
        """
        Validate SD card is ready.
        
        Returns:
            SDCardStatus if ready, None otherwise
        """
        sd = self.fc.get_sd_card_status()
        if not sd:
            self.log("  ERROR: Failed to query SD card status")
            return None
        
        if not sd.is_ready:
            self.log(f"  ERROR: SD card not ready (state: {sd.state_name})")
            return None
        
        self.log(f"  SD Card: {sd.state_name}, Free: {sd.free_space_kb/1024:.1f} MB")
        return sd
    
    def calculate_write_speed(self, sd_before: SDCardStatus, 
                               sd_after: SDCardStatus, 
                               duration: float) -> dict:
        """Calculate write speed from before/after SD status."""
        kb_written = sd_before.free_space_kb - sd_after.free_space_kb
        return {
            "kb_written": kb_written,
            "bytes_written": kb_written * 1024,
            "write_speed_kbps": kb_written / duration if duration > 0 else 0,
            "free_space_before_mb": sd_before.free_space_kb / 1024,
            "free_space_after_mb": sd_after.free_space_kb / 1024,
        }


class ArmedTest(TestBase):
    """
    Test that requires the FC to be armed.
    
    Automatically handles arming/disarming via context manager.
    """
    
    def run_armed(self, test_func, duration: float = 60, timeout: float = 300):
        """
        Run a test function while armed.
        
        Args:
            test_func: Function to run while armed
            duration: Test duration in seconds
            timeout: Arming readiness timeout
            
        Returns:
            TestResult
        """
        self.log_header()
        start = time.time()
        
        # Validate SD card first
        sd_before = self.validate_sd_ready()
        if not sd_before:
            return self.error_result("SD card not ready", time.time() - start)
        
        # Run test while armed
        with self.contexts.armed(timeout=timeout) as armed:
            if not armed:
                return self.error_result(armed.error or "Failed to arm", time.time() - start)
            
            self.log(f"  Running test for {duration} seconds...")
            result = test_func(duration)
        
        return result
