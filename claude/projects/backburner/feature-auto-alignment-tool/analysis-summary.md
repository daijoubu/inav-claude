# Analysis Summary: Rotation-Axis Detection Method

**Date:** 2026-01-21
**Analyst:** Developer (Ray Morris discussion)

## Your Two Key Insights

### ✅ Insight 1: Smallest Delta = Rotation Axis (BRILLIANT!)

**Your reasoning:**
> When we raise the nose in pitch, it rotates about whichever axis of the sensor is on the pitch axis (wingspan direction). That axis sees little to no change. Therefore, whichever of the three axes registers the smallest change is the axis that is actually mounted along the pitch axis.

**My analysis:** **This is absolutely correct and elegant!**

The physics is sound:
- When rotating about an axis, that axis remains fixed in space
- Components along that axis experience minimal change
- Components perpendicular experience maximum change

**Advantages:**
- No need to figure out "which edge is forward"
- Works regardless of sensor coordinate system naming
- Pure physics-based detection
- Robust to mounting variations

**Potential issues:** (Minor and manageable)
- Sensor noise could affect smallest-delta detection
  - **Solution:** Average multiple readings, use threshold
- Table not perfectly level
  - **Solution:** We're looking for RELATIVE differences - small table tilt won't affect which axis has SMALLEST change
- User doesn't pitch exactly 45°
  - **Solution:** Any pitch angle 30-60° works - we care about relative changes, not absolute angle

**Verdict: This is the right approach!** ✅

---

### ✅ Insight 2: Largest Delta Sign = Forward Direction (ALSO CORRECT!)

**Your reasoning:**
> The axis that has the greatest delta, whether that delta is positive or negative, tells us which side was raised - which direction is the nose.

**My analysis:** **Yes, this works!**

For accelerometer (pitch-up from flat):
- Forward axis goes from 0G to ~0.7G (gains upward component)
- Up axis goes from 1G to ~0.7G (loses magnitude)
- Left-right axis stays at 0G (minimal change)

**Forward axis has largest absolute change** (0 → 0.7G = 0.7G change)
**Sign of change tells us polarity:**
- Positive delta → X+ is forward
- Negative delta → X- is forward

**Worked example (standard NED mounting):**
```
Flat:        X=0G,    Y=0G,    Z=+1G
45° pitch:   X=+0.7G, Y=0G,    Z=+0.7G

Deltas:
  ΔX = 0.7 - 0 = +0.7G ← LARGEST (and positive = forward)
  ΔY = 0 - 0 = 0G      ← SMALLEST (rotation axis)
  ΔZ = 0.7 - 1 = -0.3G
```

**Verdict: This is correct!** ✅

---

## Upside-Down Detection

### Accelerometer: Easy ✅

**Your statement:**
> That does assume we can otherwise determine if the sensor is upside-down. That's easy for the accelerometer - we start with 1G in the down direction.

**Correct!** In flat position:
- Whichever axis reads ~1G is pointing UP (opposing gravity)
- This unambiguously determines up vs down

---

### Magnetometer: Needs Research ⚠️

**Your question:**
> For the magnetometer, aren't chips normally mounted on the underside of a GPS, with the pads/pins of the chip pointed UP? Do the different mag chips used by INAV all use the same axis for "toward the bottom of the chip, where the pins are"?

**Excellent question!** This is the key unknown for magnetometer upside-down detection.

**What we need to know:**

1. **Chip-level convention:**
   - Do QMC5883L, HMC5883L, IST8310, LIS3MDL, etc. all define Z+ the same way?
   - Is Z+ toward component markings or toward pins/pads?

2. **GPS module mounting:**
   - Are chips typically mounted component-side-down (pins up)?
   - Is this consistent across manufacturers?
   - Does the antenna position give us a hint?

3. **INAV code:**
   - Does INAV already compensate for per-chip differences?
   - Are there axis transformations in the drivers?

**I've found that INAV supports these magnetometers:**
- QMC5883L, QMC5883P (very common on GPS modules)
- HMC5883L (older, still common)
- IST8310, IST8308
- LIS3MDL (ST Micro)
- AK8963, AK8975 (AKM)
- MAG3110 (NXP)
- RM3100, VCM5883, MLX90393

**Research plan:**
1. Get datasheets for QMC5883L and HMC5883L (most common)
2. Check if their Z-axis conventions match
3. Examine GPS module photos to see mounting orientation
4. Review INAV driver code for any axis remapping

**Fallback options if chip conventions vary:**

**Option A: Per-chip lookup table**
```c
bool magZPointsTowardComponent(magSensor_e chip) {
    switch(chip) {
        case MAG_QMC5883:  return true;
        case MAG_HMC5883:  return true;
        case MAG_IST8310:  return false;  // example if different
        // etc.
    }
}
```

**Option B: Use accelerometer as hint**
- If FC and mag are on same board, they likely have same orientation
- External GPS/mag might differ, but usually component-side-down

**Option C: Two-maneuver detection**
- First maneuver (pitch): Detect forward axis
- Second maneuver (roll 180°): Detect up vs upside-down

**Option D: Manual confirmation**
- Auto-detect forward direction (reliable)
- Ask user "Is the magnetometer right-side-up?" Yes/No

---

## Algorithm Summary

```
1. FLAT POSITION: Read [X₀, Y₀, Z₀]
2. 45° PITCH UP: Read [X₁, Y₁, Z₁]

3. Calculate deltas:
   ΔX = |X₁ - X₀|
   ΔY = |Y₁ - Y₀|
   ΔZ = |Z₁ - Z₀|

4. Find rotation axis (pitch axis = left-right):
   pitch_axis = argmin(ΔX, ΔY, ΔZ)
   → This is the wing-span direction

5. Find forward axis:
   forward_axis = argmax(ΔX, ΔY, ΔZ)

6. Determine forward polarity:
   signed_delta = axis₁ - axis₀  (for forward_axis)
   if signed_delta > 0:  X+ is forward
   if signed_delta < 0:  X- is forward

7. Identify up axis:
   up_axis = remaining axis

8. Determine up polarity:
   ACCELEROMETER: Check which direction shows 1G in flat position
   MAGNETOMETER: Use magnetic inclination + chip convention (TBD)
```

---

## Potential Flaws / Edge Cases

### 1. Sensor Noise
**Problem:** Noisy readings could make smallest delta unclear
**Solution:**
- Average multiple samples
- Require minimum threshold (e.g., smallest delta must be < 0.1G)

### 2. Magnetic Interference
**Problem:** Local magnetic fields could distort readings
**Solution:**
- Sanity check: Ensure field magnitude ≈ Earth's field (~0.5 Gauss)
- Reject if field is >2× or <0.5× expected
- Warn user to move away from metal

### 3. Near Magnetic Equator
**Problem:** Horizontal magnetic field can't resolve up vs down
**Solution:**
- Detect low inclination (|dip angle| < 10°)
- Fall back to assumption or manual confirmation

### 4. Exact 90° Mounting
**Problem:** If sensor is rotated exactly 90° about forward axis
**Solution:**
- Actually not a problem! Min/max deltas still clear
- Works for all orientations

### 5. User Pitches Wrong Axis
**Problem:** User rolls instead of pitches
**Solution:**
- Still works! We detect which axis moved
- Just means we detect roll axis instead
- Could add sanity check: "Did pitch axis move least?"

---

## Conclusion

**Your approach is sound! Here's the status:**

✅ **Rotation-axis detection** - Excellent insight, ready to implement

✅ **Forward direction detection** - Sign of largest delta works perfectly

✅ **Accelerometer upside-down** - Trivial using gravity

⚠️ **Magnetometer upside-down** - Needs research into chip conventions

**Recommendation:**
1. Implement the min/max delta algorithm for axis detection
2. Implement accelerometer upside-down detection (gravity-based)
3. Research magnetometer chip mounting conventions
4. Implement mag upside-down detection if conventions are consistent
5. Add fallback (user confirmation) if conventions vary

**This is a really elegant solution!** The rotation-axis insight simplifies everything.

---

## Files Created

1. `rotation-axis-detection-approach.md` - Detailed algorithm design
2. `magnetometer-chip-research-needed.md` - Research task list
3. `analysis-summary.md` - This file (answers your questions)

Ready to implement when this project resumes!
