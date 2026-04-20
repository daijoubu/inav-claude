# Magnetometer Alignment Detection Using Tilt Maneuver

**Date:** 2026-01-21
**Status:** Concept / Proposed Enhancement

## The Idea

Extend the alignment wizard to detect **magnetometer orientation** using the same physical principle already used for the accelerometer: observing apparent rotation of a fixed field during a tilt maneuver.

## Current Implementation (Accelerometer Only)

The alignment wizard currently determines **accelerometer orientation**:

1. User raises nose ~45 degrees
2. Read accelerometer before and after tilt
3. Observe how gravity field appears to rotate in sensor frame
4. Axis showing field "rotating upward" = axis that went up = nose direction
5. Use absolute gravity direction (always down) to resolve upside-down ambiguity

**Result:** Knows accelerometer's orientation relative to aircraft

## Proposed Addition (Magnetometer Too)

Use the **same tilt maneuver** to determine **magnetometer orientation**:

1. During the same nose-raise maneuver, also read magnetometer
2. Read magnetometer before tilt: `[Mx, My, Mz]`
3. Read magnetometer after tilt: `[Mx', My', Mz']`
4. Observe how magnetic field appears to rotate in sensor frame
5. Axis showing field "rotating downward" = axis that went up = nose direction
6. Use magnetic inclination (dip angle) to resolve upside-down ambiguity

**Result:** Knows magnetometer's orientation relative to aircraft

## Key Insight: Same Physics, Different Sensors

**They are NOT cross-validating each other.** They are two separate sensors, potentially in completely different orientations, each being measured independently using the same technique:

- **Accelerometer:** Might be mounted X+ forward, right-side up
- **Magnetometer:** Might be mounted Y- forward, upside down (on external GPS module)

Both orientations are determined correctly using the same tilt maneuver.

## The Star Field Camera Analogy

Imagine two cameras mounted on different sides of a vehicle, each pointing in different directions:

1. Vehicle tilts upward
2. Camera 1: Stars appear to move down in its view → Camera 1 is tilted up
3. Camera 2: Stars appear to move left in its view → Camera 2's left edge is tilted up

Each camera independently observes the star field motion to determine its own orientation. They're not validating each other - they're just using the same technique.

**Same with sensors:**
- Accelerometer observes gravity field rotation → determines its own orientation
- Magnetometer observes magnetic field rotation → determines its own orientation

## Critical Physics Point

**Magnetic declination (horizontal angle to north) doesn't matter.**

The actual compass heading of the aircraft is irrelevant. What matters is:
- Before tilt: magnetic field is some vector in sensor frame
- After tilt: magnetic field is a rotated vector in sensor frame
- The apparent rotation tells us which axis moved

Just like with the star field - doesn't matter which stars you're looking at, only that you observe them move.

## Benefits of Adding Magnetometer Detection

1. **Automatic compass alignment:** Currently must be configured manually
2. **Handles external magnetometers:** Common on GPS modules with different mounting
3. **Reduces user error:** No manual orientation entry needed
4. **Complete sensor suite configuration:** Both IMU and compass in one wizard

## Resolving the Upside-Down Ambiguity

### Problem

For both sensors, we can detect which axis tilted (e.g., X-axis), but not the polarity:
- X+ forward, right-side up
- X- forward, upside-down

Both cases show the same apparent rotation during the tilt.

### Solution for Accelerometer

**Easy:** Use absolute gravity direction (always points down)
- If Z+ axis shows +1g in level position → Z+ points down → upside-down
- If Z- axis shows +1g in level position → Z- points down → right-side up

### Solution for Magnetometer

**Depends on location:** Use magnetic inclination (dip angle)

**Away from magnetic equator (most locations ~90% of users):**
- Earth's magnetic field has a vertical component (horizontal always points north)
- Northern Hemisphere: field points DOWN and NORTH (positive dip angle ~60-70° at mid-latitudes)
- Southern Hemisphere: field points UP and NORTH (negative dip angle ~-60-70° at mid-latitudes)
- Northern hemisphere: measure which axis shows downward field component → that's "down"
- Southern hemisphere: measure which axis shows upward field component → that's "up"
- **Result:** Can resolve upside-down ambiguity in both hemispheres

**Near magnetic equator (±10° magnetic latitude):**
- Magnetic field is nearly horizontal (dip angle ≈ 0°)
- No significant vertical component
- **Result:** Cannot resolve upside-down ambiguity with magnetometer alone
- Must use another method (manual entry, or default assumption)

### Configurator Access to Location/Inclination

**Magnetic declination/inclination availability:**

The configurator SOMETIMES knows the location:
- ✅ **Available:** When GPS reports valid position
- ❌ **Not available:**
  - Indoor testing without GPS lock
  - No GPS module installed
  - GPS hasn't acquired fix yet

**Options:**
1. Use GPS position to calculate expected inclination
2. Measure inclination directly from static magnetometer reading
3. Allow manual location entry
4. Default assumption (right-side up) when inclination unavailable

## Edge Cases

### 1. No Magnetometer Installed
- Skip magnetometer alignment
- Only configure accelerometer
- Works exactly like current implementation

### 2. Near Magnetic Equator
- Can determine which axis is forward
- Cannot determine upside-down vs right-side up from mag alone
- Could use default assumption or require manual confirmation

### 3. Strong Magnetic Interference
- Magnetic field readings may be distorted
- Detection may fail or give incorrect results
- Wizard should detect anomalous readings and warn user
- Recommend moving away from metal/motors/magnets

### 4. Tilt Parallel to Magnetic Field Vector
- Minimal apparent rotation observed
- Similar to accelerometer issue when tilt perpendicular to gravity
- Unlikely with typical mounting and 45° nose-up tilt
- Could ask user to perform a second tilt (roll instead of pitch)

## Implementation Outline

### Phase 1: Add Magnetometer Reading
1. Read magnetometer before and after tilt
2. Calculate which axis shows apparent field rotation
3. Determine forward-pointing axis
4. Display magnetometer alignment result

### Phase 2: Resolve Upside-Down Ambiguity
1. Determine if GPS position is available
2. Calculate expected magnetic inclination from position
3. Alternatively: measure inclination from static reading
4. Use inclination to resolve upside-down orientation
5. Handle equatorial edge case

### Phase 3: Error Detection and User Feedback
1. Detect anomalous readings (interference)
2. Warn user when confidence is low
3. Provide troubleshooting guidance
4. Allow manual override if needed

## Algorithm Outline

```
1. Pre-tilt reading:
   - accel_before = [Ax, Ay, Az]
   - mag_before = [Mx, My, Mz]

2. User raises nose ~45°

3. Post-tilt reading:
   - accel_after = [Ax', Ay', Az']
   - mag_after = [Mx', My', Mz']

4. Determine ACCELEROMETER orientation:
   - accel_delta = accel_after - accel_before
   - accel_nose_axis = axis with largest positive delta (most upward)
   - accel_up_axis = axis showing ~1g in level position
   - Result: "Accelerometer: X+ forward, Z- up"

5. Determine MAGNETOMETER orientation:
   - mag_rotation = compute_apparent_rotation(mag_before, mag_after)
   - mag_nose_axis = axis showing "downward" field rotation
   - mag_up_axis = axis showing downward magnetic field component (if detectable)
   - Result: "Magnetometer: Y- forward, X+ up"

6. Apply separate alignment settings:
   - Set FC alignment based on accelerometer orientation
   - Set compass alignment based on magnetometer orientation
   - These are INDEPENDENT settings, may be completely different

7. Display results to user:
   - "Flight Controller (IMU) alignment: CW270_DEG"
   - "Compass alignment: CW180_DEG_FLIP"
```

## Example Scenarios

### Scenario 1: FC and Mag Both Standard Mounting
- Accelerometer: X+ forward, Z- up → No rotation needed
- Magnetometer: X+ forward, Z- up → No rotation needed
- Both aligned the same way

### Scenario 2: FC Standard, External GPS/Mag Rotated
- Accelerometer: X+ forward, Z- up → No rotation needed
- Magnetometer: Y+ forward, Z- up → Need 90° CW rotation
- Different alignments, both correctly detected

### Scenario 3: FC Rotated, No Magnetometer
- Accelerometer: Y- forward, Z- up → Need 90° CCW rotation
- Magnetometer: Not installed → Skip magnetometer alignment
- Only FC alignment configured

## Next Steps When Resuming Project

1. Review existing PR #2158 implementation
2. Examine current accelerometer detection algorithm
3. Check what magnetometer data is currently available in wizard
4. Assess GPS position availability during alignment
5. Design UI to display both sensor orientations
6. Implement magnetometer detection algorithm
7. Add inclination-based upside-down resolution
8. Test with various mounting configurations

## References

- **PR #2158:** https://github.com/iNavFlight/inav-configurator/pull/2158
- **Project:** `claude/projects/backburner/feature-auto-alignment-tool/`
- **Discussion date:** 2026-01-21
- **Key principle:** Same physics (observing fixed field rotation), different sensors, independent measurements
