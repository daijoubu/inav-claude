"""
Context Managers for FC Operations

Provides clean, reusable patterns for common FC operations.
Eliminates repeated try/finally/disarm boilerplate.
"""
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Generator, Callable


@dataclass
class ArmedContext:
    """Result of arming context"""
    success: bool
    error: Optional[str] = None
    duration: float = 0.0


@dataclass  
class MSCContext:
    """Result of MSC context"""
    success: bool
    mount_point: Optional[str] = None
    error: Optional[str] = None


class FCContextManager:
    """
    Context managers for FC operations.
    
    Usage:
        fc = FCConnection('/dev/ttyACM0')
        fc.connect()
        
        ctx = FCContextManager(fc)
        
        # Armed context - auto-disarms on exit
        with ctx.armed(timeout=300) as armed:
            if not armed:
                print(f"Failed: {armed.error}")
                return
            # ... test logic ...
        
        # MSC context - auto-exits on exit  
        with ctx.msc() as msc:
            if not msc:
                print(f"MSC failed: {msc.error}")
                return
            logs = download_logs(msc.mount_point)
    """
    
    def __init__(self, fc):
        self.fc = fc
    
    @contextmanager
    def armed(self, 
              timeout: float = 300.0,
              rc_rate_hz: float = 50.0,
              arm_channel: int = 4) -> Generator[ArmedContext, None, None]:
        """
        Context manager for armed operations.
        
        Automatically:
        1. Waits for arming readiness
        2. Arms the FC
        3. Keeps RC link active during operation
        4. Disarms on exit (even on exception)
        
        Args:
            timeout: Max seconds to wait for ready
            rc_rate_hz: RC update rate
            arm_channel: Channel for arm switch
            
        Yields:
            ArmedContext with success status
        """
        start = time.time()
        
        # Wait for ready
        ready, msg = self.fc.wait_for_arming_ready(timeout=timeout)
        if not ready:
            yield ArmedContext(success=False, error=msg)
            return
        
        # Arm
        if not self.fc.arm(timeout=5.0, arm_channel=arm_channel):
            yield ArmedContext(success=False, error="Failed to arm")
            return
        
        try:
            yield ArmedContext(
                success=True, 
                duration=time.time() - start
            )
        finally:
            # Always disarm
            self.fc.disarm()
    
    @contextmanager
    def msc(self, 
            timeout: float = 60.0,
            openocd_config: str = None) -> Generator[MSCContext, None, None]:
        """
        Context manager for MSC operations.
        
        Automatically:
        1. Enables MSC mode
        2. Returns mount point
        3. Exits MSC and restores CDC on exit
        
        Args:
            timeout: Max seconds to wait for MSC
            openocd_config: OpenOCD config for exit
            
        Yields:
            MSCContext with mount point
        """
        # Enable MSC
        if not self.fc.enable_msc_mode(timeout=timeout):
            yield MSCContext(success=False, error="Failed to enable MSC")
            return
        
        # Find mount point
        mount = self.fc.find_msc_mount_point()
        if not mount:
            # Try to exit cleanly anyway
            self._exit_msc(openocd_config)
            yield MSCContext(success=False, error="Mount point not found")
            return
        
        try:
            yield MSCContext(
                success=True,
                mount_point=str(mount)
            )
        finally:
            # Always exit MSC mode
            self._exit_msc(openocd_config)
    
    def _exit_msc(self, openocd_config: str = None):
        """Exit MSC mode safely"""
        try:
            self.fc.exit_msc_mode_and_reenumerate(openocd_config)
        except Exception:
            pass  # Best effort
    
    @contextmanager
    def armed_with_stress(self,
                          duration: float,
                          stress_pattern: str = 'sweep',
                          stress_rate: float = 10.0,
                          **armed_kwargs) -> Generator[ArmedContext, None, None]:
        """
        Context manager for armed operation with servo stress.
        
        Combines arming with background servo stress testing.
        Useful for tests that need load during logging.
        """
        stress_handle = None
        
        # Start stress in background when armed
        with self.armed(**armed_kwargs) as ctx:
            if ctx.success:
                stress_handle = self.fc.start_servo_stress_background(
                    duration=duration,
                    pattern=stress_pattern,
                    rate_hz=stress_rate
                )
            yield ctx
        
        # Wait for stress to complete (already disarmed)
        if stress_handle:
            self.fc.wait_for_servo_stress(stress_handle)


# Convenience function for one-liners
def with_armed(fc, func: Callable, **kwargs):
    """
    Run a function with FC armed.
    
    Usage:
        result = with_armed(fc, lambda: measure_write_speed(60))
    """
    ctx = FCContextManager(fc)
    with ctx.armed(**kwargs) as armed:
        if not armed:
            return None
        return func()


def with_msc(fc, func: Callable, **kwargs):
    """
    Run a function with FC in MSC mode.
    
    Usage:
        logs = with_msc(fc, lambda m: download_from(m.mount_point))
    """
    ctx = FCContextManager(fc)
    with ctx.msc(**kwargs) as msc:
        if not msc:
            return None
        return func(msc)
