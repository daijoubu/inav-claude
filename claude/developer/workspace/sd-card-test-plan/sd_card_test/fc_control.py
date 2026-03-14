"""
Flight Controller Control Operations.

Arming, RC control, GPS operations, and servo stress testing.
"""
import random
import threading
import time
from typing import Optional, Tuple, List

from .connection import MSPConnection
from .models import ArmingFlag, ArmingStatus, ServoStressResult
from .msp import MSPCode, MSPBuilder


class FCControl(MSPConnection):
    """
    Flight controller control operations.
    
    Extends MSPConnection with arming, RC, GPS, and servo control.
    """
    
    def set_arming_disabled(self, disabled: bool, runaway_takeoff: bool = False) -> bool:
        """Enable/disable arming via MSP2_SET_ARMING_DISABLED"""
        data = MSPBuilder.set_arming_disabled(disabled, runaway_takeoff)
        response = self.send_receive(MSPCode.SET_ARMING_DISABLED, data)
        return response is not None
    
    def wait_for_arming_ready(self, timeout: float = 300.0, poll_interval: float = 0.5,
                               rc_rate_hz: float = 50.0) -> Tuple[bool, str]:
        start_time = time.time()
        last_status = None
        rc_interval = 1.0 / rc_rate_hz
        last_rc = start_time
        
        BLOCKING_FLAGS = {
            ArmingFlag.ARMING_DISABLED_NOT_LEVEL: "Not level",
            ArmingFlag.ARMING_DISABLED_FAILSAFE: "Failsafe active",
            ArmingFlag.ARMING_DISABLED_THROTTLE: "Throttle not LOW",
            ArmingFlag.ARMING_DISABLED_NO_PREARM: "PreArm checks failed",
            ArmingFlag.ARMING_DISABLED_ARM_SWITCH: "Arm switch not ready (needs LOW)",
        }
        
        rc_channels = [1500] * 16
        rc_channels[2] = 1000
        rc_channels[4] = 1000
        
        blockers = []
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        print("  Sending RC commands to establish link...")
        for _ in range(100):
            self.send_rc_channels(rc_channels)
            time.sleep(0.02)
        
        while time.time() - start_time < timeout:
            now = time.time()
            
            if now - last_rc >= rc_interval:
                self.send_rc_channels(rc_channels)
                last_rc = now
            
            try:
                status = self.get_arming_status()
                consecutive_errors = 0
            except Exception:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    return False, "Too many MSP errors"
                time.sleep(1)
                continue
            
            if not status:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    return False, "Cannot query arming status"
                time.sleep(poll_interval)
                continue
            
            if status.arming_flags & ArmingFlag.ARMED:
                return False, "Already armed"
            
            blockers = []
            for flag, reason in BLOCKING_FLAGS.items():
                if status.arming_flags & flag:
                    blockers.append(reason)
            
            status_str = "Waiting: " + ", ".join(blockers) if blockers else "Ready to arm"
            
            if status_str != last_status:
                print(f"  {status_str}")
                last_status = status_str
            
            if not blockers:
                return True, "Ready to arm"
            
            time.sleep(poll_interval)
        
        return False, f"Timeout: {', '.join(blockers) if blockers else 'unknown'}"
    
    def arm(self, timeout: float = 5.0, arm_channel: int = 4) -> bool:
        status = self.get_arming_status()
        if status and status.is_armed:
            return True
        
        self.set_arming_disabled(True)
        time.sleep(0.1)
        self.set_arming_disabled(False)
        
        channels = [1500] * 16
        channels[2] = 1000
        channels[arm_channel] = 1000
        
        print("  Establishing RC link (arm LOW)...")
        start = time.time()
        
        while time.time() - start < 10.0:
            self.send_rc_channels(channels)
            time.sleep(0.02)
            
            status = self.get_arming_status()
            if not status:
                continue
            
            arm_switch_block = status.arming_flags & ArmingFlag.ARMING_DISABLED_ARM_SWITCH
            
            if not arm_switch_block:
                print("  ✓ Ready to arm (ARM_SWITCH cleared)")
                break
        else:
            print("  ⚠ Timeout waiting for ARM_SWITCH to clear")
        
        print(f"  Sending ARM command (CH{arm_channel+1} HIGH)...")
        channels[arm_channel] = 2000
        
        start = time.time()
        while time.time() - start < timeout:
            self.send_rc_channels(channels)
            time.sleep(0.02)
            
            status = self.get_arming_status()
            if status and status.is_armed:
                print("  ARMED!")
                return True
        
        print("  Failed to arm within timeout")
        return False
    
    def disarm(self, timeout: float = 3.0, arm_channel: int = 4) -> bool:
        channels = [1500] * 16
        channels[2] = 1000
        channels[arm_channel] = 1000
        
        start = time.time()
        while time.time() - start < timeout:
            self.send_rc_channels(channels)
            time.sleep(0.02)
            
            status = self.get_arming_status()
            if status and not status.is_armed:
                return True
        
        return self.set_arming_disabled(True)
    
    def wait_for_gps_fix(self, timeout: float = 300.0, poll_interval: float = 1.0) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            gps = self.get_gps_status()
            if gps and gps.has_fix:
                return True
            time.sleep(poll_interval)
        return False
    
    def run_rc_loop(self, duration: float, throttle: int = 1000, arm_high: bool = True):
        channels = [1500] * 16
        channels[2] = throttle
        channels[4] = 2000 if arm_high else 1000
        
        start = time.time()
        while time.time() - start < duration:
            self.send_rc_channels(channels)
            time.sleep(0.02)
    
    def move_servos(self, duration: float, pattern: str = 'sweep',
                    rate_hz: float = 10.0, servo_channels: Optional[List[int]] = None) -> ServoStressResult:
        import math
        
        if servo_channels is None:
            servo_channels = [6, 7, 8, 9]
        
        result = ServoStressResult(success=True, pattern=pattern)
        
        if not self.is_connected:
            result.success = False
            return result
        
        start = time.time()
        interval = 1.0 / rate_hz
        last_update = start
        phase = 0.0
        
        while time.time() - start < duration:
            now = time.time()
            
            if now - last_update >= interval:
                channels = [1500] * 16
                channels[2] = 1000
                channels[4] = 2000
                
                if pattern == 'sweep':
                    phase = (now - start) * 2.0
                    servo_value = int(1500 + 500 * math.sin(phase * math.pi))
                elif pattern == 'random':
                    servo_value = 1500 + random.randint(-250, 250)
                elif pattern == 'rapid':
                    phase = (now - start) * 10.0
                    servo_value = 1000 if int(phase) % 2 == 0 else 2000
                else:
                    servo_value = 1500
                
                for ch in servo_channels:
                    if ch < 16:
                        channels[ch] = servo_value
                
                if self.send_rc_channels(channels):
                    result.updates_sent += 1
                else:
                    result.errors += 1
                    result.success = False
                
                last_update = now
            
            time.sleep(0.01)
        
        result.duration = time.time() - start
        return result
    
    def start_servo_stress_background(self, duration: float, pattern: str = 'sweep',
                                       rate_hz: float = 10.0) -> dict:
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
    
    def wait_for_servo_stress(self, handle: dict, timeout: Optional[float] = None) -> ServoStressResult:
        handle['join'](timeout)
        return handle['callback']()
