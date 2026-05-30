#!/usr/bin/env python3
"""
test_dma_ordering.py — Hardware test for DMA disable ordering bug (STM32F4 stdperiph)

BUG DESCRIPTION
===============
STM32 Reference Manual (RM0090 §10.3.17) requires this order when stopping
a DMA-driven timer channel:

    1. Disable the TIMER DMA request:  TIM_DMACmd(tim, src, DISABLE)
    2. THEN disable the DMA stream:    DMA_Cmd(stream, DISABLE)

The buggy code had it backwards in five places across three driver files:
    - timer_impl_stdperiph.c: impl_timerPWMStopDMA, impl_timerPWMPrepareDMA, IRQ handler
    - timer_impl_stdperiph_at32.c: impl_timerPWMStopDMA
    - timer_impl_hal.c: IRQ handler

WHY ARMING IS NOT REQUIRED
===========================
impl_timerPWMPrepareDMA is called on EVERY DShot scheduler frame (~2000Hz at
DShot600) regardless of arm state — the FC continuously sends motor_disarmed[]
values via DShot even when disarmed. Each call executes the buggy DISABLE
sequence inside an ATOMIC_BLOCK. The race window is ~one timer period (~400ns
at DShot600) per frame: after DMA_Cmd(DISABLE) but before TIM_DMACmd(DISABLE),
the timer hardware can assert a DMA request directly to the DMA controller
(bypassing CPU interrupts) to a stream that is now disabled.

Over ~2000 frames/sec, the race fires on some boards within seconds. No arming
needed.

HOW THE TEST WORKS
==================
1. Connect to FC (must be DISARMED — props off recommended)
2. Send MSP_SET_MOTOR commands to cycle motor values (maximises DShot DMA traffic)
3. Between motor commands, query FC status and measure round-trip latency
4. After all iterations, check whether latency degraded over the run

If the DMA controller gets corrupted by the race:
- The DMA stream EN bit may refuse to clear cleanly
- impl_timerPWMPrepareDMA's polling loop (if present) spins longer
- Or the DMA fires a transfer-error interrupt that preempts the main loop
- Both show as increased MSP response latency

INTERPRETING RESULTS
====================
BUGGY firmware — expected pattern on susceptible boards:
  - Early iterations (1-50):   normal latency ~1-5 ms
  - Mid iterations (50-200):   occasional spikes, latency climbing
  - Late iterations (200+):    persistent latency > 20ms or MSP timeouts

FIXED firmware — expected pattern:
  - All iterations: flat latency, zero timeouts

NOTE: The race is non-deterministic. A PASS with buggy firmware does NOT
prove correctness — it means the race wasn't triggered this run.
Compare buggy vs fixed runs across multiple boards/runs for confidence.

PREREQUISITES
=============
- Physical FC with DShot configured on motor outputs (AIKONF4V3, MATEKF405, etc.)
- FC DISARMED (the test will abort if armed)
- PROPS OFF if using --motor-value > 0
- mspapi2 installed: cd ~/Documents/planes/inavflight/mspapi2 && pip install .
- If running in sandbox: use dangerouslyDisableSandbox: true for serial port access

USAGE
=====
  # Basic run — 300 iterations, motor values toggled, no spin
  python3 test_dma_ordering.py /dev/ttyACM0

  # More iterations for a longer soak (better chance of triggering race)
  python3 test_dma_ordering.py /dev/ttyACM0 --iterations 1000

  # Spin motors slightly (REMOVE PROPS) — more DShot DMA activity
  python3 test_dma_ordering.py /dev/ttyACM0 --motor-value 1050

  # Verbose per-iteration output
  python3 test_dma_ordering.py /dev/ttyACM0 --verbose

CONNECTION NOTES
================
read_timeout in MSPSerial is the serial-chunk read interval for the background
reader thread — NOT the MSP request timeout.  Keeping it at the default 0.05 s
lets the reader thread deliver responses promptly.  Using 1.0 s means responses
can arrive up to 1 s late relative to the request deadline, causing false
timeouts even when the FC responds correctly.

MSP2_INAV_STATUS (code 8192) requires MSP v2 framing.  The script probes this
first and falls back to MSP_STATUS_EX (code 150, MSP v1) automatically if the
FC does not support MSP v2.  MSP_STATUS_EX also carries the full armingFlags
field and is sufficient for both the arming check and latency measurement.
"""

from __future__ import annotations

import argparse
import statistics
import struct
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Locate mspapi2 relative to this script
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_MSPAPI2_ROOT = _SCRIPT_DIR.parents[3] / "mspapi2"
if _MSPAPI2_ROOT.exists():
    sys.path.insert(0, str(_MSPAPI2_ROOT))

try:
    from mspapi2 import MSPApi
    from mspapi2.mspcodec import InavMSP
except ImportError:
    print()
    print("ERROR: mspapi2 library not found.")
    print(f"  Expected location: {_MSPAPI2_ROOT}")
    print("  Install with: cd ~/Documents/planes/inavflight/mspapi2 && pip install .")
    print()
    sys.exit(1)

# ---------------------------------------------------------------------------
# MSP constants
# ---------------------------------------------------------------------------
MSP_SET_MOTOR = 214   # write motor_disarmed[] values (safe while disarmed)

# Motor value alternation: toggle between LOW and HIGH each iteration to
# maximise DShot DMA prepare/stop cycles.
MOTOR_LOW  = 1000   # digital idle (no spin)
MOTOR_HIGH = 1050   # just above idle (no spin at this value on most ESCs)

# Arming flag bitmask — armingFlag_e.ARMED = (1 << 2) in runtime_config.h
_ARMED_BIT = 1 << 2


# ---------------------------------------------------------------------------
# Status query backend — probes MSP2 first, falls back to MSP v1
# ---------------------------------------------------------------------------

class _StatusBackend:
    """
    Queries FC status for armingFlags and measures round-trip latency.

    Tries MSP2_INAV_STATUS (MSP v2, code 8192) first.  If the FC does not
    respond (older firmware or MSP v2 not enabled), falls back permanently to
    MSP_STATUS_EX (MSP v1, code 150) which also carries the full armingFlags
    field.

    This fallback is tried once during _probe() so the hot loop never spends
    time on doomed MSP v2 attempts.
    """

    # MSP_STATUS_EX reply layout (little-endian):
    #   uint16 cycleTime, uint16 i2cErrors, uint16 sensorStatus,
    #   uint32 activeModesLow, uint8 profile, uint16 cpuLoad,
    #   uint16 armingFlags, uint8 accCalibAxisFlags
    # Total: 14 bytes minimum.
    _STATUS_EX_CODE = int(InavMSP.MSP_STATUS_EX)   # 150
    _INAV_STATUS_CODE = InavMSP.MSP2_INAV_STATUS    # enum member (8192)

    def __init__(self, api: MSPApi) -> None:
        self._api = api
        self._use_msp2: Optional[bool] = None   # None = not probed yet

    def probe(self) -> bool:
        """
        Determine which backend works.  Returns True if at least one works.
        Sets self._use_msp2 to True or False.
        """
        # Try MSP2_INAV_STATUS
        try:
            info, _ = self._api._request(self._INAV_STATUS_CODE, timeout=2.0)
            if info.get("latency_ms") is not None:
                self._use_msp2 = True
                print(f"  [INFO] FC supports MSP2_INAV_STATUS "
                      f"(latency={info['latency_ms']:.0f}ms)")
                return True
        except Exception as exc:
            print(f"  [INFO] MSP2_INAV_STATUS not available: {exc}")

        # Fall back to MSP_STATUS_EX (v1)
        try:
            raw_info, raw_payload = self._api._request_raw(
                InavMSP.MSP_STATUS_EX, timeout=2.0
            )
            if raw_info.get("latency_ms") is not None:
                self._use_msp2 = False
                print(f"  [INFO] Using MSP_STATUS_EX fallback "
                      f"(latency={raw_info['latency_ms']:.0f}ms)")
                return True
        except Exception as exc:
            print(f"  [FAIL] MSP_STATUS_EX also failed: {exc}")

        return False

    def query(self) -> Optional[Tuple[float, int]]:
        """
        Query FC status.  Returns (latency_ms, armingFlags) or None on error.
        """
        if self._use_msp2 is None:
            # Should not happen after probe(), but guard anyway
            if not self.probe():
                return None

        if self._use_msp2:
            return self._query_msp2()
        else:
            return self._query_status_ex()

    def _query_msp2(self) -> Optional[Tuple[float, int]]:
        try:
            info, rep = self._api._request(self._INAV_STATUS_CODE, timeout=2.0)
            latency = info.get("latency_ms") or 0.0
            arming_flags = rep["armingFlags"]
            return float(latency), int(arming_flags)
        except Exception:
            return None

    def _query_status_ex(self) -> Optional[Tuple[float, int]]:
        """
        MSP_STATUS_EX reply layout (16 bytes):
          u16 cycleTime, u16 i2cErrors, u16 sensorStatus,
          u32 activeModesLow, u8 profile, u16 cpuLoad,
          u16 armingFlags, u8 accCalibAxisFlags
        armingFlags is at byte offset 13 (2+2+2+4+1+2 = 13), uint16.
        """
        try:
            info, payload = self._api._request_raw(InavMSP.MSP_STATUS_EX, timeout=2.0)
            latency = info.get("latency_ms") or 0.0
            if len(payload) < 15:
                return None
            arming_flags = struct.unpack_from("<H", payload, 13)[0]
            return float(latency), int(arming_flags)
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ok(msg: str) -> None:   print(f"  [PASS] {msg}")
def _fail(msg: str) -> None: print(f"  [FAIL] {msg}")
def _info(msg: str) -> None: print(f"  [INFO] {msg}")
def _warn(msg: str) -> None: print(f"  [WARN] {msg}")


def _connect(endpoint: str) -> Optional[MSPApi]:
    is_tcp = ":" in endpoint and not endpoint.startswith("/")
    print(f"Connecting to FC: {endpoint} ({'TCP' if is_tcp else 'serial'}) ...")

    # IMPORTANT: read_timeout here is the serial chunk read interval for the
    # background reader thread — NOT the MSP request timeout.  Keep it at
    # the default 0.05 s so responses are delivered promptly.  Using 1.0 s
    # causes false timeouts: the reader can block for up to 1 s before
    # delivering an MSP frame, which races with the 1–2 s request deadline.
    try:
        if is_tcp:
            api = MSPApi(tcp_endpoint=endpoint)
        else:
            api = MSPApi(port=endpoint, baudrate=115200)
        api.open()
    except PermissionError as exc:
        _fail(f"Permission denied on {endpoint}: {exc}")
        print("  Fix: sudo usermod -aG dialout $USER  (then log out and back in)")
        print("  If running in sandbox: retry with dangerouslyDisableSandbox: true")
        return None
    except Exception as exc:
        _fail(f"Cannot open connection: {exc}")
        print("  Check: is another program (configurator) using the port?")
        print("  If running in sandbox: retry with dangerouslyDisableSandbox: true")
        return None

    _ok(f"Port opened: {endpoint}")
    _info("Waiting 2 s for USB-CDC to settle (Linux DTR toggle resets STM32) ...")
    time.sleep(2.0)

    # Sanity check using MSP_API_VERSION (v1, code 1) — this always works
    # regardless of MSP v2 support, confirming the FC is alive and speaking MSP.
    try:
        info, version = api.get_api_version()
        latency = info.get("latency_ms") or 0.0
        _ok(f"FC responding — MSP API {version['apiVersionMajor']}."
            f"{version['apiVersionMinor']} (latency={latency:.0f}ms)")
    except Exception as exc:
        _fail(f"FC not responding to MSP_API_VERSION: {exc}")
        print("  FC may be in CLI mode — send 'exit\\n' to the port, or reset FC.")
        print("  Is the configurator still connected?")
        api.close()
        return None

    return api


def _set_motors(api: MSPApi, value: int, count: int = 8) -> bool:
    """Send MSP_SET_MOTOR with all motors at the given value."""
    payload = struct.pack(f"<{count}H", *([value] * count))
    try:
        # MSPSerial.send(code: int, payload: bytes) — code 214 < 256 → MSP v1
        api._serial.send(MSP_SET_MOTOR, payload)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Latency trend analysis
# ---------------------------------------------------------------------------

def _analyse_trend(latencies: List[float]) -> Tuple[bool, str]:
    """
    Split run into first/second half and compare mean latency.
    Returns (is_degrading, description).
    A >50% increase indicates progressive DMA controller corruption.
    """
    if len(latencies) < 20:
        return False, "too few samples"

    half = len(latencies) // 2
    mean_first  = statistics.mean(latencies[:half])
    mean_second = statistics.mean(latencies[half:])

    if mean_first > 0 and mean_second > mean_first * 1.5:
        ratio = mean_second / mean_first
        return True, (
            f"degraded {ratio:.1f}x  "
            f"(first-half avg={mean_first:.1f}ms  second-half avg={mean_second:.1f}ms)"
        )

    return False, (
        f"stable  "
        f"(first-half avg={mean_first:.1f}ms  second-half avg={mean_second:.1f}ms)"
    )


# ---------------------------------------------------------------------------
# Main test
# ---------------------------------------------------------------------------

def run_test(
    endpoint: str,
    iterations: int = 300,
    motor_value: int = 0,
    verbose: bool = False,
) -> int:
    """
    Run the disarmed motor-test DMA stress loop.
    Returns 0 = PASS, 1 = FAIL, 2 = setup error.
    """
    print()
    print("=" * 70)
    print("DMA DISABLE ORDERING BUG — Disarmed Motor-Test Stress Loop")
    print("=" * 70)
    print()
    print("Bug: timer_impl_stdperiph.c — impl_timerPWMPrepareDMA and IRQ handler")
    print("     Wrong order: DMA_Cmd(DISABLE) before TIM_DMACmd(DISABLE)")
    print("     Correct: TIM_DMACmd(DISABLE) first, then DMA_Cmd(DISABLE)")
    print()
    print(f"Parameters:")
    print(f"  Endpoint:        {endpoint}")
    print(f"  Iterations:      {iterations}")
    print(f"  Motor value:     {motor_value}  "
          f"{'(no spin — digital idle)' if motor_value <= 1000 else '(PROPS OFF!)'}")
    print()

    if motor_value > 1000:
        print("  !! Motors WILL spin. Remove propellers before continuing.")
        try:
            input("  Press ENTER to continue or Ctrl-C to abort ... ")
        except KeyboardInterrupt:
            print("\n  Aborted.")
            return 2

    # --- Connect ---
    api = _connect(endpoint)
    if api is None:
        return 2

    try:
        # --- Probe which status backend works ---
        _info("Probing FC status backend ...")
        backend = _StatusBackend(api)
        if not backend.probe():
            _fail("FC is not responding to any status command — cannot run test.")
            return 2

        # --- Safety: must be disarmed ---
        result = backend.query()
        if result is None:
            _fail("Could not read arming state — check connection")
            return 2
        _, arming_flags = result
        is_armed = bool(arming_flags & _ARMED_BIT)
        if is_armed:
            _fail("FC is ARMED. Disarm before running this test.")
            return 2
        _ok(f"FC is disarmed (armingFlags=0x{arming_flags:08X})")

        # --- Brief warm-up: set motors to idle to ensure DShot DMA is active ---
        _info("Setting motors to idle value to activate DShot DMA path ...")
        _set_motors(api, MOTOR_LOW)
        time.sleep(0.5)

        # --- Main stress loop ---
        print()
        print(f"Starting {iterations} iterations ...")
        print("(Each iteration: toggle motor value → query MSP latency)")
        if not verbose:
            print("(Use --verbose for per-iteration output)")
        print()

        latencies: List[float] = []
        timeouts = 0
        motor_errors = 0

        for i in range(1, iterations + 1):
            # Alternate motor value each iteration to maximise DMA prepare cycles
            value = motor_value if motor_value > MOTOR_LOW else (
                MOTOR_HIGH if i % 2 == 0 else MOTOR_LOW
            )
            if not _set_motors(api, value):
                motor_errors += 1

            # Small gap so the DShot scheduler runs at least one frame
            time.sleep(0.01)

            # Measure MSP latency — proxy for main-loop / DMA health
            result = backend.query()
            if result is None:
                timeouts += 1
                latencies.append(0.0)
                if verbose:
                    print(f"  Iter {i:4d}/{iterations}  TIMEOUT")
            else:
                latency, _ = result
                latencies.append(latency)
                if verbose:
                    print(f"  Iter {i:4d}/{iterations}  latency={latency:6.1f}ms")

            if not verbose and i % 50 == 0:
                recent = [l for l in latencies[max(0, i-50):] if l > 0]
                avg = statistics.mean(recent) if recent else 0
                print(f"  Iter {i:4d}/{iterations}  "
                      f"recent avg={avg:.1f}ms  timeouts={timeouts}  motor_errors={motor_errors}")

    finally:
        # Leave motors at idle before disconnecting
        try:
            _set_motors(api, MOTOR_LOW)
            api.close()
        except Exception:
            pass

    # --- Analysis ---
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()

    good = [l for l in latencies if l > 0]
    timeout_pct = 100.0 * timeouts / iterations
    error_pct   = 100.0 * motor_errors / iterations

    print(f"  Iterations:      {iterations}")
    print(f"  MSP timeouts:    {timeouts}  ({timeout_pct:.1f}%)")
    print(f"  Motor cmd errors:{motor_errors}  ({error_pct:.1f}%)")
    print()

    degrading = False
    trend_desc = "no data"

    if good:
        print(f"  Latency (ms):")
        print(f"    min:   {min(good):.1f}")
        print(f"    max:   {max(good):.1f}")
        print(f"    mean:  {statistics.mean(good):.1f}")
        if len(good) > 1:
            print(f"    stdev: {statistics.stdev(good):.1f}")
        print()

        degrading, trend_desc = _analyse_trend(good)
        print(f"  Latency trend:  {trend_desc}")
        print()

    # --- Verdict ---
    max_latency = max(good) if good else 0.0

    failures = []
    if timeout_pct > 5.0:
        failures.append(f"MSP timeout rate {timeout_pct:.1f}% > 5%  (DMA may be wedged)")
    if max_latency > 50.0:
        failures.append(f"Max latency {max_latency:.1f}ms > 50ms  (DMA stop path too slow)")
    if degrading:
        failures.append(f"Latency degraded over run: {trend_desc}")

    if failures:
        print("VERDICT: FAIL")
        print()
        print("  Failure reasons:")
        for f in failures:
            print(f"    - {f}")
        print()
        print("  Consistent with DMA disable ordering bug.")
        print("  After applying fix (TIM_DMACmd DISABLE before DMA_Cmd DISABLE),")
        print("  re-run — all metrics should be within normal bounds.")
        return 1
    else:
        print("VERDICT: PASS")
        print()
        print("  All metrics within normal bounds.")
        print("  NOTE: Race is non-deterministic. A PASS with buggy firmware")
        print("  does not prove correctness. Run more iterations or compare")
        print("  buggy vs fixed firmware across multiple runs.")
        return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stress-test DMA disable ordering bug via disarmed motor-test loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "endpoint",
        help="Serial port (/dev/ttyACM0) or TCP endpoint (localhost:5760)",
    )
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=300,
        help="Number of motor-toggle + MSP-query cycles (default: 300)",
    )
    parser.add_argument(
        "--motor-value",
        type=int,
        default=0,
        metavar="THROTTLE",
        help=(
            "Fixed motor value to hold (0 = alternate 1000/1050 each iter, default: 0). "
            "Values 1000-2000. REMOVE PROPS if > 1000."
        ),
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-iteration latency",
    )

    args = parser.parse_args()

    if args.motor_value != 0 and not (1000 <= args.motor_value <= 2000):
        parser.error("--motor-value must be 0 or between 1000 and 2000")

    sys.exit(run_test(
        endpoint=args.endpoint,
        iterations=args.iterations,
        motor_value=args.motor_value,
        verbose=args.verbose,
    ))


if __name__ == "__main__":
    main()
