#!/usr/bin/env python3
"""
UART1 vs UART2 CRSF Receiver Discrimination Probe
===================================================
Tests whether MSP commands can distinguish:
  Case A: CRSF receiver correctly on UART1 (working)
  Case B: CRSF configured on UART2 (nothing connected)

Protocol:
  1. Read baseline on current config (expected: UART0/id=0 has RX_SERIAL)
  2. Move RX_SERIAL to UART2 (id=2), reboot, read again
  3. Restore RX_SERIAL to original port, reboot

Note: If running in a sandbox, use dangerouslyDisableSandbox: true.

Usage:
    python3 probe_uart_discrimination.py [port]
    python3 probe_uart_discrimination.py /dev/ttyACM0
"""

import sys
import time
import struct

DEVICE = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD = 115200

FUNCTION_RX_SERIAL = (1 << 6)   # 64  — from inav/src/main/io/serial.h

# Baud index 8 = 400000 (what the FC currently uses for all ports)
BAUD_INDEX_400K = 8
BAUD_INDEX_AUTO = 0

PORT_NAMES = {
    0: 'UART0/VCP', 1: 'UART1', 2: 'UART2', 3: 'UART3',
    4: 'UART4', 5: 'UART5', 6: 'UART6',
    20: 'USB_VCP', 100: 'LPUART1',
}

try:
    from mspapi2 import MSPApi
    from mspapi2.lib import InavEnums
except ImportError as e:
    print(f"FAILED to import mspapi2: {e}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def connect(device=DEVICE, baud=BAUD, retries=5, delay=1.5):
    """Open MSP connection with retries (FC may be rebooting)."""
    for attempt in range(1, retries + 1):
        try:
            api = MSPApi(port=device, baudrate=baud)
            api.open()
            # Sanity check
            _, ver = api.get_api_version()
            print(f"    Connected (attempt {attempt}): API {ver.get('apiVersionMajor','?')}.{ver.get('apiVersionMinor','?')}")
            return api
        except Exception as e:
            print(f"    Attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
    print("FATAL: Could not connect to FC.")
    print("  Check: Is FC plugged in? Is configurator closed?")
    print("  If running in sandbox: retry with dangerouslyDisableSandbox: true")
    sys.exit(1)


def read_serial_config(api):
    """Return list of dicts, one per serial port."""
    code_ret, raw = api._serial.request(4105, payload=bytes(), timeout=2.0)
    entry_size = 9
    ports = []
    for i in range(len(raw) // entry_size):
        off = i * entry_size
        ident = raw[off]
        func_mask = struct.unpack_from('<I', raw, off + 1)[0]
        bauds = raw[off + 5: off + 9]
        ports.append({
            'id': ident,
            'name': PORT_NAMES.get(ident, f'PORT_{ident}'),
            'func_mask': func_mask,
            'bauds': list(bauds),
            'has_rx_serial': bool(func_mask & FUNCTION_RX_SERIAL),
        })
    return ports


def print_serial_config(ports):
    print("  Serial port configuration:")
    for p in ports:
        rx_marker = " <-- RX_SERIAL" if p['has_rx_serial'] else ""
        print(f"    {p['name']} (id={p['id']}): funcMask=0x{p['func_mask']:08X}{rx_marker}")


def set_serial_port_function(api, port_id, func_mask, bauds):
    """Send MSP2_COMMON_SET_SERIAL_CONFIG for one port (9 bytes)."""
    payload = struct.pack('<BIBBBb', port_id, func_mask,
                          bauds[0], bauds[1], bauds[2], bauds[3])
    # MSP v2 request — use _serial directly
    code_ret, reply = api._serial.request(
        4106, payload=payload, timeout=2.0, mspv=2
    )
    return reply


def read_status(api, label):
    """Read arming flags and RC channels, print a summary, return dict."""
    print(f"\n  --- {label} ---")

    # Arming flags via MSP2_INAV_STATUS (8192)
    _, status = api.get_inav_status()
    af_list = status.get('armingFlags', [])
    af_names = [f.name for f in af_list]
    rc_link_blocked = any(f.name == 'ARMING_DISABLED_RC_LINK' for f in af_list)
    failsafe_active = any(m['boxName'] == 'FAILSAFE'
                          for m in status.get('activeModes', []))

    print(f"  armingFlags:          {af_names}")
    print(f"  ARMING_DISABLED_RC_LINK: {rc_link_blocked}")
    print(f"  FAILSAFE mode active: {failsafe_active}")

    # RC channels
    _, rc = api.get_rc_channels()
    ch_count = len(rc)
    print(f"  RC channel count:     {ch_count}")
    print(f"  CH1-8:                {rc[:8]}")
    if ch_count > 8:
        print(f"  CH9-{ch_count}:               {rc[8:]}")

    return {
        'af_names': af_names,
        'rc_link_blocked': rc_link_blocked,
        'failsafe_active': failsafe_active,
        'ch_count': ch_count,
        'rc': rc,
    }


def sample_jitter(api, n=20, interval=0.1):
    """Sample MSP_RC n times. Return (any_change, all_samples)."""
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
    any_change = False
    ch_changes = [0] * ch_count
    for s in samples[1:]:
        for c in range(min(ch_count, len(s))):
            if s[c] != first[c]:
                any_change = True
                ch_changes[c] += 1

    print(f"  Jitter analysis ({n} samples over {n * interval:.1f}s):")
    print(f"    Any channel changed:  {any_change}")
    changed_chs = [(i + 1, ch_changes[i]) for i in range(ch_count) if ch_changes[i] > 0]
    if changed_chs:
        print(f"    Channels with changes: {changed_chs}")
    else:
        print(f"    All channels perfectly stable across all samples")
    print(f"    First sample:  {first}")
    print(f"    Last  sample:  {samples[-1]}")
    return any_change, samples


def reboot_and_reconnect(api, device=DEVICE, baud=BAUD):
    """Send MSP_REBOOT, close port, wait, reconnect."""
    print("  Sending MSP_REBOOT ...")
    try:
        api._serial.request(68, payload=bytes(), timeout=2.0)
    except Exception:
        pass  # FC reboots before it can send ACK sometimes
    api.close()
    print("  Waiting 5s for FC to reboot ...")
    time.sleep(5)
    print("  Reconnecting ...")
    return connect(device, baud, retries=8, delay=1.5)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

print("=" * 65)
print("  UART1 vs UART2 CRSF Receiver Discrimination Probe")
print("=" * 65)
print(f"  FC device: {DEVICE}")
print()

print("Connecting to FC ...")
api = connect()

# -----------------------------------------------------------------------
# Read and save current serial config
# -----------------------------------------------------------------------
print("\nReading current serial port configuration ...")
orig_ports = read_serial_config(api)
print_serial_config(orig_ports)

rx_port = next((p for p in orig_ports if p['has_rx_serial']), None)
if rx_port is None:
    print("\nWARNING: No port currently has RX_SERIAL configured!")
    print("  The baseline may not be meaningful.")
else:
    print(f"\n  RX_SERIAL is on: {rx_port['name']} (id={rx_port['id']})")

print()

# -----------------------------------------------------------------------
# Experiment 6: Baseline — current state (receiver on its configured port)
# -----------------------------------------------------------------------
print("=" * 65)
print("  EXPERIMENT 6: Baseline — current working configuration")
print("=" * 65)

baseline = read_status(api, "Baseline status")

print()
print("  Jitter test (20 samples x 100ms = 2s):")
baseline_jitter, baseline_samples = sample_jitter(api, n=20, interval=0.1)

# -----------------------------------------------------------------------
# Experiment 7: Reconfigure RX_SERIAL to UART2 (id=2), nothing connected
# -----------------------------------------------------------------------
print()
print("=" * 65)
print("  EXPERIMENT 7: Move RX_SERIAL to UART2 (nothing connected)")
print("=" * 65)

# Find UART2 (id=2) current config
uart2 = next((p for p in orig_ports if p['id'] == 2), None)
if uart2 is None:
    print("  UART2 (id=2) not found in serial config — cannot run this experiment.")
    print("  Skipping Experiment 7.")
    wrongport_result = None
else:
    # Step 1: Remove RX_SERIAL from current port (set its funcMask to 0, or
    # clear only the RX_SERIAL bit)
    if rx_port:
        new_func_orig = rx_port['func_mask'] & ~FUNCTION_RX_SERIAL
        print(f"  Removing RX_SERIAL from {rx_port['name']} (id={rx_port['id']}): "
              f"funcMask 0x{rx_port['func_mask']:08X} -> 0x{new_func_orig:08X}")
        try:
            set_serial_port_function(api, rx_port['id'], new_func_orig, rx_port['bauds'])
            print("    OK")
        except Exception as e:
            print(f"    Error: {e}")

    # Step 2: Add RX_SERIAL to UART2 (id=2)
    new_func_uart2 = uart2['func_mask'] | FUNCTION_RX_SERIAL
    print(f"  Adding RX_SERIAL to UART2 (id=2): "
          f"funcMask 0x{uart2['func_mask']:08X} -> 0x{new_func_uart2:08X}")
    try:
        set_serial_port_function(api, 2, new_func_uart2, uart2['bauds'])
        print("    OK")
    except Exception as e:
        print(f"    Error: {e}")

    # Verify config was accepted
    print()
    print("  Verifying serial config before reboot ...")
    new_ports = read_serial_config(api)
    print_serial_config(new_ports)

    # Reboot
    print()
    api = reboot_and_reconnect(api)

    # Read state with RX on wrong port
    wrongport = read_status(api, "Wrong port (UART2, nothing connected)")

    print()
    print("  Jitter test (20 samples x 100ms = 2s) on wrong port:")
    wrongport_jitter, wrongport_samples = sample_jitter(api, n=20, interval=0.1)

    wrongport_result = {
        'status': wrongport,
        'jitter': wrongport_jitter,
    }

    # -----------------------------------------------------------------------
    # Restore original config
    # -----------------------------------------------------------------------
    print()
    print("=" * 65)
    print("  RESTORING original serial configuration")
    print("=" * 65)

    # Remove RX_SERIAL from UART2
    print("  Removing RX_SERIAL from UART2 ...")
    try:
        set_serial_port_function(api, 2, uart2['func_mask'], uart2['bauds'])
        print("    OK")
    except Exception as e:
        print(f"    Error: {e}")

    # Restore to original port
    if rx_port:
        print(f"  Restoring RX_SERIAL to {rx_port['name']} (id={rx_port['id']}) ...")
        try:
            set_serial_port_function(api, rx_port['id'], rx_port['func_mask'], rx_port['bauds'])
            print("    OK")
        except Exception as e:
            print(f"    Error: {e}")

    # Verify
    print()
    print("  Verifying restored config before reboot ...")
    restored_ports = read_serial_config(api)
    print_serial_config(restored_ports)

    # Final reboot to apply restored config
    print()
    api = reboot_and_reconnect(api)
    print("  Verifying final state after restore reboot ...")
    restored_status = read_status(api, "Restored state (should match baseline)")

# -----------------------------------------------------------------------
# Final comparison summary
# -----------------------------------------------------------------------
print()
print("=" * 65)
print("  FINAL COMPARISON")
print("=" * 65)
print()
print(f"{'Metric':<35} {'Case A: Working (UART1)':^25} {'Case B: Wrong port (UART2)':^25}")
print("-" * 85)

if wrongport_result:
    ws = wrongport_result['status']
    bs = baseline
    print(f"{'RC_LINK blocked':<35} {str(bs['rc_link_blocked']):^25} {str(ws['rc_link_blocked']):^25}")
    print(f"{'FAILSAFE mode active':<35} {str(bs['failsafe_active']):^25} {str(ws['failsafe_active']):^25}")
    print(f"{'Channel count':<35} {str(bs['ch_count']):^25} {str(ws['ch_count']):^25}")
    print(f"{'Any channel jitter':<35} {str(baseline_jitter):^25} {str(wrongport_result['jitter']):^25}")
    print(f"{'CH1 value':<35} {str(bs['rc'][0] if bs['rc'] else 'N/A'):^25} {str(ws['rc'][0] if ws['rc'] else 'N/A'):^25}")
    print(f"{'CH4 value':<35} {str(bs['rc'][3] if len(bs['rc'])>3 else 'N/A'):^25} {str(ws['rc'][3] if len(ws['rc'])>3 else 'N/A'):^25}")
    print(f"{'Arming flags':<35}")
    print(f"  Baseline:   {bs['af_names']}")
    print(f"  Wrong port: {ws['af_names']}")

    print()
    print("DISTINGUISHABLE?")
    distinguishable = []
    if bs['rc_link_blocked'] != ws['rc_link_blocked']:
        distinguishable.append("RC_LINK flag differs")
    if bs['ch_count'] != ws['ch_count']:
        distinguishable.append(f"Channel count differs ({bs['ch_count']} vs {ws['ch_count']})")
    if baseline_jitter != wrongport_result['jitter']:
        distinguishable.append(f"Jitter differs ({baseline_jitter} vs {wrongport_result['jitter']})")
    if bs['af_names'] != ws['af_names']:
        distinguishable.append(f"Arming flags differ")

    if distinguishable:
        print(f"  YES — distinguishing signals: {distinguishable}")
    else:
        print("  NO — both cases look identical via MSP")
else:
    print("  (Experiment 7 was skipped — UART2 not found in config)")

api.close()
print()
print("Done.")
