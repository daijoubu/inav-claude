#!/usr/bin/env python3
"""
Calculate local derivative dT/dγ for pitch-to-throttle compensation.

This is the LOCAL approach - how much does thrust need to change
for a small pitch change to maintain constant airspeed?
"""

import math

def thrust_for_angle(gamma_deg, L_D):
    """
    Calculate required thrust (as fraction of weight) to maintain
    constant airspeed at pitch angle gamma.

    T/W = cos(γ)/(L/D) + sin(γ)

    Args:
        gamma_deg: Pitch angle in degrees
        L_D: Lift-to-drag ratio

    Returns:
        T/W ratio needed at this angle
    """
    gamma_rad = math.radians(gamma_deg)
    return math.cos(gamma_rad) / L_D + math.sin(gamma_rad)

def derivative_dT_dgamma(gamma_deg, L_D):
    """
    Calculate dT/dγ (derivative of thrust with respect to pitch angle).

    dT/dγ = W × [-sin(γ)/(L/D) + cos(γ)]

    Returns the coefficient (excluding W), per radian.
    To convert to per degree, divide by 57.3.

    Args:
        gamma_deg: Pitch angle in degrees
        L_D: Lift-to-drag ratio

    Returns:
        Derivative coefficient (will be multiplied by W and divided by 57.3 for per-degree)
    """
    gamma_rad = math.radians(gamma_deg)
    # Per radian
    deriv_per_rad = -math.sin(gamma_rad) / L_D + math.cos(gamma_rad)
    # Convert to per degree
    deriv_per_deg = deriv_per_rad / 57.3
    return deriv_per_deg

def throttle_gain_us_per_deg(gamma_deg, L_D, T_W):
    """
    Calculate nav_fw_pitch2thr gain in μs/° for a given pitch angle.

    The gain is: (dT/dγ_deg) / T_max × 1000 μs

    Args:
        gamma_deg: Pitch angle in degrees
        L_D: Lift-to-drag ratio
        T_W: Thrust-to-weight ratio (T_max/W)

    Returns:
        Gain in μs/° at this pitch angle
    """
    # dT/dγ in terms of W per degree
    dT_dgamma_coeff = derivative_dT_dgamma(gamma_deg, L_D)

    # Convert to throttle fraction per degree
    # throttle_fraction = T/T_max = (T/W) / (T_max/W) = (T/W) / α
    # d(throttle_fraction)/dγ = (dT/dγ)/T_max = (W × coeff) / (α × W) = coeff / α

    throttle_fraction_per_deg = dT_dgamma_coeff / T_W

    # Convert to μs (1000 μs range)
    gain_us_per_deg = throttle_fraction_per_deg * 1000

    return gain_us_per_deg

# Test for various T/W ratios and pitch angles
L_D = 10.0

print("=" * 70)
print("LOCAL DERIVATIVE ANALYSIS: dT/dγ for constant airspeed")
print("=" * 70)
print(f"\nAssuming L/D = {L_D}\n")

# Test different T/W ratios
T_W_ratios = [0.5, 0.75, 1.0, 1.5, 2.0]

for T_W in T_W_ratios:
    print(f"\n{'='*70}")
    print(f"T/W = {T_W}:1")
    print(f"{'='*70}")
    print(f"{'Pitch (°)':<12} {'T/W needed':<15} {'dT/dγ coeff':<15} {'Gain (μs/°)':<15}")
    print("-" * 70)

    for gamma in [-20, -10, -5, 0, 5, 10, 15, 20]:
        T_W_needed = thrust_for_angle(gamma, L_D)
        derivative_coeff = derivative_dT_dgamma(gamma, L_D)
        gain = throttle_gain_us_per_deg(gamma, L_D, T_W)

        print(f"{gamma:<12} {T_W_needed:<15.4f} {derivative_coeff:<15.4f} {gain:<15.2f}")

# Summary: Gain at level flight for different T/W
print("\n" + "=" * 70)
print("SUMMARY: nav_fw_pitch2thr gain at level flight (γ=0°)")
print("=" * 70)
print(f"{'T/W Ratio':<15} {'Gain (μs/°)':<20} {'Approximate':<20}")
print("-" * 70)

for T_W in T_W_ratios:
    gain_exact = throttle_gain_us_per_deg(0, L_D, T_W)
    # Approximate formula: 1000/(57.3 × α)
    gain_approx = 1000 / (57.3 * T_W)
    print(f"{T_W:<15.2f} {gain_exact:<20.2f} {gain_approx:<20.2f}")

print("\n" + "=" * 70)
print("KEY INSIGHT: Higher T/W aircraft need LOWER gain!")
print("=" * 70)
print("""
Why? Because the same thrust change (in Newtons) represents a smaller
fraction of their total available thrust.

For local pitch changes (±20°), the gain is approximately:

    nav_fw_pitch2thr ≈ 17.5 / (T/W ratio)

Example:
  - 0.5:1 T/W (glider): gain ≈ 35 μs/°
  - 1:1 T/W (typical):  gain ≈ 17.5 μs/°
  - 2:1 T/W (sport):    gain ≈ 8.75 μs/°

The current INAV default of 10 μs/° is optimized for high-performance
aircraft (T/W ≈ 1.75:1), which explains why it under-compensates for
typical aircraft (T/W ≈ 1:1).
""")
