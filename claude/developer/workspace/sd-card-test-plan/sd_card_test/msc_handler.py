"""
USB Mass Storage (MSC) Handler.

Handles entering/exiting MSC mode and file operations.
"""
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Optional

try:
    import serial as pyserial
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False


class MSCHandler:
    """
    USB Mass Storage operations for flight controller.
    
    Handles:
    - Entering MSC mode via CLI
    - Block device detection
    - Mount point discovery
    - Exiting MSC mode via ST-Link reset
    """
    
    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
    
    def enable_msc_mode(self, timeout: float = 30.0) -> bool:
        if not PYSERIAL_AVAILABLE:
            print("ERROR: pyserial not available")
            return False
        
        try:
            print("  [MSC] Opening serial port...")
            ser = pyserial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(0.5)
            
            # Drain all pending MSP data - FC sends continuously
            print("  [MSC] Draining MSP data...")
            for _ in range(20):
                data = ser.read(2000)
                if not data:
                    break
                time.sleep(0.05)
            
            ser.reset_input_buffer()
            time.sleep(0.2)
            
            # Enter CLI mode with CR
            print("  [MSC] Entering CLI mode...")
            ser.write(b"#\r")
            time.sleep(1.0)
            
            response = ser.read(2000)
            if b'# ' not in response and b'CLI' not in response:
                print("  [MSC] ✗ CLI mode not detected")
                ser.close()
                return False
            
            print("  [MSC] ✓ CLI mode entered")
            
            # Send msc command
            print("  [MSC] Sending 'msc' command...")
            ser.write(b"msc\r")
            time.sleep(0.5)
            
            # FC will reboot - read response
            try:
                ser.read(500)
            except:
                pass
            
            try:
                ser.close()
            except:
                pass
            
            # FC will reboot - read may fail when it disconnects
            try:
                time.sleep(0.3)
                ser.read(500)
            except:
                pass  # FC disconnected during read - expected
            
            try:
                ser.close()
            except:
                pass
            
            # FC is now rebooting into MSC mode
            print("  [MSC] FC rebooting into MSC mode...")
            
            # Wait for CDC device to disappear (FC is rebooting)
            print("  [MSC] Waiting for CDC device to disconnect...")
            cdc_disconnect_timeout = 10
            start = time.time()
            while time.time() - start < cdc_disconnect_timeout:
                if not os.path.exists(self.port):
                    print("  [MSC] ✓ CDC device disconnected")
                    break
                time.sleep(0.2)
            
            # Wait for block device
            print("  [MSC] Waiting for USB block device...")
            if not self._wait_for_block_device(timeout):
                print("  [MSC] ✗ Block device not found")
                return False
            
            print("  [MSC] ✓ Block device detected")
            
            # Mount device
            print("  [MSC] Mounting USB MSC device...")
            time.sleep(1)
            
            for i in range(10):
                try:
                    result = subprocess.run(
                        ["udisksctl", "mount", "-b", "/dev/sdb1"],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0 or "already mounted" in (result.stderr or ""):
                        print("  [MSC] ✓ Mounted")
                        time.sleep(0.5)
                        return True
                except subprocess.TimeoutExpired:
                    pass
                except Exception:
                    pass
                time.sleep(1)
            
            print("  [MSC] ✗ Mount failed")
            return False
            
        except Exception as e:
            print(f"  [MSC] Error: {e}")
            return False
    
    def _wait_for_block_device(self, timeout: float = 30.0) -> bool:
        """Wait for USB MSC block device to appear"""
        start = time.time()
        while time.time() - start < timeout:
            for device in ['/dev/sdb', '/dev/sdb1', '/dev/sdc', '/dev/sdc1']:
                if os.path.exists(device):
                    elapsed = time.time() - start
                    print(f"  ✓ Found MSC block device: {device} (after {elapsed:.1f}s)")
                    return True
            time.sleep(0.2)
        return False
    
    def find_msc_mount_point(self) -> Optional[Path]:
        """Find the USB MSC device mount point"""
        system = platform.system()
        
        if system == "Linux":
            return self._find_mount_linux()
        elif system == "Darwin":
            return self._find_mount_macos()
        elif system == "Windows":
            return self._find_mount_windows()
        return None
    
    def _find_mount_linux(self) -> Optional[Path]:
        """Find USB MSC mount point on Linux"""
        try:
            result = subprocess.run(
                ["findmnt", "-r", "-o", "TARGET,SOURCE"],
                capture_output=True, text=True, timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if 'sd' in line.lower() or 'usb' in line.lower():
                    parts = line.split()
                    if len(parts) >= 1:
                        mount_path = Path(parts[0])
                        if mount_path.exists() and (mount_path / "LOGS").exists():
                            return mount_path
        except:
            pass
        
        for base_path in [Path("/run/media"), Path("/media"), Path("/mnt")]:
            if not base_path.exists():
                continue
            try:
                for item in base_path.iterdir():
                    if item.is_dir() and (item / "LOGS").exists():
                        return item
            except:
                pass
        
        return None
    
    def _find_mount_macos(self) -> Optional[Path]:
        """Find USB MSC mount point on macOS"""
        volumes = Path("/Volumes")
        if not volumes.exists():
            return None
        try:
            for item in volumes.iterdir():
                if item.is_dir() and (item / "LOGS").exists():
                    return item
        except:
            pass
        return None
    
    def _find_mount_windows(self) -> Optional[Path]:
        """Find USB MSC mount point on Windows"""
        import string
        for letter in string.ascii_uppercase:
            drive = Path(f"{letter}:\\")
            try:
                if drive.exists() and (drive / "LOGS").exists():
                    return drive
            except:
                pass
        return None
    
    def exit_msc_mode(self, openocd_config: str = None) -> bool:
        """
        Exit USB MSC mode and restore normal INAV operation.
        
        Process:
        1. Unmount USB MSC storage
        2. Reset FC via ST-Link
        3. Wait for serial port to reappear
        
        Args:
            openocd_config: Path to OpenOCD config file
        """
        print("\n" + "="*60)
        print("EXITING USB MSC MODE")
        print("="*60)
        
        # Unmount
        print("\n1. Unmounting USB MSC storage...")
        mount = self.find_msc_mount_point()
        if mount:
            try:
                subprocess.run(
                    ["udisksctl", "unmount", "-b", "/dev/sdb1"],
                    capture_output=True, timeout=5
                )
                print("   ✓ Unmounted")
            except:
                pass
        else:
            print("   ℹ Not in MSC mode")
        
        time.sleep(1)
        
        # Reset via ST-Link
        print("\n2. Resetting FC via ST-Link...")
        if openocd_config and Path(openocd_config).exists():
            try:
                cmds = [
                    "openocd", "-f", openocd_config,
                    "-c", "init",
                    "-c", "halt",
                    "-c", "mww 0x2001FFF0 0xFFFFFFFF",
                    "-c", "mww 0x40002854 0x00000000",
                    "-c", "mww 0xE000ED0C 0x05FA0004",
                    "-c", "sleep 1000",
                    "-c", "shutdown"
                ]
                subprocess.run(cmds, capture_output=True, timeout=10)
                print("   ✓ Reset triggered")
            except Exception as e:
                print(f"   ⚠ Reset error: {e}")
        else:
            print("   ⚠ OpenOCD config not found")
        
        time.sleep(2)
        
        # Wait for serial port
        print("\n3. Waiting for serial port...")
        for i in range(20):
            if Path(self.port).exists():
                print(f"   ✓ {self.port} appeared")
                time.sleep(1)
                return True
            time.sleep(1)
        
        print(f"   ✗ {self.port} did not appear")
        return False
