#!/usr/bin/env python3
"""
Unit Test: ALTHOLD Climb Rate Sign

Tests the climb rate sign computation in navigation_multicopter.c
for the adjustAltitudeFromRCInput() function.

This is a pure code-logic test (no SITL required) that verifies:
  - Throttle LOW (below midpoint) -> negative climb rate (DESCENT)
  - Throttle HIGH (above midpoint) -> positive climb rate (CLIMB)
  - Throttle MID (within deadband) -> zero climb rate (HOLD)

The PR branch introduced a bug at line 147-149 of navigation_multicopter.c:

MAINLINE (correct):
    int16_t limitValue = rcThrottleAdjustment > 0 ? getMaxThrottle() : getThrottleIdleValue();
    limitValue = applyDeadbandRescaled(limitValue - altHoldThrottleRCZero, deadband, -500, 500);
    // When throttle is LOW: limitValue is NEGATIVE -> rcClimbRate = ABS/NEG = NEGATIVE -> DESCENT ✓

PR BRANCH (buggy):
    int16_t limitValue = rcThrottleAdjustment > 0 ?
        (getMaxThrottle() - altHoldThrottleRCZero) :
        (altHoldThrottleRCZero - getThrottleIdleValue());
    // When throttle is LOW: limitValue = 1500-1000 = +500 (POSITIVE!)
    // -> rcClimbRate = ABS/POSITIVE = ALWAYS POSITIVE -> CLIMB ✗ (BUG!)

Usage:
    python3 test_althold_climb_rate_sign.py
    python3 test_althold_climb_rate_sign.py --branch [mainline|pr]

The --branch flag simulates either code path.
"""

import sys
import argparse

PASS = "PASS"
FAIL = "FAIL"


def scale_range(x: int, src_from: int, src_to: int, dest_from: int, dest_to: int) -> int:
    """Port of INAV scaleRange() from maths.c."""
    if src_to == src_from:
        return dest_from
    return int(dest_from + (x - src_from) * (dest_to - dest_from) / (src_to - src_from))


def apply_deadband_rescaled(value: int, deadband: int, min_val: int, max_val: int) -> int:
    """
    Port of INAV applyDeadbandRescaled() from common/maths.c:

    int32_t applyDeadbandRescaled(int32_t value, int32_t deadband, int32_t min, int32_t max)
    {
        if (ABS(value) < deadband) {
            value = 0;
        } else if (value > 0) {
            value = scaleRange(value - deadband, 0, max - deadband, 0, max);
        } else if (value < 0) {
            value = scaleRange(value + deadband, min + deadband, 0, min, 0);
        }
        return value;
    }
    """
    if abs(value) < deadband:
        return 0
    elif value > 0:
        return scale_range(value - deadband, 0, max_val - deadband, 0, max_val)
    else:
        return scale_range(value + deadband, min_val + deadband, 0, min_val, 0)


def compute_climb_rate_mainline(
        throttle: int,
        alt_hold_throttle_rc_zero: int,
        alt_hold_deadband: int,
        max_manual_climb_rate: int,
        throttle_idle: int,
        throttle_max: int,
) -> int:
    """
    Simulate the MAINLINE version of adjustAltitudeFromRCInput() climb rate calculation.

    Source: navigation_multicopter.c (mainline, commit 86247026 and earlier):
        const int16_t rcThrottleAdjustment = applyDeadbandRescaled(
            rcCommand[THROTTLE] - altHoldThrottleRCZero, deadband, -500, 500);
        if (rcThrottleAdjustment) {
            int16_t limitValue = rcThrottleAdjustment > 0 ? getMaxThrottle() : getThrottleIdleValue();
            limitValue = applyDeadbandRescaled(limitValue - altHoldThrottleRCZero, deadband, -500, 500);
            int16_t rcClimbRate = ABS(rcThrottleAdjustment) * max_manual_climb_rate / limitValue;
            ...
        }
    """
    rc_adj = apply_deadband_rescaled(
        throttle - alt_hold_throttle_rc_zero,
        alt_hold_deadband, -500, 500
    )

    if rc_adj == 0:
        return 0  # Within deadband -> HOLD

    limit_raw = throttle_max if rc_adj > 0 else throttle_idle
    limit_value = apply_deadband_rescaled(
        limit_raw - alt_hold_throttle_rc_zero,
        alt_hold_deadband, -500, 500
    )

    if limit_value == 0:
        return 0  # Avoid division by zero

    rc_climb_rate = abs(rc_adj) * max_manual_climb_rate // limit_value
    return rc_climb_rate


def compute_climb_rate_pr_branch(
        throttle: int,
        alt_hold_throttle_rc_zero: int,
        alt_hold_deadband: int,
        max_manual_climb_rate: int,
        throttle_idle: int,
        throttle_max: int,
) -> int:
    """
    Simulate the PR BRANCH version of adjustAltitudeFromRCInput() climb rate calculation.

    Source: navigation_multicopter.c (PR branch):
        const int16_t rcThrottleAdjustment = applyDeadbandRescaled(
            rcCommand[THROTTLE] - altHoldThrottleRCZero, deadband, -500, 500);
        if (rcThrottleAdjustment) {
            int16_t limitValue = rcThrottleAdjustment > 0 ?
                (getMaxThrottle() - altHoldThrottleRCZero) :
                (altHoldThrottleRCZero - getThrottleIdleValue());
            if (limitValue <= 0) {
                limitValue = 1;  // Prevent division by zero/negative
            }
            int16_t rcClimbRate = ABS(rcThrottleAdjustment) * max_manual_climb_rate / limitValue;
            ...
        }

    BUG: When throttle < altHoldThrottleRCZero (stick LOW):
      limitValue = altHoldThrottleRCZero - getThrottleIdleValue() = 1500 - 1000 = +500 (POSITIVE!)
      rcClimbRate = ABS(negative_adj) * rate / POSITIVE = ALWAYS POSITIVE = CLIMB (wrong!)
    """
    rc_adj = apply_deadband_rescaled(
        throttle - alt_hold_throttle_rc_zero,
        alt_hold_deadband, -500, 500
    )

    if rc_adj == 0:
        return 0  # Within deadband -> HOLD

    # BUG IS HERE: limit_value is always positive
    if rc_adj > 0:
        limit_value = throttle_max - alt_hold_throttle_rc_zero   # e.g. 2000-1500 = +500
    else:
        limit_value = alt_hold_throttle_rc_zero - throttle_idle  # e.g. 1500-1000 = +500 (POSITIVE!)

    if limit_value <= 0:
        limit_value = 1  # PR branch defensive check

    rc_climb_rate = abs(rc_adj) * max_manual_climb_rate // limit_value
    # BUG: rc_climb_rate is ALWAYS positive because limit_value is always positive
    return rc_climb_rate


def run_tests(branch: str):
    """
    Run climb rate sign tests for the specified branch.
    Returns (passed, failed) counts.
    """
    # Default INAV parameters
    ALT_HOLD_DEADBAND = 40
    ALT_HOLD_THROTTLE_RC_ZERO = 1500   # Default hover throttle = throttle mid
    MAX_MANUAL_CLIMB_RATE = 500        # cm/s
    THROTTLE_IDLE = 1000              # min throttle (default)
    THROTTLE_MAX = 2000               # max throttle (default)

    compute_fn = compute_climb_rate_pr_branch if branch == "pr" else compute_climb_rate_mainline

    print(f"\nTesting branch: {branch.upper()}")
    print(f"  altHoldThrottleRCZero={ALT_HOLD_THROTTLE_RC_ZERO}")
    print(f"  deadband={ALT_HOLD_DEADBAND}")
    print(f"  max_manual_climb_rate={MAX_MANUAL_CLIMB_RATE} cm/s")
    print(f"  throttle_idle={THROTTLE_IDLE}, throttle_max={THROTTLE_MAX}")

    test_cases = [
        # (description, throttle, expected_sign, expected_direction)
        ("Throttle LOW=1200 (stick below midpoint)", 1200, -1, "DESCENT"),
        ("Throttle LOW=1100 (stick well below midpoint)", 1100, -1, "DESCENT"),
        ("Throttle MID=1500 (at midpoint, within deadband)", 1500, 0, "HOLD"),
        ("Throttle HIGH=1800 (stick above midpoint)", 1800, +1, "CLIMB"),
        ("Throttle HIGH=1900 (stick well above midpoint)", 1900, +1, "CLIMB"),
    ]

    passed = 0
    failed = 0

    for desc, throttle, expected_sign, expected_dir in test_cases:
        climb_rate = compute_fn(
            throttle,
            ALT_HOLD_THROTTLE_RC_ZERO,
            ALT_HOLD_DEADBAND,
            MAX_MANUAL_CLIMB_RATE,
            THROTTLE_IDLE,
            THROTTLE_MAX,
        )

        actual_dir = "DESCENT" if climb_rate < 0 else "CLIMB" if climb_rate > 0 else "HOLD"

        if actual_dir == expected_dir:
            status = PASS
            passed += 1
        else:
            status = FAIL
            failed += 1

        icon = "+" if status == PASS else "x"
        print(f"\n  [{icon}] {desc}")
        print(f"       throttle={throttle}, rcClimbRate={climb_rate:+d} cm/s")
        print(f"       Expected: {expected_dir}, Got: {actual_dir} -> {status}")

    return passed, failed


def main():
    parser = argparse.ArgumentParser(description="ALTHOLD climb rate sign unit test")
    parser.add_argument("--branch", choices=["mainline", "pr", "both"], default="both",
                        help="Which branch to test (default: both)")
    args = parser.parse_args()

    print("=" * 70)
    print("ALTHOLD CLIMB RATE SIGN TEST")
    print("Tests navigation_multicopter.c adjustAltitudeFromRCInput() function")
    print("=" * 70)

    total_passed = 0
    total_failed = 0

    branches = ["mainline", "pr"] if args.branch == "both" else [args.branch]

    for branch in branches:
        p, f = run_tests(branch)
        total_passed += p
        total_failed += f

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Total Passed: {total_passed}")
    print(f"  Total Failed: {total_failed}")
    print()

    if args.branch == "both":
        main_p, _ = run_tests.__wrapped__("mainline") if hasattr(run_tests, '__wrapped__') else (0, 0)
        print("VERDICT:")
        print("  MAINLINE: All tests should PASS (correct behavior)")
        print("  PR BRANCH: Tests for LOW throttle should FAIL (direction inverted)")
        print()
        print("BUG: The PR branch changes limitValue from signed (via applyDeadbandRescaled)")
        print("     to unsigned (always positive subtraction). This makes rcClimbRate always")
        print("     positive, so the copter always CLIMBS regardless of stick position.")
        print()
        print("Affected code in navigation_multicopter.c adjustAltitudeFromRCInput():")
        print()
        print("  BEFORE (mainline - correct):")
        print("    int16_t limitValue = rcThrottleAdj > 0 ? getMaxThrottle() : getThrottleIdleValue();")
        print("    limitValue = applyDeadbandRescaled(limitValue - altHoldThrottleRCZero, ...);")
        print("    // limitValue is NEGATIVE when stick LOW -> rcClimbRate = ABS/NEG = NEGATIVE = DESCENT")
        print()
        print("  AFTER (PR branch - BUGGY):")
        print("    int16_t limitValue = rcThrottleAdj > 0 ?")
        print("        (getMaxThrottle() - altHoldThrottleRCZero) :     // +500 when HIGH")
        print("        (altHoldThrottleRCZero - getThrottleIdleValue()); // +500 when LOW (BUG!)")
        print("    // limitValue is ALWAYS POSITIVE -> rcClimbRate is ALWAYS POSITIVE = always CLIMB")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
