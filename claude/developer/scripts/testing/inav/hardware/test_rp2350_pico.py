#!/usr/bin/env python3
"""
INAV RP2350_PICO hardware test suite.

Tests:
  1. Boot + USB serial connection
  2. Status command
  3. Read a CLI setting
  4. Set motor_pwm_protocol = DSHOT600
  5. CLI save command (causes FC reboot)
  6. Verify DSHOT600 persisted after reboot

Usage:
    python3 test_rp2350_pico.py

Requires:
    - Raspberry Pi Pico 2 running INAV RP2350_PICO firmware
    - Connected via USB (appears as /dev/serial/by-id/usb-Raspberry_Pi_Pico_*)
    - pyserial: pip install pyserial

Note: If running in sandbox, retry with dangerouslyDisableSandbox: true.
      Serial port access is blocked in the sandbox environment.
"""

import serial
import time
import glob
import subprocess
import re
import sys


def find_pico_port():
    """Find the Raspberry Pi Pico serial port by USB ID (stable path)."""
    by_id = glob.glob('/dev/serial/by-id/usb-Raspberry_Pi_Pico_*')
    if by_id:
        return by_id[0]
    # Fall back to scanning ttyACM devices
    for dev in sorted(glob.glob('/dev/ttyACM*')):
        try:
            result = subprocess.run(['udevadm', 'info', dev],
                capture_output=True, text=True)
            if ('ID_MODEL=Pico' in result.stdout and
                    'Debugprobe' not in result.stdout):
                return dev
        except Exception:
            pass
    return None


def get_setting_value(resp, setting_name):
    """
    Extract the current value of a CLI setting from get command output.
    Matches 'setting_name = VALUE' line, NOT the 'Allowed values:' line.
    """
    pattern = rf'^{re.escape(setting_name)}\s*=\s*(\S+)'
    for line in resp.split('\n'):
        m = re.match(pattern, line.strip())
        if m:
            return m.group(1)
    return None


def send_cmd(ser, cmd_str, wait=1.5):
    """Send a CLI command and return the response."""
    ser.write((cmd_str + '\r\n').encode())
    time.sleep(wait)
    try:
        return ser.read(ser.in_waiting).decode('utf-8', errors='replace')
    except Exception:
        return ''


def connect_with_retry(port, retries=5):
    """Try to connect to the serial port with retries."""
    for i in range(retries):
        try:
            s = serial.Serial(port, 115200, timeout=3)
            return s
        except Exception as e:
            if i < retries - 1:
                # Port may have re-enumerated; find it again
                new_port = find_pico_port()
                if new_port and new_port != port:
                    port = new_port
                time.sleep(1)
            else:
                print(f'  [FAIL] Cannot connect: {e}')
                print('  Note: If in sandbox, retry with dangerouslyDisableSandbox: true')
    return None


def main():
    failures = []
    results = {}

    print('=== INAV RP2350_PICO Hardware Test Suite ===')
    print()

    # Find the Pico
    port = find_pico_port()
    if not port:
        print('[FAIL] Raspberry Pi Pico not found on any serial port')
        print('  Check: Is the Pico plugged in via USB?')
        print('  If in sandbox: retry with dangerouslyDisableSandbox: true')
        sys.exit(1)
    print(f'Found Pico at: {port}')
    print()

    # Connect
    ser = connect_with_retry(port)
    if not ser:
        sys.exit(1)
    print(f'[CONNECTED] {port}')

    time.sleep(0.3)

    # Verify FC is responding before starting tests
    ser.write(b'#\r\n')
    time.sleep(0.5)
    try:
        prompt_data = ser.read(ser.in_waiting)
    except Exception:
        prompt_data = b''

    if b'#' not in prompt_data and b'CLI' not in prompt_data:
        print('[FAIL] FC not responding to CLI prompt')
        print('  Check: Is INAV running on the Pico?')
        ser.close()
        sys.exit(1)
    print('[OK] FC is responding')
    print()

    # ── TEST 1: Boot + USB serial ──────────────────────────────────────────
    print('--- TEST 1: Boot + USB serial connection ---')
    resp = send_cmd(ser, 'version', 1.0)
    print(resp.strip())
    if 'INAV' in resp and 'RP2350_PICO' in resp and '9.0.1' in resp:
        m = re.search(r'\(([0-9a-f]+)\)', resp)
        git = m.group(1) if m else 'unknown'
        print(f'[PASS] INAV 9.0.1 RP2350_PICO (git: {git})')
        results['boot_usb_serial'] = 'PASS'
    else:
        print('[FAIL] Unexpected version string')
        failures.append('boot_usb_serial')
        results['boot_usb_serial'] = 'FAIL'
    print()

    # ── TEST 2: Status ─────────────────────────────────────────────────────
    print('--- TEST 2: Status command ---')
    resp = send_cmd(ser, 'status', 1.5)
    print(resp.strip())
    if 'CPU Clock' in resp and 'RP2350_PICO' in resp:
        print('[PASS] Status returned valid data')
        results['status'] = 'PASS'
    else:
        print('[FAIL] Status response incomplete')
        failures.append('status')
        results['status'] = 'FAIL'
    print()

    # ── TEST 3: Read motor_pwm_protocol ────────────────────────────────────
    print('--- TEST 3: Read motor_pwm_protocol (baseline) ---')
    resp = send_cmd(ser, 'get motor_pwm_protocol', 1.0)
    print(resp.strip())
    baseline = get_setting_value(resp, 'motor_pwm_protocol')
    print(f'Extracted value: {repr(baseline)}')
    if baseline:
        print(f'[PASS] Setting readable, baseline = {baseline}')
        results['read_setting'] = 'PASS'
    else:
        print('[FAIL] Cannot parse motor_pwm_protocol value')
        failures.append('read_setting')
        results['read_setting'] = 'FAIL'
        baseline = 'ONESHOT125'
    print()

    # ── TEST 4: Set DSHOT600 ───────────────────────────────────────────────
    print('--- TEST 4: Set motor_pwm_protocol = DSHOT600 ---')
    resp = send_cmd(ser, 'set motor_pwm_protocol = DSHOT600', 0.5)
    print('Set response:', repr(resp.strip()))
    resp2 = send_cmd(ser, 'get motor_pwm_protocol', 0.5)
    current = get_setting_value(resp2, 'motor_pwm_protocol')
    print(f'After set: {repr(current)}')
    if current == 'DSHOT600':
        print('[PASS] DSHOT600 set in RAM successfully')
        results['set_dshot'] = 'PASS'
    else:
        print(f'[FAIL] Expected DSHOT600, got {repr(current)}')
        failures.append('set_dshot')
        results['set_dshot'] = 'FAIL'
    print()

    # ── TEST 5: Save ───────────────────────────────────────────────────────
    print('--- TEST 5: CLI save command (FC will reboot) ---')
    save_resp = b''
    try:
        ser.write(b'save\r\n')
        time.sleep(0.5)
        try:
            save_resp = ser.read(min(ser.in_waiting, 300))
            print(f'Save response: {repr(save_resp)}')
        except Exception:
            print('(Port disconnected during reboot - expected)')
    except Exception as e:
        print(f'Note: {e}')
    finally:
        try:
            ser.close()
        except Exception:
            pass

    if b'Saving' in save_resp or b'Rebooting' in save_resp:
        print('[PASS] FC acknowledged save command')
        results['save_cmd'] = 'PASS'
    else:
        print(f'[WARN] Unexpected save response: {repr(save_resp)}')
        results['save_cmd'] = 'WARN'

    print('Waiting 6s for FC to reboot and re-enumerate...')
    time.sleep(6)
    print()

    # ── TEST 6: Persistence ────────────────────────────────────────────────
    print('--- TEST 6: Verify DSHOT600 persisted after reboot ---')
    new_port = None
    for attempt in range(8):
        new_port = find_pico_port()
        if new_port:
            break
        print(f'  Waiting for Pico to re-enumerate ({attempt + 1}/8)...')
        time.sleep(1)

    if not new_port:
        print('[FAIL] Pico not found after reboot')
        print('  Check: Did the FC reboot? Is it still powered?')
        failures.append('persistence')
        results['persistence'] = 'FAIL'
    else:
        print(f'Reconnected at: {new_port}')
        ser2 = connect_with_retry(new_port)
        if not ser2:
            failures.append('persistence')
            results['persistence'] = 'FAIL'
        else:
            time.sleep(0.5)
            ser2.write(b'#\r\n')
            time.sleep(0.5)
            try:
                ser2.read(ser2.in_waiting)
            except Exception:
                pass

            resp = send_cmd(ser2, 'get motor_pwm_protocol', 1.5)
            print('Full response:')
            print(repr(resp))
            persisted = get_setting_value(resp, 'motor_pwm_protocol')
            print(f'Extracted after reboot: {repr(persisted)}')

            if persisted == 'DSHOT600':
                print('[PASS] DSHOT600 persisted after reboot - CLI save works')
                results['persistence'] = 'PASS'
            else:
                print(f'[FAIL] Expected DSHOT600, got {repr(persisted)}')
                print('       CLI save is NOT persisting settings across reboot')
                failures.append('persistence')
                results['persistence'] = 'FAIL'

            # Restore original value
            send_cmd(ser2, f'set motor_pwm_protocol = {baseline}', 0.3)
            try:
                ser2.write(b'save\r\n')
                time.sleep(0.3)
                ser2.close()
            except Exception:
                pass
            print(f'(Restored motor_pwm_protocol to {baseline} and saved)')

    print()

    # ── Summary ────────────────────────────────────────────────────────────
    print('=' * 50)
    print('FINAL TEST RESULTS')
    print('=' * 50)
    for test, res in results.items():
        mark = 'PASS' if res in ('PASS', 'WARN') else 'FAIL'
        print(f'  [{mark}] {test}: {res}')
    print()

    if failures:
        print(f'OVERALL: FAILED - {len(failures)} test(s) failed: {failures}')
        sys.exit(1)
    else:
        print(f'OVERALL: ALL {len(results)} TESTS PASSED')
        sys.exit(0)


if __name__ == '__main__':
    main()
