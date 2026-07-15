#!/usr/bin/env python3
"""
OSD MSP Displayport Regression Test
====================================
Checks whether the SITL firmware sends MSP Displayport frames (MSP code 182)
to a connected client.  A blank OSD (no frames / no DRAW_SCREEN sub-commands)
is the "no OSD at all" regression symptom reported on the
optimize/osd-sprintf-patterns branch.

Two-part test
-------------
1. CONNECTIVITY  – verifies SITL responds to MSP_API_VERSION (code 1).
   If this fails the test cannot continue and it is almost certainly a
   sandbox network restriction (retry with dangerouslyDisableSandbox).

2. OSD ACTIVE    – sends the MSP_DISPLAYPORT heartbeat sequence expected
   from a display device, then listens for MSP 182 frames from the FC.
   Within those frames it counts MSP_DP_DRAW_SCREEN (sub-command 4)
   and MSP_DP_WRITE_STRING (sub-command 3) events.
   The OSD is considered ACTIVE if at least one DRAW_SCREEN is received
   within the listen window.

Usage
-----
    # SITL must be running first:
    #   cd <inav2>/build_sitl_inav2 && ./bin/SITL.elf &
    #
    python3 test_osd_displayport.py [--host localhost] [--port 5760] [--duration 8]

Pass/Fail criteria
------------------
    PASS  – at least 1 DRAW_SCREEN received, >=1 WRITE_STRING received
    FAIL  – 0 DRAW_SCREEN received in the listen window  → OSD regression confirmed
    ERROR – cannot connect or FC not responding to MSP

Note: If running inside Claude sandbox, network access may be blocked.
      Retry with dangerouslyDisableSandbox: true in the Bash tool call.
"""

from __future__ import annotations

import argparse
import socket
import struct
import sys
import time
import threading
from collections import defaultdict

# ---------------------------------------------------------------------------
# MSP framing constants (V1)
# ---------------------------------------------------------------------------
MSP_SYNC1      = 0x24   # '$'
MSP_SYNC2_V1   = 0x4D   # 'M'
DIR_TO_FC      = 0x3C   # '<'
DIR_FROM_FC    = 0x3E   # '>'

MSP_API_VERSION = 1     # simple sanity check – FC always responds
MSP_DISPLAYPORT = 182   # 0xB6 – FC pushes these to the display client

# Displayport sub-commands (first byte of payload)
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
# Minimal MSP V1 framing helpers (no external dependencies)
# ---------------------------------------------------------------------------

def _xor_checksum(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b
    return crc & 0xFF


def build_msp_v1_request(code: int, payload: bytes = b"") -> bytes:
    """Build an MSP V1 request frame (direction TO_FC)."""
    ln = len(payload)
    header = bytes([MSP_SYNC1, MSP_SYNC2_V1, DIR_TO_FC, ln & 0xFF, code & 0xFF])
    crc = _xor_checksum(bytes([ln, code]) + payload)
    return header + payload + bytes([crc])


def parse_msp_v1_frames(buf: bytearray) -> tuple[list[tuple[int, bytes]], bytearray]:
    """
    Parse zero or more complete MSP V1 frames out of buf.
    Returns (list_of_(code, payload), remaining_unconsumed_bytes).
    Only frames with DIR_FROM_FC direction are returned.
    """
    frames: list[tuple[int, bytes]] = []
    i = 0
    n = len(buf)
    while i < n:
        # Search for '$'
        if buf[i] != MSP_SYNC1:
            i += 1
            continue
        # Need at least 6 bytes: $ M > len code crc
        if i + 5 > n:
            break
        if buf[i + 1] != MSP_SYNC2_V1:
            i += 1
            continue
        direction = buf[i + 2]
        length    = buf[i + 3]
        code      = buf[i + 4]
        # Need header (5) + payload (length) + crc (1)
        if i + 5 + length + 1 > n:
            break   # frame not complete yet
        payload = bytes(buf[i + 5 : i + 5 + length])
        crc_byte = buf[i + 5 + length]
        expected_crc = _xor_checksum(bytes([length, code]) + payload)
        if crc_byte != expected_crc:
            # bad checksum – skip this '$' and keep scanning
            i += 1
            continue
        if direction == DIR_FROM_FC:
            frames.append((code, payload))
        # advance past this frame regardless of direction
        i += 6 + length
    return frames, bytearray(buf[i:])


# ---------------------------------------------------------------------------
# TCP connection helper
# ---------------------------------------------------------------------------

class TCPConn:
    def __init__(self, host: str, port: int, timeout: float = 2.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock: socket.socket | None = None
        self._buf = bytearray()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.on_frame: callable | None = None   # (code, payload) -> None

    def connect(self) -> bool:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            s.connect((self.host, self.port))
            s.settimeout(0.05)   # short timeout for recv loop
            self._sock = s
            return True
        except (ConnectionRefusedError, socket.timeout, OSError) as exc:
            print(f"  [TCP] Connection to {self.host}:{self.port} failed: {exc}")
            return False

    def start_reader(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()

    def _reader(self) -> None:
        while not self._stop.is_set():
            try:
                chunk = self._sock.recv(4096)
                if not chunk:
                    break
                with self._lock:
                    self._buf.extend(chunk)
                    frames, self._buf = parse_msp_v1_frames(self._buf)
                for code, payload in frames:
                    if self.on_frame:
                        self.on_frame(code, payload)
            except socket.timeout:
                continue
            except (OSError, BrokenPipeError):
                break

    def send(self, data: bytes) -> bool:
        if not self._sock:
            return False
        try:
            self._sock.sendall(data)
            return True
        except OSError as exc:
            print(f"  [TCP] Send failed: {exc}")
            return False

    def close(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None


# ---------------------------------------------------------------------------
# Test logic
# ---------------------------------------------------------------------------

def run_test(host: str, port: int, duration: float) -> int:
    """
    Run the displayport OSD test.
    Returns 0 on PASS, 1 on FAIL (OSD regression), 2 on ERROR.
    """
    print()
    print("=" * 65)
    print("  OSD MSP Displayport Regression Test")
    print("=" * 65)
    print(f"  Target : {host}:{port}")
    print(f"  Listen : {duration:.0f} seconds")
    print()

    conn = TCPConn(host, port)

    # -----------------------------------------------------------------------
    # Part 1: Connectivity check
    # -----------------------------------------------------------------------
    print("Part 1: Connectivity check (MSP_API_VERSION)")
    print("-" * 50)

    if not conn.connect():
        print()
        print("  RESULT: ERROR – cannot connect")
        print("  Is SITL running?  cd build_sitl_inav2 && ./bin/SITL.elf &")
        print()
        print("  Note: If running in Claude sandbox, network is blocked by default.")
        print("        Retry the Bash tool call with  dangerouslyDisableSandbox: true")
        return 2

    print("  ✓ TCP connection established")

    # Set up a simple sync check: send MSP_API_VERSION request, look for reply
    version_reply: list[tuple[int, bytes]] = []
    version_evt = threading.Event()

    def on_frame_version(code: int, payload: bytes) -> None:
        if code == MSP_API_VERSION:
            version_reply.append((code, payload))
            version_evt.set()

    conn.on_frame = on_frame_version
    conn.start_reader()

    req = build_msp_v1_request(MSP_API_VERSION)
    if not conn.send(req):
        print("  ✗ Failed to send MSP_API_VERSION request")
        conn.close()
        return 2

    if not version_evt.wait(timeout=2.0):
        print("  ✗ No response to MSP_API_VERSION (timeout 2s)")
        print()
        print("  FC is NOT responding.  Possible causes:")
        print("    • SITL is not running")
        print("    • Another process is connected (close Configurator)")
        print("    • SITL is stuck in CLI mode – send 'exit\\n' to port")
        print("    • Sandbox network restriction")
        conn.close()
        return 2

    print(f"  ✓ FC responded to MSP_API_VERSION  (payload: {version_reply[0][1].hex()})")
    print()

    # -----------------------------------------------------------------------
    # Part 2: OSD displayport activity check
    # -----------------------------------------------------------------------
    print("Part 2: OSD MSP Displayport activity")
    print("-" * 50)
    print(f"  Sending periodic displayport heartbeats for {duration:.0f}s …")
    print()

    sub_counts: dict[int, int] = defaultdict(int)
    frame_count = 0

    def on_frame_osd(code: int, payload: bytes) -> None:
        nonlocal frame_count
        if code == MSP_DISPLAYPORT:
            frame_count += 1
            subcmd = payload[0] if payload else -1
            sub_counts[subcmd] += 1

    conn.on_frame = on_frame_osd

    # Send displayport heartbeat at ~10 Hz to stimulate OSD rendering.
    # The FC only pushes displayport frames when a display client is present,
    # signalled by receiving MSP_DISPLAYPORT heartbeat (sub-command 0) from us.
    heartbeat_frame = build_msp_v1_request(MSP_DISPLAYPORT, bytes([MSP_DP_HEARTBEAT]))

    deadline = time.monotonic() + duration
    tick = 0
    while time.monotonic() < deadline:
        conn.send(heartbeat_frame)
        time.sleep(0.1)   # 10 Hz
        tick += 1
        if tick % 20 == 0:   # progress dot every 2s
            elapsed = duration - (deadline - time.monotonic())
            draws = sub_counts.get(MSP_DP_DRAW, 0)
            writes = sub_counts.get(MSP_DP_WRITE, 0)
            print(f"  [{elapsed:4.1f}s] MSP-182 frames: {frame_count:4d}  "
                  f"DRAW_SCREEN: {draws:3d}  WRITE_STRING: {writes:4d}")

    conn.close()

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
    print(f"  Total MSP-182 frames received : {frame_count}")
    for subcmd, count in sorted(sub_counts.items()):
        name = SUBCMD_NAMES.get(subcmd, f"UNKNOWN({subcmd})")
        print(f"    sub-cmd {subcmd} ({name:15s}) : {count:4d}")
    print("=" * 65)
    print()

    if draws == 0:
        print("  RESULT: FAIL")
        print()
        print("  BUG CONFIRMED: No DRAW_SCREEN frames received in "
              f"{duration:.0f} seconds.")
        print("  The OSD is completely silent – matches the reported")
        print("  'no OSD at all' regression on optimize/osd-sprintf-patterns.")
        print()
        if frame_count == 0:
            print("  No MSP-182 frames at all.  Possible additional causes:")
            print("    • OSD not enabled in SITL config")
            print("    • displayport not configured on UART1")
        else:
            print(f"  Received {frame_count} MSP-182 frames but none had DRAW_SCREEN.")
            print("  This suggests the OSD loop is running but not completing renders.")
        return 1
    else:
        print("  RESULT: PASS")
        print()
        print(f"  OSD is active: {draws} DRAW_SCREEN + {writes} WRITE_STRING frames.")
        if writes == 0:
            print()
            print("  WARNING: DRAW_SCREEN received but no WRITE_STRING frames.")
            print("  This could mean all OSD elements produce empty strings –")
            print("  a partial regression where rendering runs but outputs nothing.")
        return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="OSD MSP Displayport regression test for SITL"
    )
    parser.add_argument("--host",     default="localhost", help="SITL host (default: localhost)")
    parser.add_argument("--port",     type=int, default=5760, help="SITL MSP port (default: 5760)")
    parser.add_argument("--duration", type=float, default=8.0,
                        help="Seconds to listen for displayport frames (default: 8)")
    args = parser.parse_args()

    rc = run_test(args.host, args.port, args.duration)
    return rc


if __name__ == "__main__":
    sys.exit(main())
