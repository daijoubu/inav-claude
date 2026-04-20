#!/usr/bin/env python3
"""
CRSF Context Manager for HITL Testing.

Provides context manager for running tests with CRSF receiver simulation.
This simulates a CRSF receiver on a UART while testing via USB MSP.

Usage:
    from crsf_context import CRSFTestContext
    
    with CRSFTestContext(fc, crsf_port='/dev/ttyUSB0') as ctx:
        # Run tests while CRSF is being simulated
        result = suite.run_test(8)
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, List
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class CRSFSimulator:
    """
    CRSF receiver simulator for testing.
    
    Sends CRSF RC channel frames at 150Hz to simulate a real receiver.
    """
    
    def __init__(self, port: str, baudrate: int = 420000,
                 frame_rate_hz: float = 150.0,
                 armed: bool = False,
                 throttle: int = 1000):
        self.port = port
        self.baudrate = baudrate
        self.frame_rate_hz = frame_rate_hz
        self.armed = armed
        self.throttle = throttle
        
        self.process: Optional[subprocess.Popen] = None
        self.script_path = Path(__file__).parent / "crsf_simulator.py"
    
    def start(self) -> bool:
        """Start CRSF simulation."""
        if not self.script_path.exists():
            print(f"CRSF simulator script not found: {self.script_path}")
            return False
        
        try:
            # Start the CRSF simulator
            self.process = subprocess.Popen(
                [sys.executable, str(self.script_path), self.port,
                 "--baud", str(self.baudrate),
                 "--rate", str(self.frame_rate_hz),
                 "--throttle", str(self.throttle)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for it to start
            time.sleep(0.5)
            
            # Check if it's still running
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                print(f"CRSF simulator failed to start:")
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")
                return False
            
            print(f"CRSF simulator started on {self.port}")
            return True
            
        except Exception as e:
            print(f"Failed to start CRSF simulator: {e}")
            return False
    
    def stop(self):
        """Stop CRSF simulation."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except:
                pass
            self.process = None
            print("CRSF simulator stopped")
    
    def set_armed(self, armed: bool):
        """Set arm state via MSP command (if connected to same FC)."""
        self.armed = armed
        # Note: This doesn't actually control the simulator since it's on a different port
        # The simulator sends fixed RC values
    
    def set_throttle(self, throttle: int):
        """Set throttle value."""
        self.throttle = throttle


class CRSFTestContext:
    """
    Context manager for running tests with CRSF simulation.
    
    Usage:
        with CRSFTestContext(fc, crsf_port='/dev/ttyUSB0') as ctx:
            # CRSF is now running
            result = suite.run_test(8)
            # Check results
    """
    
    def __init__(self, fc, crsf_port: str,
                 crsf_baudrate: int = 420000,
                 crsf_rate_hz: float = 150.0,
                 crsf_armed: bool = False,
                 crsf_throttle: int = 1000):
        self.fc = fc
        self.crsf_port = crsf_port
        self.crsf_baudrate = crsf_baudrate
        self.crsf_rate_hz = crsf_rate_hz
        self.crsf_armed = crsf_armed
        self.crsf_throttle = crsf_throttle
        
        self.simulator: Optional[CRSFSimulator] = None
    
    def __enter__(self):
        """Start CRSF simulation when entering context."""
        print(f"\n{'='*60}")
        print("Starting CRSF Simulation")
        print(f"{'='*60}")
        print(f"  Port: {self.crsf_port}")
        print(f"  Baud: {self.crsf_baudrate}")
        print(f"  Rate: {self.crsf_rate_hz} Hz")
        
        self.simulator = CRSFSimulator(
            self.crsf_port,
            self.crsf_baudrate,
            self.crsf_rate_hz,
            self.crsf_armed,
            self.crsf_throttle
        )
        
        if not self.simulator.start():
            raise RuntimeError("Failed to start CRSF simulator")
        
        # Give it time to establish
        time.sleep(1.0)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop CRSF simulation when exiting context."""
        if self.simulator:
            self.simulator.stop()
        
        print(f"{'='*60}")
        print("CRSF Simulation Ended")
        print(f"{'='*60}\n")
        
        return False


def test_crsf_context():
    """Test the CRSF context manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test CRSF Context")
    parser.add_argument("--crsf-port", default="/dev/ttyUSB0", help="CRSF serial port")
    args = parser.parse_args()
    
    print("Testing CRSF context manager...")
    print(f"Note: This will try to open {args.crsf_port}")
    print("Connect an FTDI adapter to test CRSF simulation.")
    
    # Just test the simulator can be instantiated
    sim = CRSFSimulator(args.crsf_port)
    print("CRSFSimulator instantiated OK")
    print("Use with CRSFTestContext to run tests with CRSF simulation")


if __name__ == '__main__':
    test_crsf_context()
