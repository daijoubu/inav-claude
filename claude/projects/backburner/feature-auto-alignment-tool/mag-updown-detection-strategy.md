# Magnetometer Up/Down Detection Strategy

**Date:** 2026-01-21
**Challenge:** How to determine if magnetometer is right-side-up or upside-down

## The Challenge

Unlike accelerometer (which has gravity as absolute reference), magnetometer up/down detection depends on:
1. **Magnetic inclination** (dip angle) - varies by location
2. **Chip mounting convention** - varies by manufacturer?
3. **GPS module assembly** - how is chip mounted on the PCB?

## The Pins-Up Assumption

**Your hypothesis:**
> "Aren't chips normally mounted on the underside of a GPS, with the pads/pins of the chip pointed UP?"

**This is likely correct for most GPS modules!** Here's why:

### GPS Module Construction

**Typical GPS module layout:**
```
[Top view]
┌────────────────────────────┐
│   GPS Antenna (ceramic)    │  ← Top side of PCB
│         (exposed)          │
├────────────────────────────┤
│                            │
│    [GPS Chip - top side]   │
│    [Other components]      │
│                            │
└────────────────────────────┘

[Bottom view]
┌────────────────────────────┐
│                            │
│   [Mag Chip - pins UP]     │  ← Bottom side of PCB
│   [Voltage regulators]     │     Component markings facing DOWN
│   [Connectors]             │     toward ground/aircraft
│                            │
└────────────────────────────┘
```

**Why magnetometer is on bottom:**
1. GPS antenna needs clear sky view (must be on top)
2. Magnetometer needs distance from GPS chip's high-frequency signals
3. Pins/pads naturally face toward PCB (up in this case)
4. Component markings face away from PCB (down toward ground)

**Therefore:**
- **Pins point UP** (toward antenna/sky)
- **Component markings point DOWN** (toward ground)

### Chip Z-Axis Convention

**Most 3-axis sensors use right-hand rule:**
- X+ → Right (when looking at chip markings)
- Y+ → Forward (away from pin 1)
- Z+ → Up (out of component markings toward you)

**If this is true for mag chips:**
- When mounted pins-up on GPS, Z+ points DOWN (toward ground)
- When GPS is placed on table with antenna up, Z- points UP (sky)

## Detection Algorithm (Flat Position)

### Option A: GPS Fix Available (Preferred)

**If GPS has position fix:**

1. **Calculate magnetic inclination for location:**
   ```javascript
   // Use World Magnetic Model (WMM) or lookup table
   inclination = calculateInclination(lat, lon);
   // Returns: +60° (Northern Hemisphere), -60° (Southern), ~0° (Equator)
   ```

2. **Measure which axis has vertical field component:**
   ```javascript
   flat_reading = [Mx, My, Mz];

   // In Northern Hemisphere, field points DOWN
   if (inclination > 10°) {
       // Largest negative component is DOWN axis
       down_axis = argmin(Mx, My, Mz);
   }

   // In Southern Hemisphere, field points UP
   else if (inclination < -10°) {
       // Largest positive component is UP axis
       up_axis = argmax(Mx, My, Mz);
   }

   // Near equator - can't determine from inclination alone
   else {
       // Fall through to Option B
   }
   ```

3. **Determine axis polarity:**
   ```javascript
   if (inclination > 10°) {
       // Northern: down_axis points down
       // Therefore, opposite polarity points UP
       if (down_axis == X && Mx < 0) → X+ is UP
       if (down_axis == X && Mx > 0) → X- is UP
       // (same logic for Y, Z)
   }
   ```

**Pros:**
- Accurate and reliable
- Works in any hemisphere (except equator ±10°)
- No assumptions needed

**Cons:**
- Requires GPS fix (takes time, may not work indoors)
- Doesn't work near magnetic equator

---

### Option B: No GPS Fix - Use Pins-Up Assumption

**If GPS doesn't have fix (indoors, fast setup):**

1. **Identify which magnetometer chip is installed:**
   ```javascript
   chip_type = mag.dev.magHardware;  // From INAV detection
   // Returns: MAG_QMC5883, MAG_HMC5883, MAG_IST8310, etc.
   ```

2. **Look up chip Z-axis convention:**
   ```javascript
   // Requires research! (See magnetometer-chip-research-needed.md)
   const chipConventions = {
       MAG_QMC5883:  { zPlusTowardPins: true },   // Example - needs verification
       MAG_HMC5883:  { zPlusTowardPins: true },   // Example - needs verification
       MAG_IST8310:  { zPlusTowardPins: true },   // Example - needs verification
       MAG_LIS3MDL:  { zPlusTowardPins: false },  // Example - if different
       // etc.
   };

   const convention = chipConventions[chip_type];
   ```

3. **Apply pins-up mounting assumption:**
   ```javascript
   // GPS module assumption: Mag chip mounted pins-up (toward antenna)
   // Therefore:
   //   - Pins point UP (sky)
   //   - Component markings point DOWN (ground)

   if (convention.zPlusTowardPins) {
       // Z+ points toward pins → UP
       // Measure which axis is Z
       // Z+ is UP
   } else {
       // Z+ points toward markings → DOWN
       // Z- is UP
   }
   ```

4. **Measure which physical axis corresponds to chip Z:**
   ```javascript
   // Read magnetometer flat on table
   // We expect vertical axis to show largest field component (in most locations)

   flat_reading = [Mx, My, Mz];

   // Rough heuristic: Vertical axis likely has largest absolute value
   // (Works in mid-latitudes where inclination is significant)
   vertical_axis = argmax(|Mx|, |My|, |Mz|);

   // This vertical_axis is the chip's Z-axis
   // Apply convention to determine polarity
   ```

**Pros:**
- Works indoors without GPS
- Fast - no wait for GPS fix
- Good enough for initial setup

**Cons:**
- Makes assumptions (pins-up, chip convention)
- May be wrong in some cases
- Needs validation

---

### Option C: Validation Roll (Verify Assumption)

**After Step 2 (pitch-up), optionally add:**

1. **Ask user to rotate aircraft 90° clockwise (viewed from behind):**
   ```
   "Now rotate your aircraft 90° clockwise (right wing down)"
   ```

2. **Take new reading of both sensors:**
   ```javascript
   roll_90_reading = readSensors();
   ```

3. **Verify detected orientations are consistent:**
   ```javascript
   // If our up/down determination was correct,
   // the new readings should match a 90° rotation of the original

   expected_reading = rotate(flat_reading, detected_axes, 90°);

   if (close_enough(roll_90_reading, expected_reading)) {
       // Validation passed! Our up/down detection was correct
       status = "Validated ✓";
   } else {
       // Something's wrong - maybe up/down was flipped?
       suggested_flip = tryFlippingUpDown();
       if (close_enough(roll_90_reading, suggested_flip)) {
           // Ah! Up and down were reversed
           flipUpDownAxis();
           status = "Corrected ✓";
       } else {
           // Unexpected - sensor may be bad or interference
           status = "Validation failed - manual confirmation needed";
       }
   }
   ```

**Pros:**
- Validates the pins-up assumption
- Catches errors in up/down detection
- Increases confidence

**Cons:**
- Extra step for user
- More complex UI flow

---

## Recommended Strategy

### Phase 1 Implementation (Simple)

**For initial release:**

1. **If GPS has fix:** Use inclination method (Option A)
2. **If no GPS fix:**
   - Use accelerometer orientation as HINT (if mag is on same board as FC)
   - If mag is external (detect via I2C bus vs internal), use pins-up assumption
   - Add "Flip Up/Down" button in results screen for manual override

### Phase 2 Enhancement (Robust)

**After chip research complete:**

1. Implement per-chip Z-axis convention lookup (Option B)
2. Add validation roll step (Option C) as optional advanced feature
3. Add heuristic validation even without roll:
   ```javascript
   // After pitch-up, check if detected orientation makes sense
   // E.g., magnetic field magnitude should be constant
   // Field should follow right-hand rotation
   ```

### Phase 3 Polish (Production-Ready)

1. Add comprehensive error messages
2. Add troubleshooting guide in UI
3. Store successful detections to build confidence database:
   ```javascript
   // "For M8N GPS with QMC5883L, 95% of users detected: Y- forward, Z+ up"
   // Use this as sanity check
   ```

---

## Chip Research Priority

**Must research first (most common):**
1. ✅ QMC5883L - Very common on M8N/M9N GPS
2. ✅ HMC5883L - Common on older GPS
3. ✅ IST8310 - Increasingly common

**Can research later:**
- LIS3MDL, AK8963, MAG3110, etc.
- If unknown chip detected, fall back to inclination method or manual confirmation

---

## UI Mock-up for No GPS Fix

```
╔════════════════════════════════════════════╗
║  Step 1: Place aircraft flat on table     ║
║                                            ║
║  ⚠️  No GPS fix available                  ║
║                                            ║
║  Magnetometer orientation will be          ║
║  estimated using standard mounting         ║
║  convention.                               ║
║                                            ║
║  You can validate this in the next step.   ║
║                                            ║
║         [ Continue ]  [ Use GPS ]          ║
║                                            ║
╚════════════════════════════════════════════╝

... (pitch-up step) ...

╔════════════════════════════════════════════╗
║  Results                                   ║
║                                            ║
║  Flight Controller: X+ fwd, Z+ up ✓        ║
║  Compass: Y- fwd, Z+ up ⚠️                  ║
║          (estimated - no GPS)              ║
║                                            ║
║  ⚠️  Compass up/down was estimated.        ║
║     To validate:                           ║
║                                            ║
║     Option 1: Wait for GPS fix, retry      ║
║     Option 2: Validate with roll test      ║
║     Option 3: Apply and test heading       ║
║                                            ║
║  [ Validate ]  [ Apply Anyway ]  [ Retry ] ║
║                                            ║
╚════════════════════════════════════════════╝
```

---

## Summary

**For magnetometer up/down detection:**

1. **Best method:** GPS inclination (requires GPS fix)
2. **Fast method:** Pins-up assumption + chip convention (needs research)
3. **Validation:** Optional roll test to confirm
4. **Fallback:** Manual flip button if auto-detection fails

**The pins-up assumption is likely correct for most GPS modules**, but we need to:
1. ✅ Research chip Z-axis conventions
2. ✅ Verify GPS module mounting (photos/schematics)
3. ✅ Implement validation method
4. ✅ Provide manual override

**Key insight:** Even if up/down detection isn't perfect, we've still auto-detected:
- ✅ Pitch axis (wingspan direction)
- ✅ Forward axis and its polarity
- ✅ Which axis is vertical (just maybe not which end is up vs down)

**This is still MUCH better than manual configuration!** User only needs to potentially flip one bit (up vs down), rather than selecting from 12+ orientation options.
