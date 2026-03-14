"""
Base MSP Connection.

Low-level MSP protocol communication with flight controller.
"""
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import SDCardStatus, GPSStatus, ArmingStatus
from .msp import MSPCode, MSPParse

try:
    from mspapi2 import MSPSerial
    MSPAPI2_AVAILABLE = True
except ImportError:
    MSPAPI2_AVAILABLE = False
    MSPSerial = None


class MSPConnection:
    """
    Low-level MSP connection to flight controller.
    
    Handles connection management and basic MSP commands.
    Higher-level operations (arming, MSC, etc.) are in separate modules.
    """
    
    def __init__(self, port: str, baudrate: int = 115200, 
                 debug_on_lockup: bool = True, 
                 openocd_config: str = "openocd_matekf765_no_halt.cfg"):
        self.port = port
        self.baudrate = baudrate
        self.conn: Optional[MSPSerial] = None
        self.debug_on_lockup = debug_on_lockup
        self.openocd_config = openocd_config
        self._consecutive_timeouts = 0
        self._max_consecutive_timeouts = 3
    
    @property
    def is_connected(self) -> bool:
        return self.conn is not None
    
    def connect(self) -> bool:
        """Establish connection to flight controller"""
        if not MSPAPI2_AVAILABLE:
            print("ERROR: mspapi2 library not available")
            print("       Install with: pip install mspapi2")
            return False
        
        try:
            self.conn = MSPSerial(
                self.port,
                self.baudrate,
                read_timeout=0.1,
                write_timeout=0.5
            )
            self.conn.open()
            self._consecutive_timeouts = 0
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
            self.conn = None
    
    def _check_msc_mode(self) -> bool:
        """Check if FC is in MSC mode (block device present)"""
        for device in ['/dev/sdb', '/dev/sdb1', '/dev/sdc', '/dev/sdc1']:
            if os.path.exists(device):
                return True
        return False
    
    def _capture_lockup_state(self, code: int) -> bool:
        """
        Capture FC state via GDB when lockup is detected.
        
        Returns True if capture succeeded.
        """
        print("\n" + "="*60)
        print("FC LOCKUP DETECTED - CAPTURING DEBUG STATE")
        print("="*60)
        
        # Check CDC still exists
        if not os.path.exists(self.port):
            print("  CDC device disconnected - cannot capture")
            return False
        
        # Check not in MSC mode
        if self._check_msc_mode():
            print("  FC is in MSC mode - not a lockup")
            return False
        
        print(f"  MSP code {code} timed out")
        print(f"  CDC device present: {self.port}")
        print(f"  MSC mode: No")
        print()
        
        # Create output directory
        output_dir = Path("debug_captures")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        output_file = output_dir / f"lockup_{timestamp}.txt"
        
        # Create GDB commands
        gdb_commands = f"""
set pagination off
set confirm off
target extended-remote :3333
echo \\n=== REGISTERS ===\\n
info registers
echo \\n=== BACKTRACE ===\\n
bt
echo \\n=== CURRENT FRAME ===\\n
info frame
echo \\n=== DISASSEMBLY AT PC ===\\n
disassemble $pc-20,$pc+20
echo \\n=== THREAD INFO ===\\n
info threads
echo \\n=== MEMORY AT SP ===\\n
x/16x $sp
quit
"""
        
        gdb_cmd_file = output_dir / f"gdb_commands_{timestamp}.txt"
        with open(gdb_cmd_file, 'w') as f:
            f.write(gdb_commands)
        
        # Start OpenOCD
        print("  Starting OpenOCD (connect without halt)...")
        openocd_proc = subprocess.Popen(
            ['openocd', '-f', self.openocd_config],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(2)
        
        if openocd_proc.poll() is not None:
            stdout, stderr = openocd_proc.communicate()
            print(f"  OpenOCD failed:")
            print(stderr[-500:] if len(stderr) > 500 else stderr)
            return False
        
        print("  Running GDB...")
        
        try:
            gdb_result = subprocess.run(
                ['arm-none-eabi-gdb', '-x', str(gdb_cmd_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            with open(output_file, 'w') as f:
                f.write(f"FC Lockup Debug Capture\n")
                f.write(f"Time: {datetime.now().isoformat()}\n")
                f.write(f"MSP code that timed out: {code}\n")
                f.write("="*60 + "\n\n")
                f.write("=== GDB OUTPUT ===\n")
                f.write(gdb_result.stdout)
                f.write("\n=== GDB STDERR ===\n")
                f.write(gdb_result.stderr)
            
            print(f"  ✓ Debug state saved: {output_file}")
            
        except subprocess.TimeoutExpired:
            print("  GDB timed out")
        except FileNotFoundError:
            print("  arm-none-eabi-gdb not found - install ARM toolchain")
        except Exception as e:
            print(f"  GDB error: {e}")
        
        finally:
            try:
                openocd_proc.terminate()
                openocd_proc.wait(timeout=5)
            except:
                openocd_proc.kill()
        
        return True
    
    def send_receive(self, code: int, data: bytes = b'', timeout: float = 1.0) -> Optional[bytes]:
        """
        Send MSP command and receive response.
        
        Args:
            code: MSP command code
            data: Payload data
            timeout: Response timeout in seconds
            
        Returns:
            Response payload bytes, or None on error
        """
        if not self.conn:
            return None
        try:
            _, payload = self.conn.request(code, data, timeout=timeout)
            self._consecutive_timeouts = 0
            return payload
        except Exception as e:
            self._consecutive_timeouts += 1
            print(f"MSP error (code {code}): {e}")
            
            # Check for lockup condition
            if self._consecutive_timeouts >= self._max_consecutive_timeouts:
                if self.debug_on_lockup:
                    self._capture_lockup_state(code)
                    self._consecutive_timeouts = 0
            
            return None
    
    def get_sd_card_status(self) -> Optional[SDCardStatus]:
        """Query SD card status via MSP_SDCARD_SUMMARY"""
        response = self.send_receive(MSPCode.SDCARD_SUMMARY)
        if not response:
            return None
        
        parsed = MSPParse.sd_card_status(response)
        if not parsed:
            return None
        
        from .models import SDCardState
        return SDCardStatus(
            supported=parsed['supported'],
            state=SDCardState(parsed['state']) if parsed['state'] <= 4 else SDCardState.NOT_PRESENT,
            fs_error=parsed['fs_error'],
            free_space_kb=parsed['free_space_kb'],
            total_space_kb=parsed['total_space_kb']
        )
    
    def get_gps_status(self) -> Optional[GPSStatus]:
        """Query GPS status via MSP_RAW_GPS"""
        response = self.send_receive(MSPCode.RAW_GPS)
        if not response:
            return None
        
        parsed = MSPParse.gps_status(response)
        if not parsed:
            return None
        
        from .models import GPSFixType
        return GPSStatus(
            fix_type=GPSFixType(parsed['fix_type']) if parsed['fix_type'] <= 2 else GPSFixType.NO_FIX,
            num_sat=parsed['num_sat'],
            latitude=parsed['latitude'],
            longitude=parsed['longitude'],
            altitude_cm=parsed['altitude_cm'],
            speed_cms=parsed['speed_cms'],
            ground_course=parsed['ground_course'],
            hdop=parsed['hdop']
        )
    
    def get_arming_status(self) -> Optional[ArmingStatus]:
        """Query arming status via MSP2_INAV_STATUS"""
        response = self.send_receive(MSPCode.INAV_STATUS)
        if not response:
            return None
        
        parsed = MSPParse.arming_status(response)
        if not parsed:
            return None
        
        return ArmingStatus(
            cycle_time=parsed['cycle_time'],
            i2c_errors=parsed['i2c_errors'],
            cpu_load=parsed['cpu_load'],
            arming_flags=parsed['arming_flags']
        )
    
    def get_blackbox_config(self) -> Optional[dict]:
        """Query blackbox config via MSP2_BLACKBOX_CONFIG"""
        response = self.send_receive(MSPCode.BLACKBOX_CONFIG)
        return MSPParse.blackbox_config(response)
    
    def send_rc_channels(self, channels: list) -> bool:
        """
        Send RC channels via MSP_SET_RAW_RC.
        
        Args:
            channels: List of channel values (1000-2000)
            
        Returns:
            True if sent successfully
        """
        if not self.conn:
            return False
        
        while len(channels) < 16:
            channels.append(1500)
        
        payload = b''.join(
            b'\x00' + bytes([v & 0xFF, (v >> 8) & 0xFF]) 
            for v in channels[:16]
        )
        
        from .msp import MSPBuilder
        payload = MSPBuilder.set_raw_rc(channels[:16])
        
        try:
            self.conn.send(MSPCode.SET_RAW_RC, payload)
            return True
        except Exception as e:
            print(f"Error sending RC channels: {e}")
            return False
