# IDEAL PITCH-TO-THROTTLE COMPENSATION SYSTEM

**Local Derivative Approach: Throttle Change for Small Pitch Changes**

---

## Executive Summary

The INAV `nav_fw_pitch2thr` setting controls how much throttle changes when pitch changes to maintain constant airspeed. This is a **local calculation** - a derivative, not a global envelope mapping.

**Key Finding:** The optimal gain is **inversely proportional to T/W ratio**:

```
nav_fw_pitch2thr ≈ 17.5 / (T/W ratio) μs/°
```

**Critical Insight:** Higher T/W aircraft need **LOWER** gain values.

**Current Problem:** The default value of 10 μs/° is optimized for high-performance aircraft (T/W ≈ 1.75:1), which explains why it severely under-compensates for typical aircraft (T/W ≈ 1:1).

---

## The Physics: Local Derivative Approach

### What nav_fw_pitch2thr Actually Does

**NOT:** "Map the full pitch envelope to throttle range"
**YES:** "Calculate how much throttle to change for a small pitch change to maintain airspeed"

This is fundamentally a **derivative calculation**:

```
throttle_change = pitch_change × nav_fw_pitch2thr
```

For small pitch changes (within ±20°), this linear approximation works well.

### Force Balance for Constant Airspeed

To maintain constant airspeed at pitch angle γ:

```
T = W[cos(γ)/(L/D) + sin(γ)]
```

Where:
- **T** = thrust required
- **W** = weight
- **γ** = pitch angle (flight path angle)
- **L/D** = lift-to-drag ratio

### The Local Derivative

Taking the derivative with respect to pitch angle:

```
dT/dγ = W[-sin(γ)/(L/D) + cos(γ)]
```

Converting to degrees (instead of radians):

```
dT/dγ_deg = W[-sin(γ)/(L/D) + cos(γ)] / 57.3
```

At level flight (γ = 0°):

```
dT/dγ_deg = W × 1.0 / 57.3 = W / 57.3 per degree
```

### Converting to Throttle Percentage

The throttle change needed is:

```
d(throttle_fraction)/dγ_deg = (dT/dγ_deg) / T_max
                               = (W / 57.3) / (α × W)
                               = 1 / (57.3 × α)
```

Where **α = T/W ratio** (thrust-to-weight at full throttle).

### Converting to Microseconds

INAV uses 1000-2000 μs for throttle (1000 μs range):

```
nav_fw_pitch2thr = 1000 μs / (57.3 × α)
                 ≈ 17.5 / α μs/°
```

---

## Optimal Gain by T/W Ratio

### Calculated Values (at level flight, L/D = 10)

| T/W Ratio (α) | Optimal Gain (μs/°) | Aircraft Type |
|---------------|---------------------|---------------|
| **0.5:1** | 35.0 | Glider, very efficient |
| **0.75:1** | 23.3 | Motorglider, long endurance |
| **1:1** | 17.5 | **Typical RC aircraft** |
| **1.5:1** | 11.7 | Sport aircraft |
| **1.75:1** | 10.0 | **Current INAV default** |
| **2:1** | 8.75 | High-performance sport |

### Key Observations

1. **The current default (10 μs/°) matches T/W ≈ 1.75:1**
   - This is a high-performance sport aircraft
   - Most RC aircraft have T/W closer to 1:1

2. **Typical aircraft (1:1 T/W) need 17.5 μs/°**
   - Current default under-compensates by ~43%
   - This explains airspeed loss in climbs and gain in descents

3. **Higher T/W → Lower gain needed**
   - Same thrust change (in Newtons) represents smaller fraction of total thrust
   - Counterintuitive but physically correct!

### Variation with Pitch Angle

The gain varies slightly with pitch angle:

| Pitch Angle | Gain for 1:1 T/W | Variation |
|-------------|------------------|-----------|
| -20° | 17.0 μs/° | -2.9% |
| -10° | 17.5 μs/° | -0.2% |
| **0°** | **17.5 μs/°** | **baseline** |
| +10° | 16.9 μs/° | -3.4% |
| +20° | 15.8 μs/° | -9.7% |

**Conclusion:** Using the level-flight value (17.5 / α) gives <10% error across ±20° pitch range.

---

## Current INAV Implementation

### Formula

```c
throttle_correction = pitch_angle_deg × nav_fw_pitch2thr
```

**Units:** μs/° (microseconds per degree)

**Default:** 10 μs/°
**Range:** 0-100 μs/°

### Why the Default is Too Low for Most Aircraft

The default assumes T/W ≈ 1.75:1 (high-performance aircraft).

**For a typical 1:1 T/W aircraft:**
- **Optimal:** 17.5 μs/°
- **Current default:** 10 μs/°
- **Under-compensation:** 43%

**Symptoms:**
- Airspeed bleeds off in climbs
- Airspeed builds up in descents
- Poor altitude hold performance
- Sluggish TECS response

---

## Proposed Improvement

### Option 1: Simple T/W-Based Auto-Tuning

Add a user-configurable T/W ratio parameter:

```c
// New parameter
float nav_fw_thrust_weight_ratio;  // default: 1.0

// Auto-calculate gain
float nav_fw_pitch2thr = 17.5f / nav_fw_thrust_weight_ratio;
```

**User settings:**
```
nav_fw_thrust_weight_ratio = 1.0   (typical aircraft)
nav_fw_thrust_weight_ratio = 0.75  (efficient/glider)
nav_fw_thrust_weight_ratio = 1.5   (sport aircraft)
nav_fw_thrust_weight_ratio = 2.0   (high performance)
```

### Option 2: Simple Preset Modes

```c
enum fw_aircraft_type {
    FW_TYPE_GLIDER = 0,      // T/W ≈ 0.5, gain = 35
    FW_TYPE_EFFICIENT = 1,   // T/W ≈ 0.75, gain = 23
    FW_TYPE_TYPICAL = 2,     // T/W ≈ 1.0, gain = 17.5 [DEFAULT]
    FW_TYPE_SPORT = 3,       // T/W ≈ 1.5, gain = 11.7
    FW_TYPE_PERFORMANCE = 4  // T/W ≈ 2.0, gain = 8.75
};
```

### Option 3: Keep Current System, Update Default

**Simplest migration:**
- Change default from 10 → 17.5 μs/°
- Benefits most users (1:1 T/W)
- High-performance users can lower it
- Backward compatible

---

## Estimating T/W Ratio

### Method 1: Maximum Climb Angle Test

Fly at full throttle in a sustained climb, measure maximum climb angle:

```
T/W = sin(γ_max) + 1/(L/D)
```

For L/D = 10 and γ_max = 30°:
```
T/W = sin(30°) + 0.1 = 0.5 + 0.1 = 0.6
```

### Method 2: Level Flight Acceleration

Measure horizontal acceleration at full throttle in level flight:

```
T/W = 1/(L/D) + (a/g)
```

For L/D = 10 and a = 5 m/s²:
```
T/W = 0.1 + 5/9.8 = 0.1 + 0.51 = 0.61
```

### Method 3: User Knowledge

Many RC pilots know their aircraft's approximate T/W from specifications or experience.

---

## Comparison Table: Current vs Optimal

### For Typical 1:1 T/W Aircraft

| Pitch Angle | Current (10 μs/°) | Optimal (17.5 μs/°) | Difference |
|-------------|-------------------|---------------------|------------|
| **-10°** (descent) | -100 μs | -175 μs | 75 μs under |
| **0°** (level) | 0 μs | 0 μs | exact |
| **10°** (climb) | +100 μs | +175 μs | 75 μs under |
| **20°** (steep climb) | +200 μs | +350 μs | 150 μs under |

**Pattern:** Current system under-compensates across the entire envelope except at level flight.

---

## Constant-Airspeed Envelopes (Visualization Only)

**Note:** For visualization purposes, we use T/W < 1.0 to show full 0-100% throttle envelopes. Aircraft with T/W > 1.0 can only use a fraction of their throttle range to maintain constant airspeed.

### 0.5:1 T/W Aircraft (Glider-Like)

At airspeed V = V_ref:
- **0% throttle:** -5.7° (glide)
- **50% throttle:** 8.6° (symmetry point)
- **100% throttle:** 23.6° (maximum climb)
- **Envelope width:** 29.3°

### 0.75:1 T/W Aircraft

At airspeed V = V_ref:
- **0% throttle:** -5.7° (glide)
- **50% throttle:** 16.0° (symmetry point)
- **100% throttle:** 40.5° (maximum climb)
- **Envelope width:** 46.3°

### Why T/W > 1.0 is Different

**Critical constraint:** At constant airspeed, maximum thrust needed is ~W (at 0% throttle glide, gravity provides "boost"). An aircraft with 2W thrust available (2:1 T/W) can only use ~50% throttle to stay within the constant-airspeed envelope.

**For nav_fw_pitch2thr:** This doesn't matter! The LOCAL gain is still:
```
nav_fw_pitch2thr = 17.5 / (T/W)
```

Even for 2:1 aircraft (which would use 8.75 μs/°).

---

## Implementation Considerations

### Backward Compatibility

**Phase 1: Optional T/W parameter**
- Add `nav_fw_thrust_weight_ratio` (default: disabled/0.0)
- If set, auto-calculate `nav_fw_pitch2thr`
- If not set, use manual `nav_fw_pitch2thr` (current behavior)

**Phase 2: Change default**
- Update default `nav_fw_pitch2thr` from 10 → 17.5 μs/°
- Helps typical aircraft immediately
- High-performance users adjust downward

**Phase 3: Auto-detection**
- Estimate T/W from flight data
- Auto-tune during first flights
- Store calibrated value

### Code Example

```c
// In navigation_fixedwing.c

float calculate_pitch2thr_gain(float thrust_weight_ratio, float lift_drag_ratio) {
    // Local derivative approach
    // At level flight: dT/dγ_deg = W / 57.3
    // Throttle per degree = (W / 57.3) / (α × W) = 1 / (57.3 × α)
    // In μs: 1000 / (57.3 × α) ≈ 17.5 / α

    if (thrust_weight_ratio > 0.1f && thrust_weight_ratio < 5.0f) {
        // Use T/W-based calculation
        return 1000.0f / (57.3f * thrust_weight_ratio);
    } else {
        // Fallback to manual setting
        return navConfig()->fw.pitch_to_throttle;
    }
}

// Usage:
float pitch2thr_gain;
if (navConfig()->fw.thrust_weight_ratio > 0.0f) {
    pitch2thr_gain = calculate_pitch2thr_gain(
        navConfig()->fw.thrust_weight_ratio,
        navConfig()->fw.lift_drag_ratio  // optional refinement
    );
} else {
    pitch2thr_gain = navConfig()->fw.pitch_to_throttle;
}

throttle_correction = pitch_angle_deg * pitch2thr_gain;
```

---

## Benefits of This Approach

### 1. Physically Correct
- Based on fundamental force balance
- Accounts for aircraft T/W ratio
- Valid for all aircraft types

### 2. Simple to Implement
- Single formula: `17.5 / (T/W)`
- No complex envelopes or multi-parameter systems
- Works for any T/W ratio

### 3. Works for All Aircraft
- **Low T/W (gliders):** Correctly uses high gain (~35 μs/°)
- **Typical aircraft:** Uses optimal gain (~17.5 μs/°)
- **High T/W (sport):** Correctly uses low gain (~8-12 μs/°)

### 4. User-Friendly
- Easy to estimate T/W (from specs or simple test)
- Preset modes for common aircraft types
- Auto-tuning possible

---

## Summary

**Current System:**
- Single parameter: `nav_fw_pitch2thr`
- Default: 10 μs/° (optimized for T/W ≈ 1.75:1)
- Under-compensates for typical aircraft

**Proposed Improvement:**
- Add T/W ratio parameter (optional)
- Auto-calculate gain: `17.5 / (T/W)` μs/°
- Or update default to 17.5 μs/° for typical aircraft

**Key Formula:**
```
nav_fw_pitch2thr = 1000 / (57.3 × T/W_ratio)
                 ≈ 17.5 / T/W_ratio μs/°
```

**Derived from:**
```
T = W[cos(γ)/(L/D) + sin(γ)]
dT/dγ = W[-sin(γ)/(L/D) + cos(γ)]
```

At level flight (γ = 0°):
```
dT/dγ = W / 57.3 per degree
d(throttle)/dγ = 1 / (57.3 × α) per degree
In μs: 1000 / (57.3 × α) ≈ 17.5 / α
```

---

## References

**Calculations:**
- `calculate-local-derivative.py` - Full derivative analysis
- `calculate-envelopes-tw-below-1.py` - Constant-airspeed envelopes for T/W < 1

**Visualizations:**
- `equal-airspeed-0.5to1-corrected.png` - 0.5:1 T/W envelope
- `equal-airspeed-0.75to1-corrected.png` - 0.75:1 T/W envelope

**Current implementation:**
- `inav/src/main/navigation/navigation_fixedwing.c` (lines 635-662)
- `inav/src/main/fc/settings.yaml` (line 1162)

**Related analysis:**
- `inav-pitch2thr-analysis.md` - Current system analysis
- `nav_fw_pitch2thr-tuning-guide.md` - User tuning guide

---

*Created: 2026-01-19*
*Purpose: Proposal for improved pitch-to-throttle compensation using local derivative approach*
*Key Finding: Optimal gain is inversely proportional to T/W ratio: nav_fw_pitch2thr ≈ 17.5 / (T/W)*
*Status: Proposal - requires implementation and testing*
