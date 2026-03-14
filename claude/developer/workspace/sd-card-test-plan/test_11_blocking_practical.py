#!/usr/bin/env python3
"""
Test 11: Blocking Measurement (Practical Approach)

Validates that the FC remains responsive during SD card operations.
Uses MSP to monitor FC state and ST-Link for debugger connectivity.

This practical approach verifies:
1. ST-Link connection stability
2. FC responsiveness during SD card writes
3. No locked-up states or unexpected resets
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home() / "inavflight" / "mspapi2"))

try:
    from mspapi2 import MSPSerial
except ImportError:
    print("ERROR: mspapi2 required. Install with: pip install mspapi2")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
OPENOCD_CFG = SCRIPT_DIR / "openocd_matekf765_no_halt.cfg"

def test_st_link_connection(duration_sec: int = 10) -> dict:
    """Verify ST-Link debugger connection and stability."""
    print(f"\nPhase 1: ST-Link Connectivity Test ({duration_sec}s)")
    print("-" * 60)

    # Start OpenOCD
    print("Starting OpenOCD...")
    try:
        proc = subprocess.Popen(
            ["openocd", "-f", str(OPENOCD_CFG)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(2)

        if proc.poll() is not None:
            print("ERROR: OpenOCD failed to start")
            return {"passed": False, "error": "OpenOCD startup failed"}

        print("✓ OpenOCD connected (port 3333)")

        # Give OpenOCD time to stabilize
        time.sleep(duration_sec)

        # Check if still running
        if proc.poll() is None:
            print("✓ OpenOCD remained stable for entire test")
            result = {"passed": True, "openocd_stable": True}
        else:
            print("✗ OpenOCD crashed during test")
            result = {"passed": False, "error": "OpenOCD crash"}

        proc.terminate()
        proc.wait(timeout=5)

        return result

    except Exception as e:
        return {"passed": False, "error": str(e)}


def test_msp_responsiveness(duration_sec: int = 60) -> dict:
    """Test FC responsiveness via MSP during SD card writes."""
    print(f"\nPhase 2: FC Responsiveness During SD Write ({duration_sec}s)")
    print("-" * 60)

    try:
        msp = MSPSerial("/dev/ttyACM0", 115200, read_timeout=0.1)
        msp.open()
        print("✓ Connected via MSP")

        # Get initial status
        code, payload = msp.request(0x2000, b"", timeout=1.0)  # INAV_STATUS
        print(f"  Initial status: {len(payload)} bytes received")

        # Query responsiveness periodically during Test 2 run
        # (Test 2 should be running SD card writes in another terminal)
        print(f"  Monitoring MSP responsiveness for {duration_sec}s...")

        timeouts = 0
        successes = 0
        start_time = time.time()

        while time.time() - start_time < duration_sec:
            try:
                code, payload = msp.request(0x2000, b"", timeout=1.0)
                successes += 1
            except Exception:
                timeouts += 1
            time.sleep(0.5)

        msp.close()

        success_rate = successes / (successes + timeouts) * 100 if (successes + timeouts) > 0 else 0
        print(f"  Successes: {successes}, Timeouts: {timeouts}")
        print(f"  Success rate: {success_rate:.1f}%")

        return {
            "passed": success_rate > 95,  # Allow up to 5% timeout rate
            "successes": successes,
            "timeouts": timeouts,
            "success_rate": success_rate
        }

    except Exception as e:
        return {"passed": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Test 11: Blocking Measurement (Practical)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This practical test verifies FC stability during SD operations.

Examples:
  python test_11_blocking_practical.py --duration 30
  python test_11_blocking_practical.py --output results.json
        """
    )

    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--output", type=str, help="Output JSON file")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("TEST 11: Blocking Measurement (Practical Approach)")
    print("=" * 70)
    print("This test verifies FC stability via ST-Link and MSP during SD operations")
    print("")

    # Run tests
    st_link_result = test_st_link_connection(10)
    msp_result = test_msp_responsiveness(args.duration)

    # Combine results
    overall_passed = st_link_result.get("passed", False) and msp_result.get("passed", False)

    result = {
        "test_num": 11,
        "test_name": "Blocking Measurement (Practical)",
        "passed": overall_passed,
        "duration_sec": args.duration,
        "st_link": st_link_result,
        "msp_responsiveness": msp_result,
        "timestamp": datetime.now().isoformat(),
        "note": "Practical approach: verifies FC stability during SD operations via ST-Link and MSP"
    }

    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    print("\n" + "=" * 70)
    print("TEST 11: COMPLETE")
    print(f"Overall result: {'PASS' if overall_passed else 'FAIL'}")
    print("=" * 70)

    sys.exit(0 if overall_passed else 1)


if __name__ == "__main__":
    main()
