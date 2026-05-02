#!/usr/bin/env python3
"""
FC Lockup Debugger

When MSP times out, this script captures the FC state via ST-Link/GDB
to help diagnose the lockup cause.

Usage:
    python3 debug_lockup.py [--port /dev/ttyACM0] [--openocd-config path]

Workflow:
    1. Try MSP communication
    2. On timeout, verify FC is still in CDC mode (not MSC)
    3. If CDC and not MSC, capture debug state via GDB
    4. Save registers, backtrace, thread info to log file
"""
import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def check_cdc_device(port: str) -> bool:
    """Check if CDC device exists"""
    return os.path.exists(port)


def check_msc_device() -> bool:
    """Check if MSC block device exists (FC in MSC mode)"""
    for device in ['/dev/sdb', '/dev/sdb1', '/dev/sdc', '/dev/sdc1']:
        if os.path.exists(device):
            return True
    return False


def try_msp_query(port: str, timeout: float = 2.0) -> bool:
    """Try a simple MSP query. Returns True if successful."""
    try:
        import serial
        import struct
        
        ser = serial.Serial(port, 115200, timeout=timeout)
        
        # Send MSP_SDCARD_SUMMARY (79)
        # MSP v1: $M< len code checksum
        msp_request = b'$M<\x00\x4f\x4f'  # len=0, code=79, checksum=79
        ser.write(msp_request)
        ser.flush()
        
        # Try to read response
        start = time.time()
        response = b''
        while time.time() - start < timeout:
            chunk = ser.read(100)
            if chunk:
                response += chunk
                if b'$M!' in response or b'$M>' in response:
                    break
            time.sleep(0.1)
        
        ser.close()
        
        # Check for valid MSP response
        if b'$M>' in response and len(response) >= 10:
            return True
        return False
        
    except Exception as e:
        print(f"  MSP query error: {e}")
        return False


def capture_gdb_state(openocd_config: str, output_file: str):
    """
    Capture FC state via GDB.
    
    Requires OpenOCD running in the background or spawns it.
    """
    print("\n" + "="*60)
    print("CAPTURING DEBUG STATE VIA GDB")
    print("="*60)
    
    # Create GDB command file
    gdb_commands = f"""
set pagination off
set confirm off

target extended-remote :3333

echo \\n=== REGISTERS ===\\n
info registers

echo \\n=== BACKTRACE ===\\n
bt

echo \\n=== CURRENT FRAME ===\\n
info frame

echo \\n=== DISASSEMBLY AT PC ===\\n
disassemble $pc-20,$pc+20

echo \\n=== THREAD INFO ===\\n
info threads

echo \\n=== MEMORY AT SP ===\\n
x/16x $sp

echo \\n=== TASK STATE (if FreeRTOS) ===\\n
x/32x 0x20000000

quit
"""
    
    gdb_cmd_file = Path(output_file).parent / "gdb_commands.txt"
    with open(gdb_cmd_file, 'w') as f:
        f.write(gdb_commands)
    
    # Start OpenOCD in background (connect without halting)
    print("  Starting OpenOCD...")
    openocd_proc = subprocess.Popen(
        ['openocd', '-f', openocd_config],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for OpenOCD to connect
    time.sleep(2)
    
    # Check if OpenOCD connected
    if openocd_proc.poll() is not None:
        stdout, stderr = openocd_proc.communicate()
        print(f"  OpenOCD failed to start:")
        print(stderr[-500:] if len(stderr) > 500 else stderr)
        return False
    
    print("  OpenOCD connected, running GDB...")
    
    # Run GDB
    gdb_result = subprocess.run(
        ['arm-none-eabi-gdb', '-x', str(gdb_cmd_file)],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Save output
    with open(output_file, 'w') as f:
        f.write(f"FC Lockup Debug Capture\n")
        f.write(f"Time: {datetime.now().isoformat()}\n")
        f.write("="*60 + "\n\n")
        f.write("=== GDB OUTPUT ===\n")
        f.write(gdb_result.stdout)
        f.write("\n=== GDB STDERR ===\n")
        f.write(gdb_result.stderr)
    
    print(f"  GDB output saved to: {output_file}")
    
    # Shutdown OpenOCD
    try:
        openocd_proc.terminate()
        openocd_proc.wait(timeout=5)
    except:
        openocd_proc.kill()
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Debug FC lockup via GDB")
    parser.add_argument('--port', default='/dev/ttyACM0', help='CDC port')
    parser.add_argument('--openocd-config', default='openocd_matekf765_no_halt.cfg',
                        help='OpenOCD config file')
    parser.add_argument('--output-dir', default='debug_captures', help='Output directory')
    parser.add_argument('--skip-msp', action='store_true', help='Skip MSP check, go straight to GDB')
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    print("="*60)
    print("FC LOCKUP DEBUGGER")
    print("="*60)
    print(f"Port: {args.port}")
    print(f"OpenOCD config: {args.openocd_config}")
    print(f"Output: {output_dir}")
    print()
    
    # Step 1: Check CDC device
    print("[1/5] Checking CDC device...")
    if not check_cdc_device(args.port):
        print(f"  ✗ CDC device {args.port} not found")
        print("  FC may be disconnected or in MSC mode")
        return 1
    print(f"  ✓ CDC device exists: {args.port}")
    
    # Step 2: Check MSC device
    print("\n[2/5] Checking for MSC device...")
    if check_msc_device():
        print("  ! MSC device detected - FC is in MSC mode, not a lockup")
        print("  Use 'msc_exit' to return to CDC mode")
        return 2
    print("  ✓ No MSC device - FC should be in CDC mode")
    
    # Step 3: Try MSP query
    if not args.skip_msp:
        print("\n[3/5] Testing MSP communication...")
        if try_msp_query(args.port):
            print("  ✓ MSP responding - FC is not locked up")
            return 0
        print("  ✗ MSP timeout - FC appears locked up")
    else:
        print("\n[3/5] Skipping MSP test (--skip-msp)")
    
    # Step 4: Capture debug state
    print("\n[4/5] Capturing debug state via GDB...")
    output_file = output_dir / f"lockup_{timestamp}.txt"
    
    if not os.path.exists(args.openocd_config):
        print(f"  ✗ OpenOCD config not found: {args.openocd_config}")
        return 3
    
    if capture_gdb_state(args.openocd_config, str(output_file)):
        print(f"  ✓ Debug state captured: {output_file}")
    else:
        print("  ✗ Failed to capture debug state")
        return 4
    
    # Step 5: Summary
    print("\n[5/5] Summary")
    print("-"*40)
    print(f"  CDC device: {args.port} (exists)")
    print(f"  MSC mode: No")
    print(f"  MSP response: Timeout (locked up)")
    print(f"  Debug capture: {output_file}")
    print()
    print("NEXT STEPS:")
    print("  1. Review the debug capture file")
    print("  2. Look at PC/LR to identify where FC is stuck")
    print("  3. Check backtrace for call chain")
    print("  4. FC may need power cycle to recover")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())