#!/usr/bin/env python3
"""Compare Betaflight ACTUAL rates vs INAV rate curves.

Usage: python3 plot_rates_comparison.py [--save filename.png]
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt


def bf_actual_rate(s, center_sens, max_rate, expo):
    """Betaflight ACTUAL rates curve.

    s: normalized stick input [0, 1]
    center_sens: center sensitivity in dps
    max_rate: max rate in dps
    expo: 0.0 to 1.0
    """
    stick_movement = max(0, max_rate - center_sens)
    expof = np.abs(s) * (s**5 * expo + s * (1 - expo))
    return s * center_sens + stick_movement * expof


def inav_rate(s, max_rate, expo):
    """INAV rate curve (expo + linear scaling).

    s: normalized stick input [0, 1]
    max_rate: max rate in dps (rates setting * 10)
    expo: 0.0 to 1.0
    """
    rc_command = s * (1 - expo * (1 - s**2))
    return rc_command * max_rate


def main():
    parser = argparse.ArgumentParser(description="Plot BF ACTUAL vs INAV rate curves")
    parser.add_argument("--save", type=str, help="Save plot to file instead of displaying")
    args = parser.parse_args()

    s = np.linspace(0, 1, 200)

    # User's Betaflight ACTUAL settings
    bf_center = 145  # dps
    bf_max = 533     # dps
    bf_expo = 0.5

    # INAV equivalents
    inav_max = 530   # rates=53 -> 530 dps
    inav_expo_70 = 0.70
    inav_expo_75 = 0.75

    bf_curve = bf_actual_rate(s, bf_center, bf_max, bf_expo)
    inav_curve_70 = inav_rate(s, inav_max, inav_expo_70)
    inav_curve_75 = inav_rate(s, inav_max, inav_expo_75)
    linear = s * bf_max  # reference linear curve

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left plot: absolute rate (dps)
    ax1.plot(s * 100, bf_curve, "b-", linewidth=2.5, label=f"BF ACTUAL (center={bf_center}, max={bf_max}, expo={int(bf_expo*100)})")
    ax1.plot(s * 100, inav_curve_70, "r--", linewidth=2, label=f"INAV (rates=53, expo=70)")
    ax1.plot(s * 100, inav_curve_75, "g-.", linewidth=2, label=f"INAV (rates=53, expo=75)")
    ax1.plot(s * 100, linear, "k:", linewidth=1, alpha=0.4, label="Linear (no expo)")
    ax1.set_xlabel("Stick deflection (%)", fontsize=12)
    ax1.set_ylabel("Rate (deg/sec)", fontsize=12)
    ax1.set_title("Rate vs Stick Position", fontsize=13)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, bf_max * 1.05)

    # Right plot: difference (INAV - BF)
    diff_70 = inav_curve_70 - bf_curve
    diff_75 = inav_curve_75 - bf_curve
    ax2.plot(s * 100, diff_70, "r--", linewidth=2, label="INAV expo=70 minus BF")
    ax2.plot(s * 100, diff_75, "g-.", linewidth=2, label="INAV expo=75 minus BF")
    ax2.axhline(y=0, color="b", linewidth=1, alpha=0.5)
    ax2.fill_between(s * 100, diff_70, 0, alpha=0.1, color="red")
    ax2.fill_between(s * 100, diff_75, 0, alpha=0.1, color="green")
    ax2.set_xlabel("Stick deflection (%)", fontsize=12)
    ax2.set_ylabel("Rate difference (deg/sec)", fontsize=12)
    ax2.set_title("INAV minus Betaflight ACTUAL", fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 100)

    plt.tight_layout()

    if args.save:
        plt.savefig(args.save, dpi=150, bbox_inches="tight")
        print(f"Saved to {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
