# Derived Formulas - Quick Reference

**Key mathematical relationships derived from aerodynamic principles**

---

## Vertical Flight Velocity Ratio

**Relationship between climb and descent speeds at extreme throttle settings**

### Formula

For an aircraft with thrust-to-weight ratio α = T/W:

```
V_climb (at 100% throttle, 90°)
─────────────────────────────────── = √(α - 1)
V_descent (at 0% throttle, -90°)
```

**Expressed as:**
```
V_climb = V_descent × √(α - 1)
```

Where:
- **V_climb** = airspeed at 90° nose-up, 100% throttle
- **V_descent** = airspeed at 90° nose-down, 0% throttle
- **α** = T/W = thrust-to-weight ratio
- **Both velocities at steady-state (constant airspeed)**

### Derivation

**Force balance at constant velocity (vertical flight):**

**Key principle:** At constant airspeed, parasitic drag D = ½ρV²S·C_D is the same regardless of pitch angle, climb, or descent.

90° climb at steady-state:
```
T_max = W + D
```

Where D is the parasitic drag at airspeed V_climb.

90° descent at steady-state:
```
0 = W - D
D = W
```

Where D is the parasitic drag at airspeed V_descent.

Since both represent parasitic drag at their respective airspeeds:
```
½ρV_climb²S·C_D = T_max - W = αW - W = W(α - 1)
½ρV_descent²S·C_D = W
```

Taking the ratio:
```
V_climb²/V_descent² = (α - 1)
V_climb/V_descent = √(α - 1)
```

**Only valid when steady-state is maintainable:** Requires α > 1 for any positive climb airspeed.

### Verification

| T/W Ratio (α) | √(α - 1) | V_climb/V_descent | Steady-State Maintainable? | Physical Meaning |
|---------------|----------|-------------------|---------------------------|------------------|
| 0.5:1 | √(-0.5) | undefined | ❌ No | Cannot sustain vertical climb |
| 1:1 | √0 | 0 | ⚠️ Hover only | V_climb = 0 (hover) ✓ |
| 1.5:1 | √0.5 | 0.707 | ✅ Yes | Climb at 71% of descent speed |
| 2:1 | √1 | 1.0 | ✅ Yes | Same speed both ways ✓ |
| 2.5:1 | √1.5 | 1.225 | ✅ Yes | Climb 22% faster than descent |
| 3:1 | √2 | 1.414 | ✅ Yes | Climb 41% faster than descent |

**Special cases:**
- **α = 1:** V_climb = 0 (hover condition - limit of maintainability)
- **α = 2:** V_climb = V_descent (symmetric velocities)
- **α < 1:** No solution (insufficient thrust for vertical climb)

**For nav_fw_pitch2thr application:** This formula only applies when both climb and descent at constant airspeed are maintainable (α ≥ 1).

### Assumptions

1. **Vertical flight only** (90° pitch angles)
2. **Steady-state maintainable** (constant airspeed, no acceleration)
   - Requires α > 1 for positive climb airspeed
   - α = 1 gives hover (V_climb = 0)
   - α < 1 cannot maintain vertical climb
3. **Parasitic drag** - Drag depends only on airspeed: D = ½ρV²S·C_D
   - Same airspeed → same drag, regardless of pitch/climb/descent
4. **Constant C_D** (no Reynolds effects or compressibility)

### Limitations

- Only applies to purely vertical flight (90° pitch)
- Does not apply to intermediate angles (need L/D analysis)
- Only considers cases where steady-state flight is achievable
- For nav_fw_pitch2thr application, realistic flight uses ±20° (not ±90°)

---

## Thrust Symmetry Point (Force Balance)

**The pitch angle that is exactly halfway between max and min throttle for maintaining constant airspeed**

### Formula (Approximate, for L/D ≥ 8)

```
γ_symmetry ≈ arcsin(α/2) - 57.3°/(L/D)
```

Or in radians:
```
γ_symmetry ≈ arcsin(α/2) - 1/(L/D)
```

Where:
- **γ_symmetry** = pitch angle where 50% throttle maintains airspeed V
- **α** = T/W = thrust-to-weight ratio
- **L/D** = lift-to-drag ratio

**Practical range:** L/D typically 8-11 for RC aircraft

### Physical Meaning - Constant Airspeed Symmetry

**This is the angle at which 50% throttle maintains some airspeed V, and it's exactly halfway between:**
- **γ_high:** The steeper angle where 100% throttle maintains the same airspeed V
- **γ_low:** The shallower/descent angle where 0% throttle maintains the same airspeed V

**Mathematically:**
```
γ_symmetry = (γ_high + γ_low) / 2
```

**For maintaining constant airspeed V:**
- At angle γ_symmetry: need 50% throttle
- At angle γ_symmetry + Δγ: need 50% + ΔT throttle
- At angle γ_symmetry - Δγ: need 50% - ΔT throttle (same magnitude change)

**Perfect symmetry:** Equal angle changes above and below γ_symmetry require equal throttle changes to maintain the same airspeed.

### Relationship to nav_fw_pitch2thr

**nav_fw_pitch2thr defines the WIDTH of the pitch range we're using, not the center:**

```
pitch_range_width = throttle_range / nav_fw_pitch2thr
                  = 1000 μs / nav_fw_pitch2thr
```

**Examples:**
- nav_fw_pitch2thr = 25 μs/° → **40° width** (±20° range)
- nav_fw_pitch2thr = 50 μs/° → **20° width** (±10° range)
- nav_fw_pitch2thr = 10 μs/° → **100° width** (±50° range)

**The center** (where you operate at cruise throttle) is determined by the aircraft's T/W and L/D via the symmetry point formula above.

**This is the core principle:** nav_fw_pitch2thr defines how wide a pitch range we cover with the available throttle, not where that range is centered in the flight envelope.

**Components:**
- **arcsin(α/2)** = gravity-only symmetry point (ignoring lift)
- **-57.3°/(L/D)** = correction due to lift helping support weight

**Key insight:** Higher L/D → more efficient lift → less thrust needed → symmetry point shifts down (closer to level flight)

### Derivation

**Force balance for steady flight at angle γ:**
```
T = W [cos(γ)/(L/D) + sin(γ)]
```

At the symmetry point, thrust is at midpoint:
```
T = αW/2

Therefore:
α/2 = cos(γ)/(L/D) + sin(γ)
```

For large L/D, the cos(γ)/(L/D) term is small compared to sin(γ), giving:
```
sin(γ_symmetry) ≈ α/2 - cos(γ)/(L/D)
```

Using small angle approximation for the correction term:
```
γ_symmetry ≈ arcsin(α/2) - 1/(L/D) radians
           ≈ arcsin(α/2) - 57.3°/(L/D)
```

### Verification Examples

**Example 1: 1:1 T/W, L/D = 10**
```
γ_symmetry ≈ arcsin(0.5) - 57.3°/10
           ≈ 30° - 5.7°
           ≈ 24°
```

Checking the exact force balance at 24°:
```
T = W[cos(24°)/10 + sin(24°)]
  = W[0.0914 + 0.4067]
  = 0.498W ≈ 0.5W ✓
```

**Example 2: 2:1 T/W, L/D = 10**
```
γ_symmetry ≈ arcsin(1.0) - 57.3°/10
           ≈ 90° - 5.7°
           ≈ 84°
```

In practice, 2:1 T/W aircraft operate well below 84° in normal flight, so the symmetry is effectively centered around level flight (0°) for the realistic ±20° envelope.

### Comparison Table

| T/W (α) | Gravity Only<br>(L/D = ∞) | L/D = 11 | L/D = 10 | L/D = 9 | L/D = 8 |
|---------|---------------------------|----------|----------|---------|---------|
| 1:1 | 30.0° | 24.8° | 24.3° | 23.6° | 22.8° |
| 1.5:1 | 48.6° | 43.4° | 42.9° | 42.2° | 41.4° |
| 2:1 | 90.0° | 84.8° | 84.3° | 83.6° | 82.8° |

**Key observation:** For typical RC aircraft (L/D = 8-11), the L/D correction shifts symmetry down by approximately **5-7 degrees** from the gravity-only prediction.

### Implications for nav_fw_pitch2thr

**For 1:1 T/W with L/D = 10:**
- Symmetry at ~24° (not 30° gravity-only, not 0° level)
- Default setting (10 μs/°) assumes symmetry around 50° (1000 μs / 20° on each side)
- This explains why default under-compensates: it's centered too high!

**Recommended setting (25 μs/°):**
- Assumes symmetry around 20° (1000 μs / 40° range = ±20°)
- Better matches actual 1:1 T/W with L/D = 10 symmetry point (24°)
- Provides good coverage for realistic flight envelope

### Assumptions

1. **Steady-state flight** (constant airspeed, no acceleration)
2. **L/D ≥ 8** for the approximation to be accurate
3. **Small angles** (γ < 60°) where lift ≈ W cos(γ)
4. **Constant L/D** (no variation with angle or airspeed)

### Limitations

- Approximation breaks down for L/D < 8 or γ > 60°
- Assumes steady-state maintainable flight at the symmetry angle
- Does not account for propeller efficiency variations
- Exact formula requires solving transcendental equation numerically

---

## Operational Envelope Width

**How wide is the pitch range that can maintain the same airspeed?**

### Formula

```
Width = γ_max - γ_min = 2 × arcsin(α/2)
```

**This width is completely independent of L/D!** It depends only on T/W ratio (α).

Where:
- **Width** = total pitch range that can maintain airspeed V
- **γ_max** = maximum angle (100% throttle maintains V)
- **γ_min** = minimum angle (0% throttle maintains V)
- **α** = T/W = thrust-to-weight ratio

### Derivation

The symmetry point is:
```
γ_symmetry = arcsin(α/2) - 57.3°/(L/D)
```

The envelope is symmetric about this point, and the minimum angle (0% throttle) occurs at:
```
γ_min ≈ -57.3°/(L/D)
```

Since the envelope is symmetric:
```
γ_max = 2 × γ_symmetry - γ_min
      = 2[arcsin(α/2) - 57.3°/(L/D)] - (-57.3°/(L/D))
      = 2 × arcsin(α/2) - 2 × 57.3°/(L/D) + 57.3°/(L/D)
      = 2 × arcsin(α/2) - 57.3°/(L/D)

Width = γ_max - γ_min
      = [2 × arcsin(α/2) - 57.3°/(L/D)] - [-57.3°/(L/D)]
      = 2 × arcsin(α/2)
```

**The L/D terms cancel perfectly!**

### Width Values

| T/W Ratio (α) | Envelope Width |
|---------------|----------------|
| 0.75:1 | 44° |
| 1:1 | 60° |
| 1.5:1 | 97° |
| 2:1 | 180° |

### Physical Interpretation

**For 1:1 T/W, any L/D:**
- Width: 60° (±30° from symmetry point)
- L/D only shifts where this 60° envelope is centered
- The width itself is constant regardless of L/D

**Key insight:**
- **T/W determines the width** (how broad the operational envelope is)
- **L/D shifts the center** (where the envelope is located)
- Higher T/W → wider envelope → can maintain given airspeed over larger pitch range

### Profound Conclusion

**The pitch-throttle relationship for maintaining constant airspeed is fundamentally driven by T/W, not L/D:**

1. **Width (envelope size):** Depends only on T/W, completely independent of L/D
2. **Center (symmetry point):** Shifts by only ~2° across L/D 8-11, but shifts ~60° across T/W 1:1→2:1

**The relationship between pitch and throttle isn't affected much by L/D. It's driven by T/W.**

---

## Power Required vs Flight Path Angle

**Power needed to maintain constant airspeed at different pitch angles**

### Formula

For climb at angle γ:
```
P_climb = P_level × (1 + sin(γ) × L/D)
```

For descent at angle γ:
```
P_descent = P_level × (1 - sin(γ) × L/D)
```

Where:
- **P** = power required to maintain constant airspeed
- **γ** = flight path angle (positive for climb, positive for descent)
- **L/D** = lift-to-drag ratio
- **P_level** = power required for level flight at same airspeed

### Special Cases

**Glide (zero power):**
```
γ_glide = arcsin(1/[L/D])
```

For L/D = 10: γ_glide = 5.74°

**Maximum climb angle (at max power):**
```
sin(γ_max) = (P_max - P_level)/(W × V)
```

### Small Angle Approximation

For γ < 15°:
```
sin(γ) ≈ γ (in radians) = γ_deg × π/180 ≈ γ_deg × 0.01745
```

Error < 1.2% for angles up to 15°

---

## INAV nav_fw_pitch2thr Theoretical Optimum

**Relating aerodynamic theory to INAV implementation**

### Theoretical Formula

From power relationship:
```
nav_fw_pitch2thr ≈ throttle_cruise × 0.01745 × L/D
```

**Example (L/D = 10, cruise = 1500 μs):**
```
nav_fw_pitch2thr ≈ 1500 × 0.01745 × 10 = 262 μs/°
```

**Problem:** Saturates throttle at only 2° pitch!

### Gravity-Only Formula

For vertical flight (90° pitch):
```
nav_fw_pitch2thr = throttle_range / 90°
                 = 1000 μs / 90°
                 ≈ 11.1 μs/°
```

Valid for 1:1 T/W aircraft at vertical angles.

### Practical Compromise

For symmetric ±θ coverage:
```
nav_fw_pitch2thr = throttle_range / (2θ)
```

**Examples:**
- ±10° coverage: 1000 / 20 = 50 μs/°
- ±20° coverage: 1000 / 40 = 25 μs/° (recommended default)
- ±25° coverage: 1000 / 50 = 20 μs/°

---

## Standard Aerodynamic Symbols

**Common notation used throughout these formulas**

| Symbol | Meaning | Units |
|--------|---------|-------|
| **W** | Weight (force) | N or lbf |
| **m** | Mass | kg or slugs |
| **g** | Gravitational acceleration | 9.81 m/s² |
| **T** | Thrust | N or lbf |
| **D** | Drag | N or lbf |
| **L** | Lift | N or lbf |
| **V** | Airspeed (velocity) | m/s or ft/s |
| **P** | Power | W (watts) or hp |
| **γ** | Flight path angle | degrees or radians |
| **α** | Thrust-to-weight ratio | dimensionless (T/W) |
| **ρ** | Air density | kg/m³ |
| **S** | Wing planform area | m² |
| **C_D** | Drag coefficient | dimensionless |
| **C_L** | Lift coefficient | dimensionless |
| **L/D** | Lift-to-drag ratio | dimensionless |

---

## References

**Derived from:**
- Houghton & Carpenter, *Aerodynamics for Engineering Students*, 5th Ed.
- INAV source code analysis
- First principles force/power balance

**Related documentation:**
- `gravity-thrust-vertical-flight.md` - Vertical flight analysis
- `power-flight-path-angle.md` - Power vs angle derivations
- `inav-pitch2thr-analysis.md` - Complete INAV implementation analysis

---

*Created: 2026-01-19*
*Purpose: Quick reference for key derived formulas*
*Status: Living document - will be expanded as we derive more relationships*
