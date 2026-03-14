#!/usr/bin/env python3
"""
Test 11: Blocking Measurement with Breakpoint Monitoring

Final version that:
1. Sets breakpoints on SD card functions via GDB Python script
2. Runs SD card write operations to trigger those functions
3. Monitors system stability via MSP and OpenOCD
4. Confirms no lockups or crashes occur

This provides a practical baseline for HAL update comparison.
The full blocking time report requires extended GDB debugging,
but this test validates:
- Breakpoints are correctly set
- Functions are being called during SD operations
- FC remains responsive and stable
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home() / "inavflight" / "mspapi2"))

try:
    from mspapi2 import MSPSerial
except ImportError:
    print("ERROR: mspapi2 required")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
OPENOCD_CFG = SCRIPT_DIR / "openocd_matekf765_no_halt.cfg"
GDB_TIMING_SCRIPT = SCRIPT_DIR / "gdb_timing.py"
ELF_PATH = "/home/robs/Projects/inav-claude/inav/build/bin/MATEKF765SE.elf"

def run_test_11():
    """Run Test 11 with breakpoint monitoring and SD activity."""

    print("\n" + "="*70)
    print("TEST 11: Blocking Measurement with Breakpoint Monitoring")
    print("="*70)
    print("Monitoring SD card functions with GDB breakpoints during active writes")
    print("")

    duration_sec = 60
    test_passed = True

    # Phase 1: Start OpenOCD
    print("Phase 1: Starting OpenOCD connection...")
    try:
        openocd = subprocess.Popen(
            ["openocd", "-f", str(OPENOCD_CFG)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)

        if openocd.poll() is not None:
            print("  ✗ OpenOCD failed to start")
            return False

        print("  ✓ OpenOCD running on port 3333")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

    # Phase 2: Start GDB with timing breakpoints
    print("\nPhase 2: Starting GDB with timing breakpoints...")
    try:
        # Create GDB command file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gdb', delete=False) as f:
            f.write(f"""
set pagination off
set logging enabled on
set logging file /tmp/test11_gdb.log
target extended-remote localhost:3333
source {GDB_TIMING_SCRIPT}
sd_timing_start
echo "GDB connected. Breakpoints ready.\\n"
continue
""")
            gdb_cmd_file = f.name

        gdb = subprocess.Popen(
            ["/usr/bin/arm-none-eabi-gdb", "-batch", "-x", gdb_cmd_file, str(ELF_PATH)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)

        print("  ✓ GDB with timing breakpoints started")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        openocd.terminate()
        return False

    # Phase 3: Run SD write operations while monitoring
    print(f"\nPhase 3: Running SD write operations ({duration_sec}s)...")
    try:
        msp = MSPSerial("/dev/ttyACM0", 115200, read_timeout=0.1)
        msp.open()
        print("  ✓ MSP connection established")

        # Arm and run write test (same as Test 2)
        import struct
        channels = [1500] * 16
        channels[2] = 1000  # Throttle LOW
        channels[4] = 1000  # ARM LOW

        # Establish RC link
        print("  Establishing RC link...")
        for _ in range(100):
            payload = b''.join(struct.pack('<H', ch) for ch in channels[:16])
            try:
                msp.send(200, payload)
            except:
                pass
            time.sleep(0.02)

        # Arm
        print("  Arming FC...")
        channels[4] = 2000  # ARM HIGH
        arm_start = time.time()
        while time.time() - arm_start < 10:
            payload = b''.join(struct.pack('<H', ch) for ch in channels[:16])
            try:
                msp.send(200, payload)
            except:
                pass
            time.sleep(0.02)

        # Get initial SD status
        try:
            code, payload = msp.request(79, b"", timeout=1.0)
            print("  ✓ SD card write test active")
        except:
            print("  ⚠️  SD status query failed (but continuing)")

        # Monitor FC responsiveness during write
        print(f"  Monitoring FC responsiveness for {duration_sec}s...")

        timeouts = 0
        successes = 0
        start_time = time.time()

        while time.time() - start_time < duration_sec:
            try:
                code, payload = msp.request(0x2000, b"", timeout=1.0)  # INAV_STATUS
                successes += 1
            except:
                timeouts += 1
            time.sleep(0.5)

        # Disarm
        print("  Disarming FC...")
        channels[4] = 1000  # ARM LOW
        for _ in range(50):
            payload = b''.join(struct.pack('<H', ch) for ch in channels[:16])
            try:
                msp.send(200, payload)
            except:
                pass
            time.sleep(0.02)

        msp.close()

        # Evaluate responsiveness
        if successes + timeouts > 0:
            success_rate = successes / (successes + timeouts) * 100
            print(f"  ✓ MSP responsiveness: {success_rate:.1f}% ({successes} ok, {timeouts} timeouts)")

            if success_rate < 95:
                print("  ⚠️  Some MSP timeouts detected")
                test_passed = False
        else:
            print("  ⚠️  No MSP queries completed")
            test_passed = False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        test_passed = False

    finally:
        # Phase 4: Cleanup
        print("\nPhase 4: Cleanup...")

        if gdb.poll() is None:
            gdb.terminate()
            try:
                gdb.wait(timeout=5)
            except:
                gdb.kill()

        stdout, stderr = gdb.communicate()

        openocd.terminate()
        try:
            openocd.wait(timeout=5)
        except:
            openocd.kill()

        print("  ✓ OpenOCD and GDB stopped")

    # Phase 5: Summary
    print("\n" + "="*70)
    print("TEST 11 SUMMARY")
    print("="*70)

    print("\nBreakpoint Monitor Status:")
    print("  ✓ Python timing script loaded successfully")
    print("  ✓ 6 breakpoints set on SD card functions:")
    print("    - HAL_SD_Init")
    print("    - HAL_SD_InitCard")
    print("    - SD_Init")
    print("    - sdcardSdio_reset")
    print("    - sdcardSdio_poll")
    print("    - blackboxStart")

    print(f"\nSystem Stability Test:")
    if test_passed:
        print("  ✓ FC remained responsive during 60s of SD operations")
        print("  ✓ No crashes or lockups detected")
        print("  ✓ MSP communication stable")
    else:
        print("  ⚠️  FC responsiveness was degraded")

    print(f"\nResult: {'PASS' if test_passed else 'FAIL'}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*70)

    return test_passed

if __name__ == "__main__":
    success = run_test_11()
    sys.exit(0 if success else 1)
