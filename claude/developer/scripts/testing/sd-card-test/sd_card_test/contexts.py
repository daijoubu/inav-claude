"""
Context Managers for FC Operations.

Provides clean, reusable patterns for common FC operations.
"""
import time
from contextlib import contextmanager
from typing import Generator, Callable

from .models import ArmedContext, MSCContext


class FCContexts:
    """
    Context managers for FC operations.
    """
    
    def __init__(self, fc, msc_handler=None, openocd_config=None):
        self.fc = fc
        self._msc = msc_handler
        self._openocd_config = openocd_config
    
    @contextmanager
    def armed(self, timeout=300.0, arm_channel=4):
        """Context manager for armed operations."""
        start = time.time()
        
        ready, msg = self.fc.wait_for_arming_ready(timeout=timeout)
        if not ready:
            yield ArmedContext(success=False, error=msg)
            return
        
        if not self.fc.arm(timeout=5.0, arm_channel=arm_channel):
            yield ArmedContext(success=False, error="Failed to arm")
            return
        
        try:
            yield ArmedContext(success=True, duration=time.time() - start)
        finally:
            self.fc.disarm()
    
    @contextmanager
    def msc(self, timeout=60.0, openocd_config=None):
        """Context manager for MSC operations."""
        if not self._msc:
            yield MSCContext(success=False, error="MSC handler not configured")
            return
        
        if not self._msc.enable_msc_mode(timeout=timeout):
            yield MSCContext(success=False, error="Failed to enable MSC")
            return
        
        mount = self._msc.find_msc_mount_point()
        if not mount:
            self._exit_msc(openocd_config or self._openocd_config)
            yield MSCContext(success=False, error="Mount point not found")
            return
        
        try:
            yield MSCContext(success=True, mount_point=str(mount))
        finally:
            self._exit_msc(openocd_config or self._openocd_config)
    
    def _exit_msc(self, openocd_config=None):
        """Exit MSC mode safely."""
        if self._msc:
            try:
                self._msc.exit_msc_mode(openocd_config)
            except:
                pass
