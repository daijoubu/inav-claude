# INAV nav_fw_pitch2thr Tuning Guide

**Quick Reference for Users**

---

## What Does This Setting Do?

**nav_fw_pitch2thr** adjusts throttle to maintain constant airspeed when pitch angle changes.

**Units:** PWM microseconds per degree (μs/°)

**Example:**
- Aircraft pitches to 10° climb (altitude controller wants to gain altitude)
- To maintain the same airspeed during the climb, we need more power
- With `nav_fw_pitch2thr = 25`: throttle increases by 10° × 25 = 250 μs

**Why this matters:**
- Too low → airspeed bleeds off during climbs, builds up during descents
- Correct → airspeed stays constant through altitude changes
- Too high → over-compensates, airspeed increases in climbs

**Not about:** Control speed or responsiveness (altitude controller handles that separately)

**Is about:** Maintaining your target airspeed while climbing or descending

---

## Current Default Problem

**Default value: 10 μs/°**

**What this means:**
- 10° climb: adds only 100 μs throttle
- 20° climb: adds only 200 μs throttle
- Reaches max throttle only at 50° pitch (unrealistic)

**Problem:** Severe under-compensation leads to:
- Airspeed loss during climbs (not enough throttle added)
- Airspeed gain during descents (not enough throttle reduced)
- Poor altitude hold performance (speed variations affect altitude)
- RTH altitude changes cause speed fluctuations

**Theoretical requirement for 10° climb (L/D = 10):**
- Need ~173% more power to maintain airspeed
- Default only adds ~20% throttle
- Result: airspeed drops significantly

---

## Recommended Values

### Universal Default: 25 μs/°

**Calculation:** 1000 μs throttle range ÷ 40° pitch span (±20°) = 25 μs/°

**Benefits:**
- 10° climb: +250 μs (maintains airspeed better)
- 20° climb: +500 μs (reaches max throttle)
- Good airspeed stability for most aircraft
- 2.5× improvement over current default
- Conservative enough for all aircraft types

**Best for:** All aircraft, especially P/W ratio 0.5:1 to 2:1

### Alternative: 35 μs/°

**Calculation:** 1000 μs range ÷ 28° span (±14°) = ~35 μs/°

**Benefits:**
- Better airspeed compensation
- 10° climb: +350 μs (good compensation)
- 14° climb: +490 μs (near max throttle)

**Best for:** Sport aircraft with P/W > 1.5:1

### Aggressive: 50 μs/°

**Calculation:** 500 μs range ÷ 10° span = 50 μs/°

**Benefits:**
- Best airspeed stability for typical aircraft
- 10° climb: +500 μs (reaches max throttle)

**Risk:** May saturate throttle early on climbs

**Best for:** High P/W aircraft (>1:1) with good L/D (8-12)

---

## Quick Selection Guide

**Choose based on your aircraft type:**

| Aircraft Type | P/W Ratio | L/D | Recommended Setting |
|---------------|-----------|-----|---------------------|
| Glider / Sailplane | 0.3-0.6:1 | 20-60 | 15-25 μs/° |
| Trainer / Cruiser | 0.8-1.2:1 | 10-15 | 25-35 μs/° |
| Sport / FPV Wing | 1.2-1.8:1 | 8-12 | 30-40 μs/° |
| Aerobatic / 3D | 2:1+ | 4-8 | 20-30 μs/° |

**General rule:** Start with 25 μs/° for any aircraft, then adjust based on flight testing.

---

## Flight Testing & Tuning Procedure

### Step 1: Baseline Test (Current Setting)

1. Fly in Position Hold or Loiter mode (GPS stabilized)
2. Note current nav_fw_pitch2thr value
3. Command altitude change: +50m climb
4. **Observe airspeed during climb:**
   - Does it decrease significantly? → Setting too low
   - Does it stay constant? → Setting correct
   - Does it increase? → Setting too high
5. Repeat for descent: -50m
6. **Observe airspeed during descent:**
   - Does it increase significantly? → Setting too low
   - Does it stay constant? → Setting correct
   - Does it decrease? → Setting too high

### Step 2: Adjust Value

**If airspeed decreases in climbs:**
- Current setting under-compensates
- Increase nav_fw_pitch2thr by 10-15 μs/°
- Example: 10 → 25, or 25 → 35

**If airspeed increases in climbs:**
- Current setting over-compensates (rare!)
- Decrease nav_fw_pitch2thr by 5-10 μs/°

**If airspeed increases in descents:**
- Current setting under-compensates (not reducing throttle enough)
- Increase nav_fw_pitch2thr by 10-15 μs/°

### Step 3: Verify

1. Set new value
2. Repeat climb/descent tests
3. Check airspeed stability
4. Iterate until airspeed remains constant through altitude changes

### Step 4: Edge Case Testing

1. Steeper climb test (+30° pitch if safe)
   - Should hit max throttle at realistic angles
   - If not, setting might be too conservative
2. Descent test (-15° pitch)
   - Should reduce throttle significantly
   - If airspeed builds up, increase setting

---

## Signs of Incorrect Tuning

### Too Low (Current Default Problem)

**Symptoms:**
- Airspeed drops 2-5 m/s during climbs
- Airspeed increases 2-5 m/s during descents
- Altitude overshoots (controller pitches steeper to compensate for slow climb)
- RTH altitude changes cause speed variations
- May trigger low-speed alarms during climbs

**Fix:** Increase by 10-15 μs/°

### Too High (Rare)

**Symptoms:**
- Airspeed increases during climbs
- Airspeed decreases during descents
- Throttle hits max/min at gentle pitch angles (<5°)
- Altitude hunting (over-compensation)

**Fix:** Decrease by 5-10 μs/°

### Correct

**Symptoms:**
- Airspeed remains within ±1 m/s during altitude changes
- Smooth altitude transitions
- No speed alarms during climbs
- Predictable behavior in Position Hold/RTH

---

## Theoretical Background (Optional)

### The Physics

**Power required at climb angle γ:**
```
P_climb = P_level × (1 + sin(γ) × L/D)
```

**For typical RC aircraft (L/D = 10):**
- 10° climb: need 274% of level flight power
- 15° climb: need 359% of level flight power

**Current default (10 μs/°) only adds:**
- 10° climb: ~20% throttle increase
- Result: massive under-compensation

**With 25 μs/° setting:**
- 10° climb: ~50% throttle increase
- Better compensation (though still conservative)

### Why Not Match Theory Exactly?

**Theoretical optimal (L/D = 10, cruise = 1500 μs):**
```
nav_fw_pitch2thr ≈ 250 μs/°
```

**Problem:** Saturates throttle at only 2° pitch!

**Practical compromise:**
- Throttle range is limited (1000-2000 μs, only 1000 μs span)
- Physical limits prevent matching theory exactly
- 25-50 μs/° provides best balance of:
  - Airspeed stability
  - Avoiding constant saturation
  - Usable pitch range

---

## Advanced: Calculate Your Optimal Value

### Method 1: Symmetric Range Coverage

**Determine realistic pitch range:**
- Conservative: ±15° → setting = 1000 / 30 = 33 μs/°
- Moderate: ±20° → setting = 1000 / 40 = 25 μs/°
- Aggressive: ±10° → setting = 1000 / 20 = 50 μs/°

### Method 2: Based on Max Climb Angle

**Measure/estimate maximum sustained climb angle:**
1. Fly at cruise throttle (typically 40-50% motor power)
2. Pitch up until climb rate stabilizes
3. Note pitch angle (let's say 12°)

**Calculate:**
```
nav_fw_pitch2thr = (max_throttle - cruise_throttle) / max_climb_angle
                 = (2000 - 1500) / 12
                 = 42 μs/°
```

This ensures you reach max throttle at your aircraft's physical limit.

### Method 3: From Glide Test

**Measure L/D ratio:**
1. Throttle to idle
2. Trim for best glide
3. Measure descent rate and ground speed
4. Glide ratio = ground_speed / descent_rate
5. L/D ≈ glide ratio

**Theoretical optimal:**
```
nav_fw_pitch2thr = cruise_throttle × 0.01745 × L/D
```

**Example (L/D = 10, cruise = 1500 μs):**
```
nav_fw_pitch2thr = 1500 × 0.01745 × 10 = 262 μs/°
```

**Then reduce by 50-80% for practical use:**
```
Practical = 262 × 0.2 = 52 μs/°
```

---

## Comparison to Current Default

| Metric | Default (10) | Recommended (25) | Improvement |
|--------|--------------|------------------|-------------|
| 10° climb throttle increase | 100 μs | 250 μs | 2.5× |
| 20° climb throttle increase | 200 μs | 500 μs | 2.5× |
| Airspeed stability in climbs | Poor | Good | Much better |
| Airspeed stability in descents | Poor | Good | Much better |
| Altitude hold performance | Struggles | Stable | Better |
| RTH altitude changes | Speed varies | Speed stable | Smoother |

---

## Common Questions

### Q: Won't higher values cause throttle to saturate?

**A:** Yes, at steep angles - but that's intentional!
- With 25 μs/°, saturates at ±20° (very steep, rarely used)
- With 50 μs/°, saturates at ±10° (moderate, but better airspeed compensation)
- Saturation prevents over-compensation at extreme angles
- The clamping is a feature, not a bug

### Q: My aircraft has high P/W (2:1), do I need a different value?

**A:** You still want correct airspeed compensation!
- High P/W means you CAN achieve steeper climbs
- But you still need correct throttle to maintain airspeed during those climbs
- Start with 25 μs/°, may need to reduce slightly to 20-30 to avoid early saturation
- The physics of airspeed vs. pitch still apply regardless of available power

### Q: Why is the current default so low?

**A:** Historical conservatism and sailplane bias
- Default (10 μs/°) implies L/D = 0.38 (nonsensical)
- Only makes sense for high-performance sailplanes (L/D > 30)
- Prioritizes stability over accuracy
- Never updated as INAV expanded to more aircraft types

### Q: Will changing this affect my manual flying?

**A:** No - only affects GPS-assisted modes
- nav_fw_pitch2thr only active in Position Hold, RTH, Waypoint, etc.
- Manual/Acro/Angle modes unaffected
- You can test in Position Hold without affecting manual flight

### Q: Can I tune this empirically without knowing L/D or P/W?

**A:** Yes! Use the flight test procedure above
1. Start with 25 μs/°
2. Do climb/descent tests in Position Hold
3. Watch airspeed behavior
4. Adjust until airspeed stays constant
5. No calculations needed

---

## Summary

**Current default (10 μs/°):**
- Severely under-compensates
- Causes airspeed loss in climbs, gain in descents
- Degrades altitude hold performance

**Recommended universal default (25 μs/°):**
- 2.5× improvement
- Better airspeed stability
- Works for all aircraft types
- Still conservative enough for safety

**Next steps:**
1. Change nav_fw_pitch2thr from 10 to 25
2. Test in Position Hold mode
3. Observe airspeed during climbs/descents
4. Adjust ±10 μs/° based on results

---

**Related Documentation:**
- `inav-pitch2thr-analysis.md` - Complete theoretical analysis
- `power-flight-path-angle.md` - Aerodynamic derivations
- INAV settings.yaml line 1162 - Setting definition

**Created:** 2026-01-18
**Purpose:** Practical tuning guide for nav_fw_pitch2thr setting
**Recommendation:** Change default from 10 μs/° to 25 μs/° for better airspeed stability
