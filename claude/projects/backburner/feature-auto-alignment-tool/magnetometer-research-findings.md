# Magnetometer Chip Research Findings

**Date:** 2026-01-21
**Research Completed By:** Developer (Ray Morris)

## Executive Summary

**Key findings:**
1. ✅ **Most mag chips follow standard convention:** Z+ points UP from component markings (away from pins)
2. ⚠️ **IST8310 is NON-STANDARD:** Uses left-hand rule instead of right-hand rule
3. ⚠️ **GPS module mounting varies:** Some modules require "CW 270° Flip", suggesting upside-down chip mounting
4. ⚠️ **No hardcoded presets exist:** INAV configurator has no GPS module → mag orientation mappings

---

## Magnetometer Chip Axis Conventions

### QMC5883L (Most Common)

**Sources:**
- [QST Datasheet](https://qstcorp.com/upload/pdf/202202/13-52-04%20QMC5883L%20Datasheet%20Rev.%20A(1).pdf)
- [How to Setup a Magnetometer on Arduino](https://www.circuitbasics.com/how-to-setup-a-magnetometer-on-the-arduino/)
- [Betaflight Magnetometer Guide](https://www.betaflight.com/docs/wiki/guides/current/Magnetometer)

**Findings:**
- **Z-axis points UP** from component markings (perpendicular to PCB)
- **X-axis points FORWARD**
- **Y-axis points LEFT** (standard right-hand rule)
- Package: 3.0 x 3.0 x 0.9 mm, 16-pin LCC
- **Convention:** "When looking at the top of the sensor package, the Z-axis extends upward from the package surface"

**Confirmed:** Z+ points away from pins, toward component side

---

### HMC5883L (Common on Older GPS)

**Sources:**
- [Adafruit Datasheet](https://cdn-shop.adafruit.com/datasheets/HMC5883L_3-Axis_Digital_Compass_IC.pdf)
- [Farnell Datasheet](https://www.farnell.com/datasheets/1683374.pdf)
- [Microcontrollers Lab HMC5883L Guide](https://microcontrollerslab.com/hmc5883l-3-axis-magnometer-interfacing-arduino/)

**Findings:**
- Datasheet shows **arrows indicating sensitive axis directions** on pinout diagram
- Arrows show "direction of magnetic field that generates positive output"
- Resistive elements have **common sensitive axis indicated by arrows**
- Z-axis is **perpendicular to X-Y plane** (package surface)
- Uses **standard right-hand rule**

**Confirmed:** Similar to QMC5883L, Z+ points from component side

**Note:** Honeywell stopped production; QST licensed the design. Modern "5883" chips are QMC5883L, while "L883" indicates original HMC5883L.

---

### IST8310 (Increasingly Common) ⚠️ NON-STANDARD

**Sources:**
- [Betaflight Issue #13678 - IST8310 magnetometer orientation](https://github.com/betaflight/betaflight/issues/13678)
- [INAV Issue #4524 - IST8310 compass does not work](https://github.com/iNavFlight/inav/issues/4524)
- [Isentek Datasheet](https://isentek.com/userfiles/files/IST8310Datasheet_3DMagneticSensors.pdf)

**Critical Finding: LEFT-HAND RULE!**

**The Problem:**
- **Y-axis points to the RIGHT instead of LEFT** (left-hand rule instead of right-hand rule)
- When turning LEFT from north, compass shows EAST instead of WEST
- Cannot be fixed with standard rotations (roll, pitch, yaw)
- Requires **custom axis remapping** in firmware

**From Betaflight Issue #13678:**
> "The y-axis of the IST8310 points to the right instead of the left (left-hand rule instead of right-hand rule)... with the available rotations (mag_align_roll, mag_align_pitch, mag_align_yaw), you can't rotate only the y-axis by 180 degrees."

**Workaround:**
- Betaflight: Custom axis orientation required via CLI
- INAV: Use `align_mag_roll`, `align_mag_pitch`, `align_mag_yaw` settings (trial and error)
- Chip can have I2C addresses 12, 13, 14, or 15 (driver defaults to 12)

**Package:** 16-pin LGA, 2.0 x 2.0 x 1.0 mm
**Range:** ±1600 µT (X/Y axes), ±2500 µT (Z axis)

**Implication for auto-alignment:** Need **special handling** for IST8310 - can't use same algorithm!

---

### MAG3110 (NXP/Freescale)

**Sources:**
- [MAG3110 Datasheet](https://cdn.sparkfun.com/datasheets/Sensors/Magneto/MAG3110.pdf)
- [MathWorks MAG3110 Documentation](https://www.mathworks.com/help/supportpkg/microbit/ref/mag31103axismagnetometer.html)

**Findings:**
- **Z+ axis points toward component side** (away from PCB, perpendicular to surface)
- When mounted with pins down, Z+ points UP
- Standard right-hand rule convention

**Confirmed:** Same as QMC5883L and HMC5883L

---

### LIS3MDL (ST Microelectronics)

**Sources:**
- [Adafruit LIS3MDL Learning Guide](https://learn.adafruit.com/lis3mdl-triple-axis-magnetometer)
- [Pololu LIS3MDL Product Page](https://www.pololu.com/product/2737)
- INAV Driver: `inav/src/main/drivers/compass/compass_lis3mdl.c`

**Findings:**
- Standard 3-axis magnetometer
- I2C addresses: 0x1E or 0x1C (selectable by pin)
- Range: ±4, ±8, ±12, ±16 gauss (programmable)
- Likely follows ST's standard axis convention

**Status:** Need datasheet to confirm Z-axis direction

---

### Summary: Chip Axis Conventions

| Chip | Z+ Direction | Hand Rule | Quirks |
|------|-------------|-----------|---------|
| **QMC5883L** | UP (component side) | Right-hand | ✅ Standard |
| **HMC5883L** | UP (component side) | Right-hand | ✅ Standard |
| **IST8310** | UP (component side) | **LEFT-HAND** | ⚠️ Y-axis reversed! |
| **MAG3110** | UP (component side) | Right-hand | ✅ Standard |
| **LIS3MDL** | (Likely UP) | Right-hand | ✅ Likely standard |

**General Convention:** Z+ points AWAY from pins (UP from component markings)

---

## GPS Module Mounting Analysis

### INAV Configurator Findings

**Source:** `/home/raymorris/Documents/planes/inavflight/inav-configurator/tabs/magnetometer.js`

**Key Discovery:** **NO hardcoded GPS module → mag orientation presets exist!**

- Configurator has generic mag alignment presets (CW0°, CW90°, CW180°, CW270°, plus FLIP variants)
- 3D visualization shows 29 GPS/mag module models
- Models are for **visualization only** - no orientation data
- User must **manually select** alignment from dropdown

**GPS Models with 3D Visualizations:**
- Matek: `matek_m8q`, `matek_m9n`, `matek_m10q`
- Holybro: `holybro_m9n_micro`
- Foxeer: `foxeer_m10q_120`, `foxeer_m10q_180`, `foxeer_m10q_250`
- Diatone: `diatone_mamba_m10_pro`
- Flywoo: `flywoo_goku_m10_pro_v3`
- GEPRC: `geprc_gep_m10_dq`
- HGLRC: `hglrc_m100`
- Beitian: `bn_880`
- Raw sensors: `qmc5883`, `gy271`, `gy273`, `ist8308`, `ist8310`, `lis3mdl`, etc.

**Implication:** Auto-alignment wizard would be **extremely valuable** - currently users must figure this out manually!

---

### Matek M8Q/M9N GPS Modules

**Sources:**
- [Matek M8Q-5883 Product Page](https://www.mateksys.com/?portfolio=m8q-5883)
- [Matek M9N-5883 Product Page](https://www.mateksys.com/?portfolio=m9n-5883)
- [Matek M8Q GPS Orientation Thread](https://intofpv.com/t-matek-m8q-gps-orientation-in-betaflight)

**Configuration Requirements:**

**For M8Q-5883 and M9N-5883:**
- **INAV/BetaFlight:** `CW 270° Flip` when FC arrow pointing forward
- **ArduPilot:** `Rotation None`

**Analysis:**
- `CW 270° Flip` = 270° clockwise rotation + 180° roll flip
- This suggests the magnetometer chip is:
  - Rotated 90° CCW relative to GPS mounting
  - **Mounted upside-down** (component side DOWN, pins UP)

**Physical Construction Inference:**
1. GPS ceramic antenna is on TOP of PCB
2. Magnetometer chip likely on BOTTOM of PCB (away from GPS RF)
3. Chip mounted **component-side-down** (pins facing UP toward antenna)
4. This puts chip's Z+ pointing DOWN into PCB (toward ground when GPS on top)

---

### Beitian BN-880 GPS Module

**Sources:**
- [Flying Tech BN-880 Product](https://www.flyingtech.co.uk/electronics/beitian-bn-880-gps-compass-module-inav-betaflight)
- [RaceDayQuads BN-880](https://www.racedayquads.com/products/rdq-bn-880-flight-control-gps-module-dual-module-compass-with-cable)
- [Amazon BN-880 Listings](https://www.amazon.com/Geekstory-Navigation-Raspberry-Aircraft-Controller/dp/B078Y6323W)

**Variants:**
- **BN-880:** M8N GPS + HMC5883L compass
- **BN-880Q:** M8N GPS + QMC5883L compass (newer)

**Mounting Guidance:**
- "Antenna should be pointing up towards the sky"
- "Position away from VTX antenna and interference sources"
- Requires flat mounting, no tilting

**Alignment Configuration:**
- No specific preset mentioned in search results
- Users report needing various CW rotations
- Suggests chip orientation varies by manufacturing batch?

---

### GPS Module Construction Pattern

**Typical GPS Module Layers (from top to bottom):**

```
┌─────────────────────────────┐
│    Ceramic Patch Antenna    │  ← TOP (sky-facing)
│         (18x18mm)           │
├─────────────────────────────┤
│                             │
│   [GPS Chip - component up] │  ← GPS receiver on component side
│   [Other components]        │
│                             │
│ ═══════════════════════════ │  ← PCB (possibly 2-layer)
│                             │
│ [Mag Chip - component DOWN] │  ← Magnetometer on opposite side
│      (pins facing UP)       │     (away from GPS RF noise)
│                             │
└─────────────────────────────┘  ← BOTTOM (aircraft-facing)
```

**Reasoning:**
1. **Antenna must be on top** - needs clear sky view
2. **Magnetometer wants distance from GPS** - high-frequency GPS signals can interfere
3. **Placing mag on bottom** achieves best separation
4. **Component-side-down mounting** - pins face UP (standard PCB assembly)

**Result:** When GPS module sits antenna-up on aircraft:
- Chip Z+ points DOWN (into aircraft body)
- Chip Z- points UP (toward antenna/sky)
- This matches "CW 270° Flip" requirement (includes 180° roll = upside-down)

---

## Implications for Auto-Alignment Algorithm

### Standard Chips (QMC5883L, HMC5883L, MAG3110, LIS3MDL)

**For chips following standard convention:**

1. **Flat position reading:**
   - If GPS antenna is UP (normal mounting)
   - Mag chip is likely component-side-down
   - Therefore Z+ points DOWN (into aircraft)
   - Z- points UP (toward sky/antenna)

2. **Detection strategy:**
   ```
   // Read flat position
   flat_mag = [Mx, My, Mz]

   // In Northern Hemisphere, magnetic field points DOWN and NORTH
   // Largest downward component indicates DOWN axis

   // If Z shows largest downward field component:
   //   Z+ points down OR Z- points down (ambiguous)

   // Use magnetic inclination to resolve:
   //   Expected field has downward component
   //   Measure which polarity shows downward field
   //   → That polarity points DOWN
   ```

3. **Pins-up assumption:**
   ```javascript
   // ASSUMPTION: GPS modules mount mag chips component-side-down
   // This means:
   //   - Pins point UP (toward antenna)
   //   - Z+ points DOWN (into aircraft body)
   //   - Z- points UP (toward sky)

   // Validate this by:
   // 1. Checking if detected "up" axis has polarity matching assumption
   // 2. If not, assume unusual mounting (chip on same side as antenna)
   ```

### IST8310 (Non-Standard) ⚠️

**Special handling required:**

```javascript
function detectMagOrientation(chip_type, readings) {
    if (chip_type === MAG_IST8310) {
        // IST8310 uses LEFT-HAND RULE
        // Y-axis is reversed relative to standard chips

        // After standard detection:
        // 1. Find pitch, forward, up axes normally
        // 2. FLIP Y-axis polarity
        //    If Y+ detected, actually means Y-
        //    If Y- detected, actually means Y+

        // OR: Detect normally, then apply firmware axis remapping
        console.warn("IST8310 requires axis remapping - Y-axis non-standard");
        return detectIST8310Orientation(readings);
    } else {
        return detectStandardMagOrientation(readings);
    }
}
```

**Why this matters:**
- Standard min/max delta algorithm will work for X and Z
- But Y-axis interpretation must be **reversed**
- Firmware already has IST8310-specific code to handle this
- Wizard must account for it too

---

## Validation Strategy

### Option 1: Use GPS Position (If Available)

**If GPS has fix:**
```javascript
if (GPS.numSat >= 6 && GPS.fixType >= 2) {
    // Calculate expected magnetic inclination
    const inclination = calculateInclination(GPS.lat, GPS.lon);

    // Use inclination to determine up/down axis
    // Northern hemisphere: Field points DOWN
    // Southern hemisphere: Field points UP

    if (Math.abs(inclination) > 10°) {
        // Reliable detection possible
        up_axis = detectFromInclination(flat_reading, inclination);
        confidence = "HIGH";
    } else {
        // Near equator - unreliable
        up_axis = applyPinsUpAssumption(chip_type);
        confidence = "LOW - near magnetic equator";
    }
}
```

### Option 2: Pins-Up Assumption (No GPS)

```javascript
else {
    // No GPS fix - use assumption
    // ASSUMPTION: GPS modules mount mag component-side-down (pins-up)

    const pinsUpConvention = {
        MAG_QMC5883: { zPlusTowardPins: false },  // Z+ toward component markings
        MAG_HMC5883: { zPlusTowardPins: false },  // Z+ toward component markings
        MAG_IST8310: { zPlusTowardPins: false },  // Z+ toward component markings (but Y is reversed!)
        MAG_MAG3110: { zPlusTowardPins: false },  // Z+ toward component markings
        MAG_LIS3MDL: { zPlusTowardPins: false },  // Z+ toward component markings (assumed)
    };

    // If chip is mounted pins-up (toward antenna):
    //   Z+ points DOWN (into aircraft)
    //   Z- points UP (toward sky)

    // Measure which axis is vertical
    vertical_axis = detectVerticalAxis(flat_reading);

    // Apply convention
    if (pinsUpConvention[chip_type].zPlusTowardPins === false) {
        // Z+ points to component side
        // Component side is DOWN (pins UP)
        // Therefore Z+ is DOWN, Z- is UP
        up_axis_polarity = negative;  // Z- is UP
    }

    confidence = "MEDIUM - assumed pins-up mounting";
}
```

### Option 3: Validation Roll (Confirm Assumption)

```javascript
function validateUpDownAxis(flat_reading, detected_axes) {
    // Ask user to roll 90° clockwise
    console.log("Rotate aircraft 90° clockwise (right wing down)");

    // Wait for reading
    roll_90_reading = waitForStableReading();

    // Expected reading based on detected axes
    expected = rotateReading(flat_reading, detected_axes, roll=90°);

    // Compare
    if (readingsMatch(roll_90_reading, expected, tolerance=20%)) {
        return { validated: true, confidence: "HIGH" };
    }

    // Try flipping up/down axis
    flipped_axes = {...detected_axes, up_polarity: -detected_axes.up_polarity};
    expected_flipped = rotateReading(flat_reading, flipped_axes, roll=90°);

    if (readingsMatch(roll_90_reading, expected_flipped, tolerance=20%)) {
        console.log("Up/down axis was reversed - correcting");
        return { validated: true, corrected: true, axes: flipped_axes };
    }

    return { validated: false, confidence: "LOW - manual check needed" };
}
```

---

## Recommended Implementation

### Phase 1: Basic Detection

1. **Detect forward and pitch axes** (min/max delta) - Always reliable
2. **For accelerometer:** Use gravity for up/down (trivial)
3. **For magnetometer:**
   - If GPS fix available → use inclination
   - If no GPS → assume pins-up, provide "Flip Up/Down" button

### Phase 2: Chip-Specific Handling

1. **Detect which mag chip** is installed
2. **Apply chip-specific logic:**
   - Standard chips: Use standard algorithm
   - IST8310: Apply Y-axis reversal
3. **Validate with** known GPS module patterns:
   - Matek M8Q/M9N → expect CW 270° Flip
   - If detected alignment matches known pattern → high confidence

### Phase 3: Validation Roll

1. **Optional advanced feature**
2. Ask user to roll 90°
3. Validate detected orientation
4. Auto-correct if up/down flipped

---

## Key Takeaways

1. ✅ **Most mag chips use same Z-axis convention** - Z+ points from component side
2. ⚠️ **IST8310 is special** - needs Y-axis reversal due to left-hand rule
3. ✅ **GPS modules likely mount chips upside-down** - Matek's CW 270° Flip confirms this
4. ✅ **Pins-up assumption is sound** - matches typical GPS module construction
5. ✅ **Algorithm is viable** - with chip-specific handling and validation

---

## Sources

### Chip Datasheets
- [QMC5883L Datasheet (QST)](https://qstcorp.com/upload/pdf/202202/13-52-04%20QMC5883L%20Datasheet%20Rev.%20A(1).pdf)
- [HMC5883L Datasheet (Adafruit)](https://cdn-shop.adafruit.com/datasheets/HMC5883L_3-Axis_Digital_Compass_IC.pdf)
- [IST8310 Datasheet (Isentek)](https://isentek.com/userfiles/files/IST8310Datasheet_3DMagneticSensors.pdf)
- [MAG3110 Datasheet (SparkFun)](https://cdn.sparkfun.com/datasheets/Sensors/Magneto/MAG3110.pdf)

### GPS Modules
- [Matek M8Q-5883](https://www.mateksys.com/?portfolio=m8q-5883)
- [Matek M9N-5883](https://www.mateksys.com/?portfolio=m9n-5883)
- [Beitian BN-880](https://www.flyingtech.co.uk/electronics/beitian-bn-880-gps-compass-module-inav-betaflight)

### Technical Guides
- [Betaflight Magnetometer Guide](https://www.betaflight.com/docs/wiki/guides/current/Magnetometer)
- [How to Setup Magnetometer on Arduino](https://www.circuitbasics.com/how-to-setup-a-magnetometer-on-the-arduino/)
- [Adafruit LIS3MDL Guide](https://learn.adafruit.com/lis3mdl-triple-axis-magnetometer)

### Issues/Forums
- [Betaflight Issue #13678 - IST8310 orientation](https://github.com/betaflight/betaflight/issues/13678)
- [INAV Issue #4524 - IST8310 compass](https://github.com/iNavFlight/inav/issues/4524)
- [Matek M8Q GPS Orientation Discussion](https://intofpv.com/t-matek-m8q-gps-orientation-in-betaflight)
