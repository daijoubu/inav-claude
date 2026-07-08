#!/usr/bin/env python3
"""
Monitor INAV FC memory and CPU load via CLI status command.
Keeps CLI session open (no 'exit') to avoid reboot.
Polls every INTERVAL_MINUTES minutes.
"""

import re
import sys
import time
import serial
import datetime

PORT        = "/dev/ttyACM0"
BAUD        = 115200
INTERVAL_S  = 15 * 60   # 15 minutes
READ_TIMEOUT = 5.0       # seconds to wait for response

HEAP_RE  = re.compile(r"Heap available:\s*(\d+)")
LOAD_RE  = re.compile(r"System load:\s*(\d+)")


def read_until_prompt(ser, timeout=READ_TIMEOUT):
    """Read until the CLI prompt '#' appears or timeout."""
    buf = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        chunk = ser.read(ser.in_waiting or 1)
        if chunk:
            buf += chunk
            if b"# " in buf or buf.endswith(b"#"):
                break
    return buf.decode("utf-8", errors="replace")


def enter_cli(ser):
    ser.write(b"#\r\n")
    time.sleep(0.5)
    ser.read(ser.in_waiting)  # discard banner


def send_status(ser):
    ser.write(b"status\r\n")
    return read_until_prompt(ser, timeout=READ_TIMEOUT)


def parse(output):
    heap = load = None
    m = HEAP_RE.search(output)
    if m:
        heap = int(m.group(1))
    m = LOAD_RE.search(output)
    if m:
        load = int(m.group(1))
    return heap, load


def main():
    print(f"Opening {PORT} at {BAUD} baud …", flush=True)
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(1.0)
    ser.reset_input_buffer()

    enter_cli(ser)
    print("CLI session open. First poll now, then every 15 minutes.", flush=True)
    print(f"{'TIMESTAMP':<26} {'CPU LOAD':>10} {'HEAP (bytes)':>14}", flush=True)
    print("-" * 54, flush=True)

    while True:
        output = send_status(ser)
        heap, load = parse(output)
        ts = datetime.datetime.now().isoformat(timespec="seconds")

        load_s = f"{load}%" if load is not None else "?"
        heap_s = str(heap)  if heap is not None else "?"
        print(f"{ts:<26} {load_s:>10} {heap_s:>14}", flush=True)

        if heap is None or load is None:
            # Print raw output so we can see what went wrong
            print("  [raw output below]")
            print(output)

        time.sleep(INTERVAL_S)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped. CLI session left open (no exit sent).")
        sys.exit(0)
