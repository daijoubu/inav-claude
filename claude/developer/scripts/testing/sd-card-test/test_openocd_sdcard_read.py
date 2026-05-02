#!/usr/bin/env python3
"""
Test: Read SD Card Status via OpenOCD

Validates that we can read SD card state from FC memory using OpenOCD + GDB.
This is the first step in extending the test suite with hardware introspection.

Usage:
    cd /home/robs/Projects/inav-claude
    python3 claude/developer/workspace/sd-card-test-plan/test_openocd_sdcard_read.py /dev/ttyACM0 inav/build/bin/MATEKF765SE.elf
"""
import sys
import os
from pathlib import Path

# Setup path - must be done before imports
# Go up from sd-card-test-plan -> workspace -> developer -> claude -> project root
project_root = Path(__file__).parents[4]
scripts_dir = str(project_root / 'claude' / 'developer' / 'scripts')

# Change working directory to project root
os.chdir(project_root)

# Add scripts dir to path
sys.path.insert(0, scripts_dir)

# NOW import from our packages
from testing.hitl.hitl_sdcard import HITLSDCard

def main():
    if len(sys.argv) < 2:
        port = '/dev/ttyACM0'
        elf = 'inav/build/bin/MATEKF765SE.elf'
        print(f"Usage: {sys.argv[0]} [port] [elf_file]")
        print(f"Using defaults: {port} {elf}")
    else:
        port = sys.argv[1]
        elf = sys.argv[2] if len(sys.argv) > 2 else 'inav/build/bin/MATEKF765SE.elf'

    print("="*60)
    print("TEST: Read SD Card Status via OpenOCD")
    print("="*60)
    print(f"Port: {port}")
    print(f"ELF:  {elf}")
    print(f"CWD:  {os.getcwd()}")
    print()

    # Step 1: Verify files exist
    print("[1/4] Verifying files...")
    if not os.path.exists(port):
        print(f"  ✗ CDC device not found: {port}")
        return 1
    print(f"  ✓ CDC device exists: {port}")

    if not os.path.exists(elf):
        print(f"  ✗ ELF file not found: {elf}")
        return 1
    print(f"  ✓ ELF file found: {elf}")

    # Step 2: Initialize HITL
    print("\n[2/4] Initializing HITL SD Card module...")
    try:
        hitl = HITLSDCard(port, elf_path=elf)
        print("  ✓ HITL module initialized")
    except Exception as e:
        print(f"  ✗ Failed to initialize: {e}")
        return 1

    # Step 3: Load symbols
    print("\n[3/4] Loading ELF symbols...")
    if not hitl.load_symbols():
        print("  ✗ Failed to load symbols")
        print("     This may be expected if symbols are stripped")
        # Don't fail - some builds might not have symbols
    else:
        print("  ✓ Symbols loaded successfully")

    # Step 4: Read SD card state
    print("\n[4/4] Reading SD card state via OpenOCD...")
    try:
        state = hitl.get_sdcard_state()
        if state:
            print(f"  ✓ SD card state read successfully:")
            print(f"     State: {state.state_name} ({state.state})")
            print(f"     Consecutive Errors: {state.consecutive_errors}")
            print(f"     DMA Busy: {state.dma_busy}")
            print(f"     Total Writes: {state.total_writes}")
            print(f"     Total Reads: {state.total_reads}")
            print(f"     Write Errors: {state.write_errors}")
            print(f"     Read Errors: {state.read_errors}")
        else:
            print("  ✗ Failed to read SD card state (got None)")
            return 1
    except Exception as e:
        print(f"  ✗ Exception reading SD card state: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Step 5: Read AFATFS filesystem state
    print("\n[5/5] Reading AFATFS filesystem state via OpenOCD...")
    try:
        afatfs_state = hitl.get_afatfs_state()
        if afatfs_state:
            print(f"  ✓ AFATFS state read successfully:")
            print(f"     Filesystem State: {afatfs_state.filesystem_state_name} ({afatfs_state.filesystem_state})")
            print(f"     Last Error: {afatfs_state.last_error_name} ({afatfs_state.last_error})")
        else:
            print("  ✗ Failed to read AFATFS state (got None)")
    except Exception as e:
        print(f"  ✗ Exception reading AFATFS state: {e}")
        import traceback
        traceback.print_exc()

    # Step 6: Get MSP comparable state
    print("\n[6/6] Getting MSP comparable state...")
    try:
        msp_state = hitl.get_msp_comparable_state()
        if msp_state:
            print(f"  ✓ MSP comparable state ready:")
            print(f"     sdcard state: {msp_state.get('sdcard_state')}")
            print(f"     afatfs state: {msp_state.get('afatfs_state')}")
            print(f"     Notes: {msp_state.get('notes')}")
    except Exception as e:
        print(f"  ✗ Exception getting MSP comparable state: {e}")

    print("\n" + "="*60)
    print("SUCCESS: SD Card state can be read via OpenOCD!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Integrate into baseline test suite")
    print("  2. Add fault injection for error scenarios")
    print("  3. Monitor SD card state during test execution")

    return 0

if __name__ == '__main__':
    sys.exit(main())
