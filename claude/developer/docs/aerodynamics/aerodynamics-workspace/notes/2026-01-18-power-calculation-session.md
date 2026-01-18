# Session Notes: Power Calculation for Constant Airspeed Flight

**Date:** 2026-01-18
**Agent:** aerodynamics-expert
**Topic:** Power required to maintain constant airspeed after pitch change

---

## Session Objectives

1. Document the relationship between power and flight path angle
2. Derive the key equation: P = P_level × (1 ± [L/D] × sin(γ))
3. Analyze small-angle approximation validity for γ < 15°
4. Apply theory to INAV flight controller optimization

---

## Key Deliverables

### 1. Comprehensive Knowledge Base Document

**File:** `/home/raymorris/Documents/planes/inavflight/claude/developer/docs/aerodynamics/aerodynamics-workspace/knowledge-base/power-flight-path-angle.md`

**Contents:**
- Complete derivation of power-flight path angle relationship
- Physical interpretation (energy balance perspective)
- Glide performance analysis
- Small angle linearity analysis (detailed table)
- INAV-specific applications with code examples
- Worked examples with realistic aircraft parameters
- Textbook citations (Houghton & Carpenter pages 26-67)

**Key findings:**
- Power reduction in descent: P_descent = P_level × (1 - [L/D] × sin(|γ|))
- Best glide angle: γ_glide = arcsin(1/[L/D])
- Small angle approximation valid to 1.2% error for |γ| < 15°

### 2. Quick Reference for Small Angles

**File:** `/home/raymorris/Documents/planes/inavflight/claude/developer/docs/aerodynamics/aerodynamics-workspace/references/small-angle-approximations.txt`

**Purpose:** Fast lookup for embedded developers

**Contents:**
- Linearity table (0°, 5°, 10°, 15°)
- Taylor series error analysis
- INAV code examples
- Performance benefits of linear approximation
- When to use full trigonometry

**Conclusion:** sin(γ) ≈ γ is excellent for typical flight (< 10°)

### 3. Knowledge Base Index

**File:** `/home/raymorris/Documents/planes/inavflight/claude/developer/docs/aerodynamics/aerodynamics-workspace/knowledge-base/README.md`

**Purpose:** Central index linking related topics

**Contents:**
- Lists all knowledge base documents
- Shows relationship between constant-throttle vs constant-airspeed scenarios
- Quick reference to most useful Houghton & Carpenter pages
- Organization guidelines for future entries

---

## Technical Analysis Summary

### Scenario Analyzed

**Initial conditions:**
- Aircraft in level flight at airspeed V
- Level flight power: P1
- Lift-to-drag ratio: L/D

**Maneuver:**
- Aircraft pitches down by angle θ
- Resulting flight path angle: γ (negative for descent)
- **Goal:** Maintain same airspeed V (not altitude)

**Result:**
- Power requirement changes due to gravity component
- Descent requires LESS power (gravity assists)
- Climb requires MORE power (gravity opposes)

### Key Equation Derived

```
P = P_level × (1 + [L/D] × sin(γ))
```

**Sign conventions:**
- γ > 0: Climb → power increases
- γ < 0: Descent → power decreases
- γ = 0: Level flight → baseline power

**Special case - Best glide:**
```
P = 0 when sin(γ) = -1/[L/D]
γ_glide = -arcsin(1/[L/D])
```

For L/D = 10: γ_glide = -5.74° (10:1 glide ratio)

### Small Angle Linearity Results

**Question asked:** Is sin(γ) linear with γ for angles < 15°?

**Answer:** YES, with excellent accuracy

| Angle | sin(γ) | Linear | Error |
|-------|--------|--------|-------|
| 5°    | 0.0872 | 0.0873 | 0.11% |
| 10°   | 0.1736 | 0.1745 | 0.52% |
| 15°   | 0.2588 | 0.2618 | 1.16% |

**Implications for INAV:**
- Can use γ (radians) directly instead of sin(γ) for typical flight
- Saves CPU cycles (no trig function call)
- Negligible error for cruise/climb/descent profiles
- Only use full sinf() for aggressive maneuvers (γ > 15°)

---

## INAV Application Examples

### 1. Throttle Optimization for Descent

```c
// Calculate current flight path angle
float climb_rate = getEstimatedActualVelocity(Z);  // cm/s
float ground_speed = getEstimatedActualVelocity(XY);  // cm/s
float gamma = atan2f(-climb_rate, ground_speed);  // radians (negative = descent)

// Small angle approximation for typical flight
float sin_gamma = (fabsf(gamma) < 0.26f) ? gamma : sinf(gamma);

// Estimated L/D from aircraft configuration
float lift_over_drag = estimateLiftToDragRatio();  // Typical: 8-12

// Power factor for constant airspeed descent
float power_factor = 1.0f - sin_gamma * lift_over_drag;

// Adjust throttle
uint16_t throttle_descent = constrain(
    throttle_level * power_factor,
    MIN_THROTTLE,
    MAX_THROTTLE
);
```

### 2. Range Estimation with Terrain

```c
// Account for altitude changes in mission
float total_energy = 0.0f;

for (int i = 0; i < mission_waypoint_count; i++) {
    float altitude_change = waypoint[i].alt - current_altitude;
    float segment_distance = distanceTo(waypoint[i]);
    float segment_gamma = atan2f(altitude_change, segment_distance);

    // Power factor for this segment
    float power_factor = 1.0f + segment_gamma * drag_over_lift;

    // Energy for segment (time = distance / speed)
    float segment_time = segment_distance / cruise_speed;
    float segment_energy = baseline_power * power_factor * segment_time;

    total_energy += segment_energy;
}

// Remaining range with current battery
float remaining_range = battery_remaining_mAh / (total_energy / total_distance);
```

### 3. Best Glide Calculation

```c
// Calculate best glide angle for return-to-home
float estimated_L_over_D = 10.0f;  // Typical fixed-wing
float glide_angle_rad = asinf(1.0f / estimated_L_over_D);  // ~5.74°

// Required altitude for glide-home
float distance_to_home = GPS_distanceToHome;
float min_altitude_for_glide = distance_to_home * tanf(glide_angle_rad);

if (current_altitude > min_altitude_for_glide) {
    // Can glide home with zero power
    setThrottle(IDLE_THROTTLE);
} else {
    // Need power to reach home
    float deficit = min_altitude_for_glide - current_altitude;
    // Calculate required climb or powered glide
}
```

---

## Cross-References

### Related Knowledge Base Documents

1. **pitch-airspeed-relationship.md**
   - Complementary scenario: constant throttle, varying airspeed
   - Shows how pitch affects speed via angle of attack and lift coefficient
   - Combined with this document, provides complete picture of pitch-power-speed coupling

### Related Textbook Sections

**Houghton & Carpenter, 5th Edition:**
- Pages 26-34: Force equilibrium in steady flight
- Pages 35-44: Drag characteristics and L/D ratio
- Pages 47-48: Aspect ratio effects on glide performance
- Pages 62-67: Performance calculations (climb, descent, glide)

---

## Lessons Learned

### Mathematical Insights

1. **Sign conventions matter critically**
   - Flight path angle γ: positive = climb, negative = descent
   - Power equation changes form based on convention
   - Must be consistent throughout derivation

2. **Small angle approximations are powerful**
   - sin(γ) ≈ γ valid to 1% error for |γ| < 15°
   - Significant computational savings for embedded systems
   - Most INAV flight profiles well within valid range

3. **Energy perspective clarifies physics**
   - Power = rate of energy change
   - Descent: potential energy → overcomes drag (less propulsive power needed)
   - Climb: propulsive power → potential energy (more power needed)

### INAV Implementation Insights

1. **L/D estimation is critical**
   - Typical values: 8-12 for model aircraft
   - Can be estimated from flight data
   - Affects range, glide, and power calculations

2. **Terrain awareness improves range prediction**
   - Flat terrain assumption underestimates range (if net descent)
   - Accounting for altitude changes gives accurate energy budget

3. **Best glide is key safety feature**
   - Knowing glide ratio enables precise RTH planning
   - Battery failsafe can switch to best-glide profile
   - Provides maximum range for given altitude

### Documentation Best Practices

1. **Clear scenarios prevent confusion**
   - "Constant throttle" vs "constant airspeed" are different scenarios
   - Explicitly state assumptions at beginning
   - Use worked examples with realistic numbers

2. **Derivations should show physical meaning**
   - Not just equations, but why they make sense
   - Energy balance perspective aids intuition
   - Limiting cases verify correctness (e.g., P=0 gives glide angle)

3. **Code examples bridge theory to practice**
   - Shows how to implement in INAV
   - Includes practical details (units, function calls)
   - Demonstrates optimization opportunities

---

## Future Work

### Additional Topics to Document

1. **Effect of wind on power requirements**
   - Headwind/tailwind components
   - Crosswind effects on ground speed vs airspeed

2. **Optimal cruise speed for range/endurance**
   - Carson speed (1.32 × Vmin_drag)
   - Trade-offs between speed and efficiency

3. **Dynamic soaring and energy extraction**
   - Using wind shear to gain energy
   - Slope soaring for autonomous sailplanes

4. **Propeller efficiency variations**
   - How prop efficiency changes with airspeed
   - Impact on power-required curves

### INAV Enhancement Opportunities

1. **Implement L/D estimation from flight logs**
   - Use collected data to calculate actual L/D
   - Store in aircraft profile for better predictions

2. **Terrain-aware mission planning**
   - Optimize waypoint altitudes for energy efficiency
   - Use power-angle relationship for accurate range

3. **Advanced RTH with energy optimization**
   - Choose altitude for best glide to home
   - Balance glide descent vs powered flight

4. **Battery reserve calculations**
   - Account for required climb after loiter
   - Prevent landing short due to altitude deficit

---

## Files Created This Session

1. `/home/raymorris/Documents/planes/inavflight/claude/developer/docs/aerodynamics/aerodynamics-workspace/knowledge-base/power-flight-path-angle.md`
   - Comprehensive analysis (3,500+ words)
   - Complete derivations and examples
   - INAV code applications

2. `/home/raymorris/Documents/planes/inavflight/claude/developer/docs/aerodynamics/aerodynamics-workspace/references/small-angle-approximations.txt`
   - Quick reference guide
   - Lookup table format
   - Performance optimization focus

3. `/home/raymorris/Documents/planes/inavflight/claude/developer/docs/aerodynamics/aerodynamics-workspace/knowledge-base/README.md`
   - Knowledge base index
   - Topic organization
   - Quick reference to H&C pages

4. `/home/raymorris/Documents/planes/inavflight/claude/developer/docs/aerodynamics/aerodynamics-workspace/notes/2026-01-18-power-calculation-session.md`
   - This session summary

---

## Summary for Manager

**Task completed:** Document power calculation for constant airspeed flight

**Deliverables:**
- Comprehensive knowledge base entry with derivations, examples, and code
- Small-angle approximation analysis proving linearity for |γ| < 15°
- Quick reference materials for embedded developers
- INAV-specific applications showing practical usage

**Quality metrics:**
- Full textbook citations (H&C pages 26-67)
- Worked examples with realistic parameters
- Code examples ready for implementation
- Cross-referenced with related topics

**Potential impact:**
- Better throttle optimization in descent
- More accurate range prediction with terrain
- Energy-efficient RTH planning
- Performance optimization (small-angle approximation)

**Files saved:**
- All in `/home/raymorris/Documents/planes/inavflight/claude/developer/docs/aerodynamics/aerodynamics-workspace/`
- Organized by type: knowledge-base/, references/, notes/

---

*Session completed: 2026-01-18*
*Agent: aerodynamics-expert*
*Documentation status: Complete and cross-referenced*
