# Thrust Symmetry Point - Calculated Values

**The symmetry point doesn't change much for reasonable L/D values. It is driven primarily by T/W.**

---

## Symmetry Point by T/W and L/D

The pitch angle where 50% throttle maintains airspeed V, exactly halfway between:
- The angle where 100% throttle maintains the same airspeed V
- The angle where 0% throttle maintains the same airspeed V

**Formula:** γ_symmetry ≈ arcsin(α/2) - 57.3°/(L/D)
57.3 is to convert between radians and degrees.

**Angle convention:** Measured from horizontal (0° = level, 90° = vertical up). All values below are **nose up** angles.

| T/W Ratio (α) | L/D = 8 | L/D = 9 | L/D = 10 | L/D = 11 |
|---------------|---------|---------|----------|----------|
| **0.75:1** | 14.9° nose up | 15.7° nose up | 16.3° nose up | 16.8° nose up |
| **1:1** | 22.8° nose up | 23.6° nose up | 24.3° nose up | 24.8° nose up |
| **1.5:1** | 41.4° nose up | 42.2° nose up | 42.9° nose up | 43.4° nose up |
| **2:1** | 82.8° nose up | 83.6° nose up | 84.3° nose up | 84.8° nose up |

---

## Operational Envelope Width

**How wide is the pitch range that can maintain the same airspeed?**

The width of the operational envelope (from minimum to maximum angle that can maintain airspeed V) is:

```
Width = γ_max - γ_min = 2 × arcsin(α/2)
```

**This width is completely independent of L/D!** It depends only on T/W ratio.

| T/W Ratio (α) | Envelope Width | γ_min | γ_max | Notes |
|---------------|----------------|-------|-------|-------|
| **0.75:1** | 44° | γ_sym - 22° | γ_sym + 22° | Narrow range |
| **1:1** | 60° | γ_sym - 30° | γ_sym + 30° | Moderate range |
| **1.5:1** | 97° | γ_sym - 48.6° | γ_sym + 48.6° | Wide range |
| **2:1** | 180° | γ_sym - 90° | γ_sym + 90° | Full ±90° range |

### Example: 1:1 T/W, L/D = 10

- **Center (γ_symmetry):** 24.3° nose up
- **Width:** 60° total
- **Minimum angle (0% throttle):** 24.3° - 30° = **-5.7° (descent)**
- **Maximum angle (100% throttle):** 24.3° + 30° = **54.3° (steep climb)**

**For any airspeed V maintainable at the symmetry point, the aircraft can maintain that same airspeed V anywhere from -5.7° to +54.3° by adjusting throttle from 0% to 100%.**

---

## Key Observations

**The pitch-throttle relationship for maintaining constant airspeed is fundamentally driven by T/W ratio, not L/D:**

**Width (envelope range):**
- Formula: 2 × arcsin(α/2)
- **Completely independent of L/D**
- Only depends on T/W ratio
- 1:1 T/W: 60° width
- 2:1 T/W: 180° width (full range)

**Center (symmetry point):**
- Formula: arcsin(α/2) - 57.3°/(L/D)
- L/D variation (8-11): only ~2° shift
- T/W variation (1:1 → 2:1): ~60° shift
- **T/W dominates** where the envelope is located

**Profound conclusion:**
- **T/W determines the shape and size** of the pitch-throttle envelope (the width)
- **L/D only shifts the center** by a small amount (5-7°)
- **The relationship between pitch and throttle isn't affected much by L/D - it's driven by T/W**

---

## Practical Implications for nav_fw_pitch2thr

**nav_fw_pitch2thr defines the WIDTH of the pitch range:**
```
pitch_range_width = 1000 μs / nav_fw_pitch2thr
```

**For typical RC aircraft (1:1 T/W, L/D = 8-11):**
- Natural symmetry point: **~23-25° nose up**
- Natural envelope width: **60°** (from ~-6° to ~54°)
- Recommended setting: **25 μs/°** → covers **40° width** (±20°)
- This 40° range is narrower than the full 60° envelope, but covers the most-used flight angles

**Current default (10 μs/°):**
- Covers **100° width** (±50° range)
- Much wider than necessary, spreading throttle authority too thinly
- Only provides 10 μs per degree, causing poor airspeed compensation at typical angles (±20°)
- Results in airspeed bleed during climbs, speed buildup during descents

**Key insight:** The natural envelope (60° for 1:1 T/W) is wider than we need. Setting nav_fw_pitch2thr = 25 μs/° concentrates throttle authority over the most-used ±20° range rather than spreading it over the full ±50° range.

---

*Calculated: 2026-01-19*
*Source: Derived formula γ_symmetry ≈ arcsin(α/2) - 57.3°/(L/D)*
*Related: derived-formulas.md, inav-pitch2thr-analysis.md*
