"""
Main entry point for SD card tests.
"""
import argparse
import json
import sys
import time
from typing import List

# Force unbuffered output
sys.stdout = sys.__stdout__

from .fc_control import FCControl
from .msc_handler import MSCHandler
from .tests import TestSuite
from .models import TestResult


def main():
    parser = argparse.ArgumentParser(description="SD Card Test Suite for INAV")
    parser.add_argument("port", help="Serial port (e.g., /dev/ttyACM0)")
    parser.add_argument("--tests", default="1,2,3,4,6", help="Tests to run (comma-separated)")
    parser.add_argument("--output", default=None, help="Output file for results (JSON)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--openocd-config", default=None, help="Path to OpenOCD config for MSC exit")
    parser.add_argument("--duration-sec", type=int, default=None, help="Duration for tests 2, 4 (seconds)")
    parser.add_argument("--duration-min", type=int, default=None, help="Duration for tests 3, 9, 10 (minutes)")
    parser.add_argument("--cycles", type=int, default=None, help="Cycles for test 6")
    parser.add_argument("--attempts", type=int, default=None, help="Attempts for test 8")
    parser.add_argument("--max-logs", type=int, default=None, help="Max logs for test 7")
    parser.add_argument("--elf-path", default=None, help="ELF file path for test 11")
    
    # CRSF simulation options
    parser.add_argument("--crsf-port", default=None, help="Serial port for CRSF simulator (e.g., /dev/ttyUSB0)")
    parser.add_argument("--crsf-baud", type=int, default=420000, help="CRSF baud rate (default: 420000)")
    parser.add_argument("--crsf-rate", type=float, default=150.0, help="CRSF frame rate Hz (default: 150)")
    parser.add_argument("--crsf-armed", action="store_true", help="Start CRSF in armed state")
    parser.add_argument("--crsf-throttle", type=int, default=1000, help="Initial CRSF throttle (default: 1000)")
    
    args = parser.parse_args()
    
    test_list = [int(t) for t in args.tests.split(",")]
    
    # Start CRSF simulation if requested
    crsf_simulator = None
    if args.crsf_port:
        # Try to import CRSF simulator from hitl scripts
        try:
            from claude.developer.scripts.testing.hitl.crsf_context import CRSFSimulator
            crsf_simulator = CRSFSimulator(
                args.crsf_port,
                args.crsf_baud,
                args.crsf_rate,
                args.crsf_armed,
                args.crsf_throttle
            )
        except ImportError:
            print("Warning: CRSF simulator not available")
        
        if crsf_simulator:
            print(f"\n{'='*60}")
            print("Starting CRSF Simulation")
            print(f"{'='*60}")
            print(f"  Port: {args.crsf_port}")
            print(f"  Baud: {args.crsf_baud}")
            print(f"  Rate: {args.crsf_rate} Hz")
            
            if not crsf_simulator.start():
                print("Warning: Failed to start CRSF simulator, continuing without it")
                crsf_simulator = None
            else:
                time.sleep(1.0)  # Give CRSF time to establish
            print()
    
    fc = FCControl(args.port, elf_path=args.elf_path)
    if not fc.connect():
        print(f"Failed to connect to {args.port}")
        if crsf_simulator:
            crsf_simulator.stop()
        sys.exit(1)
    
    msc = MSCHandler(args.port)
    
    suite = TestSuite(fc, msc, verbose=args.verbose)
    
    results = []
    for test_num in test_list:
        kwargs = {}
        if test_num in (2, 4) and args.duration_sec:
            kwargs["duration_sec"] = args.duration_sec
        if test_num == 3 and args.duration_min:
            kwargs["duration_min"] = args.duration_min
        if test_num == 6 and args.cycles:
            kwargs["cycles"] = args.cycles
        if test_num == 7 and args.max_logs:
            kwargs["max_logs"] = args.max_logs
        if test_num == 8 and args.attempts:
            kwargs["attempts"] = args.attempts
        if test_num == 9 and args.duration_min:
            kwargs["duration_min"] = args.duration_min
        if test_num == 10 and args.duration_min:
            kwargs["duration_min"] = args.duration_min
        if test_num == 11:
            if args.duration_sec:
                kwargs["duration_sec"] = args.duration_sec
            if args.elf_path:
                kwargs["elf_path"] = args.elf_path
        
        result = suite.run_test(test_num, **kwargs)
        results.append(result)
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  Test {r.test_num}: {r.test_name:<30} [{status}]")
    
    print()
    print(f"Total: {passed} passed, {failed} failed")
    
    if args.output:
        output = {
            "timestamp": time.strftime("%Y%m%d-%H%M%S"),
            "port": args.port,
            "results": [r.to_dict() for r in results],
            "summary": {"passed": passed, "failed": failed}
        }
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    fc.disconnect()
    
    # Stop CRSF simulator if it was running
    if crsf_simulator:
        crsf_simulator.stop()
    
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
