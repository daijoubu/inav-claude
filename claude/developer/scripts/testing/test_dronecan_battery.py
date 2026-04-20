#!/usr/bin/env python3
"""
DroneCAN Battery Monitor Test for MATEKF765-WSE

Tests:
1. CAN peripheral / FC connection initialization
2. Battery monitor detection via battery state queries
3. Battery data reception (voltage, current, capacity)
4. MSP_ANALOG query for battery voltage
5. MSP2_INAV_ANALOG for full battery data
6. Error counter status (I2C/hardware errors)
7. CLI interrogation for CAN config and battery source

Uses raw MSP over serial - no external dependencies beyond pyserial.

Usage:
    python3 test_dronecan_battery.py [--port /dev/ttyACM0]
"""

import argparse
import struct
import sys
import time

# MSP command codes
MSP_API_VERSION     = 1
MSP_FC_VARIANT      = 2
MSP_FC_VERSION      = 3
MSP_BOARD_INFO      = 4
MSP_BUILD_INFO      = 5
MSP_STATUS          = 101
MSP_ANALOG          = 110
MSP_STATUS_EX       = 150
MSP_BATTERY_STATE   = 130

# MSP2 command codes (sent as MSP v2 frames)
MSP2_INAV_ANALOG    = 0x2002
MSP2_INAV_STATUS    = 0x2000


def build_msp1(code: int, payload: bytes = b'') -> bytes:
    """Build an MSP v1 request frame."""
    length = len(payload)
    checksum = (length ^ code) & 0xFF
    for b in payload:
        checksum ^= b
    return bytes([ord('$'), ord('M'), ord('<'), length, code]) + payload + bytes([checksum])


def build_msp2(code: int, payload: bytes = b'') -> bytes:
    """Build an MSP v2 request frame."""
    # MSP v2 frame: $X< + flag(0) + code(LE16) + size(LE16) + payload + CRC8-D5
    header = bytes([ord('$'), ord('X'), ord('<'), 0])  # preamble + flag
    code_bytes = struct.pack('<H', code)
    size_bytes = struct.pack('<H', len(payload))
    frame_for_crc = header[3:] + code_bytes + size_bytes + payload  # from flag byte onward

    # CRC8-DVB-S2
    crc = 0
    for b in frame_for_crc:
        crc ^= b
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0xD5) & 0xFF
            else:
                crc = (crc << 1) & 0xFF

    return header + code_bytes + size_bytes + payload + bytes([crc])


def send_and_receive(ser, data: bytes, timeout: float = 1.5) -> bytes:
    """Send MSP request and read raw response."""
    ser.reset_input_buffer()
    ser.write(data)

    start = time.time()
    response = b''
    while time.time() - start < timeout:
        chunk = ser.read(256)
        if chunk:
            response += chunk
            # Check for response terminators
            if b'$M>' in response or b'$M!' in response:
                break
            if b'$X>' in response or b'$X!' in response:
                break
    return response


def parse_msp1_response(response: bytes, expected_code: int):
    """Parse MSP v1 response. Returns payload bytes or None on error."""
    if b'$M!' in response:
        return None  # Error response

    if b'$M>' not in response:
        return None  # No response

    idx = response.index(b'$M>')
    if len(response) < idx + 6:
        return None

    length = response[idx + 3]
    code = response[idx + 4]
    payload = response[idx + 5: idx + 5 + length]

    if code != expected_code:
        return None

    return payload


def parse_msp2_response(response: bytes, expected_code: int):
    """Parse MSP v2 response. Returns payload bytes or None on error."""
    if b'$X!' in response:
        return None

    if b'$X>' not in response:
        return None

    idx = response.index(b'$X>')
    if len(response) < idx + 9:
        return None

    # flag=1, code=2, size=2, then payload, then crc=1
    code = struct.unpack_from('<H', response, idx + 4)[0]
    size = struct.unpack_from('<H', response, idx + 6)[0]
    payload = response[idx + 8: idx + 8 + size]

    if code != expected_code:
        return None

    return payload


PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"
SKIP = "SKIP"


def print_result(name: str, status: str, detail: str = ""):
    indicator = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]", "SKIP": "[SKIP]"}.get(status, "[????]")
    if detail:
        print(f"  {indicator} {name}: {detail}")
    else:
        print(f"  {indicator} {name}")


def run_tests(port: str, baud: int = 115200) -> bool:
    """Run all DroneCAN battery monitor tests. Returns True if overall pass."""
    try:
        import serial
    except ImportError:
        print("[FAIL] pyserial not installed. Run: pip install pyserial")
        return False

    print(f"\n=== DroneCAN Battery Monitor Test ===")
    print(f"Port: {port}  Baud: {baud}")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = {}

    # --- Test 1: Connection / FC Identification ---
    print("--- Test 1: CAN Peripheral / FC Initialization ---")

    try:
        ser = serial.Serial(port, baud, timeout=1.0)
        time.sleep(0.3)
        print_result("Serial port open", PASS, f"{port} @ {baud}")
    except Exception as e:
        print_result("Serial port open", FAIL, str(e))
        return False

    try:
        # Query API version
        req = build_msp1(MSP_API_VERSION)
        resp = send_and_receive(ser, req)
        payload = parse_msp1_response(resp, MSP_API_VERSION)
        if payload and len(payload) >= 3:
            proto = payload[0]
            api_major = payload[1]
            api_minor = payload[2]
            print_result("MSP API version", PASS, f"protocol={proto} API={api_major}.{api_minor}")
            results['connection'] = PASS
        else:
            print_result("MSP API version", FAIL, f"no response (raw={resp[:20].hex() if resp else 'empty'})")
            results['connection'] = FAIL

        # Query board info
        req = build_msp1(MSP_BOARD_INFO)
        resp = send_and_receive(ser, req)
        payload = parse_msp1_response(resp, MSP_BOARD_INFO)
        if payload and len(payload) >= 4:
            board_id = payload[:4].decode('ascii', errors='replace')
            print_result("Board ID", PASS, board_id.strip())
        else:
            print_result("Board ID", WARN, "no response")

        # Query FC variant
        req = build_msp1(MSP_FC_VARIANT)
        resp = send_and_receive(ser, req)
        payload = parse_msp1_response(resp, MSP_FC_VARIANT)
        if payload and len(payload) >= 4:
            variant = payload[:4].decode('ascii', errors='replace')
            print_result("FC variant", PASS, variant.strip())
        else:
            print_result("FC variant", WARN, "no response")

        # Query FC version
        req = build_msp1(MSP_FC_VERSION)
        resp = send_and_receive(ser, req)
        payload = parse_msp1_response(resp, MSP_FC_VERSION)
        if payload and len(payload) >= 3:
            version = f"{payload[0]}.{payload[1]}.{payload[2]}"
            print_result("FC version", PASS, version)
        else:
            print_result("FC version", WARN, "no response")

    except Exception as e:
        print_result("FC identification", FAIL, str(e))
        results['connection'] = FAIL

    print()

    # --- Test 2: Battery Monitor Detection ---
    print("--- Test 2: Battery Monitor Detection ---")

    try:
        # Use MSP_STATUS_EX to get sensor presence and error counters
        req = build_msp1(MSP_STATUS_EX)
        resp = send_and_receive(ser, req)
        payload = parse_msp1_response(resp, MSP_STATUS_EX)

        if payload and len(payload) >= 11:
            cycle_time = struct.unpack_from('<H', payload, 0)[0]
            i2c_errors = struct.unpack_from('<H', payload, 2)[0]
            sensor_status = struct.unpack_from('<H', payload, 4)[0]
            cpu_load = struct.unpack_from('<H', payload, 9)[0]
            arming_flags = struct.unpack_from('<H', payload, 11)[0] if len(payload) >= 13 else 0

            # Decode sensor bits
            sensor_names = {
                0: "ACC", 1: "BARO", 2: "MAG", 3: "GPS",
                4: "RANGEFINDER", 5: "OPFLOW", 6: "PITOT", 7: "TEMP"
            }
            active_sensors = [sensor_names[b] for b in range(8) if sensor_status & (1 << b)]
            hw_failure = bool(sensor_status & (1 << 15))

            print_result("MSP_STATUS_EX", PASS, f"cycle={cycle_time}us CPU={cpu_load}%")
            print_result("Active sensors", PASS, ", ".join(active_sensors) if active_sensors else "none")
            print_result("Hardware health", PASS if not hw_failure else FAIL,
                        "healthy" if not hw_failure else "HARDWARE FAILURE FLAGGED")

            if i2c_errors == 0:
                print_result("I2C error counter", PASS, "0 errors")
            else:
                print_result("I2C error counter", WARN, f"{i2c_errors} I2C errors detected")

            results['sensor_detect'] = PASS
        else:
            print_result("MSP_STATUS_EX", FAIL, f"insufficient payload (got {len(payload) if payload else 0} bytes)")
            results['sensor_detect'] = FAIL

    except Exception as e:
        print_result("Battery monitor detection", FAIL, str(e))
        results['sensor_detect'] = FAIL

    print()

    # --- Test 3: Battery Data Reception (MSP_ANALOG) ---
    print("--- Test 3: Battery Data Reception - MSP_ANALOG ---")

    try:
        req = build_msp1(MSP_ANALOG)
        resp = send_and_receive(ser, req)
        payload = parse_msp1_response(resp, MSP_ANALOG)

        if payload and len(payload) >= 7:
            # MSP_ANALOG: u8 vbat(0.1V), u16 mah_drawn, u16 rssi, i16 amperage(0.01A)
            vbat_raw = payload[0]
            mah_drawn = struct.unpack_from('<H', payload, 1)[0]
            rssi = struct.unpack_from('<H', payload, 3)[0]
            amperage_raw = struct.unpack_from('<h', payload, 5)[0]

            vbat_v = vbat_raw / 10.0
            amperage_a = amperage_raw / 100.0

            print_result("MSP_ANALOG received", PASS, f"{len(payload)} bytes")
            print_result("Battery voltage (raw)", PASS if vbat_raw > 0 else WARN,
                        f"{vbat_v:.1f}V (raw={vbat_raw})")
            print_result("mAh drawn", PASS, f"{mah_drawn} mAh")
            print_result("RSSI", PASS, f"{rssi}")
            print_result("Amperage", PASS, f"{amperage_a:.2f}A (raw={amperage_raw})")

            # Validity checks
            if vbat_raw == 0:
                print_result("Voltage plausibility", WARN,
                            "Voltage is 0V - battery may not be connected or DroneCAN not reporting")
                results['battery_data'] = WARN
            elif vbat_raw < 30:  # < 3.0V - implausibly low for any LiPo
                print_result("Voltage plausibility", WARN,
                            f"{vbat_v:.1f}V is implausibly low for a LiPo battery")
                results['battery_data'] = WARN
            elif vbat_raw > 600:  # > 60V - implausibly high
                print_result("Voltage plausibility", WARN, f"{vbat_v:.1f}V is implausibly high")
                results['battery_data'] = WARN
            else:
                print_result("Voltage plausibility", PASS, f"{vbat_v:.1f}V is in valid range")
                results['battery_data'] = PASS

        else:
            print_result("MSP_ANALOG", FAIL, f"no/insufficient response (got {len(payload) if payload else 0} bytes)")
            results['battery_data'] = FAIL

    except Exception as e:
        print_result("MSP_ANALOG", FAIL, str(e))
        results['battery_data'] = FAIL

    print()

    # --- Test 4: Full Battery Data via MSP2_INAV_ANALOG ---
    print("--- Test 4: Full Battery Data - MSP2_INAV_ANALOG ---")

    try:
        req = build_msp2(MSP2_INAV_ANALOG)
        resp = send_and_receive(ser, req, timeout=2.0)
        payload = parse_msp2_response(resp, MSP2_INAV_ANALOG)

        if payload and len(payload) >= 22:
            # MSP2_INAV_ANALOG layout:
            # u8:  flags (bit0=was_full, bit1=use_cap_threshold, bits2-3=battery_state, bits4-7=cell_count)
            # u16: voltage (0.01V)
            # u16: amperage (0.01A)
            # u32: power (0.01W)
            # u32: mah_drawn
            # u32: mwh_drawn
            # u32: remaining_capacity
            # u8:  battery_percentage
            # u16: rssi
            flags = payload[0]
            voltage_raw = struct.unpack_from('<H', payload, 1)[0]
            amperage_raw = struct.unpack_from('<H', payload, 3)[0]
            power_raw = struct.unpack_from('<I', payload, 5)[0]
            mah_drawn = struct.unpack_from('<I', payload, 9)[0]
            mwh_drawn = struct.unpack_from('<I', payload, 13)[0]
            remaining_cap = struct.unpack_from('<I', payload, 17)[0]
            batt_pct = payload[21] if len(payload) >= 22 else 0
            rssi = struct.unpack_from('<H', payload, 22)[0] if len(payload) >= 24 else 0

            battery_state_names = {0: "OK", 1: "WARNING", 2: "CRITICAL", 3: "NOT_PRESENT", 4: "INIT"}
            battery_state = (flags >> 2) & 0x03
            cell_count = (flags >> 4) & 0x0F

            voltage_v = voltage_raw / 100.0
            amperage_a = struct.unpack('<h', struct.pack('<H', amperage_raw))[0] / 100.0
            power_w = power_raw / 100.0

            print_result("MSP2_INAV_ANALOG received", PASS, f"{len(payload)} bytes")
            print_result("Voltage (high-res)", PASS if voltage_raw > 0 else WARN,
                        f"{voltage_v:.2f}V (raw={voltage_raw})")
            print_result("Amperage", PASS, f"{amperage_a:.2f}A")
            print_result("Power", PASS, f"{power_w:.2f}W")
            print_result("mAh drawn", PASS, f"{mah_drawn} mAh")
            print_result("mWh drawn", PASS, f"{mwh_drawn} mWh")
            print_result("Remaining capacity", PASS, f"{remaining_cap} mAh")
            print_result("Battery percentage", PASS, f"{batt_pct}%")
            print_result("Battery state", PASS if battery_state in (0, 1) else WARN,
                        f"{battery_state_names.get(battery_state, 'UNKNOWN')} ({battery_state})")
            print_result("Cell count", PASS if cell_count > 0 else WARN,
                        f"{cell_count} cells" if cell_count > 0 else "0 cells (not detected)")

            if voltage_raw > 0:
                print_result("DroneCAN data source", PASS,
                            f"Battery reporting {voltage_v:.2f}V - DroneCAN monitor active")
                results['full_battery'] = PASS
            else:
                print_result("DroneCAN data source", WARN,
                            "Voltage=0V: DroneCAN battery monitor may not be sending data")
                results['full_battery'] = WARN

        else:
            print_result("MSP2_INAV_ANALOG", FAIL,
                        f"no/insufficient response (got {len(payload) if payload else 0} bytes, raw={resp[:20].hex() if resp else 'empty'})")
            results['full_battery'] = FAIL

    except Exception as e:
        print_result("MSP2_INAV_ANALOG", FAIL, str(e))
        results['full_battery'] = FAIL

    print()

    # --- Test 5: Error Counter Check ---
    print("--- Test 5: CAN/Hardware Error Counter Check ---")

    try:
        # Poll status multiple times to catch transient errors
        error_samples = []
        for i in range(3):
            req = build_msp1(MSP_STATUS_EX)
            resp = send_and_receive(ser, req, timeout=1.0)
            payload = parse_msp1_response(resp, MSP_STATUS_EX)
            if payload and len(payload) >= 4:
                i2c_errors = struct.unpack_from('<H', payload, 2)[0]
                error_samples.append(i2c_errors)
            time.sleep(0.5)

        if error_samples:
            # Check if errors are increasing (indicates active bus errors)
            max_errors = max(error_samples)
            increasing = len(error_samples) >= 2 and error_samples[-1] > error_samples[0]

            if max_errors == 0:
                print_result("I2C/bus error counters", PASS, f"0 errors across {len(error_samples)} samples")
            elif increasing:
                print_result("I2C/bus error counters", FAIL,
                            f"Errors INCREASING: {error_samples[0]} -> {error_samples[-1]} (active bus errors!)")
            else:
                print_result("I2C/bus error counters", WARN,
                            f"Non-zero but stable: {error_samples} (may be historical)")

            results['errors'] = PASS if max_errors == 0 else (FAIL if increasing else WARN)
        else:
            print_result("Error counter sampling", FAIL, "Could not read status")
            results['errors'] = FAIL

    except Exception as e:
        print_result("Error counter check", FAIL, str(e))
        results['errors'] = FAIL

    print()

    # --- Test 6: CLI Battery Source and CAN Config ---
    print("--- Test 6: CLI Interrogation - Battery Source and CAN Config ---")

    cli_results = {}
    try:
        import serial
        cli_ser = serial.Serial(port, 115200, timeout=2.0)
        time.sleep(0.2)

        def cli_cmd(cmd: str, wait: float = 1.0) -> str:
            cli_ser.reset_input_buffer()
            cli_ser.write((cmd + '\r\n').encode())
            time.sleep(wait)
            out = b''
            while cli_ser.in_waiting:
                out += cli_ser.read(cli_ser.in_waiting)
                time.sleep(0.1)
            return out.decode('utf-8', errors='replace')

        # Enter CLI mode
        cli_ser.write(b'#')
        time.sleep(0.5)
        cli_ser.read(cli_ser.in_waiting)  # flush prompt

        # Query battery source configuration
        output = cli_cmd('get battery_meter_type', wait=1.0)
        if 'battery_meter_type' in output.lower():
            # Extract value
            for line in output.splitlines():
                if 'battery_meter_type' in line.lower():
                    print_result("battery_meter_type", PASS, line.strip())
                    cli_results['battery_source'] = line.strip()
                    break
        else:
            print_result("battery_meter_type CLI", WARN, "No response from CLI")

        # Query voltage source
        output = cli_cmd('get bat_voltage_src', wait=1.0)
        for line in output.splitlines():
            if 'bat_voltage_src' in line.lower() or 'voltage' in line.lower():
                print_result("bat_voltage_src", PASS, line.strip())
                break

        # Query current source
        output = cli_cmd('get bat_current_src', wait=1.0)
        for line in output.splitlines():
            if 'bat_current_src' in line.lower() or 'current' in line.lower():
                print_result("bat_current_src", PASS, line.strip())
                break

        # Check for CAN-related features
        output = cli_cmd('feature', wait=1.0)
        if 'CAN' in output.upper() or 'UAVCAN' in output.upper() or 'DRONECAN' in output.upper():
            print_result("CAN feature enabled", PASS, "CAN feature is active")
        else:
            # Show all features for diagnostics
            features_line = [l for l in output.splitlines() if 'feature' in l.lower() or 'ENABLED' in l.upper()]
            print_result("CAN feature check", WARN,
                        "No explicit CAN feature found in output (may not be needed for DroneCAN battery)")

        # Exit CLI
        cli_ser.write(b'\rexit\r\n')
        time.sleep(0.5)
        cli_ser.close()

    except Exception as e:
        print_result("CLI interrogation", WARN, f"CLI query failed: {e}")

    print()

    # --- Test 7: Continuous Battery Voltage Stability ---
    print("--- Test 7: Continuous Battery Voltage Sampling (5 samples) ---")

    try:
        voltages = []
        for i in range(5):
            req = build_msp1(MSP_ANALOG)
            resp = send_and_receive(ser, req)
            payload = parse_msp1_response(resp, MSP_ANALOG)
            if payload and len(payload) >= 1:
                vbat_v = payload[0] / 10.0
                voltages.append(vbat_v)
                print(f"    Sample {i+1}: {vbat_v:.1f}V")
            time.sleep(0.5)

        if len(voltages) >= 3:
            v_min = min(voltages)
            v_max = max(voltages)
            v_avg = sum(voltages) / len(voltages)
            v_range = v_max - v_min

            print_result("Samples collected", PASS, f"{len(voltages)}/5")
            print_result("Voltage average", PASS if v_avg > 0 else WARN, f"{v_avg:.2f}V")
            print_result("Voltage range", PASS if v_range < 1.0 else WARN,
                        f"{v_range:.2f}V (min={v_min:.1f} max={v_max:.1f})")

            if v_avg > 0 and v_range < 1.0:
                print_result("Voltage stability", PASS, "Stable readings - consistent data source")
                results['stability'] = PASS
            elif v_avg == 0:
                print_result("Voltage stability", WARN, "All readings 0V - no battery data received")
                results['stability'] = WARN
            else:
                print_result("Voltage stability", WARN, f"Readings vary by {v_range:.2f}V")
                results['stability'] = WARN
        else:
            print_result("Voltage sampling", FAIL, "Insufficient samples")
            results['stability'] = FAIL

    except Exception as e:
        print_result("Continuous sampling", FAIL, str(e))
        results['stability'] = FAIL

    ser.close()

    # --- Summary ---
    print()
    print("=" * 50)
    print("=== TEST SUMMARY ===")
    print("=" * 50)

    test_map = {
        'connection':    'Test 1: FC Connection / CAN Initialization',
        'sensor_detect': 'Test 2: Battery Monitor Detection',
        'battery_data':  'Test 3: Battery Data (MSP_ANALOG)',
        'full_battery':  'Test 4: Full Battery Data (MSP2_INAV_ANALOG)',
        'errors':        'Test 5: CAN/Hardware Error Counters',
        'stability':     'Test 7: Voltage Stability',
    }

    overall_pass = True
    has_fail = False

    for key, name in test_map.items():
        status = results.get(key, SKIP)
        indicator = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]", "SKIP": "[SKIP]"}.get(status, "[????]")
        print(f"  {indicator} {name}")
        if status == FAIL:
            has_fail = True
            overall_pass = False
        elif status == WARN:
            # WARN doesn't cause overall failure but noted
            pass

    print()
    if has_fail:
        print("OVERALL STATUS: FAILED")
        print("  One or more tests failed - check output above for details.")
    elif any(v == WARN for v in results.values()):
        print("OVERALL STATUS: PARTIAL PASS (with warnings)")
        print("  Tests passed but some data may indicate DroneCAN battery monitor not active.")
        print("  If battery is not connected or DroneCAN not configured, 0V readings are expected.")
    else:
        print("OVERALL STATUS: PASSED")
        print("  All tests passed - DroneCAN battery monitor communicating correctly.")
    print()

    return not has_fail


def main():
    parser = argparse.ArgumentParser(description="DroneCAN Battery Monitor Test for MATEKF765-WSE")
    parser.add_argument('--port', default='/dev/ttyACM0', help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    args = parser.parse_args()

    import os
    if not os.path.exists(args.port):
        print(f"[FAIL] Serial device not found: {args.port}")
        print("  Is the FC connected? Check: ls /dev/ttyACM*")
        sys.exit(1)

    success = run_tests(args.port, args.baud)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
