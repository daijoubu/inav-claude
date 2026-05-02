"""
CLI Handler for Flight Controller.

Handles CLI mode communication for configuration changes.
"""
import subprocess
import time
from typing import Optional

try:
    import serial as pyserial
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False


class CLIHandler:
    """
    CLI mode communication with flight controller.
    
    Handles entering CLI mode, sending commands, and clean exit.
    """
    
    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
    
    def send_command(self, command: str, timeout: float = 2.0) -> bool:
        """
        Send a CLI command to the flight controller.
        
        Process:
        1. Enter CLI mode with '#'
        2. Send command
        3. Exit CLI mode cleanly
        4. Reconnect MSP
        
        Args:
            command: CLI command (without # prefix)
            timeout: Response timeout
            
        Returns:
            True if command sent successfully
        """
        if not PYSERIAL_AVAILABLE:
            print("ERROR: pyserial not available")
            return False
        
        try:
            ser = pyserial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(0.5)
            
            # Enter CLI mode
            ser.write(b"#")
            time.sleep(0.2)
            ser.read(100)
            
            # Send command
            ser.write(f"{command}\r".encode())
            time.sleep(0.5)
            response = ser.read(500)
            
            # Exit CLI mode
            ser.write(b"\r")
            time.sleep(0.2)
            ser.read(100)
            time.sleep(0.5)
            
            ser.close()
            return True
            
        except Exception as e:
            print(f"CLI error: {e}")
            return False
    
    def apply_diff_file(self, diff_file: str, timeout: float = 30.0) -> bool:
        """
        Apply a diff file using cliterm.
        
        Args:
            diff_file: Path to diff file with commands
            timeout: Maximum time for operation
            
        Returns:
            True if applied successfully
        """
        try:
            cmd = f"cliterm -d {self.port} -f {diff_file}"
            process = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                print("  ERROR: cliterm timed out")
                return False
            
            if process.returncode != 0:
                print(f"  ERROR: cliterm failed with code {process.returncode}")
                return False
            
            print("  ✓ Configuration applied")
            return True
            
        except Exception as e:
            print(f"  ERROR: Failed to apply configuration: {e}")
            return False
    
    def set_blackbox_rate(self, rate: str) -> bool:
        """
        Set blackbox logging rate.
        
        Args:
            rate: Rate string like "1/2", "1/4", etc.
            
        Returns:
            True if set successfully
        """
        if "/" not in rate:
            return False
        
        parts = rate.split("/")
        if len(parts) != 2:
            return False
        
        try:
            num = int(parts[0].strip())
            denom = int(parts[1].strip())
        except ValueError:
            return False
        
        # Use CLI command
        return self.send_command(f"set blackbox_rate={rate}") and self.send_command("save")
