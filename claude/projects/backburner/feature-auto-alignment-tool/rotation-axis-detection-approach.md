# Rotation-Axis Detection Approach

**Date:** 2026-01-21
**Status:** Proposed Enhancement to Algorithm

## Summary

Two key insights that simplify the alignment detection algorithm:

1. **Smallest delta identifies rotation axis** - The sensor axis with minimal change during pitch-up IS the pitch axis (left-right, wingspan direction)
2. **Largest delta and its sign identify forward** - The axis with greatest change AND whether that change is positive/negative tells us which direction is the nose

## The Physics

### Insight 1: Rotation Axis = Minimum Change Axis

When you rotate an object about an axis:
- That axis itself doesn't change orientation in space
- Components along that axis remain constant (or nearly so)
- Components perpendicular to that axis experience maximum change

**Therefore:**
When we pitch the aircraft nose-up by 45°:
- The **pitch axis** (left-right, wingtip to wingtip) experiences MINIMAL change
- The **forward axis** experiences LARGE change (from horizontal to 45° up)
- The **up axis** experiences LARGE change (from vertical to 45° back)

**Key advantage:** We don't need to know which sensor edge is forward - we just find the axis with smallest delta!

### Insight 2: Forward Direction = Sign of Largest Delta

For accelerometer in flat position (NED convention):
- Z-axis (up): -1G (gravity pointing down)
- X-axis (forward): 0G
- Y-axis (right): 0G

After 45° pitch up:
- Z-axis (up): -0.707G (decreased magnitude)
- X-axis (forward): ±0.707G (NEW, large change from zero!)
- Y-axis (right): ~0G (minimal change - this is the rotation axis!)

**Changes:**
- Y-axis: ~0G change → **This is the pitch axis (left-right)**
- Z-axis: Changed by ~0.3G (from -1 to -0.707)
- X-axis: Changed by ~0.707G (from 0 to ±0.707) → **This is the forward axis**

**The sign of X-axis change tells us which direction is forward:**
- Positive delta → X+ is forward
- Negative delta → X- is forward (sensor mounted backward)

## Advantages Over Previous Approach

### Previous Approach (Edge Detection)
- Try to determine which sensor edge/face is forward
- Complex logic to map sensor coordinate system
- Requires understanding sensor package orientation

### New Approach (Axis Analysis)
1. Find axis with **smallest delta** → pitch axis (left-right)
2. Find axis with **largest delta** → forward/back axis
3. Check **sign** of largest delta → which end is forward
4. Remaining axis is up/down
5. Check upside-down separately (gravity direction for accel, mag inclination for mag)

**Much cleaner! No need to think about "edges" at all.**

## Algorithm Refinement

```
1. Flat position reading: [X₀, Y₀, Z₀]
2. 45° pitch up reading: [X₁, Y₁, Z₁]

3. Calculate absolute deltas:
   ΔX = |X₁ - X₀|
   ΔY = |Y₁ - Y₀|
   ΔZ = |Z₁ - Z₀|

4. Identify rotation axis (pitch axis = left-right):
   pitch_axis = axis with min(ΔX, ΔY, ΔZ)

   Examples:
   - If ΔY is smallest → Y-axis is pitch axis → sensor Y is left-right
   - If ΔX is smallest → X-axis is pitch axis → sensor X is left-right

5. Identify forward axis:
   forward_axis = axis with max(ΔX, ΔY, ΔZ)

6. Determine forward direction (sign):
   If forward_axis is X:
     forward_delta = X₁ - X₀  (NOT absolute value)
     if forward_delta > 0 → X+ is forward (nose raised, field appeared to tilt back)
     if forward_delta < 0 → X- is forward

   Same logic for Y or Z if those are the forward axis

7. Determine up/down:
   up_axis = remaining axis (not pitch, not forward)

8. Determine upside-down vs right-side-up:
   For accelerometer: Check which direction shows +1G in flat position
   For magnetometer: Check magnetic inclination (see below)
```

## Worked Example: Accelerometer

**Scenario:** FC mounted with X+ forward, Y+ right, Z- up (standard NED)

### Flat Position (0° pitch)
- X: 0G (horizontal)
- Y: 0G (horizontal)
- Z: -1G (gravity pointing down)

### 45° Pitch Up
- X: -0.707G (gravity component now in X direction, pointing backward)
- Y: 0G (no change, this axis is perpendicular to rotation)
- Z: -0.707G (gravity still has component in Z, but reduced)

### Deltas
- ΔX = |(-0.707) - 0| = 0.707G ← **LARGEST**
- ΔY = |0 - 0| = 0G ← **SMALLEST**
- ΔZ = |(-0.707) - (-1)| = 0.293G

### Analysis
1. **Y-axis has smallest delta** → Y is the pitch axis (left-right) ✓
2. **X-axis has largest delta** → X is the forward/back axis ✓
3. **X delta is negative** (went from 0 to -0.707) → X+ is forward ✓
   - Wait, let me reconsider this...

Actually, let me think about the sign more carefully. When we pitch up:
- The nose goes UP
- From the sensor's perspective, gravity appears to rotate BACKWARD (down and backward)
- If sensor X+ points forward, gravity appears to gain a component in the X- direction
- So X reading becomes negative (gravity pulling backward relative to sensor)

Hmm, this requires careful thought about sign convention. Let me think...

Actually, for NED (North-East-Down):
- Acceleration is measured as force per unit mass
- When stationary on table, accelerometer reads +1G in the UP direction (opposing gravity)
- So if Z- is UP, Z reads +1G (not -1G)

Let me reconsider:

### Flat Position (0° pitch) - NED Convention
- X: 0G
- Y: 0G
- Z: +1G (accelerometer reads upward force opposing gravity)

### 45° Pitch Up
- X: +0.707G (accelerometer feels upward force component in forward direction)
- Y: 0G
- Z: +0.707G (vertical component reduced)

### Deltas
- ΔX = |0.707 - 0| = 0.707G ← **LARGEST**
- ΔY = |0 - 0| = 0G ← **SMALLEST**
- ΔZ = |0.707 - 1| = 0.293G

### Signed Delta for Forward Detection
- Forward delta = X₁ - X₀ = 0.707 - 0 = +0.707
- **Positive delta means X+ is forward** ✓

This makes sense: when we pitch up, the sensor experiences an upward force in the forward direction.

## Upside-Down Detection

### Accelerometer: Easy
In flat position, check which axis reads ~1G (opposing gravity):
- If Z+ reads +1G → Z+ points up → right-side up
- If Z- reads +1G → Z- points up → upside-down

### Magnetometer: Requires Magnetic Inclination

**Question to research:** Do all magnetometer chips used by INAV follow the same convention for "which direction is toward the bottom of the chip (where the pins/pads are)"?

#### Known Magnetometer Chips in INAV

Need to verify for each:
1. **QMC5883L** - Common on GPS modules
2. **HMC5883L** - Older, common on GPS modules
3. **LIS3MDL** - ST Microelectronics
4. **MAG3110** - Freescale/NXP
5. **AK8963** - AKM (in MPU9250)
6. **AK8975** - AKM (older)
7. **IST8310** - Isentek

#### What We Need to Know

For each chip:
- What is the physical mounting convention? (component side vs pin side)
- Which axis is "Z" in the datasheet?
- Does datasheet Z+ point toward component markings or toward pins?
- How is the chip typically mounted on GPS modules?

#### Using Magnetic Inclination

Once we know which sensor axis is "up", we can use magnetic inclination:

**Northern Hemisphere (most of NA, Europe, Asia):**
- Magnetic field points DOWN and NORTH
- Inclination angle is positive (typically +60° to +70° at mid-latitudes)
- Whichever sensor axis shows the downward field component is pointing down

**Southern Hemisphere (Australia, South Africa, southern S. America):**
- Magnetic field points UP and NORTH
- Inclination angle is negative (typically -60° to -70° at mid-latitudes)
- Whichever sensor axis shows the upward field component is pointing up

**Near Magnetic Equator (±10° magnetic latitude):**
- Field is nearly horizontal
- Cannot reliably determine up/down from magnetometer alone
- Must use default assumption or manual confirmation

## Testing Considerations

### Sensor Noise
- Take multiple readings and average
- Reject outliers
- Require minimum delta threshold for confidence

### Table Not Perfectly Level
- Small tilt OK, we're looking for LARGEST change
- Could calibrate in flat position first

### User Not Exactly 45°
- Exact angle doesn't matter!
- We're looking at relative changes
- Any pitch between 30-60° should work fine

### Magnetic Interference
- Hard iron: Constant offset (not a problem for delta measurement)
- Soft iron: Scale/rotation distortion (could affect results)
- Strong local fields: Could dominate Earth's field (require sanity check)

## Action Items

### Research Required
1. **Survey INAV magnetometer chips:**
   - [ ] QMC5883L - chip orientation convention
   - [ ] HMC5883L - chip orientation convention
   - [ ] LIS3MDL - chip orientation convention
   - [ ] MAG3110 - chip orientation convention
   - [ ] AK8963 - chip orientation convention
   - [ ] AK8975 - chip orientation convention
   - [ ] IST8310 - chip orientation convention

2. **Check GPS module mounting:**
   - [ ] How are mag chips typically mounted on GPS modules?
   - [ ] Component side up or down?
   - [ ] Any variation between manufacturers?

3. **Review INAV code:**
   - [ ] How does INAV currently handle mag orientation?
   - [ ] What conventions are used in alignment settings?
   - [ ] Are there existing functions to calculate magnetic inclination?

### Algorithm Implementation
1. [ ] Implement min-delta rotation axis detection
2. [ ] Implement max-delta forward axis detection
3. [ ] Implement signed delta forward direction detection
4. [ ] Add magnetic inclination calculation or lookup
5. [ ] Add upside-down detection for magnetometer
6. [ ] Handle edge cases (equator, interference, etc.)

### Testing
1. [ ] Test with FC mounted standard orientation
2. [ ] Test with FC rotated 90° (all 4 orientations)
3. [ ] Test with FC upside-down
4. [ ] Test with external GPS/mag at various orientations
5. [ ] Test near magnetic equator (simulate with math)
6. [ ] Test with magnetic interference present

## Conclusion

The rotation-axis detection approach is:
- ✅ **Simpler** - No need to think about sensor edges
- ✅ **More robust** - Based on fundamental physics
- ✅ **Elegant** - Min/max delta directly identifies axes
- ✅ **Sign-aware** - Delta sign tells us polarity

**Key insight:** We rotated AROUND the pitch axis, so it shows minimal change. We rotated INTO the forward axis, so it shows maximal change and its sign tells us which direction is forward.

The main remaining question is magnetometer chip mounting conventions to properly handle upside-down detection.
