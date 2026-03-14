#!/usr/bin/env python3
"""
Test 11: Blocking Measurement using ST-Link + OpenOCD + GDB

Measures actual blocking times in SD card operations to identify
the root cause of F765/H743 arming lockups.

Requirements:
- OpenOCD installed
- GDB (gdb-multiarch or arm-none-eabi-gdb) installed
- ST-Link debugger connected to MATEKF765SE
- INAV firmware ELF file with debug symbols

Usage:
    python test_11_blocking.py /path/to/inav_MATEKF765.elf
    python test_11_blocking.py /path/to/inav_MATEKF765.elf --duration 120
    python test_11_blocking.py /path/to/inav_MATEKF765.elf --output results.json

Author: INAV Developer
Date: 2026-02-21
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
# Use non-halting config to keep FC running during measurement
OPENOCD_CFG = SCRIPT_DIR / "openocd_matekf765_no_halt.cfg"
# Fall back to halting config if non-halting version doesn't exist
if not OPENOCD_CFG.exists():
    OPENOCD_CFG = SCRIPT_DIR / "openocd_matekf765.cfg"
GDB_TIMING_SCRIPT = SCRIPT_DIR / "gdb_timing.py"

# GDB executable (try multiple names)
# Prefer newer GDB with Python support over older toolchain version
GDB_EXECUTABLES = [
    "/usr/bin/arm-none-eabi-gdb",  # Arch Linux v17.1 with Python support
    "gdb-multiarch",
    "arm-none-eabi-gdb",
    "gdb",
]

# OpenOCD executable
OPENOCD_EXECUTABLE = "openocd"


# =============================================================================
# Helper Functions
# =============================================================================

def find_executable(names: list) -> Optional[str]:
    """Find first available executable from list"""
    for name in names:
        try:
            subprocess.run([name, "--version"], capture_output=True, check=True)
            return name
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None


def check_dependencies() -> tuple[bool, str]:
    """Check if required tools are installed"""
    errors = []

    # Check OpenOCD
    try:
        result = subprocess.run(
            [OPENOCD_EXECUTABLE, "--version"],
            capture_output=True,
            text=True
        )
        print(f"OpenOCD: {result.stderr.split(chr(10))[0]}")
    except FileNotFoundError:
        errors.append("OpenOCD not found. Install with: sudo apt install openocd")

    # Check GDB
    gdb = find_executable(GDB_EXECUTABLES)
    if gdb:
        result = subprocess.run([gdb, "--version"], capture_output=True, text=True)
        print(f"GDB: {result.stdout.split(chr(10))[0]}")
    else:
        errors.append("GDB not found. Install with: sudo apt install gdb-multiarch")

    # Check config files
    if not OPENOCD_CFG.exists():
        errors.append(f"OpenOCD config not found: {OPENOCD_CFG}")

    if not GDB_TIMING_SCRIPT.exists():
        errors.append(f"GDB timing script not found: {GDB_TIMING_SCRIPT}")

    if errors:
        return False, "\n".join(errors)

    return True, gdb


# =============================================================================
# Test 11 Implementation
# =============================================================================

@dataclass
class Test11Result:
    """Result of Test 11"""
    passed: bool
    duration_sec: float
    max_blocking_ms: float
    total_blocking_ms: float
    function_stats: dict
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "test_num": 11,
            "test_name": "Blocking Measurement",
            "passed": self.passed,
            "duration_sec": self.duration_sec,
            "max_blocking_ms": self.max_blocking_ms,
            "total_blocking_ms": self.total_blocking_ms,
            "function_stats": self.function_stats,
            "error": self.error,
            "timestamp": datetime.now().isoformat()
        }


def run_test_11(
    elf_path: Path,
    gdb_executable: str,
    duration_sec: int = 60,
    trigger_sd_operations: bool = True
) -> Test11Result:
    """
    Run Test 11: Blocking Measurement

    This function:
    1. Starts OpenOCD to connect to the target
    2. Starts GDB with timing script
    3. Monitors for specified duration
    4. Collects and returns timing data
    """
    print("\n" + "=" * 70)
    print("TEST 11: Blocking Measurement (ST-Link + GDB)")
    print("=" * 70)
    print(f"ELF file: {elf_path}")
    print(f"Duration: {duration_sec} seconds")
    print("")

    openocd_proc = None
    gdb_proc = None

    try:
        # Start OpenOCD
        print(f"Starting OpenOCD with config: {OPENOCD_CFG.name}")
        openocd_proc = subprocess.Popen(
            [OPENOCD_EXECUTABLE, "-f", str(OPENOCD_CFG)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)  # Wait for OpenOCD to fully initialize

        # Check if OpenOCD started successfully
        if openocd_proc.poll() is not None:
            stderr = openocd_proc.stderr.read().decode()
            return Test11Result(
                passed=False,
                duration_sec=0,
                max_blocking_ms=0,
                total_blocking_ms=0,
                function_stats={},
                error=f"OpenOCD failed to start: {stderr}"
            )

        print("OpenOCD running on port 3333")

        # Create GDB command script
        gdb_commands = f"""
# Connect to OpenOCD
target extended-remote localhost:3333

# Load timing script
source {GDB_TIMING_SCRIPT}

# Start timing measurement
sd_timing_start

# Continue execution
continue

# The continue command will block; we interrupt after duration
# (This requires GDB to be running in interactive mode or with a timeout)
"""
interrupt
sd_timing_report

# Disconnect cleanly
disconnect
quit
"""
        # Write GDB commands to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gdb', delete=False) as f:
            f.write(gdb_commands)
            gdb_script_path = f.name

        print(f"Running GDB for {duration_sec} seconds...")
        print("(Monitoring SD card function timing)")
        print("")

        # Run GDB with commands
        start_time = time.time()
        result = subprocess.run(
            [gdb_executable, "-q", "-x", gdb_script_path, str(elf_path)],
            capture_output=True,
            text=True,
            timeout=duration_sec + 30  # Extra time for startup/cleanup
        )
        elapsed = time.time() - start_time

        # Clean up temp file
        os.unlink(gdb_script_path)

        # Parse GDB output for timing data
        output = result.stdout + result.stderr
        print("GDB Output:")
        print("-" * 40)
        print(output[-2000:] if len(output) > 2000 else output)  # Last 2000 chars
        print("-" * 40)

        # Extract timing information from output
        max_blocking = 0.0
        total_blocking = 0.0
        function_stats = {}

        # Parse the timing report
        lines = output.split('\n')
        in_report = False
        for line in lines:
            if "SD CARD TIMING REPORT" in line:
                in_report = True
                continue

            if in_report:
                if "Maximum single call duration:" in line:
                    try:
                        max_blocking = float(line.split(':')[1].strip().replace('ms', ''))
                    except (ValueError, IndexError):
                        pass

                if "Total time in monitored functions:" in line:
                    try:
                        total_blocking = float(line.split(':')[1].strip().replace('ms', ''))
                    except (ValueError, IndexError):
                        pass

                # Parse function stats line
                parts = line.split()
                if len(parts) >= 5 and parts[1].isdigit():
                    try:
                        func_name = parts[0]
                        hits = int(parts[1])
                        avg_ms = float(parts[2].replace('ms', ''))
                        max_ms = float(parts[3].replace('ms', ''))
                        function_stats[func_name] = {
                            "hits": hits,
                            "avg_ms": avg_ms,
                            "max_ms": max_ms
                        }
                    except (ValueError, IndexError):
                        pass

        # Determine pass/fail
        # PASS if max blocking time < 10ms
        passed = max_blocking < 10.0

        print("\n" + "=" * 70)
        print(f"RESULT: {'PASS' if passed else 'FAIL'}")
        print(f"Maximum blocking time: {max_blocking:.2f}ms")
        print(f"Threshold: 10ms")
        print("=" * 70)

        return Test11Result(
            passed=passed,
            duration_sec=elapsed,
            max_blocking_ms=max_blocking,
            total_blocking_ms=total_blocking,
            function_stats=function_stats
        )

    except subprocess.TimeoutExpired:
        return Test11Result(
            passed=False,
            duration_sec=duration_sec,
            max_blocking_ms=0,
            total_blocking_ms=0,
            function_stats={},
            error="GDB timed out"
        )
    except Exception as e:
        return Test11Result(
            passed=False,
            duration_sec=0,
            max_blocking_ms=0,
            total_blocking_ms=0,
            function_stats={},
            error=str(e)
        )
    finally:
        # Cleanup
        if gdb_proc and gdb_proc.poll() is None:
            gdb_proc.terminate()
            gdb_proc.wait(timeout=5)

        if openocd_proc and openocd_proc.poll() is None:
            print("Stopping OpenOCD...")
            openocd_proc.terminate()
            openocd_proc.wait(timeout=5)


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Test 11: Blocking Measurement using ST-Link + GDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This test measures actual blocking times in SD card operations.
Requires ST-Link debugger connected to the flight controller.

Examples:
  python test_11_blocking.py build/MATEKF765.elf
  python test_11_blocking.py build/MATEKF765.elf --duration 120
  python test_11_blocking.py build/MATEKF765.elf --output blocking_results.json
        """
    )

    parser.add_argument("elf", help="Path to firmware ELF file with debug symbols")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds (default: 60)")
    parser.add_argument("--output", type=str, help="Output JSON file for results")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies, don't run test")

    args = parser.parse_args()

    # Check dependencies
    ok, result = check_dependencies()
    if not ok:
        print(f"\nERROR: Missing dependencies:\n{result}")
        sys.exit(1)

    gdb_executable = result

    if args.check_only:
        print("\nAll dependencies OK!")
        sys.exit(0)

    # Check ELF file
    elf_path = Path(args.elf)
    if not elf_path.exists():
        print(f"ERROR: ELF file not found: {elf_path}")
        sys.exit(1)

    # Run test
    result = run_test_11(
        elf_path=elf_path,
        gdb_executable=gdb_executable,
        duration_sec=args.duration
    )

    # Save results if output specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"\nResults saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
