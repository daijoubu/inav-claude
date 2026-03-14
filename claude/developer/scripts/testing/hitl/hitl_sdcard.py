#!/usr/bin/env python3
"""
HITL SD Card Testing - Enhanced Hardware-In-The-Loop capabilities for SD card validation.

Extends the base HITL framework with:
- Fault injection (DMA errors, timeouts, CRC errors)
- State introspection (SD card state machine, DMA registers)
- Symbol-based debugging for SD card driver internals

Integration with sd_card_test.py:
    from claude.developer.scripts.testing.hitl.hitl_sdcard import HITLSDCard
    
    hitl = HITLSDCard('/dev/ttyACM0', elf_path='build/MATEKF765.elf')
    
    # Introspection: read SD card state
    state = hitl.get_sdcard_state()
    print(f"SD state: {state['state']}, errors: {state['consecutive_errors']}")
    
    # Fault injection: simulate DMA error
    hitl.inject_dma_error()
    
    # Fault injection: force SD card reset
    hitl.force_sdcard_reset()
"""
import os
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import from parent module (avoid circular import)
import sys
sys.path.insert(0, str(Path(__file__).parent))
from __init__ import HITLConnection, HITLDebugger, SymbolTable, SymbolInfo


@dataclass
class SDCardState:
    """SD card driver state from memory introspection."""
    state: int = 0
    state_name: str = "UNKNOWN"
    consecutive_errors: int = 0
    operation_in_progress: bool = False
    dma_busy: bool = False
    last_operation_ms: int = 0
    total_writes: int = 0
    total_reads: int = 0
    write_errors: int = 0
    read_errors: int = 0
    
    STATE_NAMES = {
        0: "NOT_PRESENT",
        1: "RESET",
        2: "CARD_INIT_IN_PROGRESS",
        3: "INITIALIZATION_RECEIVE_CID",
        4: "READY",
        5: "READING",
        6: "SENDING_WRITE",
        7: "WAITING_FOR_WRITE",
        8: "WRITING_MULTIPLE_BLOCKS",
        9: "STOPPING_MULTIPLE_BLOCK_WRITE",
    }
    
    def __post_init__(self):
        self.state_name = self.STATE_NAMES.get(self.state, f"UNKNOWN({self.state})")
    
    @classmethod
    def from_memory(cls, base_addr: int, raw_data: bytes) -> 'SDCardState':
        """
        Parse SD card state from raw memory dump.
        
        sdcard_t struct layout (verified against sdcard_impl.h):
        - offset 0x1C: failureCount (uint8_t)
        - offset 0x1D: operationRetries (uint8_t)
        - offset 0x24: multiWriteNextBlock (uint32_t)
        - offset 0x28: multiWriteBlocksRemain (uint32_t)
        - offset 0x2C: state (sdcardState_e, uint32_t enum)
        """
        import struct
        
        state = cls()
        
        if len(raw_data) >= 0x30:
            state.state = struct.unpack('<I', raw_data[0x2C:0x30])[0]
            state.consecutive_errors = raw_data[0x1C]
            # Need to set state_name since __post_init__ was called with default values
            state.state_name = cls.STATE_NAMES.get(state.state, f"UNKNOWN({state.state})")
        
        return state


@dataclass
class AFATFSState:
    """AFATFS filesystem state from memory introspection."""
    filesystem_state: int = 0
    filesystem_state_name: str = "UNKNOWN"
    last_error: int = 0
    last_error_name: str = "NONE"
    
    FILESYSTEM_STATE_NAMES = {
        0: "UNKNOWN",
        1: "FATAL",
        2: "INITIALIZATION",
        3: "READY",
    }
    
    ERROR_NAMES = {
        0: "NONE",
        1: "GENERIC",
        2: "BAD_MBR",
        3: "BAD_FILESYSTEM_HEADER",
    }
    
    def __post_init__(self):
        self.filesystem_state_name = self.FILESYSTEM_STATE_NAMES.get(
            self.filesystem_state, f"UNKNOWN({self.filesystem_state})"
        )
        self.last_error_name = self.ERROR_NAMES.get(
            self.last_error, f"ERROR({self.last_error})"
        )
    
    @classmethod
    def from_memory(cls, base_addr: int, raw_data: bytes) -> 'AFATFSState':
        """
        Parse AFATFS state from raw memory dump.
        
        afatfs_t struct layout:
        - offset 0x01: filesystemState (afatfsFilesystemState_e, uint8_t)
        - offset 0x11b4: lastError (afatfsError_e, uint32_t)
        """
        state = cls()
        
        if len(raw_data) >= 0x02:
            state.filesystem_state = raw_data[0x01]
        
        if len(raw_data) >= 0x11b8:
            import struct
            state.last_error = struct.unpack('<I', raw_data[0x11b4:0x11b8])[0]
        
        return state


@dataclass
class DMAState:
    """DMA channel state for SDIO."""
    stream: int = 0
    busy: bool = False
    direction: str = "IDLE"  # READ, WRITE, IDLE
    error_flags: int = 0
    transfer_complete: bool = False
    buffer_address: int = 0
    transfer_size: int = 0


@dataclass
class FaultInjectionResult:
    """Result of fault injection operation."""
    success: bool
    fault_type: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class HITLSDCardSymbols:
    """
    SD card-specific symbol lookups for HITL testing.
    
    Provides addresses for SD card driver state, DMA registers,
    and error counters for introspection and fault injection.
    """
    
    def __init__(self, symbol_table: SymbolTable):
        self.symbols = symbol_table
        self._sdcard_state_addr: Optional[int] = None
        self._sdcard_instance_addr: Optional[int] = None
        self._dma_registers_addr: Optional[int] = None
    
    def get_sdcard_state_address(self) -> Optional[int]:
        """Get address of sdcard.state (embedded in sdcard struct)."""
        if self._sdcard_state_addr:
            return self._sdcard_state_addr
        
        # First try to find separate symbol
        names = [
            'sdcardState',
            'sdCardState',
            'sdCard.state',
            'sdcard_state',
        ]
        
        for name in names:
            sym = self.symbols.lookup(name)
            if sym:
                self._sdcard_state_addr = sym.address
                return sym.address
        
        matches = self.symbols.lookup_pattern('*sdcard*State*')
        if matches:
            self._sdcard_state_addr = matches[0].address
            return matches[0].address
        
        # Fall back: use sdcard instance + offset (state is at offset 0x2C)
        instance_addr = self.get_sdcard_instance_address()
        if instance_addr:
            self._sdcard_state_addr = instance_addr + 0x2C
            return self._sdcard_state_addr
        
        return None
    
    def get_sdcard_instance_address(self) -> Optional[int]:
        """Get address of sdCard instance structure."""
        if self._sdcard_instance_addr:
            return self._sdcard_instance_addr
        
        names = [
            'sdCard',
            'sdcard',
            'sdCardInfo',
            'sdioDevice',
        ]
        
        for name in names:
            sym = self.symbols.lookup(name)
            if sym:
                self._sdcard_instance_addr = sym.address
                return sym.address
        
        matches = self.symbols.lookup_pattern('*sdCard*')
        if matches:
            for m in matches:
                if 'instance' in m.name.lower() or m.sym_type in ('B', 'b', 'D', 'd'):
                    self._sdcard_instance_addr = m.address
                    return m.address
            self._sdcard_instance_addr = matches[0].address
            return matches[0].address
        
        return None
    
    def get_sdio_dma_registers(self) -> Dict[str, int]:
        """Get SDIO DMA register addresses (STM32F7 specific)."""
        return {
            'DMA2_Stream3': 0x40026000,  # Common SDIO DMA on F7
            'DMA2_Stream6': 0x40026400,  # Alternate SDIO DMA
            'SDMMC1': 0x40012C00,        # SDMMC1 peripheral
            'SDMMC2': 0x40013C00,        # SDMMC2 peripheral
        }
    
    def get_error_counter_addresses(self) -> Dict[str, Optional[int]]:
        """Get addresses of SD card error counters."""
        counters = {}
        
        # The actual field is 'failureCount' in sdcard struct (offset 0x1C)
        # Try to find it via the sdcard instance + offset
        instance_addr = self.get_sdcard_instance_address()
        if instance_addr:
            counters['failureCount'] = instance_addr + 0x1C
            counters['consecutive_errors'] = instance_addr + 0x1C
            counters['operationRetries'] = instance_addr + 0x1D
        
        return counters
    
    def get_hal_sd_handle_address(self) -> Optional[int]:
        """Get address of SD HAL handle (hsd)."""
        names = ['hsd', 'SDHandle', 'hsd_handle']
        for name in names:
            sym = self.symbols.lookup(name)
            if sym:
                return sym.address
        return None
    
    def get_afatfs_address(self) -> Optional[int]:
        """Get address of afatfs global variable."""
        sym = self.symbols.lookup('afatfs')
        if sym:
            return sym.address
        return None
    
    def get_sdcard_metadata_address(self) -> Optional[int]:
        """Get address of sdcard metadata via sdcard_getMetadata function."""
        sym = self.symbols.lookup('sdcard_getMetadata')
        if sym:
            return sym.address
        return None


class HITLSDCard:
    """
    Enhanced HITL testing for SD card operations.
    
    Combines MSP communication with GDB-based introspection and fault injection.
    """
    
    def __init__(self, port: str, elf_path: str, 
                 openocd_config: str = 'openocd_matekf765_no_halt.cfg',
                 verbose: bool = True):
        self.port = port
        self.elf_path = elf_path
        self.openocd_config = openocd_config
        self.verbose = verbose
        
        self.connection = HITLConnection(port, elf_path, openocd_config)
        self.symbol_table = SymbolTable(elf_path)
        self.sd_symbols = HITLSDCardSymbols(self.symbol_table)
        self.debugger = HITLDebugger(elf_path, openocd_config)
        
        self._symbols_loaded = False
        self._last_gdb_output = None  # For debugging
    
    def load_symbols(self) -> bool:
        """Load symbols from ELF file."""
        if self._symbols_loaded:
            return True
        
        if self.symbol_table.load():
            self._symbols_loaded = True
            return True
        return False
    
    def connect(self) -> bool:
        """Connect to FC."""
        return self.connection.connect()
    
    def disconnect(self):
        """Disconnect from FC."""
        self.connection.disconnect()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
    
    # =========================================================================
    # State Introspection
    # =========================================================================
    
    def _run_gdb_command(self, commands: str, timeout: float = 10.0) -> Optional[str]:
        """Run GDB command and return output."""
        gdb_cmd_file = Path(f"/tmp/hitl_gdb_{os.getpid()}.cmd")
        
        full_commands = f"""
set pagination off
set confirm off
target extended-remote :3333
file {self.elf_path}
{commands}
quit
"""
        
        with open(gdb_cmd_file, 'w') as f:
            f.write(full_commands)
        
        # Try system gdb first (newer), fallback to arm-none-eabi-gdb
        gdb_candidates = ['/usr/bin/gdb', '/usr/local/bin/gdb', 'arm-none-eabi-gdb']
        gdb_path = None
        for gdb in gdb_candidates:
            if Path(gdb).exists() or (not Path(gdb).is_absolute() and subprocess.run(['which', gdb], capture_output=True).returncode == 0):
                gdb_path = gdb
                break
        
        if not gdb_path:
            if self.verbose:
                print(f"[HITL] No GDB found in {gdb_candidates}")
            return None
        
        try:
            result = subprocess.run(
                [gdb_path, '-x', str(gdb_cmd_file)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            gdb_cmd_file.unlink(missing_ok=True)
            
            # Store last output for debugging
            self._last_gdb_output = result.stdout
            
            if result.returncode != 0 and self.verbose:
                print(f"[HITL] GDB error: {result.stderr[:200]}")
            
            return result.stdout
        except subprocess.TimeoutExpired:
            if self.verbose:
                print(f"[HITL] GDB timeout after {timeout}s")
            gdb_cmd_file.unlink(missing_ok=True)
            return None
        except Exception as e:
            if self.verbose:
                print(f"[HITL] GDB exception: {e}")
            gdb_cmd_file.unlink(missing_ok=True)
            return None
    
    def get_sdcard_state(self) -> Optional[SDCardState]:
        """
        Read SD card state from FC memory via GDB.
        
        Returns SDCardState with current driver state, error counts, etc.
        """
        if not self.load_symbols():
            if self.verbose:
                print("[HITL] Failed to load symbols for SD card state")
            return None
        
        instance_addr = self.sd_symbols.get_sdcard_instance_address()
        
        if not instance_addr:
            if self.verbose:
                print("[HITL] Could not find sdcard instance address")
                # Try to show what symbols were found
                self.symbol_table.load()
                matches = self.symbol_table.lookup_pattern('*sd*')
                if matches:
                    print(f"[HITL] Found {len(matches)} SD-related symbols:")
                    for m in matches[:5]:
                        print(f"  - {m.name} at 0x{m.address:x}")
            return None
        
        if self.verbose:
            print(f"[HITL] Reading SD card state from 0x{instance_addr:x}")
        
        output = self._run_gdb_command(f"""
echo \\n=== SD CARD STATE ===\\n
x/16x 0x{instance_addr:x}
""")
        
        if not output:
            if self.verbose:
                print("[HITL] No GDB output for SD card state")
            return None
        
        return self._parse_sdcard_state(output, instance_addr)
    
    def _parse_sdcard_state(self, gdb_output: str, base_addr: int) -> SDCardState:
        """
        Parse GDB output to extract SD card state.
        
        GDB output format: "0x200273bc <sdcard>: 0x09000000 0x00040000 ..."
        
        Struct layout (verified against sdcard_impl.h):
        - offset 0x1C: failureCount (uint8_t)
        - offset 0x1D: operationRetries (uint8_t)
        - offset 0x24: multiWriteNextBlock (uint32_t)
        - offset 0x28: multiWriteBlocksRemain (uint32_t)
        - offset 0x2C: state (sdcardState_e, uint32_t)
        """
        raw_bytes = bytearray(64)
        
        lines = gdb_output.split('\n')
        for line in lines:
            # Parse address from line like "0x200273bc <sdcard>:"
            if '0x' in line and '<' in line and ':' in line:
                try:
                    addr_part = line.split('<')[0].strip()
                    addr = int(addr_part, 16)
                    offset = addr - base_addr
                    
                    # Get the hex values after the colon
                    parts = line.split(':')
                    if len(parts) >= 2:
                        hex_values = parts[1].strip().split()
                        for i, hex_val in enumerate(hex_values[:8]):
                            byte_offset = offset + (i * 4)
                            if byte_offset + 4 <= len(raw_bytes):
                                val = int(hex_val, 16)
                                raw_bytes[byte_offset] = val & 0xFF
                                raw_bytes[byte_offset + 1] = (val >> 8) & 0xFF
                                raw_bytes[byte_offset + 2] = (val >> 16) & 0xFF
                                raw_bytes[byte_offset + 3] = (val >> 24) & 0xFF
                except (ValueError, IndexError):
                    pass
        
        return SDCardState.from_memory(base_addr, bytes(raw_bytes))
    
    def get_dma_state(self) -> Optional[DMAState]:
        """
        Read DMA channel state for SDIO.
        
        Returns DMAState with current DMA status.
        """
        dma_addrs = self.sd_symbols.get_sdio_dma_registers()
        
        output = self._run_gdb_command(f"""
echo \\n=== SDIO DMA STATE ===\\n
x/8x 0x{dma_addrs['DMA2_Stream3']:x}
echo \\n=== SDMMC1 ===\\n
x/8x 0x{dma_addrs['SDMMC1']:x}
""")
        
        if not output:
            return None
        
        return self._parse_dma_state(output)
    
    def _parse_dma_state(self, gdb_output: str) -> DMAState:
        """Parse GDB output to extract DMA state."""
        dma = DMAState()
        
        lines = gdb_output.split('\n')
        for line in lines:
            if 'DMA2_Stream3' in line or '0x40026000' in line:
                dma.stream = 3
            if ':' in line and '0x' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    try:
                        values = parts[1].strip().split()
                        if values:
                            cr = int(values[0], 16)
                            dma.busy = bool(cr & 0x01)
                    except (ValueError, IndexError):
                        pass
        
        return dma
    
    def get_error_counters(self) -> Dict[str, int]:
        """
        Read SD card error counters from memory.
        
        Returns dict with error counts.
        """
        if not self.load_symbols():
            return {}
        
        counter_addrs = self.sd_symbols.get_error_counter_addresses()
        results = {}
        
        for name, addr in counter_addrs.items():
            if addr:
                output = self._run_gdb_command(f"x/1x 0x{addr:x}")
                if output:
                    try:
                        for line in output.split('\n'):
                            if ':' in line:
                                val = line.split(':')[1].strip().split()[0]
                                results[name] = int(val, 16)
                                break
                    except (ValueError, IndexError):
                        pass
        
        return results
    
    def get_afatfs_state(self) -> Optional[AFATFSState]:
        """
        Read AFATFS filesystem state from FC memory via GDB.
        
        Returns AFATFSState with filesystem state and last error.
        
        Note: On targets without SD card detect pin (like MATEKF765SE),
        sdcard_isInserted() always returns true, so the MSP state
        combines sdcard state + afatfs state.
        """
        if not self.load_symbols():
            return None
        
        afatfs_addr = self.sd_symbols.get_afatfs_address()
        if not afatfs_addr:
            return None
        
        output = self._run_gdb_command(f"""
echo \\n=== AFATFS STATE ===\\n
x/4x 0x{afatfs_addr:x}
""")
        
        if not output:
            return None
        
        return self._parse_afatfs_state(output, afatfs_addr)
    
    def _parse_afatfs_state(self, gdb_output: str, base_addr: int) -> AFATFSState:
        """
        Parse GDB output to extract AFATFS state.
        
        afatfs_t struct layout:
        - offset 0x01: filesystemState (afatfsFilesystemState_e, uint8_t)
        - offset 0x11b4: lastError (afatfsError_e, uint32_t)
        """
        raw_bytes = bytearray(4644)
        
        lines = gdb_output.split('\n')
        for line in lines:
            # Parse address from line
            if '0x' in line and '<' in line and ':' in line:
                try:
                    addr_part = line.split('<')[0].strip()
                    addr = int(addr_part, 16)
                    offset = addr - base_addr
                    
                    # Get the hex values after the colon
                    parts = line.split(':')
                    if len(parts) >= 2:
                        hex_values = parts[1].strip().split()
                        for i, hex_val in enumerate(hex_values[:4]):
                            byte_offset = offset + (i * 4)
                            if byte_offset + 4 <= len(raw_bytes):
                                val = int(hex_val, 16)
                                raw_bytes[byte_offset] = val & 0xFF
                                raw_bytes[byte_offset + 1] = (val >> 8) & 0xFF
                                raw_bytes[byte_offset + 2] = (val >> 16) & 0xFF
                                raw_bytes[byte_offset + 3] = (val >> 24) & 0xFF
                except (ValueError, IndexError):
                    pass
        
        return AFATFSState.from_memory(base_addr, bytes(raw_bytes))
    
    def get_msp_comparable_state(self) -> Optional[Dict]:
        """
        Get SD card state that can be compared to MSP_SDCARD_SUMMARY response.
        
        MSP_SDCARD_SUMMARY returns:
        - flags (0x01 = supported)
        - state: combines sdcard_isInserted() + sdcard_isFunctional() + afatfs state
        - fs_error: afatfs_getLastError()
        - free_space_kb: afatfs_getContiguousFreeSpace() / 1024
        - total_space_kb: sdcard_getMetadata()->numBlocks / 2
        
        Returns dict with all values needed for comparison.
        """
        if not self.load_symbols():
            return None
        
        sdcard_state = self.get_sdcard_state()
        afatfs_state = self.get_afatfs_state()
        
        result = {
            'sdcard_state': sdcard_state,
            'afatfs_state': afatfs_state,
            'notes': []
        }
        
        if not self.sd_symbols.get_sdcard_instance_address():
            result['notes'].append('sdcard instance not found - verify symbols')
        
        return result
    
    # =========================================================================
    # Fault Injection
    # =========================================================================
    
    def inject_dma_error(self) -> FaultInjectionResult:
        """
        Inject a DMA transfer error by setting error flags.
        
        This simulates the F765 lockup scenario where DMA errors
        cause the SD card driver to enter a blocking reset loop.
        """
        dma_addrs = self.sd_symbols.get_sdio_dma_registers()
        
        DMA_LISR = dma_addrs['DMA2_Stream3'] + 0x00  # Low interrupt status
        DMA_HISR = dma_addrs['DMA2_Stream3'] + 0x04  # High interrupt status
        
        TEIF3 = 0x00000008  # Transfer error interrupt flag for stream 3
        
        if self.verbose:
            print(f"[HITL] Injecting DMA error at 0x{DMA_HISR:x}")
        
        output = self._run_gdb_command(f"""
echo \\n=== INJECTING DMA ERROR ===\\n
set *(unsigned int *)0x{DMA_HISR:x} = 0x{TEIF3:x}
echo DMA error flag set\\n
x/1x 0x{DMA_HISR:x}
""")
        
        if not output:
            return FaultInjectionResult(
                success=False,
                fault_type="DMA_TRANSFER_ERROR",
                message="GDB command failed"
            )
        
        if 'error flag set' in output:
            return FaultInjectionResult(
                success=True,
                fault_type="DMA_TRANSFER_ERROR",
                message="DMA TEIF3 flag set on Stream 3"
            )
        
        return FaultInjectionResult(
            success=False,
            fault_type="DMA_TRANSFER_ERROR",
            message=f"Failed to inject DMA error (output: {output[:100]})"
        )
    
    def inject_sd_timeout(self) -> FaultInjectionResult:
        """
        Inject SD card timeout by corrupting timeout counter.
        
        Forces the SD card driver to think a timeout occurred.
        """
        if not self.load_symbols():
            return FaultInjectionResult(
                success=False,
                fault_type="SD_TIMEOUT",
                message="Symbols not loaded"
            )
        
        hal_handle_addr = self.sd_symbols.get_hal_sd_handle_address()
        if not hal_handle_addr:
            return FaultInjectionResult(
                success=False,
                fault_type="SD_TIMEOUT",
                message="HAL SD handle not found"
            )
        
        output = self._run_gdb_command(f"""
echo \\n=== INJECTING SD TIMEOUT ===\\n
set *(unsigned int *)0x{hal_handle_addr + 0x20:x} = 0xFFFFFFFF
echo Timeout counter set to max\\n
""")
        
        if output:
            return FaultInjectionResult(
                success=True,
                fault_type="SD_TIMEOUT",
                message="SD timeout counter set to max value"
            )
        return FaultInjectionResult(
            success=False,
            fault_type="SD_TIMEOUT",
            message="Failed to inject timeout"
        )
    
    def inject_crc_error(self) -> FaultInjectionResult:
        """
        Inject CRC error in SD card response.
        
        Sets the CRC fail flag in the SDMMC status register.
        """
        dma_addrs = self.sd_symbols.get_sdio_dma_registers()
        sdmmc_sta = dma_addrs['SDMMC1'] + 0x34  # SDMMC_STA register
        
        DCRCFAIL = 0x00000002  # Data CRC fail flag
        
        if self.verbose:
            print(f"[HITL] Injecting CRC error at SDMMC STA 0x{sdmmc_sta:x}")
        
        output = self._run_gdb_command(f"""
echo \\n=== INJECTING CRC ERROR ===\\n
set *(unsigned int *)0x{sdmmc_sta:x} |= 0x{DCRCFAIL:x}
echo CRC fail flag set\\n
x/1x 0x{sdmmc_sta:x}
""")
        
        if not output:
            return FaultInjectionResult(
                success=False,
                fault_type="SD_CRC_ERROR",
                message="GDB command failed"
            )
        
        if 'CRC fail' in output:
            return FaultInjectionResult(
                success=True,
                fault_type="SD_CRC_ERROR",
                message="SDMMC DCRCFAIL flag set"
            )
        
        return FaultInjectionResult(
            success=False,
            fault_type="SD_CRC_ERROR",
            message=f"Failed to inject CRC error (output: {output[:100]})"
        )
    
    def force_sdcard_reset(self) -> FaultInjectionResult:
        """
        Force SD card into RESET state to test recovery.
        
        Sets sdcardState to SDCARD_STATE_RESET (1) which triggers
        reinitialization on next poll.
        """
        if not self.load_symbols():
            return FaultInjectionResult(
                success=False,
                fault_type="SD_RESET",
                message="Symbols not loaded"
            )
        
        state_addr = self.sd_symbols.get_sdcard_state_address()
        if not state_addr:
            return FaultInjectionResult(
                success=False,
                fault_type="SD_RESET",
                message="SD state address not found"
            )
        
        output = self._run_gdb_command(f"""
echo \\n=== FORCING SD RESET ===\\n
set *(unsigned int *)0x{state_addr:x} = 1
echo SD state set to RESET\\n
x/1x 0x{state_addr:x}
""")
        
        if output:
            return FaultInjectionResult(
                success=True,
                fault_type="SD_RESET",
                message="SD card state forced to RESET"
            )
        return FaultInjectionResult(
            success=False,
            fault_type="SD_RESET",
            message="Failed to force reset"
        )
    
    def inject_consecutive_failures(self, count: int = 8) -> FaultInjectionResult:
        """
        Inject consecutive failure count to trigger card reset.
        
        After SDCARD_MAX_CONSECUTIVE_FAILURES (8), the driver
        marks the card as NOT_PRESENT.
        """
        if not self.load_symbols():
            return FaultInjectionResult(
                success=False,
                fault_type="CONSECUTIVE_FAILURES",
                message="Symbols not loaded"
            )
        
        counter_addrs = self.sd_symbols.get_error_counter_addresses()
        
        if 'consecutive_errors' in counter_addrs:
            addr = counter_addrs['consecutive_errors']
        else:
            return FaultInjectionResult(
                success=False,
                fault_type="CONSECUTIVE_FAILURES",
                message="Consecutive error counter not found"
            )
        
        if self.verbose:
            print(f"[HITL] Injecting {count} consecutive failures at 0x{addr:x}")
        
        output = self._run_gdb_command(f"""
echo \\n=== INJECTING CONSECUTIVE FAILURES ===\\n
set *(unsigned char *)0x{addr:x} = {count}
echo Consecutive errors set to {count}\\n
x/1b 0x{addr:x}
""")
        
        if not output:
            return FaultInjectionResult(
                success=False,
                fault_type="CONSECUTIVE_FAILURES",
                message="GDB command failed"
            )
        
        # Verify the value was set
        try:
            for line in output.split('\n'):
                if '0x' in line and ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        val_str = parts[1].strip().split()[0]
                        actual_val = int(val_str, 16)
                        if actual_val == count:
                            return FaultInjectionResult(
                                success=True,
                                fault_type="CONSECUTIVE_FAILURES",
                                message=f"Consecutive failure count set to {count}"
                            )
        except (ValueError, IndexError):
            pass
        
        return FaultInjectionResult(
            success=False,
            fault_type="CONSECUTIVE_FAILURES",
            message=f"Failed to verify injection (output: {output[:100]})"
        )
    
    # =========================================================================
    # Capture and Debug
    # =========================================================================
    
    def capture_full_state(self, output_file: str) -> bool:
        """
        Capture complete SD card and DMA state for debugging.
        
        Saves state to file for offline analysis.
        """
        if not self.load_symbols():
            return False
        
        state_addr = self.sd_symbols.get_sdcard_state_address()
        instance_addr = self.sd_symbols.get_sdcard_instance_address()
        dma_addrs = self.sd_symbols.get_sdio_dma_registers()
        counter_addrs = self.sd_symbols.get_error_counter_addresses()
        
        commands = """
echo \\n=== TIMESTAMP ===\\n
shell date
"""
        
        if state_addr:
            commands += f"""
echo \\n=== SD CARD STATE ===\\n
x/16x 0x{state_addr:x}
"""
        
        if instance_addr:
            commands += f"""
echo \\n=== SD CARD INSTANCE ===\\n
x/32x 0x{instance_addr:x}
"""
        
        commands += f"""
echo \\n=== DMA2 STREAM3 (SDIO) ===\\n
x/16x 0x{dma_addrs['DMA2_Stream3']:x}

echo \\n=== SDMMC1 PERIPHERAL ===\\n
x/32x 0x{dma_addrs['SDMMC1']:x}
"""
        
        for name, addr in counter_addrs.items():
            if addr:
                commands += f"""
echo \\n=== {name.upper()} ===\\n
x/1x 0x{addr:x}
"""
        
        output = self._run_gdb_command(commands)
        
        if output:
            with open(output_file, 'w') as f:
                f.write(f"HITL SD Card State Capture\n")
                f.write(f"Time: {datetime.now().isoformat()}\n")
                f.write(f"ELF: {self.elf_path}\n")
                f.write("=" * 60 + "\n\n")
                f.write(output)
            return True
        
        return False
    
    # =========================================================================
    # Convenience Methods
    # =========================================================================
    
    def arm(self, timeout: float = 5.0) -> bool:
        """Arm the FC."""
        return self.connection.arm(timeout)
    
    def disarm(self, timeout: float = 3.0) -> bool:
        """Disarm the FC."""
        return self.connection.disarm(timeout)
    
    def wait_for_arming_ready(self, timeout: float = 30.0):
        """Wait for FC to be ready to arm."""
        return self.connection.wait_for_arming_ready(timeout)


def main():
    """Test HITL SD card capabilities."""
    import argparse
    
    parser = argparse.ArgumentParser(description="HITL SD Card Testing")
    parser.add_argument('--port', default='/dev/ttyACM0', help='Serial port')
    parser.add_argument('--elf', required=True, help='ELF file for symbols')
    parser.add_argument('--test', choices=['state', 'dma', 'errors', 'inject', 'capture'],
                        default='state', help='Test to run')
    parser.add_argument('--fault', choices=['dma', 'timeout', 'crc', 'reset', 'failures'],
                        help='Fault type to inject (for --test inject)')
    parser.add_argument('--output', help='Output file for capture')
    args = parser.parse_args()
    
    with HITLSDCard(args.port, args.elf) as hitl:
        if args.test == 'state':
            state = hitl.get_sdcard_state()
            if state:
                print(f"SD Card State: {state.state_name} ({state.state})")
                print(f"Consecutive Errors: {state.consecutive_errors}")
            else:
                print("Failed to read SD card state")
        
        elif args.test == 'dma':
            dma = hitl.get_dma_state()
            if dma:
                print(f"DMA Stream: {dma.stream}")
                print(f"DMA Busy: {dma.busy}")
                print(f"DMA Direction: {dma.direction}")
            else:
                print("Failed to read DMA state")
        
        elif args.test == 'errors':
            errors = hitl.get_error_counters()
            if errors:
                print("Error Counters:")
                for name, value in errors.items():
                    print(f"  {name}: {value}")
            else:
                print("No error counters found")
        
        elif args.test == 'inject':
            if not args.fault:
                print("Need --fault type for injection")
                return 1
            
            result = None
            if args.fault == 'dma':
                result = hitl.inject_dma_error()
            elif args.fault == 'timeout':
                result = hitl.inject_sd_timeout()
            elif args.fault == 'crc':
                result = hitl.inject_crc_error()
            elif args.fault == 'reset':
                result = hitl.force_sdcard_reset()
            elif args.fault == 'failures':
                result = hitl.inject_consecutive_failures(8)
            
            if result:
                print(f"Fault Injection: {'SUCCESS' if result.success else 'FAILED'}")
                print(f"  Type: {result.fault_type}")
                print(f"  Message: {result.message}")
            else:
                print("Unknown fault type")
        
        elif args.test == 'capture':
            output = args.output or f"sdcard_state_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
            if hitl.capture_full_state(output):
                print(f"State captured to: {output}")
            else:
                print("Failed to capture state")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
