#!/usr/bin/env python3
"""
Calculate constant-airspeed envelopes for T/W < 1.0 aircraft.

For these aircraft, we can use the full 0-100% throttle range
and maintain constant airspeed across a range of pitch angles.
"""

import math

def solve_pitch_for_throttle(throttle_pct, T_W_max, L_D, V_ratio_squared):
    """
    Solve for pitch angle given throttle percentage.

    Force balance: T = W[cos(γ)/(L/D) + sin(γ)]
    Where T = throttle_pct × T_W_max × W

    Rearranging: sin(γ) + cos(γ)/(L/D) = throttle_pct × T_W_max

    At constant airspeed V, drag D = (W/L_D) × (V/V_ref)²
    where V_ref is the reference speed where D = W/L_D in level flight.

    Args:
        throttle_pct: Throttle percentage (0.0 to 1.0)
        T_W_max: Maximum thrust-to-weight ratio
        L_D: Lift-to-drag ratio
        V_ratio_squared: (V/V_ref)² - determines drag level

    Returns:
        Pitch angle in degrees, or None if no solution
    """
    # At this airspeed, drag in level flight is:
    # D/W = (1/L_D) × V_ratio_squared

    # Force balance for constant airspeed:
    # T/W = D/W + sin(γ) = (V²/V_ref²)/L_D + sin(γ)

    # Where T/W = throttle_pct × T_W_max

    # So: throttle_pct × T_W_max = V_ratio_squared/L_D + sin(γ)

    # Therefore: sin(γ) = throttle_pct × T_W_max - V_ratio_squared/L_D

    sin_gamma = throttle_pct * T_W_max - V_ratio_squared / L_D

    # Check if solution exists
    if sin_gamma < -1.0 or sin_gamma > 1.0:
        return None

    gamma_rad = math.asin(sin_gamma)
    gamma_deg = math.degrees(gamma_rad)

    return gamma_deg

def find_envelope(T_W_max, L_D, V_ratio_squared):
    """
    Find the pitch angle envelope for constant airspeed.

    Args:
        T_W_max: Maximum thrust-to-weight ratio
        L_D: Lift-to-drag ratio
        V_ratio_squared: (V/V_ref)²

    Returns:
        Dictionary with angles for 0%, 50%, 100% throttle
    """
    angles = {}

    for throttle_pct, label in [(0.0, "0%"), (0.5, "50%"), (1.0, "100%")]:
        angle = solve_pitch_for_throttle(throttle_pct, T_W_max, L_D, V_ratio_squared)
        angles[label] = angle

    return angles

# Calculate envelopes for T/W < 1.0
L_D = 10.0
print("=" * 70)
print("CONSTANT AIRSPEED ENVELOPES FOR T/W < 1.0 AIRCRAFT")
print("=" * 70)
print(f"\nAssuming L/D = {L_D}\n")

# Try different airspeeds (as ratio to V_ref)
for V_ratio in [0.8, 1.0, 1.2]:
    V_ratio_squared = V_ratio ** 2

    print(f"\n{'='*70}")
    print(f"Airspeed: V = {V_ratio:.1f} × V_ref")
    print(f"{'='*70}\n")

    for T_W in [0.5, 0.75, 0.9]:
        print(f"T/W = {T_W}:1")
        envelope = find_envelope(T_W, L_D, V_ratio_squared)

        if envelope["0%"] is None or envelope["100%"] is None:
            print("  Cannot maintain this airspeed with available thrust range")
        else:
            width = envelope["100%"] - envelope["0%"]
            print(f"  0% throttle:   {envelope['0%']:6.1f}°")
            print(f"  50% throttle:  {envelope['50%']:6.1f}°")
            print(f"  100% throttle: {envelope['100%']:6.1f}°")
            print(f"  Width:         {width:6.1f}°")

        print()

# Choose best airspeed for visualization
print("\n" + "=" * 70)
print("RECOMMENDED FOR VISUALIZATION: V = 1.0 × V_ref")
print("=" * 70)
print("\nThis gives clean angles suitable for diagrams:\n")

V_ratio_squared = 1.0

for T_W in [0.5, 0.75]:
    envelope = find_envelope(T_W, L_D, V_ratio_squared)
    width = envelope["100%"] - envelope["0%"]

    print(f"T/W = {T_W}:1")
    print(f"  0% throttle:   {envelope['0%']:6.1f}°")
    print(f"  50% throttle:  {envelope['50%']:6.1f}°")
    print(f"  100% throttle: {envelope['100%']:6.1f}°")
    print(f"  Width:         {width:6.1f}°")
    print()
