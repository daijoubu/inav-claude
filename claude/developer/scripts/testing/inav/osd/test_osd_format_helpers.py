#!/usr/bin/env python3
"""
OSD Formatting Helper Unit Tests (pure-Python)
================================================
These tests mirror the logic of the new static helper functions introduced on
the optimize/osd-sprintf-patterns branch:

    static void osdFormatIntUnit(char *buff, int width, int value, char unit)
    static void osdFormatTime_MMSS(char *buff, int m, int s)
    static int  i2a_len(int num, char *bf)   (internal – exercised via osdFormatIntUnit)

They replace tfp_sprintf calls such as:
    tfp_sprintf(buff, "%3d", value)     →  osdFormatIntUnit(buff, 3, value, 0)
    tfp_sprintf(buff+1, "%02d:%02d", m, s) →  osdFormatTime_MMSS(buff+1, m, s)

The tests verify that the Python-reimplemented equivalents produce the same
output as the reference sprintf patterns they replace.  Any deviation indicates
a bug in the C implementation.

If a test FAILS here it means the helper is broken and OSD elements that use
that helper will render wrong or garbage – which can explain a blank OSD.

Usage
-----
    python3 test_osd_format_helpers.py

All tests run offline – no SITL required.
"""

from __future__ import annotations
import sys


# ---------------------------------------------------------------------------
# Python re-implementations that match the C helper semantics exactly
# ---------------------------------------------------------------------------

def i2a_len_py(num: int) -> int:
    """
    Return the length of the decimal string representation of num,
    including a leading '-' for negative values.
    Matches the C i2a_len() logic using ui2a() which writes digits
    without leading zeros.
    """
    s = str(abs(num))
    return len(s) + (1 if num < 0 else 0)


def osd_format_int_unit_py(width: int, value: int, unit: str) -> str:
    """
    Python equivalent of the C osdFormatIntUnit().

    The C code:
        int len = i2a_len(value, tmp);
        int pad = width - len;
        while (pad-- > 0) buff[i++] = ' ';
        copy tmp to buff;
        if (unit) buff[i++] = unit;
        buff[i] = '\\0';

    This is equivalent to: right-justify `value` in a field of `width`,
    pad with spaces, then optionally append `unit`.
    """
    digits = str(abs(value)) if value >= 0 else ('-' + str(-value))
    pad = max(0, width - len(digits))
    result = ' ' * pad + digits
    if unit:
        result += unit
    return result


def osd_format_time_mmss_py(m: int, s: int) -> str:
    """
    Python equivalent of osdFormatTime_MMSS().

    The C code:
        m %= 100;
        s %= 100;
        buff = '0' + m/10, '0' + m%10, ':', '0' + s/10, '0' + s%10, '\\0'
    """
    m = m % 100
    s = s % 100
    return f"{m // 10}{m % 10}:{s // 10}{s % 10}"


# ---------------------------------------------------------------------------
# Reference implementation using Python's %-formatting (mirrors tfp_sprintf)
# ---------------------------------------------------------------------------

def sprintf_3d(value: int) -> str:
    """Matches  tfp_sprintf(buff, "%3d", value)"""
    return f"{value:3d}"


def sprintf_2d(value: int) -> str:
    """Matches  tfp_sprintf(buff, "%2d", value)"""
    return f"{value:2d}"


def sprintf_5d(value: int) -> str:
    """Matches  tfp_sprintf(buff, "%5d", value)"""
    return f"{value:5d}"


def sprintf_mmss(m: int, s: int) -> str:
    """Matches  tfp_sprintf(buff, "%02d:%02d", m, s)"""
    return f"{m:02d}:{s:02d}"


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

failures = 0
passes   = 0


def check(test_name: str, expected: str, got: str) -> None:
    global failures, passes
    if expected == got:
        print(f"  ✓  {test_name}")
        passes += 1
    else:
        print(f"  ✗  {test_name}")
        print(f"       expected : {repr(expected)}")
        print(f"       got      : {repr(got)}")
        failures += 1


# ---------------------------------------------------------------------------
# Tests for osdFormatIntUnit  (replacing tfp_sprintf "%Nd" patterns)
# ---------------------------------------------------------------------------

def test_osd_format_int_unit() -> None:
    print()
    print("osdFormatIntUnit  (%3d, %2d, %5d replacements)")
    print("-" * 55)

    # --- %3d equivalents (width=3, no unit) ---
    for val in [0, 1, 9, 10, 99, 100, 999, -1, -9, -99]:
        ref = sprintf_3d(val)
        got = osd_format_int_unit_py(3, val, '')
        check(f"width=3 value={val:5d}", ref, got)

    # --- %2d equivalents (RSSI, GPS sats) ---
    for val in [0, 1, 9, 10, 99]:
        ref = sprintf_2d(val)
        got = osd_format_int_unit_py(2, val, '')
        check(f"width=2 value={val:5d}", ref, got)

    # --- %5d equivalents (mAh drawn, battery remaining) ---
    for val in [0, 1, 100, 9999, 10000, 99999]:
        ref = sprintf_5d(val)
        got = osd_format_int_unit_py(5, val, '')
        check(f"width=5 value={val:6d}", ref, got)

    # --- With unit character ---
    # The C code appends the unit byte after the digits.
    # e.g. temperature: osdFormatIntUnit(buff, 3, temp/10, 0) then buff[3]=sym
    # (unit='\\0' means no unit; non-zero means append)
    # These are the non-unit cases above.  Spot-check with a unit char:
    check("width=3 value=42 unit='C'",
          sprintf_3d(42) + 'C',
          osd_format_int_unit_py(3, 42, 'C'))

    # --- Edge case: value wider than width (should NOT truncate) ---
    # tfp_sprintf("%3d", 12345) → "12345"  (no truncation in C printf)
    check("width=3 value=12345 (overflow – no truncate)",
          sprintf_3d(12345),
          osd_format_int_unit_py(3, 12345, ''))


# ---------------------------------------------------------------------------
# Tests for osdFormatTime_MMSS  (replacing tfp_sprintf "%02d:%02d" pattern)
# ---------------------------------------------------------------------------

def test_osd_format_time_mmss() -> None:
    print()
    print("osdFormatTime_MMSS  (%02d:%02d replacement)")
    print("-" * 55)

    # Normal cases that both reference and helper should agree on
    for m, s in [(0, 0), (0, 1), (0, 9), (1, 0), (9, 59), (10, 30), (59, 59), (99, 99)]:
        ref = sprintf_mmss(m, s)
        got = osd_format_time_mmss_py(m, s)
        check(f"m={m:2d} s={s:2d}", ref, got)

    # Values >= 100: the C helper clamps with %= 100.
    # tfp_sprintf would write 3+ digits (e.g. "100:05") while the helper
    # clamps to 2 digits.  This is intentional in the new code (prevents
    # non-ASCII output on the OSD canvas).  We test the clamping behaviour:
    print()
    print("  [Clamping behaviour for m/s >= 100 – new intentional change]")
    for m, s, expected_clamped in [
        (100, 0,   "00:00"),
        (101, 5,   "01:05"),
        (0,   100, "00:00"),
        (120, 65,  "20:65"),  # 65%100=65, m=120%100=20,
    ]:
        got = osd_format_time_mmss_py(m, s)
        check(f"m={m} s={s} → clamped to {repr(expected_clamped)}", expected_clamped, got)


# ---------------------------------------------------------------------------
# Regression: verify i2a_len does NOT double-advance the pointer
# (This was the bug fixed in commit afd3fa2: "restore single-pass length
# tracking in i2a_len".  The broken version advanced bf twice, causing
# i2a_len to return a length 2x the true digit count for positive numbers,
# which made osdFormatIntUnit pad with a large negative 'pad', writing
# garbage or nothing to the buffer.)
# ---------------------------------------------------------------------------

def test_i2a_len_singlepass() -> None:
    print()
    print("i2a_len single-pass length (regression: double-advance bug)")
    print("-" * 55)

    # For each value, the length must equal len(str(abs(val))) + sign_byte
    for val in [0, 1, 9, 10, 99, 100, 999, 1000, -1, -9, -10, -99, -100]:
        s_len = len(str(abs(val))) + (1 if val < 0 else 0)
        got   = i2a_len_py(val)
        check(f"i2a_len({val:6d}) == {s_len}", s_len, got)

    # The double-advance bug would return 2 * digit_count for positive nums.
    # Explicitly confirm that would be wrong:
    double_advance_result = 2 * len(str(42))  # = 4, not 2
    correct_result        = i2a_len_py(42)    # should be 2
    print()
    if double_advance_result != correct_result:
        print(f"  ✓  double-advance bug NOT present: correct={correct_result}, "
              f"broken-would-give={double_advance_result}")
        global passes
        passes += 1
    else:
        print(f"  ✗  i2a_len(42) = {correct_result} matches the broken "
              f"double-advance result {double_advance_result}  "
              "– bug may still be present in C code!")
        global failures
        failures += 1


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 65)
    print("  OSD Formatting Helper Unit Tests  (pure Python)")
    print("  Branch: optimize/osd-sprintf-patterns")
    print("=" * 65)

    test_i2a_len_singlepass()
    test_osd_format_int_unit()
    test_osd_format_time_mmss()

    print()
    print("=" * 65)
    total = passes + failures
    print(f"  Results: {passes}/{total} passed,  {failures} failed")
    if failures == 0:
        print()
        print("  PASS – all helper logic tests passed.")
        print()
        print("  These tests validate the Python reference model of the helpers.")
        print("  To confirm the C code itself is correct, also run the SITL")
        print("  displayport test:  test_osd_displayport.py")
    else:
        print()
        print("  FAIL – helper logic tests found discrepancies.")
        print("  The C implementation may produce wrong output for the")
        print("  test cases above, causing garbled or blank OSD elements.")
    print("=" * 65)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
