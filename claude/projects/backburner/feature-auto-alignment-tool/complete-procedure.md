# Complete Auto-Alignment Procedure

**Date:** 2026-01-21
**Status:** Design Complete, Ready for Implementation

## Key Principle

**CRITICAL:** The accelerometer (on FC) and magnetometer (often on external GPS) can have COMPLETELY DIFFERENT orientations. We must detect each independently!

**Common scenario:**
- FC mounted flat, X+ forward, Z- up
- GPS module rotated 90°, Y+ forward, Z- up
- OR GPS mounted on mast with different orientation entirely

This is WHY this feature is valuable - manually figuring out compass alignment is error-prone!

---

## Complete Procedure

### Step 1: Aircraft Flat on Table

#### For Accelerometer:
**Determine which axis is UP (easy):**
- Read [Ax, Ay, Az]
- Whichever axis reads ~1G is pointing UP (opposing gravity)
- This unambiguously determines up_axis and its polarity

**Example:**
```
Reading: Ax=0, Ay=0, Az=+1G
Result: Z+ points UP → Sensor is right-side-up with Z+ as up_axis
```

#### For Magnetometer (more complex):
**Determine which axis is UP:**

**Option A: If we know hemisphere (GPS has fix):**
- Calculate expected magnetic inclination for location
- Measure which axis shows downward/upward field component
- Northern Hemisphere: Field points DOWN → axis with downward component is DOWN
- Southern Hemisphere: Field points UP → axis with upward component is UP

**Option B: If hemisphere unknown (no GPS fix):**
- **Assume pins-up mounting** (component markings facing down)
  - Most GPS modules mount mag chip component-side-down
  - This means chip's Z+ likely points down toward ground
- Read [Mx, My, Mz]
- Identify which chip is installed (from INAV detection)
- Use chip-specific convention (requires research - see magnetometer-chip-research-needed.md)

**Validation method (if assumption made):**
- After determining forward direction (Step 2), can add optional Step 3
- Have user rotate aircraft 90° (roll or yaw)
- Verify detected orientations are consistent
- If inconsistent, flip up/down axis

---

### Step 2: User Raises Nose 45°

**This step works identically for BOTH sensors (independently):**

#### For Accelerometer:

1. **Read:** [Ax', Ay', Az']

2. **Calculate deltas:**
   ```
   ΔAx = |Ax' - Ax|
   ΔAy = |Ay' - Ay|
   ΔAz = |Az' - Az|
   ```

3. **Find pitch axis (minimal change):**
   ```
   pitch_axis = argmin(ΔAx, ΔAy, ΔAz)
   → This axis points left-right (wingspan direction)
   ```

4. **Find forward axis (maximal change):**
   ```
   forward_axis = argmax(ΔAx, ΔAy, ΔAz)
   ```

5. **Determine forward polarity (sign):**
   ```
   signed_delta = Aforward' - Aforward

   If signed_delta > 0:
     → forward_axis+ points forward (nose)
   If signed_delta < 0:
     → forward_axis- points forward (nose)
   ```

6. **Result for accelerometer:**
   ```
   - pitch_axis: Y (for example)
   - forward_axis: X+ (or X- depending on sign)
   - up_axis: Z+ (determined in Step 1)

   → Translation: "IMU mounted with X+ forward, Y+ right, Z+ up"
   → Alignment setting: ALIGN_CW0_DEG (or whatever matches)
   ```

#### For Magnetometer (SAME PROCESS):

1. **Read:** [Mx', My', Mz']

2. **Calculate deltas:**
   ```
   ΔMx = |Mx' - Mx|
   ΔMy = |My' - My|
   ΔMz = |Mz' - Mz|
   ```

3. **Find pitch axis (minimal change):**
   ```
   pitch_axis = argmin(ΔMx, ΔMy, ΔMz)
   ```

4. **Find forward axis (maximal change):**
   ```
   forward_axis = argmax(ΔMx, ΔMy, ΔMz)
   ```

5. **Determine forward polarity:**
   ```
   signed_delta = Mforward' - Mforward

   If signed_delta > 0:
     → forward_axis+ points forward
   If signed_delta < 0:
     → forward_axis- points forward
   ```

   **Note:** For magnetometer, we're looking at how the field APPEARS to rotate
   - In Northern Hemisphere, field points down and north
   - When we pitch up, the downward component of field appears to rotate backward
   - The math works out the same: positive delta means that axis points forward

6. **Result for magnetometer:**
   ```
   - pitch_axis: X (for example - different from IMU!)
   - forward_axis: Y- (different from IMU!)
   - up_axis: Z- (from Step 1, possibly different from IMU!)

   → Translation: "Compass mounted with Y- forward, X- right, Z- up"
   → Alignment setting: ALIGN_CW90_DEG_FLIP (or whatever matches)
   ```

---

### Step 3 (Optional): Validation Roll

**If Step 1 required assumption about up/down (no GPS fix):**

1. Have user roll aircraft 90° (or rotate 90° yaw)
2. Read both sensors again
3. Verify that detected orientations are consistent with new readings
4. If inconsistent, detected up/down axis polarity may be wrong
5. Offer to flip and retry

**This validates the pins-up assumption made in Step 1.**

---

## Example: Different Orientations

**Scenario:** Common INAV setup
- FC mounted flat in fuselage
- External GPS on wing with 90° rotation

### Step 1 Results:

**Accelerometer (on FC):**
```
Flat reading: Ax=0, Ay=0, Az=+1G
Result: Z+ is UP
```

**Magnetometer (on GPS module):**
```
Flat reading: Mx=-300, My=+150, Mz=+400
Assumption: Pins-up mounting, chip is QMC5883L where Z+ points toward pins
Result: Z+ is UP (same as IMU, but not always the case!)
```

### Step 2 Results:

**Accelerometer:**
```
Flat:      Ax=0,     Ay=0,     Az=+1.0G
Pitch 45°: Ax=+0.7G, Ay=0,     Az=+0.7G

Deltas: ΔAx=0.7G, ΔAy=0G, ΔAz=0.3G

pitch_axis = Y (minimal change)
forward_axis = X (maximal change)
signed_delta = +0.7 (positive)

Result: X+ forward, Y+ right, Z+ up
Alignment: ALIGN_CW0_DEG (standard)
```

**Magnetometer:**
```
Flat:      Mx=-300,  My=+150,  Mz=+400
Pitch 45°: Mx=+50,   My=+150,  Mz=+200

Deltas: ΔMx=350, ΔMy=0, ΔMz=200

pitch_axis = Y (minimal change) ← SAME as IMU
forward_axis = X (maximal change) ← SAME as IMU
signed_delta = +50 - (-300) = +350 (positive) ← SAME polarity

Result: X+ forward, Y+ right, Z+ up
Alignment: ALIGN_CW0_DEG (happens to match IMU in this case)
```

**In this example, both sensors have the same orientation.**

---

### Different Example: GPS Rotated 90°

**Magnetometer on GPS rotated 90° clockwise:**
```
Flat:      Mx=+150,  My=+300,  Mz=+400
Pitch 45°: Mx=+150,  My=-50,   Mz=+200

Deltas: ΔMx=0, ΔMy=350, ΔMz=200

pitch_axis = X (minimal change) ← DIFFERENT from IMU!
forward_axis = Y (maximal change) ← DIFFERENT!
signed_delta = -50 - (+300) = -350 (negative) ← Forward is Y-

Result: Y- forward, X+ right, Z+ up
Alignment: ALIGN_CW90_DEG (90° clockwise from IMU)
```

**This is exactly what we want to detect automatically!**

---

## Error Checking

### Sanity Checks:

1. **Minimal delta must be significantly smaller than maximal delta:**
   ```
   if max_delta < 2 * min_delta:
       ERROR: "Unclear rotation axis - readings too similar"
       → User may not have pitched aircraft, or sensors are bad
   ```

2. **Maximal delta must be reasonable:**
   ```
   For accelerometer:
     Expected Δmax ≈ 0.7G for 45° pitch
     if max_delta < 0.3G or max_delta > 1.0G:
         WARNING: "Unexpected pitch angle - please raise nose ~45°"

   For magnetometer:
     Expected based on local field strength and inclination
     Sanity check against Earth's field (~0.5 Gauss)
   ```

3. **Up axis must show ~1G in flat position (accelerometer):**
   ```
   if |up_reading| < 0.9G or |up_reading| > 1.1G:
       ERROR: "Aircraft not level - please place on flat surface"
   ```

4. **Magnetic field magnitude check:**
   ```
   field_magnitude = sqrt(Mx² + My² + Mz²)
   if field_magnitude < 0.25 or field_magnitude > 1.0 Gauss:
       WARNING: "Magnetic interference detected - move away from metal"
   ```

---

## Implementation Notes

### UI Flow:

1. **Screen 1:** "Place aircraft flat on level surface"
   - Button: "Continue"
   - Take flat readings for both sensors
   - Validate level (accelerometer ~1G up)

2. **Screen 2:** "Raise nose to approximately 45 degrees"
   - Visual indicator showing current pitch angle (from accelerometer)
   - Button: "Capture" (enabled when pitch is 30-60°)
   - Take pitched readings

3. **Screen 3:** "Analysis Results"
   - Show detected orientations:
     ```
     Flight Controller: X+ forward, Z+ up
     Compass: Y- forward, Z+ up
     ```
   - Option: "Apply Settings" or "Retry"

4. **Screen 4 (Optional):** "Validation - Rotate aircraft 90°"
   - Only if GPS fix not available (hemisphere unknown)
   - Verifies up/down axis determination
   - Button: "Validate"

### Settings to Apply:

```javascript
// Accelerometer determines FC alignment
compassConfig.align = detected_imu_alignment;

// Magnetometer determines compass alignment
compassConfig.mag_align = detected_mag_alignment;

// These are INDEPENDENT settings!
```

---

## Why This Is Better Than Current Method

**Current method:**
1. User looks at sensor chips with magnifying glass
2. User tries to figure out which axis is which
3. User manually selects from dropdown: CW0, CW90, CW180, CW270, FLIP variants
4. User tests heading and discovers it's wrong
5. User tries different settings until heading looks right
6. User still isn't sure if yaw is correct

**Auto-detection method:**
1. User places aircraft flat
2. User raises nose
3. Done! Both sensors configured correctly

**User experience: 1000% better!**

---

## Remaining Work

1. **Research magnetometer chip conventions** (see magnetometer-chip-research-needed.md)
   - Verify QMC5883L Z-axis definition
   - Verify HMC5883L Z-axis definition
   - Check if GPS modules consistently mount chips pins-up

2. **Implement algorithm** in configurator
   - Add wizard UI screens
   - Implement min/max delta calculation
   - Add sanity checks and error handling

3. **Test with real hardware**
   - Various FC orientations
   - External GPS at various rotations
   - Different magnetometer chips

4. **Add validation roll** (optional feature)
   - For cases without GPS fix
   - Confirms up/down axis detection

---

## Summary

**The procedure is:**

✅ **Step 1 (Flat):** Determine UP axis for each sensor
   - ACC: Easy (gravity)
   - MAG: Use inclination if known, else assume pins-up and validate later

✅ **Step 2 (Pitch up):** Determine forward and pitch axes for EACH sensor
   - Min delta → pitch axis (left-right)
   - Max delta → forward axis
   - Sign of max delta → forward polarity

✅ **Step 3 (Optional validation):** Roll 90° to verify up/down
   - Only needed if hemisphere unknown

✅ **Apply independent alignment settings** for FC and compass

**Key insight corrected:** Do NOT assume mag orientation matches IMU! That's the whole point - they're often different, especially with external GPS modules.
