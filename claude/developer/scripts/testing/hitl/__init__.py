#!/usr/bin/env python3
"""
HITL Testing Utilities for test-engineer agent.

Provides Hardware-In-The-Loop testing capabilities:
- Physical FC connection via serial MSP
- Arming/disarming with FAILSAFE clearing
- Lockup detection and GDB debug capture
- Symbol table lookup for target-specific addresses

Usage:
    from claude.developer.scripts.testing.hitl import HITLConnection, HITLDebugger
    
    with HITLConnection('/dev/ttyACM0', elf_path='build/MATEKF765.elf') as fc:
        fc.wait_for_arming_ready()
        with fc.armed():
            # Run tests while armed
            result = fc.run_test(...)
        
    # Or debug a lockup:
    debugger = HITLDebugger(elf_path='build/MATEKF765.elf')
    debugger.capture_state('debug_captures/lockup.txt')
"""
import os
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class SymbolInfo:
    """Symbol information from ELF"""
    name: str
    address: int
    size: int
    sym_type: str


class SymbolTable:
    """
    Parse and query ELF symbol table.
    
    Used to find correct memory addresses for debugging:
    - Arming flags location
    - Task control blocks
    - DMA registers
    - SD card driver state
    """
    
    def __init__(self, elf_path: str):
        self.elf_path = Path(elf_path)
        self.symbols: Dict[str, SymbolInfo] = {}
        self._loaded = False
    
    def load(self) -> bool:
        """Load symbols from ELF using nm/objdump"""
        if self._loaded:
            return True
        
        if not self.elf_path.exists():
            print(f"ELF file not found: {self.elf_path}")
            return False
        
        try:
            # Use nm to get symbols
            # Output format: address size type name
            result = subprocess.run(
                ['arm-none-eabi-nm', '-S', '-t', 'x', str(self.elf_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            for line in result.stdout.split('\n'):
                parts = line.split()
                if len(parts) >= 4:
                    # Format: address size type name
                    try:
                        addr = int(parts[0], 16)
                        size = int(parts[1], 16)
                        sym_type = parts[2]
                        name = parts[3]
                    except ValueError:
                        # Skip lines that don't match expected format
                        continue
                    
                    self.symbols[name] = SymbolInfo(
                        name=name,
                        address=addr,
                        size=size,
                        sym_type=sym_type
                    )
                elif len(parts) == 3:
                    # Format without size: address type name
                    try:
                        addr = int(parts[0], 16)
                        sym_type = parts[1]
                        name = parts[2]
                    except ValueError:
                        continue
                    
                    self.symbols[name] = SymbolInfo(
                        name=name,
                        address=addr,
                        size=0,
                        sym_type=sym_type
                    )
            
            self._loaded = True
            return True
            
        except Exception as e:
            print(f"Failed to load symbols: {e}")
            return False
    
    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """Look up a symbol by name"""
        if not self._loaded:
            self.load()
        return self.symbols.get(name)
    
    def lookup_pattern(self, pattern: str) -> List[SymbolInfo]:
        """Look up symbols matching a pattern"""
        if not self._loaded:
            self.load()
        
        import fnmatch
        return [s for n, s in self.symbols.items() 
                if fnmatch.fnmatch(n, pattern)]
    
    def get_arming_flags_address(self) -> Optional[int]:
        """Get address of armingFlags variable"""
        # Try common names
        for name in ['armingFlags', 'mwArmingFlags', 'armingDisableFlags']:
            sym = self.lookup(name)
            if sym:
                return sym.address
        
        # Try pattern search
        matches = self.lookup_pattern('*armingFlag*')
        if matches:
            return matches[0].address
        
        return None
    
    def get_current_task_address(self) -> Optional[int]:
        """Get address of current task TCB (FreeRTOS)"""
        for name in ['pxCurrentTCB', 'currentTask', 'xCurrentTask']:
            sym = self.lookup(name)
            if sym:
                return sym.address
        return None
    
    def get_sd_card_state_address(self) -> Optional[int]:
        """Get address of SD card state structure"""
        for name in ['sdCard', 'sdcardState', 'sdCardInfo']:
            sym = self.lookup(name)
            if sym:
                return sym.address
        
        matches = self.lookup_pattern('*sdCard*')
        if matches:
            return matches[0].address
        return None


class HITLDebugger:
    """
    GDB-based debugger for HITL testing.
    
    Captures FC state when lockups occur:
    - Connects via ST-Link/OpenOCD WITHOUT halting
    - Uses symbol table for meaningful variable names
    - Captures registers, backtrace, task state, key variables
    """
    
    # Known addresses for common targets (fallback if no ELF)
    TARGET_ADDRESSES = {
        'MATEKF765': {
            'arming_flags': 0x2001FFF0,  # From debug experience
            'sram_base': 0x20000000,
            'dma1_stream3': 0x40026000,  # SD DMA
        },
        'MATEKF405': {
            'arming_flags': 0x2001FFF0,
            'sram_base': 0x20000000,
            'dma1_stream3': 0x40026000,
        },
    }
    
    def __init__(self, elf_path: Optional[str] = None, 
                 openocd_config: str = 'openocd_matekf765_no_halt.cfg',
                 target_name: str = 'MATEKF765'):
        self.elf_path = elf_path
        self.openocd_config = openocd_config
        self.target_name = target_name
        self.symbols = SymbolTable(elf_path) if elf_path else None
    
    def _build_gdb_commands(self, output_file: str) -> str:
        """Build GDB command file using symbol table"""
        commands = """
set pagination off
set confirm off

target extended-remote :3333
"""
        
        if self.elf_path:
            commands += f"""
file {self.elf_path}
"""
        
        commands += """
echo \\n=== BASIC STATE ===\\n
info registers pc sp lr
echo \\n=== BACKTRACE ===\\n
bt
echo \\n=== FULL BACKTRACE ===\\n
bt full
echo \\n=== DISASSEMBLY AT PC ===\\n
disassemble $pc-16,$pc+16
"""
        
        # Add symbol-aware variable dumps
        if self.symbols and self.symbols.load():
            arming_addr = self.symbols.get_arming_flags_address()
            if arming_addr:
                commands += f"""
echo \\n=== ARMING FLAGS (0x{arming_addr:08X}) ===\\n
x/1x 0x{arming_addr:x}
"""
            
            task_addr = self.symbols.get_current_task_address()
            if task_addr:
                commands += f"""
echo \\n=== CURRENT TASK TCB (0x{task_addr:08X}) ===\\n
x/8x *0x{task_addr:x}
"""
            
            sd_addr = self.symbols.get_sd_card_state_address()
            if sd_addr:
                commands += f"""
echo \\n=== SD CARD STATE (0x{sd_addr:08X}) ===\\n
x/16x 0x{sd_addr:x}
"""
        else:
            # Use fallback addresses
            addrs = self.TARGET_ADDRESSES.get(self.target_name, {})
            if 'arming_flags' in addrs:
                commands += f"""
echo \\n=== ARMING FLAGS (fallback) ===\\n
x/1x 0x{addrs['arming_flags']:08X}
"""
        
        # FreeRTOS task list (heuristic scan)
        commands += """
echo \\n=== FreeRTOS TASK SCAN (SRAM) ===\\n
x/32x 0x20000000
echo \\n=== THREAD INFO ===\\n
info threads
"""
        
        commands += """
quit
"""
        return commands
    
    def capture_state(self, output_file: str) -> bool:
        """
        Capture FC state without halting.
        
        Args:
            output_file: Path to save debug output
            
        Returns:
            True if capture succeeded
        """
        print("  Starting OpenOCD (no halt)...")
        
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
        
            print("  OpenOCD connected, running GDB...")
        
        gdb_commands = self._build_gdb_commands(output_file)
        gdb_cmd_file = Path(output_file).parent / f"gdb_cmd_{os.getpid()}.txt"
        
        with open(gdb_cmd_file, 'w') as f:
            f.write(gdb_commands)
        
        # Try system gdb first (newer), fallback to arm-none-eabi-gdb
        gdb_candidates = ['/usr/bin/gdb', '/usr/local/bin/gdb', 'arm-none-eabi-gdb']
        gdb_path = None
        for gdb in gdb_candidates:
            if Path(gdb).exists() or (not Path(gdb).is_absolute() and subprocess.run(['which', gdb], capture_output=True).returncode == 0):
                gdb_path = gdb
                break
        
        if not gdb_path:
            print("  No GDB found (tried /usr/bin/gdb, arm-none-eabi-gdb)")
            return False
        
        try:
            gdb_result = subprocess.run(
                [gdb_path, '-x', str(gdb_cmd_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            with open(output_file, 'w') as f:
                f.write(f"FC Lockup Debug Capture\n")
                f.write(f"Time: {datetime.now().isoformat()}\n")
                f.write(f"Target: {self.target_name}\n")
                f.write(f"ELF: {self.elf_path or 'Not specified'}\n")
                f.write("="*60 + "\n\n")
                f.write("=== GDB OUTPUT ===\n")
                f.write(gdb_result.stdout)
                f.write("\n=== GDB STDERR ===\n")
                f.write(gdb_result.stderr)
            
            print(f"  ✓ Debug state saved: {output_file}")
            result = True
            
        except subprocess.TimeoutExpired:
            print("  GDB timed out")
            result = False
        except FileNotFoundError:
            print(f"  {gdb_path} not found")
            result = False
        except Exception as e:
            print(f"  GDB error: {e}")
            result = False
        finally:
            gdb_cmd_file.unlink(missing_ok=True)
            try:
                openocd_proc.terminate()
                openocd_proc.wait(timeout=5)
            except:
                openocd_proc.kill()
        
        return result


class HITLConnection:
    """
    Hardware-In-The-Loop connection to physical FC.
    
    Provides:
    - MSP communication via serial
    - Arming with FAILSAFE clearing
    - Context manager for auto-cleanup
    - Lockup detection with debug capture
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
    
    def __init__(self, port: str, elf_path: Optional[str] = None,
                 openocd_config: str = 'openocd_matekf765_no_halt.cfg',
                 debug_on_lockup: bool = True):
        self.port = port
        self.elf_path = elf_path
        self.openocd_config = openocd_config
        self.debug_on_lockup = debug_on_lockup
        
        self._serial = None
        self._consecutive_timeouts = 0
        self._max_timeouts = 3
        self._armed = False
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._armed:
            self.disarm()
        self.disconnect()
        return False
    
    def connect(self) -> bool:
        """Connect to FC via serial"""
        try:
            import serial
            self._serial = serial.Serial(self.port, 115200, timeout=0.5)
            self._consecutive_timeouts = 0
            print(f"  Connected to {self.port}")
            return True
        except Exception as e:
            print(f"  Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from FC"""
        if self._serial:
            try:
                self._serial.close()
            except:
                pass
            self._serial = None
    
    def _send_msp(self, code: int, data: bytes = b'') -> Optional[bytes]:
        """Send MSP command and get response"""
        if not self._serial:
            return None
        
        # Build MSP v1 request
        length = len(data)
        checksum = (length ^ code) & 0xFF
        for b in data:
            checksum ^= b
        
        request = bytes([ord('$'), ord('M'), ord('<'), length, code]) + data + bytes([checksum])
        
        try:
            self._serial.reset_input_buffer()
            self._serial.write(request)
            
            # Read response with timeout
            start = time.time()
            response = b''
            while time.time() - start < 1.0:
                chunk = self._serial.read(256)
                if chunk:
                    response += chunk
                    if b'$M>' in response or b'$M!' in response:
                        break
            
            if b'$M!' in response:
                # Error response
                self._consecutive_timeouts += 1
                return None
            
            if b'$M>' in response and len(response) >= 6:
                # Parse successful response
                self._consecutive_timeouts = 0
                idx = response.index(b'$M>')
                return response[idx+5:idx+5+response[idx+3]]  # Payload
            
            self._consecutive_timeouts += 1
            return None
            
        except Exception as e:
            self._consecutive_timeouts += 1
            return None
    
    def _check_lockup(self):
        """Check for lockup and capture debug state if needed"""
        if self._consecutive_timeouts >= self._max_timeouts:
            if self.debug_on_lockup:
                print(f"\n  ⚠ {self._consecutive_timeouts} MSP timeouts - capturing debug state...")
                debugger = HITLDebugger(self.elf_path, self.openocd_config)
                debugger.capture_state(f"debug_captures/lockup_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt")
                self._consecutive_timeouts = 0
    
    def send_rc_channels(self, channels: List[int]) -> bool:
        """Send RC channels (MSP_SET_RAW_RC, code 200)"""
        # Build payload: 16 channels, 2 bytes each
        payload = b''.join(
            bytes([ch & 0xFF, (ch >> 8) & 0xFF])
            for ch in (channels + [1500] * 16)[:16]
        )
        result = self._send_msp(200, payload)
        if result is None:
            self._check_lockup()
        return result is not None
    
    def get_arming_status(self) -> Optional[int]:
        """Get arming flags (MSP2_INAV_STATUS, code 0x2000)"""
        result = self._send_msp(0x2000 & 0xFF, b'')  # MSP v1 encoding for v2
        if result is None:
            self._check_lockup()
            return None
        
        # Parse arming flags from response
        if len(result) >= 13:
            import struct
            flags = struct.unpack('<I', result[9:13])[0]
            return flags
        return None
    
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
        """
        Clear FAILSAFE by sending RC commands.
        
        FC with MSP RX needs continuous RC to clear FAILSAFE flag.
        """
        print(f"  Clearing FAILSAFE ({duration_sec:.1f}s)...")
        
        channels = [1500] * 16
        channels[2] = 1000  # Throttle LOW
        channels[4] = 1000  # Arm LOW
        
        start = time.time()
        while time.time() - start < duration_sec:
            self.send_rc_channels(channels)
            time.sleep(0.02)  # 50Hz
    
    def wait_for_arming_ready(self, timeout: float = 30.0) -> Tuple[bool, str]:
        """
        Wait until FC is ready to arm.
        
        Sends RC commands to clear blockers (FAILSAFE, ARM_SWITCH, etc.)
        """
        # First clear FAILSAFE
        self.clear_failsafe()
        
        start = time.time()
        last_blockers = []
        
        # Keep sending RC while checking status
        rc_channels = [1500] * 16
        rc_channels[2] = 1000
        rc_channels[4] = 1000
        
        while time.time() - start < timeout:
            self.send_rc_channels(rc_channels)
            time.sleep(0.02)
            
            can, blockers = self.can_arm()
            
            if blockers != last_blockers:
                if blockers:
                    print(f"  Waiting: {', '.join(blockers)}")
                last_blockers = blockers
            
            if can:
                return True, "Ready to arm"
        
        return False, f"Timeout: {', '.join(blockers)}"
    
    def arm(self, timeout: float = 5.0) -> bool:
        """Arm the FC"""
        if self.is_armed():
            return True
        
        # Send arm HIGH
        channels = [1500] * 16
        channels[2] = 1000
        channels[4] = 2000  # Arm HIGH
        
        start = time.time()
        while time.time() - start < timeout:
            self.send_rc_channels(channels)
            time.sleep(0.02)
            
            if self.is_armed():
                print("  ✓ ARMED")
                self._armed = True
                return True
        
        print("  ✗ Failed to arm")
        return False
    
    def disarm(self, timeout: float = 3.0) -> bool:
        """Disarm the FC"""
        channels = [1500] * 16
        channels[2] = 1000
        channels[4] = 1000  # Arm LOW
        
        start = time.time()
        while time.time() - start < timeout:
            self.send_rc_channels(channels)
            time.sleep(0.02)
            
            if not self.is_armed():
                print("  ✓ Disarmed")
                self._armed = False
                return True
        
        self._armed = False
        return True
    
    @contextmanager
    def armed(self, timeout: float = 30.0):
        """Context manager for armed operations"""
        ready, msg = self.wait_for_arming_ready(timeout)
        if not ready:
            yield False
            return
        
        if not self.arm():
            yield False
            return
        
        try:
            yield True
        finally:
            self.disarm()


def check_cdc_device(port: str) -> bool:
    """Check if CDC serial device exists"""
    return os.path.exists(port)


def check_msc_device() -> bool:
    """Check if FC is in MSC mode (USB mass storage)"""
    for device in ['/dev/sdb', '/dev/sdb1', '/dev/sdc', '/dev/sdc1']:
        if os.path.exists(device):
            return True
    return False


def main():
    """Test HITL connection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HITL Testing Utilities")
    parser.add_argument('--port', default='/dev/ttyACM0', help='Serial port')
    parser.add_argument('--elf', help='ELF file for symbols')
    parser.add_argument('--test', choices=['connect', 'arm', 'symbols'], default='connect')
    args = parser.parse_args()
    
    if args.test == 'symbols':
        if not args.elf:
            print("Need --elf for symbol test")
            return 1
        
        sym = SymbolTable(args.elf)
        if sym.load():
            print(f"Loaded {len(sym.symbols)} symbols")
            
            arming = sym.get_arming_flags_address()
            print(f"Arming flags: 0x{arming:08X}" if arming else "Arming flags: not found")
            
            task = sym.get_current_task_address()
            print(f"Current task: 0x{task:08X}" if task else "Current task: not found")
            
            sd = sym.get_sd_card_state_address()
            print(f"SD card state: 0x{sd:08X}" if sd else "SD card state: not found")
        return 0
    
    with HITLConnection(args.port, elf_path=args.elf) as fc:
        if args.test == 'connect':
            flags = fc.get_arming_status()
            if flags is not None:
                print(f"Arming flags: 0x{flags:08X}")
                reasons = fc.decode_arming_flags(flags)
                print(f"Decoded: {reasons}")
            else:
                print("Failed to get arming status")
        
        elif args.test == 'arm':
            with fc.armed() as armed:
                if armed:
                    print("Running while armed...")
                    time.sleep(5)
                else:
                    print("Failed to arm")


if __name__ == '__main__':
    import sys
    sys.exit(main())