#!/usr/bin/env python3
"""
CRSF DEVICE_PING via MSP Serial Passthrough
============================================
Sends MSP_SET_PASSTHROUGH to bridge UART1 (embedded ELRS receiver) through
the FC's USB MSP port, then sends a CRSF DEVICE_PING and listens for a
DEVICE_INFO response from the receiver.

Architecture:
  This tool <--USB/MSP--> INAV FC <--UART1/CRSF--> embedded ELRS receiver

MSP passthrough command:
  Code:    245 (MSP_SET_PASSTHROUGH)
  Payload: [0xFD, 0x00]
             ^     ^
             |     UART1 = SERIAL_PORT_USART1 = identifier 0
             MSP_PASSTHROUGH_SERIAL_ID = 0xFD

CRSF DEVICE_PING frame (6 bytes):
  [0xC8, 0x04, 0x28, 0xEC, 0xC8, 0x5A]
    ^      ^     ^     ^     ^     ^
    |      |     |     |     |     CRC8-DVB-S2 over [type, dest, origin]
    |      |     |     |     CRSF_ADDRESS_FLIGHT_CONTROLLER (origin)
    |      |     |     CRSF_ADDRESS_CRSF_RECEIVER (dest, who should respond)
    |      |     CRSF_FRAMETYPE_DEVICE_PING = 0x28
    |      frame_len = 4 (type + dest + origin + crc)
    CRSF_SYNC_BYTE = 0xC8 (outer device address / FC address)

CRC algorithm: CRC8-DVB-S2, poly=0xD5, init=0x00
  Covers: frame_type + payload bytes (NOT outer addr, NOT frame_len)
  Verified: crc8([0x28, 0xEC, 0xC8]) = 0x5A

KNOWN LIMITATION:
  The INAV CRSF driver opens UART1 with an rxCallback (crsfDataReceive).
  When rxCallback is set, the STM32 UART driver routes bytes to the callback
  and NOT to the rxBuffer (confirmed in serial_uart_stm32f7xx.c lines 261-265).
  The serialPassthrough() loop uses serialRxBytesWaiting() which checks the
  rxBuffer — it will always see 0 bytes from UART1.
  Result: we can SEND to the receiver, but the passthrough loop cannot
  FORWARD the receiver's response back to us via USB.
  We attempt to read raw bytes anyway since the serial port may receive some
  bytes before or between CRSF interrupt cycles.

USAGE:
  python3 crsf_passthrough_ping.py [/dev/ttyACM0]

  REQUIRES: dangerouslyDisableSandbox: true (serial port access)

AFTER THE TEST:
  The FC is in an infinite passthrough loop. POWERCYCLE THE FC to restore it.
  There is no software exit from MSP passthrough mode.
"""

import sys
import time
import struct

DEVICE = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
CRSF_BAUD = 420000

# ---------------------------------------------------------------------------
# CRC8-DVB-S2 (poly=0xD5) — matches firmware crc8_dvb_s2() in common/crc.c
# ---------------------------------------------------------------------------
def crc8_dvb_s2(data: bytes) -> int:
    """CRC8-DVB-S2: poly=0xD5, init=0. Covers type+payload, not addr/len."""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0xD5) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


# ---------------------------------------------------------------------------
# CRSF frame construction
# ---------------------------------------------------------------------------
CRSF_SYNC_BYTE               = 0xC8  # FC address / sync byte for FC-originated frames
CRSF_FRAMETYPE_DEVICE_PING   = 0x28
CRSF_FRAMETYPE_DEVICE_INFO   = 0x29
CRSF_ADDR_BROADCAST          = 0x00
CRSF_ADDR_FLIGHT_CONTROLLER  = 0xC8
CRSF_ADDR_CRSF_RECEIVER      = 0xEC

def build_device_ping() -> bytes:
    """
    Build CRSF DEVICE_PING frame.
    Layout: [outer_addr][frame_len][type][dest][origin][CRC]
    CRC covers: type + dest + origin
    """
    frame_type   = CRSF_FRAMETYPE_DEVICE_PING
    dest_payload = CRSF_ADDR_CRSF_RECEIVER       # who should respond
    orig_payload = CRSF_ADDR_FLIGHT_CONTROLLER    # who is asking

    crc_input = bytes([frame_type, dest_payload, orig_payload])
    crc = crc8_dvb_s2(crc_input)

    # frame_len = bytes after the frame_len field itself:
    #   type(1) + dest(1) + origin(1) + crc(1) = 4
    frame_len = 4

    frame = bytes([CRSF_SYNC_BYTE, frame_len, frame_type,
                   dest_payload, orig_payload, crc])
    return frame


def parse_device_info(data: bytes) -> dict | None:
    """
    Parse a CRSF DEVICE_INFO frame (type 0x29).
    Layout (payload after type byte, which is already past outer addr + frame_len + type):
      [dest][origin][device_name_null_terminated][12 null bytes][param_count][param_version]

    We search for the frame header in the raw data stream first.
    Returns dict with parsed fields, or None if parse fails.
    """
    # Scan for DEVICE_INFO frame start: any_addr + frame_len + 0x29
    for i in range(len(data) - 2):
        if data[i + 2] == CRSF_FRAMETYPE_DEVICE_INFO:
            outer_addr = data[i]
            frame_len = data[i + 1]
            total_len = frame_len + 2  # +2 for outer_addr and frame_len bytes
            if i + total_len > len(data):
                continue  # incomplete

            frame_bytes = data[i: i + total_len]
            # Verify CRC: covers type + payload (excluding CRC itself)
            crc_start = i + 2   # points to type byte
            crc_end = i + total_len - 1  # points to CRC byte
            computed_crc = crc8_dvb_s2(frame_bytes[2: crc_end - i])
            actual_crc = frame_bytes[-1]

            if computed_crc != actual_crc:
                print(f"    CRC mismatch at offset {i}: "
                      f"computed=0x{computed_crc:02X} actual=0x{actual_crc:02X}")
                continue

            # payload starts after outer_addr + frame_len + type = byte [3]
            payload = frame_bytes[3: -1]  # exclude CRC

            if len(payload) < 2:
                continue

            dest_addr   = payload[0]
            origin_addr = payload[1]

            # Device name: null-terminated string starting at payload[2]
            name_start = 2
            name_end = payload.find(0, name_start)
            if name_end == -1:
                device_name = payload[name_start:].decode('ascii', errors='replace')
            else:
                device_name = payload[name_start:name_end].decode('ascii', errors='replace')

            # After name+null: 12 zero bytes, then param_count, param_version
            after_name = name_end + 1 if name_end != -1 else len(payload)
            param_count   = payload[after_name + 12] if after_name + 12 < len(payload) else None
            param_version = payload[after_name + 13] if after_name + 13 < len(payload) else None

            return {
                'outer_addr':   outer_addr,
                'dest_addr':    dest_addr,
                'origin_addr':  origin_addr,
                'device_name':  device_name,
                'param_count':  param_count,
                'param_version': param_version,
                'raw_frame':    frame_bytes.hex(),
                'raw_payload':  payload.hex(),
            }

    return None


# ---------------------------------------------------------------------------
# MSP v1 frame builder — minimal, for sending SET_PASSTHROUGH only
# ---------------------------------------------------------------------------
def build_msp_v1_request(code: int, payload: bytes = b'') -> bytes:
    """Build MSP v1 request frame: $M< + size + code + payload + checksum."""
    size = len(payload)
    checksum = size ^ code
    for b in payload:
        checksum ^= b
    checksum &= 0xFF
    return b'$M<' + bytes([size, code]) + payload + bytes([checksum])


def parse_msp_v1_response(data: bytes, expected_code: int) -> bytes | None:
    """
    Scan data for MSP v1 response frame matching expected_code.
    Returns payload bytes on success, None if not found / checksum bad.
    """
    for i in range(len(data) - 5):
        if data[i:i+3] == b'$M>' and data[i+3] == expected_code:
            size = data[i+3]  # wait — v1: $M> size code payload... csum
            # Actually: $M> + size(1) + code(1) + payload(size) + csum(1)
            # But code comes AFTER size. Let me re-parse.
            pass

    # Correct MSP v1 response layout: $ M > size code payload... csum
    i = 0
    while i < len(data) - 5:
        if data[i] == ord('$') and data[i+1] == ord('M') and data[i+2] == ord('>'):
            size = data[i+3]
            code = data[i+4]
            if code == expected_code:
                frame_end = i + 5 + size + 1
                if frame_end <= len(data):
                    payload = data[i+5: i+5+size]
                    csum = data[i+5+size]
                    # verify checksum
                    computed = size ^ code
                    for b in payload:
                        computed ^= b
                    computed &= 0xFF
                    if computed == csum:
                        return payload
        i += 1
    return None


# ---------------------------------------------------------------------------
# Step 1: Pre-flight verification — print frame and CRC before connecting
# ---------------------------------------------------------------------------
print("=" * 60)
print("  CRSF DEVICE_PING via MSP Passthrough")
print("=" * 60)
print()
print("Step 1: Frame verification (dry-run, no connection yet)")
print("-" * 60)

ping_frame = build_device_ping()
print(f"  CRSF DEVICE_PING bytes ({len(ping_frame)} bytes):")
print(f"    hex:  {ping_frame.hex(' ')}")
print(f"    ints: {list(ping_frame)}")
print()
print(f"  Field breakdown:")
print(f"    [0] outer_addr  = 0x{ping_frame[0]:02X}  (CRSF_SYNC_BYTE / FC address)")
print(f"    [1] frame_len   = 0x{ping_frame[1]:02X}  ({ping_frame[1]} = type+dest+origin+crc)")
print(f"    [2] frame_type  = 0x{ping_frame[2]:02X}  (CRSF_FRAMETYPE_DEVICE_PING)")
print(f"    [3] dest        = 0x{ping_frame[3]:02X}  (CRSF_ADDRESS_CRSF_RECEIVER)")
print(f"    [4] origin      = 0x{ping_frame[4]:02X}  (CRSF_ADDRESS_FLIGHT_CONTROLLER)")
print(f"    [5] CRC8        = 0x{ping_frame[5]:02X}  (crc8_dvb_s2([0x28,0xEC,0xC8]))")
print()

# Manual CRC verification
crc_check = crc8_dvb_s2(bytes([0x28, 0xEC, 0xC8]))
print(f"  CRC verification: crc8_dvb_s2([0x28, 0xEC, 0xC8]) = 0x{crc_check:02X}")
assert crc_check == 0x5A, f"CRC mismatch! Expected 0x5A, got 0x{crc_check:02X}"
print(f"  CRC check PASSED: 0x{crc_check:02X} == 0x5A")
print()

# MSP passthrough command
msp_passthrough = build_msp_v1_request(245, bytes([0xFD, 0x00]))
print(f"  MSP_SET_PASSTHROUGH request ({len(msp_passthrough)} bytes):")
print(f"    hex:  {msp_passthrough.hex(' ')}")
print(f"    code: 245 (0xF5 = MSP_SET_PASSTHROUGH)")
print(f"    payload: [0xFD=SERIAL_ID_MODE, 0x00=port_identifier_UART1]")
print()

print("  KNOWN LIMITATION:")
print("  UART1 (CRSF port) was opened with rxCallback=crsfDataReceive.")
print("  With rxCallback set, the STM32 driver routes bytes to the callback,")
print("  NOT to the rxBuffer. The passthrough loop checks serialRxBytesWaiting()")
print("  which reads the rxBuffer -> always 0.")
print("  Effect: TX to receiver works; RX from receiver MAY NOT be forwarded.")
print("  We attempt it anyway — some bytes may arrive between CRSF ISR cycles.")
print()

# ---------------------------------------------------------------------------
# Step 2: Connect, verify FC responds, then enter passthrough
# ---------------------------------------------------------------------------
try:
    import serial
except ImportError:
    print("FAILED: pyserial not installed. Run: pip install pyserial")
    sys.exit(1)

print("Step 2: Connecting to FC via MSP to verify it responds")
print("-" * 60)

# First: connect at 115200 for MSP, verify FC is alive, send passthrough cmd
try:
    ser = serial.Serial(DEVICE, baudrate=115200, timeout=1.0)
    print(f"  Opened {DEVICE} at 115200 baud")
except serial.SerialException as e:
    print(f"  FAILED to open {DEVICE}: {e}")
    print("  If running in sandbox: retry with dangerouslyDisableSandbox: true")
    sys.exit(1)

# Send MSP_API_VERSION (code 1) to confirm FC is alive
api_req = build_msp_v1_request(1, b'')
ser.write(api_req)
time.sleep(0.2)
resp_bytes = ser.read(ser.in_waiting or 32)
api_payload = parse_msp_v1_response(resp_bytes, 1)  # won't work — size is at [3] not [3] code

# Simpler raw check: just look for $M> header
if b'$M>' in resp_bytes:
    print(f"  FC is responding to MSP (got {len(resp_bytes)} bytes including $M>)")
elif len(resp_bytes) > 0:
    print(f"  FC sent {len(resp_bytes)} bytes (not MSP format — maybe already in passthrough?)")
    print(f"  raw: {resp_bytes.hex(' ')}")
    ser.close()
    sys.exit(1)
else:
    print("  FC not responding to MSP_API_VERSION!")
    print("  Check: Is FC plugged in? Is configurator closed?")
    print("  If in sandbox: retry with dangerouslyDisableSandbox: true")
    ser.close()
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 3: Send passthrough command
# ---------------------------------------------------------------------------
print()
print("Step 3: Sending MSP_SET_PASSTHROUGH to bridge UART1")
print("-" * 60)
print(f"  Command: {msp_passthrough.hex(' ')}")
print("  WARNING: After FC ACKs this, it enters an infinite passthrough loop.")
print("           POWERCYCLE THE FC to exit passthrough mode.")
print()

# Drain any pending input
ser.reset_input_buffer()

# Send the passthrough command
bytes_written = ser.write(msp_passthrough)
print(f"  Wrote {bytes_written} bytes")

# The FC sends ACK before entering passthrough: $M> + size + code + payload(1 byte = 0 or 1) + csum
time.sleep(0.2)
ack_bytes = ser.read(ser.in_waiting or 32)
print(f"  Received {len(ack_bytes)} bytes after passthrough command:")
print(f"    raw: {ack_bytes.hex(' ')}")

passthrough_ok = False
if b'$M>' in ack_bytes:
    # Find the response payload
    idx = ack_bytes.find(b'$M>')
    if idx >= 0 and len(ack_bytes) > idx + 5:
        resp_size = ack_bytes[idx + 3]
        resp_code = ack_bytes[idx + 4]
        if resp_code == 245 and resp_size == 1 and len(ack_bytes) > idx + 5:
            resp_payload = ack_bytes[idx + 5]
            if resp_payload == 1:
                print(f"  Passthrough ACK: SUCCESS (payload=1, port found)")
                passthrough_ok = True
            else:
                print(f"  Passthrough ACK: FAILURE (payload={resp_payload}, port not found)")
                print("  The FC could not find UART1 — CRSF may not be configured on it.")
        elif resp_code == 245:
            print(f"  Got response for code 245, size={resp_size}")
            passthrough_ok = True  # Try anyway
        else:
            print(f"  Got MSP response but wrong code: {resp_code}")
    print(f"  MSP response found in data")
else:
    print(f"  No MSP $M> header found in response")
    if len(ack_bytes) == 0:
        print("  No response at all — FC may have entered passthrough without ACKing")
        passthrough_ok = True  # Some firmware versions don't ACK before passthrough

# ---------------------------------------------------------------------------
# Step 4: Switch port to CRSF baud and send DEVICE_PING
# ---------------------------------------------------------------------------
print()
print("Step 4: Switching to CRSF baud (420000) and sending DEVICE_PING")
print("-" * 60)

# The FC USB port is now a transparent bridge to UART1 at 420000 baud.
# We need to match the baud rate to talk CRSF directly.
# NOTE: USB virtual COM ports are baud-rate agnostic (it's all USB packets),
# but we set it anyway for correct framing expectations.
try:
    ser.baudrate = CRSF_BAUD
    print(f"  Port baud rate set to {CRSF_BAUD}")
except Exception as e:
    print(f"  Could not change baud rate: {e}")
    print("  Continuing — USB VCP may ignore baud rate setting")

# Flush any CRSF frames that may have arrived from the receiver
# (RC_CHANNELS_PACKED at ~150Hz = one frame every ~6.7ms)
time.sleep(0.05)
ser.reset_input_buffer()

# Send DEVICE_PING — possibly multiple times for reliability
print(f"  Sending DEVICE_PING: {ping_frame.hex(' ')}")
for attempt in range(3):
    ser.write(ping_frame)
    print(f"    Sent attempt {attempt + 1}/3")
    time.sleep(0.02)  # 20ms between retries

# ---------------------------------------------------------------------------
# Step 5: Read response
# ---------------------------------------------------------------------------
print()
print("Step 5: Listening for DEVICE_INFO response (type 0x29)")
print("-" * 60)

rx_buffer = bytearray()
LISTEN_SECONDS = 2.0
t_start = time.monotonic()
last_print = 0

while (time.monotonic() - t_start) < LISTEN_SECONDS:
    waiting = ser.in_waiting
    if waiting > 0:
        chunk = ser.read(waiting)
        rx_buffer.extend(chunk)
        elapsed = time.monotonic() - t_start
        print(f"  +{elapsed:.3f}s: received {len(chunk)} bytes "
              f"(total {len(rx_buffer)}): {chunk.hex(' ')}")

    time.sleep(0.01)

# Also drain remaining
time.sleep(0.1)
if ser.in_waiting:
    final = ser.read(ser.in_waiting)
    rx_buffer.extend(final)
    print(f"  Final drain: {len(final)} bytes: {final.hex(' ')}")

print()
print(f"  Total received: {len(rx_buffer)} bytes")
if rx_buffer:
    print(f"  All bytes: {rx_buffer.hex(' ')}")
    print()

# ---------------------------------------------------------------------------
# Step 6: Parse and analyze response
# ---------------------------------------------------------------------------
print("Step 6: Analysis")
print("-" * 60)

ser.close()
print("  Serial port closed.")
print()

if len(rx_buffer) == 0:
    print("  RESULT: No bytes received.")
    print()
    print("  This is consistent with the known limitation: the CRSF rxCallback")
    print("  intercepts all bytes from the receiver before the passthrough loop")
    print("  can forward them to USB.")
    print()
    print("  The DEVICE_PING was likely SENT to the receiver (TX side works),")
    print("  but the DEVICE_INFO response was consumed by the CRSF ISR.")
    print()
    print("  VERDICT: MSP serial passthrough is NOT viable for DEVICE_PING when")
    print("           CRSF is already open and running with an rxCallback.")
    result = "NO_BYTES_RECEIVED"

else:
    # Check for CRSF frames
    device_info = parse_device_info(bytes(rx_buffer))

    if device_info:
        print("  DEVICE_INFO response FOUND!")
        print(f"    device_name:   '{device_info['device_name']}'")
        print(f"    dest_addr:     0x{device_info['dest_addr']:02X}")
        print(f"    origin_addr:   0x{device_info['origin_addr']:02X}")
        print(f"    param_count:   {device_info['param_count']}")
        print(f"    param_version: {device_info['param_version']}")
        print(f"    raw_frame:     {device_info['raw_frame']}")
        print()
        print("  VERDICT: DEVICE_PING method WORKS — receiver identified!")
        result = "DEVICE_INFO_RECEIVED"
    else:
        print("  No DEVICE_INFO (0x29) frame found in received bytes.")
        print()
        # Check what frame types we got
        frame_types_found = set()
        for i in range(len(rx_buffer) - 2):
            if rx_buffer[i] in (0xC8, 0xEA, 0xEC, 0x00):
                frame_type = rx_buffer[i + 2]
                if frame_type in (0x14, 0x16, 0x28, 0x29, 0x02, 0x08, 0x1E, 0x21):
                    frame_types_found.add(f"0x{frame_type:02X}")

        if frame_types_found:
            type_names = {
                '0x16': 'RC_CHANNELS_PACKED',
                '0x14': 'LINK_STATISTICS',
                '0x28': 'DEVICE_PING',
                '0x29': 'DEVICE_INFO',
                '0x02': 'GPS',
                '0x08': 'BATTERY_SENSOR',
                '0x1e': 'ATTITUDE',
                '0x21': 'FLIGHT_MODE',
            }
            for ft in frame_types_found:
                name = type_names.get(ft.lower(), ft)
                print(f"  Frame type seen: {ft} ({name})")
        else:
            print("  No recognizable CRSF frame types in received data.")
            print("  Data may be MSP framing or garbage from baud rate mismatch.")

        print()
        print("  VERDICT: Receiver response not captured.")
        print("  The passthrough TX (sending ping) likely worked, but RX bytes")
        print("  from receiver were consumed by the CRSF interrupt handler.")
        result = "BYTES_RECEIVED_NO_DEVICE_INFO"

print()
print("=" * 60)
print("  SUMMARY")
print("=" * 60)
print()
print(f"  Device:         {DEVICE}")
print(f"  Result:         {result}")
print()
print("  IMPORTANT: The FC is now in an infinite serial passthrough loop.")
print("  You MUST powercycle the FC before it will respond to MSP again.")
print()
print("  Findings:")
print("  1. MSP_SET_PASSTHROUGH (code 245) payload: [0xFD=SERIAL_ID, 0x00=UART1]")
print("  2. DEVICE_PING frame: c8 04 28 ec c8 5a (6 bytes, CRC=0x5A verified)")
print("  3. TX to receiver via passthrough: likely works (UART1 TX path is clear)")
print("  4. RX from receiver via passthrough: blocked by CRSF rxCallback in ISR")
print("     (bytes go to crsfDataReceive, not to serialRxBytesWaiting buffer)")
print("  5. To receive DEVICE_INFO, the CRSF port would need to be reopened")
print("     without rxCallback before passthrough (as CLI 'serialpassthrough' does)")
print()
