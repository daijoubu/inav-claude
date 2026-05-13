#!/usr/bin/env python3
"""
UART1 vs UART2 CRSF Receiver Discrimination Probe v2
=====================================================
Tests whether MSP commands can distinguish:
  Case A: CRSF receiver correctly configured on its working port
  Case B: CRSF configured on a port with nothing connected (UART2)

Uses correct MSP v2 SET commands (force_version=2).
Waits for sensors to calibrate before sampling.

Note: Requires dangerouslyDisableSandbox: true in sandbox environments.

Usage:
    python3 probe_uart_discrimination_v2.py [port]
"""

import sys
import time
import struct

DEVICE = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD = 115200
FUNCTION_RX_SERIAL = 0x40   # bit 6 = (1 << 6) = 64

try:
    from mspapi2 import MSPApi
except ImportError as e:
    print(f"FAILED to import mspapi2: {e}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def connect(label=""):
    """Open MSP connection with retries."""
    print(f"  Connecting{' (' + label + ')' if label else ''} ...")
    for attempt in range(1, 10):
        try:
            api = MSPApi(port=DEVICE, baudrate=BAUD)
            api.open()
            _, ver = api.get_api_version()
            print(f"    OK (attempt {attempt}): API {ver.get('apiVersionMajor','?')}.{ver.get('apiVersionMinor','?')}")
            return api
        except Exception as e:
            if attempt == 1:
                print(f"    Attempt {attempt}: {e}")
            time.sleep(1.5)
    print("FATAL: Cannot connect. Check USB and close configurator.")
    print("If in sandbox: use dangerouslyDisableSandbox: true")
    sys.exit(1)


def read_serial_cfg(api):
    """Return list of port dicts."""
    _, raw = api._serial.request(4105, payload=bytes(), timeout=2.0)
    ports = []
    for i in range(len(raw) // 9):
        off = i * 9
        ident = raw[off]
        func_mask = struct.unpack_from('<I', raw, off + 1)[0]
        bauds = list(raw[off + 5: off + 9])
        ports.append({'id': ident, 'func_mask': func_mask, 'bauds': bauds,
                      'has_rx': bool(func_mask & FUNCTION_RX_SERIAL)})
    return ports


def set_port(api, port_id, func_mask, bauds):
    """MSP2_COMMON_SET_SERIAL_CONFIG for one port."""
    payload = struct.pack('<BIBBBB', port_id, func_mask,
                          bauds[0], bauds[1], bauds[2], bauds[3])
    ret_code, _ = api._serial.request(4106, payload=payload, timeout=2.0, force_version=2)
    assert ret_code == 4106, f"Unexpected reply code {ret_code}"


def reboot_and_reconnect(api, wait_calibrate=True):
    """Send reboot, wait for FC to come back up."""
    print("  Rebooting FC ...")
    try:
        api._serial.request(68, payload=bytes(), timeout=1.5)
    except Exception:
        pass
    api.close()
    time.sleep(6)
    api = connect("after reboot")
    if wait_calibrate:
        print("  Waiting for sensors to calibrate (up to 15s) ...")
        for _ in range(30):
            _, status = api.get_inav_status()
            af_names = [f.name for f in status.get('armingFlags', [])]
            if 'ARMING_DISABLED_SENSORS_CALIBRATING' not in af_names:
                break
            time.sleep(0.5)
        print(f"    Calibration done. Flags: {af_names}")
    return api


def snap(api, label):
    """Read status + channels, print and return dict."""
    print(f"\n  [{label}]")
    _, status = api.get_inav_status()
    af_list = status.get('armingFlags', [])
    af_names = [f.name for f in af_list]
    rc_link = 'ARMING_DISABLED_RC_LINK' in af_names
    failsafe = any(m['boxName'] == 'FAILSAFE'
                   for m in status.get('activeModes', []))
    _, rc = api.get_rc_channels()
    print(f"    armingFlags:        {af_names}")
    print(f"    RC_LINK blocked:    {rc_link}")
    print(f"    FAILSAFE active:    {failsafe}")
    print(f"    channel count:      {len(rc)}")
    print(f"    CH1-8:              {rc[:8]}")
    return {'af': af_names, 'rc_link': rc_link, 'failsafe': failsafe,
            'ch_count': len(rc), 'rc': rc}


def jitter_test(api, n=20, interval=0.1):
    """Sample RC n times. Return (any_change, channel_change_counts)."""
    samples = []
    for i in range(n):
        _, rc = api.get_rc_channels()
        samples.append(rc[:])
        if i < n - 1:
            time.sleep(interval)
    if not samples:
        return False, []
    first = samples[0]
    ch_count = len(first)
    counts = [0] * ch_count
    for s in samples[1:]:
        for c in range(min(ch_count, len(s))):
            if s[c] != first[c]:
                counts[c] += 1
    any_change = any(counts)
    changed_chs = [(i + 1, counts[i]) for i in range(ch_count) if counts[i] > 0]
    print(f"    Jitter ({n}×{interval}s): any_change={any_change}  "
          f"changed_channels={changed_chs if changed_chs else 'none'}")
    print(f"    First: {first}")
    print(f"    Last:  {samples[-1]}")
    return any_change, counts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

print("=" * 65)
print("  UART CRSF Discrimination Probe v2")
print("=" * 65)

# 1. Connect and read current config
api = connect("initial")

print("\nCurrent serial config:")
orig_ports = read_serial_cfg(api)
orig_rx_port = next((p for p in orig_ports if p['has_rx']), None)
for p in orig_ports:
    rx = " <-- RX_SERIAL" if p['has_rx'] else ""
    print(f"  id={p['id']} funcMask=0x{p['func_mask']:08X} bauds={p['bauds']}{rx}")

if orig_rx_port is None:
    print("WARNING: No RX_SERIAL port found in current config!")
else:
    print(f"\nRX_SERIAL is on port id={orig_rx_port['id']}")

# Find UART2 (id=2) for the "wrong" port test
uart2 = next((p for p in orig_ports if p['id'] == 2), None)
if uart2 is None:
    print("FATAL: UART2 (id=2) not in serial config — cannot run wrong-port test.")
    api.close()
    sys.exit(1)

# -----------------------------------------------------------------------
# Reboot first to get a clean post-reboot baseline (not mid-session state)
# -----------------------------------------------------------------------
print("\n" + "=" * 65)
print("  CASE A: Rebooting with CORRECT config (receiver on working port)")
print("=" * 65)
api = reboot_and_reconnect(api, wait_calibrate=True)

print()
case_a = snap(api, "Case A: correct port, post-reboot steady state")
print()
print("  Jitter test Case A:")
jitter_a, counts_a = jitter_test(api, n=20, interval=0.1)

# -----------------------------------------------------------------------
# Switch to wrong port: move RX_SERIAL from id=orig to id=2
# -----------------------------------------------------------------------
print("\n" + "=" * 65)
print("  Switching CRSF to UART2 (nothing connected)")
print("=" * 65)

# Remove from current port
if orig_rx_port:
    new_func = orig_rx_port['func_mask'] & ~FUNCTION_RX_SERIAL
    print(f"  id={orig_rx_port['id']}: 0x{orig_rx_port['func_mask']:08X} -> 0x{new_func:08X}")
    set_port(api, orig_rx_port['id'], new_func, orig_rx_port['bauds'])

# Add to UART2
new_func_uart2 = uart2['func_mask'] | FUNCTION_RX_SERIAL
print(f"  id=2: 0x{uart2['func_mask']:08X} -> 0x{new_func_uart2:08X}")
set_port(api, 2, new_func_uart2, uart2['bauds'])

# Verify
print("\n  Config after changes (before reboot):")
new_ports = read_serial_cfg(api)
for p in new_ports:
    rx = " <-- RX_SERIAL" if p['has_rx'] else ""
    print(f"  id={p['id']} funcMask=0x{p['func_mask']:08X}{rx}")

# -----------------------------------------------------------------------
# Reboot with wrong config, read Case B
# -----------------------------------------------------------------------
print("\n" + "=" * 65)
print("  CASE B: Rebooting with WRONG config (UART2, nothing connected)")
print("=" * 65)
api = reboot_and_reconnect(api, wait_calibrate=True)

print()
case_b = snap(api, "Case B: wrong port (UART2), post-reboot steady state")
print()
print("  Jitter test Case B:")
jitter_b, counts_b = jitter_test(api, n=20, interval=0.1)

# -----------------------------------------------------------------------
# Restore original config and reboot
# -----------------------------------------------------------------------
print("\n" + "=" * 65)
print("  RESTORING original config")
print("=" * 65)

# Remove from UART2
set_port(api, 2, uart2['func_mask'], uart2['bauds'])
print(f"  id=2: restored to 0x{uart2['func_mask']:08X}")

# Restore original port
if orig_rx_port:
    set_port(api, orig_rx_port['id'], orig_rx_port['func_mask'], orig_rx_port['bauds'])
    print(f"  id={orig_rx_port['id']}: restored to 0x{orig_rx_port['func_mask']:08X}")

print("\n  Config after restore (before final reboot):")
restored_ports = read_serial_cfg(api)
for p in restored_ports:
    rx = " <-- RX_SERIAL" if p['has_rx'] else ""
    print(f"  id={p['id']} funcMask=0x{p['func_mask']:08X}{rx}")

api = reboot_and_reconnect(api, wait_calibrate=True)
print()
case_r = snap(api, "Restored config, should match Case A")
api.close()

# -----------------------------------------------------------------------
# Final comparison
# -----------------------------------------------------------------------
print()
print("=" * 65)
print("  FINAL COMPARISON")
print("=" * 65)
print()
w = 30
print(f"{'Metric':<{w}}  {'Case A (correct port)':^22}  {'Case B (wrong/UART2)':^22}")
print("-" * (w + 50))


def row(name, a, b):
    diff = " <-- DIFFERS" if a != b else ""
    print(f"  {name:<{w-2}}  {str(a):^22}  {str(b):^22}{diff}")


row("RC_LINK blocked", case_a['rc_link'], case_b['rc_link'])
row("FAILSAFE active", case_a['failsafe'], case_b['failsafe'])
row("Channel count", case_a['ch_count'], case_b['ch_count'])
row("Any jitter on CH6", counts_a[5] > 0 if len(counts_a) > 5 else 'N/A',
    counts_b[5] > 0 if len(counts_b) > 5 else 'N/A')
row("Any jitter (any ch)", jitter_a, jitter_b)
row("CH1 value", case_a['rc'][0] if case_a['rc'] else 'N/A',
    case_b['rc'][0] if case_b['rc'] else 'N/A')
row("CH4 value", case_a['rc'][3] if len(case_a['rc']) > 3 else 'N/A',
    case_b['rc'][3] if len(case_b['rc']) > 3 else 'N/A')

print()
print("  Arming flags:")
print(f"    Case A: {case_a['af']}")
print(f"    Case B: {case_b['af']}")
print()

# Determine if distinguishable
signals = []
if case_a['rc_link'] != case_b['rc_link']:
    signals.append("RC_LINK flag")
if case_a['failsafe'] != case_b['failsafe']:
    signals.append("FAILSAFE active mode")
if case_a['ch_count'] != case_b['ch_count']:
    signals.append(f"channel count ({case_a['ch_count']} vs {case_b['ch_count']})")
if jitter_a != jitter_b:
    signals.append("channel jitter")
if (len(counts_a) > 5 and len(counts_b) > 5 and
        (counts_a[5] > 0) != (counts_b[5] > 0)):
    signals.append("CH6 jitter specifically")
if case_a['af'] != case_b['af']:
    signals.append(f"arming flags differ")

if signals:
    print(f"  RESULT: Cases ARE distinguishable via: {signals}")
else:
    print("  RESULT: Cases are NOT distinguishable — both look identical.")

print()
print("Done.")
