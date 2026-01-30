# Gravity vs Thrust in Vertical Flight

**Simple Analysis for 90° Pitch (Vertical Flight Only)**

---

## Overview

At **90° pitch angles** (straight up or straight down), aircraft fly vertically. In this regime:
- **Gravity dominates** - Weight acts directly along the flight path
- **Drag is constant** - Same airspeed → same parasitic drag regardless of pitch
- **Pure force balance** - Only thrust and weight matter (drag cancels out when comparing cases)

**Key insight for nav_fw_pitch2thr:** Since this setting is about **maintaining the same airspeed** at different pitch angles, we only consider steady-state cases where constant velocity is achievable.

This provides an intuitive foundation for understanding pitch-to-throttle relationships before considering aerodynamic effects (L/D ratio).

---

## Force Balance (Vertical Flight)

**Along the flight path:**
```
Net force = Thrust ± Weight
```

- **90° climb (nose up):** Net = T - W (gravity opposes thrust)
- **90° descent (nose down):** Net = T + W (gravity assists thrust)

**Key insight:** At the same airspeed, drag is identical for climb and descent, so it cancels out when comparing the two cases.

---

## Example 1: Aircraft with 1:1 Thrust-to-Weight Ratio

**Given:**
- Maximum thrust: T_max = W
- Throttle range: 1000-2000 μs (1000 μs span)

### 90° Climb at 100% Throttle

**Steady-state force balance:**
```
T = W + D
W = W + D
D = 0
```

**Result:** At 100% throttle, aircraft can only hover (zero airspeed, zero drag).

**Limitation:** Cannot maintain any positive airspeed in vertical climb because T_max = W, and any airspeed would require T > W + D.

### 90° Descent at 0% Throttle

**Steady-state force balance:**
```
T = W - D
0 = W - D
D = W
```

**Result:** Aircraft descends at whatever airspeed produces drag equal to weight.

For that airspeed V_descent:
```
½ρV_descent²S·C_D = W
```

### Throttle Compensation

**Symmetric range:**
- From level (0°) to +90° climb: need +100% throttle (1000 μs increase)
- From level (0°) to -90° descent: need -100% throttle (1000 μs decrease)
- Total pitch range: 180° (-90° to +90°)
- Total throttle range: 1000 μs

**Therefore:**
```
nav_fw_pitch2thr = 1000 μs / 90° ≈ 11.1 μs/°
```

**This is the origin of INAV's default value of 10 μs/°!**

---

## Example 2: Aircraft with 2:1 Thrust-to-Weight Ratio

**Given:**
- Maximum thrust: T_max = 2W
- Throttle range: 1000-2000 μs (1000 μs span)

### 90° Climb at 100% Throttle - Steady State

**For constant airspeed V (no acceleration):**
```
T = W + D
2W = W + D
D = W
```

**This determines the climb airspeed:**
```
½ρV_climb²S·C_D = W
```

### 90° Descent at 0% Throttle - Steady State

**For constant airspeed V (no acceleration):**
```
T = W - D
0 = W - D
D = W
```

**This determines the descent airspeed:**
```
½ρV_descent²S·C_D = W
```

### Key Observation

**Both cases have the same drag: D = W**

Since drag depends only on airspeed:
```
½ρV_climb²S·C_D = W = ½ρV_descent²S·C_D
```

Therefore: **V_climb = V_descent**

**Symmetric velocities!**
- **+90° climb at 100% throttle** → airspeed V
- **-90° descent at 0% throttle** → same airspeed V
- The system is perfectly symmetric about level flight
- Throttle perfectly compensates for gravity over the full ±90° range

**For 2:1 T/W where steady-state is achievable:**
```
nav_fw_pitch2thr = 1000 μs / 180° ≈ 5.6 μs/°
```

Or from cruise perspective:
```
Available range from cruise: ±500 μs
Pitch coverage: ±90°
nav_fw_pitch2thr = 500 μs / 90° ≈ 5.6 μs/°
```

**Important limitation:** This only applies when the aircraft can maintain steady-state flight at both extremes.

---

## General Formula (Any T/W Ratio)

**For symmetric ±90° vertical coverage:**
```
nav_fw_pitch2thr = throttle_range / 180°
                 = 1000 μs / 180°
                 ≈ 5.6 μs/°
```

**Or from maximum climb perspective (level to +90°):**
```
nav_fw_pitch2thr = throttle_range / 90°
                 = 1000 μs / 90°
                 ≈ 11.1 μs/°
```

**Relationship to T/W ratio:**
- **1:1 T/W** → 11.1 μs/° (matches INAV default of 10!)
- **2:1 T/W** → 5.6 μs/° (half as much)
- **Higher T/W** → *lower* gain needed

This counterintuitive result (higher power needs lower gain) occurs because:
- Higher T/W allows greater acceleration at full throttle
- The throttle range (1000 μs) is the same regardless of T/W
- You're spreading the same throttle range over more available thrust

---

## Why Drag Cancels Out

**Key principle: We maintain the same airspeed in both cases.**

### Drag is Independent of Pitch

At a given airspeed V:
- Parasitic drag: D = ½ρV²S·C_D
- **Drag depends only on airspeed, not pitch angle, climb, or descent**
- Same airspeed → same drag force

This is the parasitic drag at that airspeed, regardless of whether the aircraft is:
- Climbing vertically at 90°
- Descending vertically at -90°
- Flying level at 0°
- At any other pitch angle

**Drag is constant across all pitch angles when airspeed is constant.**

### Force Balance Comparison

**90° climb at steady velocity V:**
```
Forces along path: T - W - D = 0
Therefore: T = W + D
```

**90° descent at steady velocity V (same airspeed, same drag):**
```
Forces along path: W - T - D = 0
Therefore: T = W - D
```

**When comparing climb to descent:**
```
Climb:   T_climb = W + D
Descent: T_descent = W - D

Difference: T_climb - T_descent = 2W
```

The drag term (D) appears in both equations and cancels out when we compare them. **Only the thrust vs weight relationship matters** for determining the throttle difference needed.

**Important:** This analysis makes **no assumptions about level flight**. We're only comparing 90° climb to 90° descent at the same airspeed.

---

## Steady-State Maintainability Limits

**For nav_fw_pitch2thr to apply, we need maintainable constant airspeed.**

### Minimum T/W for Vertical Climb

To maintain steady vertical climb at any positive airspeed:
```
T_max > W + D

Since D > 0 for any V > 0:
T/W > 1.0 (strictly)
```

**T/W = 1.0 exactly:** Can only hover (V = 0)
**T/W < 1.0:** Cannot maintain vertical climb at all

### Maximum Maintainable Airspeed

For a given T/W ratio α, the maximum vertical climb airspeed occurs at 100% throttle:
```
T_max = W + D
αW = W + D
D = W(α - 1)
```

From the derived velocity ratio formula:
```
V_climb_max = V_descent × √(α - 1)
```

Where V_descent is determined by D = W at 0% throttle.

**Key insight:** As T/W approaches 1.0, the maximum maintainable vertical climb airspeed approaches zero (hover).

---

## Comparison Table: T/W vs Vertical Flight Capability

| T/W Ratio | Steady Vertical Climb? | V_climb/V_descent | Gravity-Only Setting | INAV Default |
|-----------|------------------------|-------------------|---------------------|--------------|
| 0.5:1 | ❌ No (insufficient thrust) | undefined | Not applicable | 10 μs/° |
| 1:1 | ⚠️ Hover only (V=0) | 0 | **11.1 μs/°** | **10 μs/°** ✓ |
| 1.5:1 | ✅ Yes | 0.707 | 7.4 μs/° | 10 μs/° |
| 2:1 | ✅ Yes (symmetric) | 1.0 | 5.6 μs/° | 10 μs/° |
| 3:1 | ✅ Yes | 1.414 | 3.7 μs/° | 10 μs/° |

**Key finding:**
- The default value (10 μs/°) matches 1:1 T/W where vertical climb is barely maintainable (hover only)
- For aircraft that can actually maintain airspeed in vertical flight (T/W > 1), the setting is too conservative

---

## Physical Interpretation

**Energy perspective:**

At constant vertical speed:
- **Climb:** Kinetic energy constant (V unchanged), potential energy increasing
- **Descent:** Kinetic energy constant (V unchanged), potential energy decreasing

**Power required:**
```
P = Force × Velocity
```

**90° climb:**
```
P_climb = (T - W) × V_vertical
```

**90° descent:**
```
P_descent = (W - T) × V_vertical
```

If both maintain the same vertical speed: T - W in climb equals W - T in descent.

**Symmetric throttle compensation follows directly from force balance.**

---

## Aircraft Weight Symbol

**Standard notation (from aerodynamics textbooks):**

- **W** = Weight (force due to gravity)
  - Units: Newtons (N) or pounds-force (lbf)
- **m** = Mass
  - Units: kilograms (kg) or slugs
- **g** = Gravitational acceleration
  - Standard value: 9.81 m/s² or 32.2 ft/s²

**Relationship:** W = m × g

In aerodynamics and flight dynamics, we use **W** (weight) because we're working with forces. The force balance equations naturally use weight, not mass.

---

## Scope and Limitations

### What This Analysis Covers

This analysis is **strictly limited to steady-state vertical flight:**

1. **Vertical flight only** - 90° pitch angles (up or down)
2. **Constant airspeed** - No acceleration (nav_fw_pitch2thr is about maintaining airspeed)
3. **Maintainable flight** - Only considers cases where T/W allows steady-state
4. **Parasitic drag only** - Drag depends only on airspeed: D = ½ρV²S·C_D

**Key principles:**
- Same airspeed → same parasitic drag (regardless of pitch, climb, or descent)
- Drag cancels out when comparing vertical climb to vertical descent
- Only thrust vs weight relationship matters

### What This Analysis Doesn't Cover

**This analysis makes NO assumptions about level flight or intermediate angles.**

**Limitations:**

- Most GPS-assisted flight occurs at **±20° or less** (not ±90°)
- At non-vertical angles, the relationship is different (L/D ratio matters)
- The simple 90° analysis gives us 11 μs/°, but this **under-compensates by ~2.5×** for realistic flight angles
- Requires T/W ≥ 1 for meaningful vertical climb analysis

**Hint about intermediate angles:**
- 0° (level) is exactly halfway between -90° and +90°
- For 2:1 T/W, this suggests ~50% throttle as a starting point
- But actual level flight throttle depends on drag (the L/D ratio)
- Analysis of intermediate angles covered in `inav-pitch2thr-analysis.md`

---

## Practical Implications

**What this analysis explains:**
- ✅ Origin of the 10 μs/° default (gravity-only for 1:1 T/W)
- ✅ Why higher T/W needs lower gain (counterintuitive but correct)
- ✅ Symmetric throttle compensation for vertical flight

**What this analysis doesn't explain:**
- ❌ Airspeed stability in climbs/descents at realistic angles (<30°)
- ❌ Why 10 μs/° causes airspeed bleed in climbs
- ❌ How L/D ratio affects required throttle changes

**For realistic flight:** See the full aerodynamic analysis in `inav-pitch2thr-analysis.md` which accounts for drag and recommends **25 μs/°** as the universal default.

---

## Summary

**Gravity-only (vertical flight):**
```
nav_fw_pitch2thr = 1000 μs / 90° ≈ 11 μs/° (for 1:1 T/W)
```

**This is intuitive and explains the current default,** but it only applies to vertical flight where drag is negligible.

**For GPS-assisted flight at realistic angles,** drag effects (L/D ratio) dominate and require higher values (25-50 μs/°) to maintain constant airspeed.

**The gravity-only approach is pedagogically useful** for understanding the physics, but shouldn't drive the default value for practical flight operations.

---

## References

**Related Documentation:**
- `inav-pitch2thr-analysis.md` - Complete analysis including L/D effects
- `nav_fw_pitch2thr-tuning-guide.md` - User-focused tuning guide
- `power-flight-path-angle.md` - Power required vs flight path angle

**Aerodynamic Theory:**
- Houghton & Carpenter, *Aerodynamics for Engineering Students*, 5th Ed.
  - Pages 26-34: Force equilibrium in steady flight
  - Pages 62-67: Climb and descent performance

---

*Created: 2026-01-19*
*Purpose: Intuitive gravity-thrust analysis for vertical flight (90° pitch only)*
*Scope: Simplified analysis ignoring drag - see full analysis for realistic flight*
