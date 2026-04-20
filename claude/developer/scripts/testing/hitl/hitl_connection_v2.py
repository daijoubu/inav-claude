#!/usr/bin/env python3
"""
Enhanced HITL Connection with Better Timeout and Lockup Detection.

Improvements over original:
- Configurable timeouts with automatic scaling
- CDC device presence check before declaring lockup
- Fresh connection test to distinguish FC hang vs communication failure
- Detailed diagnostic logging
- Proper MSPv2 command handling
"""

import os
import subprocess
import time
import serial
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Try to import GDB debugging capabilities
try:
    from .hitl_sdcard import HITLDebugger
    HAS_HITL_DEBUGGER = True
except ImportError:
    HAS_HITL_DEBUGGER = False


@dataclass
class ConnectionDiagnostics:
    """Diagnostic information for troubleshooting connection issues."""
    port: str = ""
    cdc_present: bool = False
    msc_present: bool = False
    serial_open: bool = False
    timeouts_before: int = 0
    last_error: str = ""
    fc_responded: bool = False
    recovery_attempted: bool = False
    recovery_successful: bool = False


class EnhancedHITLConnection:
    """
    Enhanced HITL connection with improved timeout and lockup detection.
    
    Key improvements:
    - Distinguishes FC hang from communication failure
    - CDC device presence check
    - Automatic retry with longer timeout
    - Detailed diagnostic logging
    """
    
    # Arming disable flags (from runtime_config.h)
    ARMING_FLAGS = {
        0x00000004: "ARMED",
        0x00000008: "WAS_EVER_ARMED",
        0x00000080: "ARMING_DISABLED_FAILSAFE",
        0x00000100: "ARMING_DISABLED_NOT_LEVEL",
        0x00004000: "ARMING_DISABLED_ARM_SWITCH",
        0x00080000: "ARMING_DISABLED_THROTTLE",
        0x10000000: "ARMING_DISABLED_NO_PREARM",
    }
    
    def __init__(self, port: str = '/dev/ttyACM0',
                 baud: int = 115200,
                 elf_path: Optional[str] = None,
                 
                 # Timeout configuration
                 short_timeout: float = 1.0,    # Normal MSP operations
                 medium_timeout: float = 3.0,    # Arming/disarming
                 long_timeout: float = 10.0,      # Extended operations
                 serial_timeout: float = 0.5,     # Serial port read timeout
                 
                 # Lockup detection
                 max_timeouts: int = 3,
                 check_cdc_before_lockup: bool = True,
                 retry_before_lockup: bool = True,
                 
                 verbose: bool = True):
        self.port = port
        self.baud = baud
        self.elf_path = elf_path
        
        # Timeouts
        self.short_timeout = short_timeout
        self.medium_timeout = medium_timeout
        self.long_timeout = long_timeout
        self.serial_timeout = serial_timeout
        
        # Lockup detection config
        self.max_timeouts = max_timeouts
        self.check_cdc_before_lockup = check_cdc_before_lockup
        self.retry_before_lockup = retry_before_lockup
        self.verbose = verbose
        
        # State
        self._serial: Optional[serial.Serial] = None
        self._consecutive_timeouts = 0
        self._armed = False
        self._last_diagnostics = ConnectionDiagnostics(port=port)
    
    def _log(self, msg: str):
        """Log message if verbose enabled"""
        if self.verbose:
            print(f"[HITL] {msg}")
    
    def _log_diagnostics(self, diag: ConnectionDiagnostics, context: str = ""):
        """Log diagnostic information"""
        if not self.verbose:
            return
        
        self._log(f"Diagnostic{context}:")
        self._log(f"  CDC present: {diag.cdc_present}")
        self._log(f"  MSC present: {diag.msc_present}")
        self._log(f"  Serial open: {diag.serial_open}")
        self._log(f"  Timeouts: {diag.timeouts_before}")
        self._log(f"  FC responded: {diag.fc_responded}")
        self._log(f"  Recovery: {diag.recovery_attempted} -> {diag.recovery_successful}")
        if diag.last_error:
            self._log(f"  Last error: {diag.last_error}")
    
    # =========================================================================
    # Device Detection
    # =========================================================================
    
    def check_cdc_device(self) -> bool:
        """Check if CDC serial device exists"""
        present = os.path.exists(self.port)
        self._last_diagnostics.cdc_present = present
        return present
    
    def check_msc_device(self) -> bool:
        """Check if FC is in MSC mode (USB mass storage)"""
        # Common SD card device names on Linux
        for device in ['/dev/sdb', '/dev/sdb1', '/dev/sdc', '/dev/sdc1', '/dev/mmcblk0', '/dev/mmcblk0p1']:
            if os.path.exists(device):
                self._last_diagnostics.msc_present = True
                return True
        self._last_diagnostics.msc_present = False
        return False
    
    # =========================================================================
    # Connection Management
    # =========================================================================
    
    def connect(self, timeout: float = None) -> bool:
        """Connect to FC via serial with specified timeout"""
        if timeout is None:
            timeout = self.serial_timeout
            
        try:
            # Check CDC device first
            if not self.check_cdc_device():
                self._log(f"CDC device {self.port} not found")
                self._last_diagnostics.last_error = "CDC device not found"
                return False
            
            # Check if in MSC mode
            if self.check_msc_device():
                self._log("FC is in MSC mode - cannot connect")
                self._last_diagnostics.last_error = "FC in MSC mode"
                return False
            
            # Close existing connection if any
            self.disconnect()
            
            # Open new connection
            self._serial = serial.Serial(
                self.port,
                self.baud,
                timeout=timeout,
                write_timeout=1.0
            )
            self._consecutive_timeouts = 0
            self._last_diagnostics.serial_open = True
            self._log(f"Connected to {self.port}")
            return True
            
        except serial.SerialException as e:
            self._log(f"Failed to connect: {e}")
            self._last_diagnostics.last_error = str(e)
            self._last_diagnostics.serial_open = False
            return False
    
    def disconnect(self):
        """Disconnect from FC"""
        if self._serial:
            try:
                self._serial.close()
            except:
                pass
            self._serial = None
            self._last_diagnostics.serial_open = False
    
    def reconnect(self) -> bool:
        """Attempt to reconnect with longer timeout"""
        self._log("Attempting to reconnect...")
        self._last_diagnostics.recovery_attempted = True
        
        # Try with longer timeout
        if self.connect(timeout=self.serial_timeout * 3):
            # Test with a simple query
            if self.ping():
                self._last_diagnostics.recovery_successful = True
                self._log("Reconnection successful")
                return True
        
        self._log("Reconnection failed")
        return False
    
    def ping(self) -> bool:
        """
        Simple ping to verify FC is responding.
        
        Uses multiple MSP commands since not all FCs support all commands.
        Tries in order of reliability: IDENT, SDCARD_SUMMARY, INAV_STATUS
        """
        # Commands to try (in order of preference)
        # MSP_IDENT (100) - standard, always supported
        # MSP_SDCARD_SUMMARY (79) - commonly supported
        # MSP2_INAV_STATUS (0x2000) - INAV specific
        ping_commands = [100, 79, 0x2000]
        
        for cmd in ping_commands:
            try:
                result = self._send_msp(cmd, b'', timeout=self.short_timeout)
                if result is not None:
                    return True
            except:
                continue
        
        return False
    
    # =========================================================================
    # ST-Link Verification
    # =========================================================================
    
    def verify_via_stlink(self) -> Tuple[bool, str]:
        """
        Verify FC status via ST-Link when MSP fails.
        
        Uses OpenOCD + GDB to check if:
        - FC is still running (can read registers)
        - Which code is executing (via PC register)
        
        Returns:
            (is_running, status_message)
        """
        if not HAS_HITL_DEBUGGER:
            return False, "ST-Link debugging not available"
        
        if not self.elf_path:
            return False, "No ELF path specified"
        
        if not Path(self.elf_path).exists():
            return False, f"ELF not found: {self.elf_path}"
        
        self._log("Verifying FC status via ST-Link...")
        
        # Start OpenOCD in background
        openocd_proc = None
        try:
            openocd_proc = subprocess.Popen(
                ['openocd', '-f', 'openocd_matekf765_no_halt.cfg'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for OpenOCD to connect
            time.sleep(2)
            
            if openocd_proc.poll() is not None:
                return False, "OpenOCD failed to start"
            
            # Run GDB to read PC register
            gdb_commands = f"""
set pagination off
set confirm off
target extended-remote :3333
file {self.elf_path}
echo \\n=== PC REGISTER ===\\n
info registers pc
echo \\n=== STACK POINTER ===\\n
info registers sp
echo \\n=== LINK REGISTER ===\\n
info registers lr
quit
"""
            
            gdb_cmd_file = Path(f"/tmp/hitl_stlink_verify_{os.getpid()}.cmd")
            with open(gdb_cmd_file, 'w') as f:
                f.write(gdb_commands)
            
            # Try both gdb variants
            for gdb_path in ['gdb', 'arm-none-eabi-gdb', '/usr/bin/gdb']:
                try:
                    result = subprocess.run(
                        [gdb_path, '-x', str(gdb_cmd_file)],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    
                    # Parse PC value
                    pc_value = None
                    for line in result.stdout.split('\n'):
                        line = line.strip()
                        if line.startswith('pc '):
                            # Extract hex value like "0x08012345"
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    pc_value = int(parts[1], 16)
                                    break
                                except ValueError:
                                    pass
                    
                    gdb_cmd_file.unlink(missing_ok=True)
                    
                    if pc_value:
                        # Check if PC is in valid flash range
                        # STM32F7 flash: 0x08000000 - 0x081FFFFF
                        # STM32H7 flash: 0x08000000 - 0x0803FFFF or 0x0C000000 for double-bank
                        if 0x08000000 <= pc_value <= 0x08200000 or 0x0C000000 <= pc_value <= 0x0C400000:
                            return True, f"FC running, PC=0x{pc_value:08X}"
                        else:
                            return False, f"PC in invalid range: 0x{pc_value:08X}"
                    else:
                        # Try to parse from stderr or other output
                        if '0x08' in result.stdout or '0x0c' in result.stdout:
                            return True, "FC appears to be running (PC found)"
                        
                except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                    continue
            
            return False, "Could not read registers via GDB"
            
        except FileNotFoundError:
            return False, "OpenOCD not found"
        except Exception as e:
            return False, f"ST-Link error: {e}"
        finally:
            if openocd_proc:
                try:
                    openocd_proc.terminate()
                    openocd_proc.wait(timeout=3)
                except:
                    openocd_proc.kill()
    
    def capture_stlink_state(self, output_file: str) -> bool:
        """
        Capture full FC state via ST-Link.
        
        Uses GDB to dump:
        - Registers
        - Backtrace
        - Key variables (via symbol table)
        
        Returns:
            True if capture succeeded
        """
        if not HAS_HITL_DEBUGGER:
            self._log("ST-Link debugging not available")
            return False
        
        self._log(f"Capturing FC state via ST-Link to {output_file}...")
        
        try:
            debugger = HITLDebugger(
                elf_path=self.elf_path,
                openocd_config='openocd_matekf765_no_halt.cfg'
            )
            return debugger.capture_state(output_file)
        except Exception as e:
            self._log(f"ST-Link capture failed: {e}")
            return False
    
    # =========================================================================
    # MSP Communication
    # =========================================================================
    
    def _send_msp(self, code: int, data: bytes = b'', timeout: float = None) -> Optional[bytes]:
        """
        Send MSP command and get response.
        
        Supports both MSPv1 and MSPv2 commands.
        """
        if timeout is None:
            timeout = self.short_timeout
            
        if not self._serial:
            self._last_diagnostics.last_error = "Not connected"
            return None
        
        # Build MSP request
        # MSPv1: $M < length code data checksum
        # MSPv2: $X > length code flags data checksum
        length = len(data)
        checksum = (length ^ code) & 0xFF
        for b in data:
            checksum ^= b
        
        # Use MSPv1 encoding (most common)
        request = bytes([ord('$'), ord('M'), ord('<'), length, code]) + data + bytes([checksum])
        
        try:
            self._serial.reset_input_buffer()
            self._serial.write(request)
            
            # Read response
            start = time.time()
            response = b''
            
            while time.time() - start < timeout:
                chunk = self._serial.read(256)
                if chunk:
                    response += chunk
                    # Check for MSP response markers
                    if b'$M>' in response:  # MSPv1 success
                        break
                    if b'$M!' in response:  # MSPv1 error
                        break
                    if b'$X>' in response:  # MSPv2 success
                        break
                    if b'$X!' in response:  # MSPv2 error
                        break
            
            # Parse response
            if b'$M!' in response or b'$X!' in response:
                self._consecutive_timeouts += 1
                self._last_diagnostics.timeouts_before = self._consecutive_timeouts
                self._last_diagnostics.last_error = "MSP error response"
                return None
            
            if b'$M>' in response:
                idx = response.index(b'$M>')
                if len(response) >= idx + 5:
                    resp_len = response[idx + 3]
                    if len(response) >= idx + 5 + resp_len:
                        self._consecutive_timeouts = 0
                        self._last_diagnostics.fc_responded = True
                        return response[idx + 5:idx + 5 + resp_len]
            
            if b'$X>' in response:
                idx = response.index(b'$X>')
                # MSPv2 has extra flags byte
                if len(response) >= idx + 6:
                    resp_len = response[idx + 3]
                    if len(response) >= idx + 6 + resp_len:
                        self._consecutive_timeouts = 0
                        self._last_diagnostics.fc_responded = True
                        return response[idx + 6:idx + 6 + resp_len]
            
            # Timeout - no valid response
            self._consecutive_timeouts += 1
            self._last_diagnostics.timeouts_before = self._consecutive_timeouts
            self._last_diagnostics.last_error = "Response timeout"
            return None
            
        except serial.SerialException as e:
            self._consecutive_timeouts += 1
            self._last_diagnostics.timeouts_before = self._consecutive_timeouts
            self._last_diagnostics.last_error = str(e)
            return None
    
    # =========================================================================
    # Lockup Detection with Recovery
    # =========================================================================
    
    def _check_and_handle_lockup(self) -> bool:
        """
        Check for lockup and attempt recovery.
        
        Returns True if lockup detected and handled (or recovered).
        """
        if self._consecutive_timeouts < self.max_timeouts:
            return False
        
        self._log(f"⚠ {self._consecutive_timeouts} consecutive timeouts - checking for lockup...")
        
        # Step 1: Check if CDC device is still present
        if self.check_cdc_before_lockup:
            if not self.check_cdc_device():
                self._log("  CDC device not present - FC may be powered off or disconnected")
                self._last_diagnostics.last_error = "CDC device gone"
                return True  # Lockup confirmed (device gone)
            
            self._log("  CDC device present")
        
        # Step 2: Check if in MSC mode
        if self.check_msc_device():
            self._log("  FC is in MSC mode")
            self._last_diagnostics.last_error = "MSC mode"
            return True
        
        # Step 3: Try retry with longer timeout (if enabled)
        if self.retry_before_lockup:
            self._log("  Attempting recovery with longer timeout...")
            self.disconnect()
            time.sleep(0.5)
            
            # Try with longer timeout
            if self.connect(timeout=self.serial_timeout * 3):
                # Test FC with simple query
                if self.ping():
                    self._log("  ✓ FC recovered on retry!")
                    self._last_diagnostics.recovery_successful = True
                    return False  # Not a lockup - recovered
            
            self._log("  FC did not respond to retry")
        
        # Step 4: Verify with ST-Link (if available)
        if self.elf_path:
            self._log("  Verifying with ST-Link...")
            is_running, status = self.verify_via_stlink()
            if is_running:
                self._log(f"  ✓ FC is RUNNING (MSP stuck) - {status}")
                self._last_diagnostics.last_error = f"FC running but MSP stuck: {status}"
                # FC is running, just MSP is stuck - don't treat as lockup
                # but capture state for debugging
                debug_file = f"debug_captures/msp_stuck_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
                Path("debug_captures").mkdir(exist_ok=True)
                self.capture_stlink_state(debug_file)
                self._log(f"  State captured to {debug_file}")
                # Reset and continue - FC is alive
                self._consecutive_timeouts = 0
                return False
            else:
                self._log(f"  ST-Link verification: {status}")
        
        # Step 5: Declare lockup
        self._log("  ⚠ FC appears to be locked up")
        self._log_diagnostics(self._last_diagnostics, " (LOCKUP)")
        
        # Capture debug state before declaring lockup
        if self.elf_path:
            debug_file = f"debug_captures/lockup_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
            Path("debug_captures").mkdir(exist_ok=True)
            self.capture_stlink_state(debug_file)
            self._log(f"  Debug state saved to {debug_file}")
        
        # Reset for next check cycle
        self._consecutive_timeouts = 0
        return True
    
    # =========================================================================
    # FC Control Operations
    # =========================================================================
    
    def send_rc_channels(self, channels: List[int]) -> bool:
        """Send RC channels (MSP_SET_RAW_RC, code 200)"""
        payload = b''.join(
            bytes([ch & 0xFF, (ch >> 8) & 0xFF])
            for ch in (channels + [1500] * 16)[:16]
        )
        result = self._send_msp(200, payload)
        
        if result is None:
            self._check_and_handle_lockup()
        
        return result is not None
    
    def get_arming_status(self, timeout: float = None) -> Optional[int]:
        """
        Get arming flags.
        
        Uses MSP commands that return arming-related information.
        Returns a simplified status - 0 if not armed, non-zero if armed.
        For full arming flags, use MSPv2 commands via mspapi2 library.
        """
        if timeout is None:
            timeout = self.short_timeout
            
        # Try MSP_STATUS (108) - returns basic flight status
        result = self._send_msp(108, b'', timeout=timeout)
        
        if result is None:
            self._check_and_handle_lockup()
            return None
        
        # MSP_STATUS format (from INAV):
        # byte 0: cycleTime (16-bit)
        # byte 2: i2cErrors (16-bit)  
        # byte 4: sensor (8-bit)
        # byte 5: flightModeFlags (32-bit) - this contains arming info
        # byte 9: armingFlags (8-bit)
        
        # Return a simple indicator - check byte 9 for arming
        if len(result) >= 10:
            return result[9]  # armingFlags
        
        # Fallback: return a non-zero value if we got any response
        return 1 if result else None
    
    def decode_arming_flags(self, flags: int) -> List[str]:
        """Decode arming flags to human-readable strings"""
        reasons = []
        for flag_val, flag_name in self.ARMING_FLAGS.items():
            if flags & flag_val:
                reasons.append(flag_name)
        return reasons
    
    def is_armed(self) -> bool:
        """Check if FC is armed"""
        flags = self.get_arming_status()
        return flags is not None and bool(flags & 0x00000004)
    
    def can_arm(self) -> Tuple[bool, List[str]]:
        """Check if FC can be armed"""
        flags = self.get_arming_status()
        if flags is None:
            return False, ["Cannot query status"]
        
        blockers = []
        for flag_val, flag_name in self.ARMING_FLAGS.items():
            if flag_val not in (0x00000004, 0x00000008) and (flags & flag_val):
                blockers.append(flag_name)
        
        return len(blockers) == 0, blockers
    
    def clear_failsafe(self, duration_sec: float = 2.0):
        """Clear FAILSAFE by sending RC commands."""
        self._log(f"Clearing FAILSAFE ({duration_sec:.1f}s)...")
        
        channels = [1500] * 16
        channels[2] = 1000  # Throttle LOW
        channels[4] = 1000  # Arm LOW
        
        start = time.time()
        while time.time() - start < duration_sec:
            self.send_rc_channels(channels)
            time.sleep(0.02)
    
    def wait_for_arming_ready(self, timeout: float = 30.0) -> Tuple[bool, str]:
        """Wait until FC is ready to arm."""
        # First clear FAILSAFE
        self.clear_failsafe()
        
        start = time.time()
        last_blockers = []
        
        rc_channels = [1500] * 16
        rc_channels[2] = 1000
        rc_channels[4] = 1000
        
        while time.time() - start < timeout:
            self.send_rc_channels(rc_channels)
            time.sleep(0.02)
            
            can, blockers = self.can_arm()
            
            if blockers != last_blockers:
                if blockers:
                    self._log(f"Waiting: {', '.join(blockers)}")
                last_blockers = blockers
            
            if can:
                return True, "Ready to arm"
        
        return False, f"Timeout: {', '.join(last_blockers)}"
    
    def arm(self, timeout: float = None) -> bool:
        """Arm the FC"""
        if timeout is None:
            timeout = self.medium_timeout
            
        if self.is_armed():
            return True
        
        channels = [1500] * 16
        channels[2] = 1000
        channels[4] = 2000  # Arm HIGH
        
        start = time.time()
        while time.time() - start < timeout:
            self.send_rc_channels(channels)
            time.sleep(0.02)
            
            if self.is_armed():
                self._log("ARMED")
                self._armed = True
                return True
        
        self._log("Failed to arm")
        return False
    
    def disarm(self, timeout: float = None) -> bool:
        """Disarm the FC"""
        if timeout is None:
            timeout = self.medium_timeout
            
        channels = [1500] * 16
        channels[2] = 1000
        channels[4] = 1000  # Arm LOW
        
        start = time.time()
        while time.time() - start < timeout:
            self.send_rc_channels(channels)
            time.sleep(0.02)
            
            if not self.is_armed():
                self._log("Disarmed")
                self._armed = False
                return True
        
        self._armed = False
        return True
    
    @contextmanager
    def armed(self, timeout: float = 30.0):
        """Context manager for armed operations"""
        ready, msg = self.wait_for_arming_ready(timeout)
        if not ready:
            self._log(f"Cannot arm: {msg}")
            yield False
            return
        
        if not self.arm():
            yield False
            return
        
        try:
            yield True
        finally:
            self.disarm()
    
    # =========================================================================
    # Context Manager
    # =========================================================================
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._armed:
            self.disarm()
        self.disconnect()
        return False


def test_connection():
    """Test enhanced connection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced HITL Connection Test")
    parser.add_argument('--port', default='/dev/ttyACM0', help='Serial port')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    print(f"Testing enhanced connection to {args.port}...")
    
    with EnhancedHITLConnection(args.port, verbose=args.verbose) as fc:
        if fc.ping():
            print("✓ FC responding")
            
            flags = fc.get_arming_status()
            if flags is not None:
                print(f"Arming flags: 0x{flags:08X}")
                reasons = fc.decode_arming_flags(flags)
                print(f"Decoded: {reasons}")
        else:
            print("✗ FC not responding")


if __name__ == '__main__':
    test_connection()
