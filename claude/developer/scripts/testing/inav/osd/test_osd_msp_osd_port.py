#!/usr/bin/env python3
"""
OSD MSP_OSD Port Regression Test
==================================
Tests OSD output via the MSP_OSD protocol on UART2 (port 5761).

This is the CORRECT test for the SITL OSD path.  The SITL target uses
USE_MSP_OSD (not USE_MSP_DISPLAYPORT), which means:

  - OSD frames are pushed out on a UART configured as FUNCTION_MSP_OSD
  - In SITL that is UART2, mapped to TCP port 5761
  - The FC only sends OSD frames when a VTX device is detected (vtxActive=true)
  - vtxActive becomes true when ANY MSP request arrives on port 5761

Setup required (one-time via Configurator or CLI):
  serial 1 33554432 115200 115200 0 115200
  save

Where 33554432 = FUNCTION_MSP_OSD (1 << 25).

Usage
-----
    # Start SITL first:
    #   cd <inav>/build_sitl && ./bin/SITL.elf &
    #
    python3 test_osd_msp_osd_port.py [--host localhost] [--msp-port 5760]
                                      [--osd-port 5761] [--duration 12]

Pass/Fail criteria
------------------
    PASS  - at least 1 DRAW_SCREEN (sub-cmd 4) received on osd-port
    FAIL  - 0 DRAW_SCREEN frames received  →  OSD regression confirmed
    ERROR - cannot connect or FC not responding

Note: If running in Claude sandbox, retry with dangerouslyDisableSandbox: true.
"""

from __future__ import annotations

import argparse
import socket
import time
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# MSP V1 framing constants
# ---------------------------------------------------------------------------
MSP_SYNC1      = 0x24   # '$'
MSP_SYNC2_V1   = 0x4D   # 'M'
DIR_TO_FC      = 0x3C   # '<'
DIR_FROM_FC    = 0x3E   # '>'

MSP_API_VERSION = 1     # ping to trigger vtxActive
MSP_DISPLAYPORT = 182   # 0xB6

# Displayport sub-commands
MSP_DP_HEARTBEAT   = 0
MSP_DP_RELEASE     = 1
MSP_DP_CLEAR       = 2
MSP_DP_WRITE       = 3
MSP_DP_DRAW        = 4
MSP_DP_OPTIONS     = 5

SUBCMD_NAMES = {
    MSP_DP_HEARTBEAT: "HEARTBEAT",
    MSP_DP_RELEASE:   "RELEASE",
    MSP_DP_CLEAR:     "CLEAR_SCREEN",
    MSP_DP_WRITE:     "WRITE_STRING",
    MSP_DP_DRAW:      "DRAW_SCREEN",
    MSP_DP_OPTIONS:   "OPTIONS",
}


# ---------------------------------------------------------------------------
# MSP helpers
# ---------------------------------------------------------------------------

def xor_crc(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b
    return crc & 0xFF


def build_req(code: int, payload: bytes = b"") -> bytes:
    ln = len(payload)
    header = bytes([MSP_SYNC1, MSP_SYNC2_V1, DIR_TO_FC, ln & 0xFF, code & 0xFF])
    crc = xor_crc(bytes([ln, code]) + payload)
    return header + payload + bytes([crc])


def parse_frames(buf: bytearray) -> tuple[list[tuple[int, bytes]], bytearray]:
    frames: list[tuple[int, bytes]] = []
    i = 0
    n = len(buf)
    while i < n:
        if buf[i] != MSP_SYNC1:
            i += 1
            continue
        if i + 5 > n:
            break
        if buf[i + 1] != MSP_SYNC2_V1:
            i += 1
            continue
        direction = buf[i + 2]
        length    = buf[i + 3]
        code      = buf[i + 4]
        if i + 5 + length + 1 > n:
            break
        payload = bytes(buf[i + 5 : i + 5 + length])
        i += 6 + length
        if direction == DIR_FROM_FC:
            frames.append((code, payload))
    return frames, bytearray(buf[i:])


def connect(host: str, port: int, label: str = "") -> socket.socket | None:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        s.connect((host, port))
        s.settimeout(0.05)
        if label:
            print(f"  ✓ Connected to {label} ({host}:{port})")
        return s
    except (ConnectionRefusedError, socket.timeout, OSError) as exc:
        label_str = f" ({label})" if label else ""
        print(f"  ✗ Cannot connect to {host}:{port}{label_str}: {exc}")
        print()
        print("  Note: If running in Claude sandbox, network is blocked by default.")
        print("        Retry the Bash tool call with  dangerouslyDisableSandbox: true")
        return None


def check_msp_responding(sock: socket.socket) -> bool:
    """Send MSP_API_VERSION and check for a response."""
    req = build_req(MSP_API_VERSION)
    try:
        sock.sendall(req)
    except OSError:
        return False

    buf = bytearray()
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                return False
            buf.extend(chunk)
            frames, buf = parse_frames(buf)
            for code, payload in frames:
                if code == MSP_API_VERSION:
                    return True
        except socket.timeout:
            pass
    return False


# ---------------------------------------------------------------------------
# Test logic
# ---------------------------------------------------------------------------

def run_test(host: str, msp_port: int, osd_port: int, duration: float) -> int:
    print()
    print("=" * 65)
    print("  OSD MSP_OSD Port Regression Test")
    print("=" * 65)
    print(f"  Host        : {host}")
    print(f"  MSP port    : {msp_port}  (main MSP, for sanity check)")
    print(f"  OSD port    : {osd_port}  (FUNCTION_MSP_OSD / UART2)")
    print(f"  Listen time : {duration:.0f} s")
    print()

    # -----------------------------------------------------------------------
    # Part 1: Connectivity via main MSP port
    # -----------------------------------------------------------------------
    print("Part 1: Connectivity (MSP_API_VERSION on main MSP port)")
    print("-" * 55)

    msp_sock = connect(host, msp_port, "MSP port")
    if not msp_sock:
        return 2

    if not check_msp_responding(msp_sock):
        print(f"  ✗ FC is not responding to MSP_API_VERSION on port {msp_port}")
        print()
        print("  Possible causes:")
        print("    • SITL is not running")
        print("    • Another client is connected (close Configurator)")
        print("    • SITL left in CLI mode – send 'exit\\n' to the port")
        msp_sock.close()
        return 2

    print(f"  ✓ FC responds to MSP on port {msp_port}")
    msp_sock.close()
    print()

    # -----------------------------------------------------------------------
    # Part 2: OSD activity on the MSP_OSD port
    # -----------------------------------------------------------------------
    print("Part 2: OSD output on MSP_OSD port")
    print("-" * 55)
    print()
    print("  IMPORTANT: The FC only pushes OSD frames after receiving an MSP")
    print("  request on the OSD port (vtxActive trigger).  This test sends")
    print("  MSP_API_VERSION at 10 Hz to keep the FC producing OSD frames.")
    print()

    osd_sock = connect(host, osd_port, "MSP_OSD port")
    if not osd_sock:
        print()
        print("  Is the SITL serial port configured as FUNCTION_MSP_OSD?")
        print("  Run via CLI:  serial 1 33554432 115200 115200 0 115200")
        print("                save")
        return 2

    print(f"  Listening for {duration:.0f}s …")
    print()

    sub_counts: dict[int, int] = defaultdict(int)
    total_182 = 0
    buf = bytearray()
    api_req = build_req(MSP_API_VERSION)

    # Send first request immediately to trigger vtxActive
    try:
        osd_sock.sendall(api_req)
    except OSError as exc:
        print(f"  ✗ Failed to send initial trigger: {exc}")
        osd_sock.close()
        return 2

    deadline = time.monotonic() + duration
    tick = 0
    while time.monotonic() < deadline:
        # Send heartbeat to keep vtxActive = true
        try:
            osd_sock.sendall(api_req)
        except OSError:
            print("  ✗ Connection lost during test")
            break

        time.sleep(0.1)   # 10 Hz

        try:
            chunk = osd_sock.recv(4096)
            if chunk:
                buf.extend(chunk)
                frames, buf = parse_frames(buf)
                for code, payload in frames:
                    if code == MSP_DISPLAYPORT:
                        total_182 += 1
                        subcmd = payload[0] if payload else -1
                        sub_counts[subcmd] += 1
        except socket.timeout:
            pass

        tick += 1
        if tick % 20 == 0:
            elapsed = duration - (deadline - time.monotonic())
            draws  = sub_counts.get(MSP_DP_DRAW, 0)
            writes = sub_counts.get(MSP_DP_WRITE, 0)
            print(f"  [{elapsed:5.1f}s] MSP-182: {total_182:5d}  "
                  f"DRAW_SCREEN: {draws:4d}  WRITE_STRING: {writes:4d}")

    osd_sock.close()

    # -----------------------------------------------------------------------
    # Results
    # -----------------------------------------------------------------------
    draws  = sub_counts.get(MSP_DP_DRAW, 0)
    writes = sub_counts.get(MSP_DP_WRITE, 0)
    clears = sub_counts.get(MSP_DP_CLEAR, 0)

    print()
    print("=" * 65)
    print("  MSP Displayport frame summary")
    print("-" * 65)
    print(f"  Total MSP-182 frames received : {total_182}")
    for subcmd, count in sorted(sub_counts.items()):
        name = SUBCMD_NAMES.get(subcmd, f"UNKNOWN({subcmd})")
        print(f"    sub-cmd {subcmd} ({name:15s}) : {count:5d}")
    print("=" * 65)
    print()

    if draws == 0:
        print("  RESULT: FAIL")
        print()
        print("  BUG CONFIRMED: No DRAW_SCREEN frames received in "
              f"{duration:.0f} seconds.")
        print()
        if total_182 == 0:
            print("  Zero MSP-182 frames received at all.  Check:")
            print("    • Is the serial port configured as FUNCTION_MSP_OSD?")
            print("      CLI: serial 1 33554432 115200 115200 0 115200")
            print("    • Is FEATURE_OSD enabled?  CLI: feature OSD")
            print("    • Has the config been saved?  CLI: save")
        elif writes == 0:
            print("  MSP-182 frames were received but none had DRAW_SCREEN.")
            print("  The OSD loop is running but not completing any draws.")
            print("  This could indicate the rendering pipeline is crashing")
            print("  or skipping all elements.")
        else:
            print(f"  {writes} WRITE_STRING frames but 0 DRAW_SCREEN.")
            print("  OSD is writing strings but never flushing the screen.")
        return 1
    else:
        print("  RESULT: PASS")
        print()
        print(f"  OSD is active: {draws} DRAW_SCREEN + {writes} WRITE_STRING frames.")
        if writes == 0:
            print()
            print("  WARNING: DRAW_SCREEN received but no WRITE_STRING.")
            print("  OSD renders but writes nothing – possible empty element regression.")
        return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="OSD MSP_OSD port regression test for INAV SITL"
    )
    parser.add_argument("--host",     default="localhost",
                        help="SITL host (default: localhost)")
    parser.add_argument("--msp-port", type=int, default=5760,
                        help="Main MSP port for connectivity check (default: 5760)")
    parser.add_argument("--osd-port", type=int, default=5761,
                        help="MSP_OSD port (UART2, default: 5761)")
    parser.add_argument("--duration", type=float, default=12.0,
                        help="Seconds to listen for OSD frames (default: 12)")
    args = parser.parse_args()

    return run_test(args.host, args.msp_port, args.osd_port, args.duration)


if __name__ == "__main__":
    sys.exit(main())
