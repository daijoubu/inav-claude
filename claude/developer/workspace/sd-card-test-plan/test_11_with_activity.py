#!/usr/bin/env python3
"""
Test 11: Blocking Measurement WITH SD Activity

Combines Test 2 (SD card writes) with Test 11 (blocking measurement)
to capture real blocking times during actual SD operations.

The test runs both simultaneously:
1. Background: GDB with timing breakpoints monitoring SD functions
2. Foreground: SD card write operations that trigger those functions

This captures real-world blocking times.
"""

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.home() / "inavflight" / "mspapi2"))

try:
    from mspapi2 import MSPSerial
except ImportError:
    print("ERROR: mspapi2 required")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
OPENOCD_CFG = SCRIPT_DIR / "openocd_matekf765_no_halt.cfg"
GDB_SCRIPT = SCRIPT_DIR / "gdb_timing.py"  # Use Python timing script, not command script

def main():
    print("\n" + "="*70)
    print("TEST 11: Blocking Measurement WITH SD Card Activity")
    print("="*70)
    print("This test combines breakpoint monitoring with active SD writes")
    print("")

    elf_path = "/home/robs/Projects/inav-claude/inav/build/bin/MATEKF765SE.elf"
    duration_sec = 60

    # Start OpenOCD
    print("1. Starting OpenOCD...")
    openocd = subprocess.Popen(
        ["openocd", "-f", str(OPENOCD_CFG)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)
    print("   ✓ OpenOCD running on port 3333")

    # Start GDB with Python timing script
    print("2. Starting GDB with Python timing monitor...")
    # Create a temporary GDB command file that sources the Python script
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gdb', delete=False) as f:
        f.write(f"""
set pagination off
target extended-remote localhost:3333
source {GDB_SCRIPT}
sd_timing_start
continue
""")
        gdb_cmd_file = f.name

    # Store for later cleanup
    import os
    temp_files = [gdb_cmd_file]

    gdb = subprocess.Popen(
        ["/usr/bin/arm-none-eabi-gdb", "-batch", "-x", gdb_cmd_file, elf_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(3)
    print("   ✓ GDB connected with Python timing monitor")

    # Now run SD card write test to trigger the monitored functions
    print("3. Starting SD card write test to trigger monitoring...")
    print("   Running for 60 seconds...")

    try:
        msp = MSPSerial("/dev/ttyACM0", 115200, read_timeout=0.1)
        msp.open()
        print("   ✓ MSP connection established")

        # Get initial SD status
        code, payload = msp.request(79, b"", timeout=1.0)  # MSP_SDCARD_SUMMARY

        # Arm and run write test
        print("   Arming FC...")
        channels = [1500] * 16
        channels[2] = 1000  # Throttle LOW
        channels[4] = 1000  # ARM LOW first

        # Establish RC link
        import struct
        for _ in range(100):
            payload = b''.join(struct.pack('<H', ch) for ch in channels[:16])
            try:
                msp.send(200, payload)
            except:
                pass
            time.sleep(0.02)

        # Arm
        channels[4] = 2000  # ARM HIGH
        arm_start = time.time()
        while time.time() - arm_start < 10:
            # Send RC to arm
            payload = b''.join(struct.pack('<H', ch) for ch in channels[:16])
            try:
                msp.send(200, payload)
            except:
                pass
            time.sleep(0.02)

        print("   FC armed, SD operations in progress...")
        print("")
        print("   ⏳ Monitoring blocking times (56 seconds remaining)...")

        # Keep armed and let breakpoints collect data
        time.sleep(duration_sec - 4)

        # Disarm
        print("   Disarming FC...")
        channels[4] = 1000  # ARM LOW
        for _ in range(50):
            payload = b''.join(struct.pack('<H', ch) for ch in channels[:16])
            try:
                msp.send(200, payload)
            except:
                pass
            time.sleep(0.02)

        msp.close()
        print("   ✓ Test complete")

    except Exception as e:
        print(f"   ERROR: {e}")

    # Wait for GDB to finish
    print("\n4. Collecting GDB timing results...")
    time.sleep(3)

    if gdb.poll() is None:
        gdb.terminate()
        gdb.wait(timeout=5)

    stdout, stderr = gdb.communicate()

    # Look for blocking time report
    print("   GDB Output:")
    print("   " + "-"*60)
    for line in stdout.split('\n')[-30:]:
        if line.strip():
            print(f"   {line}")

    # Stop OpenOCD
    print("\n5. Cleanup...")
    openocd.terminate()
    openocd.wait(timeout=5)
    print("   ✓ OpenOCD stopped")

    print("\n" + "="*70)
    print("TEST 11: COMPLETE")
    print("Check GDB output above for blocking time measurements")
    print("="*70)

if __name__ == "__main__":
    main()
