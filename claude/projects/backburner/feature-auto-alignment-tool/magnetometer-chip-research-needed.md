# Magnetometer Chip Orientation Research

**Date:** 2026-01-21
**Status:** Research Required
**Question:** Do all magnetometer chips used by INAV follow the same physical mounting convention?

## Context

For the auto-alignment tool to correctly detect magnetometer upside-down orientation, we need to understand:

1. **Chip-level convention:** Which chip axis corresponds to "Z" (perpendicular to chip surface)?
2. **Mounting convention:** Are chips consistently mounted component-side-up or component-side-down on GPS modules?
3. **Datasheet conventions:** Do all datasheets define Z+ as pointing toward the component markings or toward the pins/pads?

## INAV Supported Magnetometers

Based on `inav/src/main/sensors/compass.h` and driver files:

| Chip | Driver File | Common Use Case |
|------|-------------|-----------------|
| **QMC5883L** | `compass_qmc5883l.c` | Very common on GPS modules |
| **QMC5883P** | (variant of QMC5883L) | Newer variant |
| **HMC5883L** | `compass_hmc5883l.c` | Common on older GPS modules |
| **AK8975** | `compass_ak8975.c` | Standalone or GPS |
| **AK8963** | `compass_ak8963.c` | In MPU9250 IMU |
| **MAG3110** | `compass_mag3110.c` | Freescale/NXP |
| **IST8310** | `compass_ist8310.c` | Common on GPS modules |
| **IST8308** | `compass_ist8308.c` | Newer IST variant |
| **LIS3MDL** | `compass_lis3mdl.c` | ST Microelectronics |
| **RM3100** | `compass_rm3100.c` | High precision |
| **VCM5883** | `compass_vcm5883l.c` | Variant of HMC5883L |
| **MLX90393** | `compass_mlx90393.c` | Melexis |
| **MPU9250** | (integrated with gyro) | Combo IMU+mag |

## Research Tasks

### Phase 1: Datasheet Review

For each chip, obtain datasheet and document:

- [ ] **QMC5883L**
  - Datasheet link
  - Z-axis definition (toward component or toward pins?)
  - Typical package (QFN, LGA, etc.)
  - Right-hand rule verification

- [ ] **HMC5883L**
  - Datasheet link
  - Z-axis definition
  - Package type
  - Axis marking on chip

- [ ] **IST8310**
  - Datasheet link
  - Z-axis definition
  - Package type
  - Axis orientation

- [ ] **LIS3MDL**
  - Datasheet link
  - Z-axis definition
  - Package type
  - ST's convention

- [ ] **AK8963**
  - Datasheet link
  - Z-axis definition
  - How it's oriented in MPU9250

- [ ] Other chips (as needed)

### Phase 2: GPS Module Survey

Check common GPS modules used with INAV:

- [ ] **Ublox M8N/M9N GPS modules**
  - Which mag chip is used?
  - How is chip mounted (component side up/down)?
  - Any module schematics available?

- [ ] **Beitian BN-880**
  - Mag chip model
  - Mounting orientation

- [ ] **Matek M8Q-5883**
  - Mag chip model
  - Mounting orientation

- [ ] **Other popular GPS/mag combos**

### Phase 3: Physical Inspection

If possible, examine actual GPS modules:

- [ ] Take photos of chip mounting
- [ ] Identify component markings
- [ ] Verify which side faces up/down
- [ ] Check if PCB has antenna on top

### Phase 4: Code Analysis

Check if INAV has any hardcoded orientation assumptions:

- [ ] Review `inav/src/main/sensors/compass.c`
- [ ] Check for any axis transformations
- [ ] Look for per-chip orientation quirks
- [ ] Review alignment calculation code

## Key Questions

1. **Is there industry-standard convention?**
   - Do most 3-axis magnetometer chips follow right-hand rule with Z+ toward component markings?
   - Or is it inconsistent between manufacturers?

2. **GPS module mounting pattern:**
   - Are mag chips typically mounted component-side-down (pins up) to be under the antenna?
   - Or component-side-up with antenna on opposite side of PCB?

3. **Does INAV already handle this?**
   - Are there per-chip axis remappings in the drivers?
   - Does alignment setting compensate for different chip conventions?

## Expected Findings

### Hypothesis 1: Consistent Convention
If all chips follow the same convention (e.g., Z+ toward component markings, component mounted face-down):
- **Result:** Auto-detection can use same logic for all chips
- **Implementation:** Simple upside-down detection based on magnetic inclination

### Hypothesis 2: Inconsistent Convention
If chips have different conventions:
- **Result:** Need per-chip orientation knowledge
- **Implementation:** Lookup table mapping chip type to Z-axis convention
- **Complexity:** Medium - add chip-specific logic

### Hypothesis 3: GPS Module Variation
If chip convention is consistent but GPS module mounting varies:
- **Result:** Cannot reliably auto-detect upside-down from mag alone
- **Implementation:** Must rely on user confirmation or default assumption
- **Complexity:** High - may need manual override option

## Fallback Approaches

If upside-down detection proves unreliable:

1. **Use accelerometer orientation as hint:**
   - If ACC is right-side-up, assume MAG is too (most cases)
   - Only external mags on rotated GPS modules would differ

2. **Require manual confirmation:**
   - Auto-detect forward direction (reliable)
   - Ask user to confirm up vs upside-down

3. **Default assumption:**
   - Assume standard mounting (component-side-down for external GPS)
   - Provide easy flip button if wrong

4. **Two-step wizard:**
   - First maneuver: Detect forward direction
   - Second maneuver: Roll 180° to detect up vs upside-down

## Resources

**Datasheets to find:**
- QMC5883L: QST Corporation
- HMC5883L: Honeywell (now TE Connectivity)
- IST8310: Isentek
- LIS3MDL: ST Microelectronics (readily available)
- AK8963: AKM Semiconductor
- MAG3110: NXP (formerly Freescale)

**Community resources:**
- INAV Discord - users with various GPS modules
- GitHub issues mentioning compass alignment
- RC Groups forum threads
- GPS module product pages with photos

## Next Steps When Resuming

1. Start with **QMC5883L** (most common) - find datasheet and verify Z-axis convention
2. Check **HMC5883L** (second most common) - compare convention
3. If first two match, check one more (IST8310 or LIS3MDL)
4. If conventions match, proceed with simple implementation
5. If conventions differ, design lookup table approach
6. Document findings in this file

## Related Documents

- `rotation-axis-detection-approach.md` - Main algorithm design
- `magnetometer-alignment-detection-idea.md` - Original concept
- `summary.md` - Project overview

---

**Status:** Awaiting datasheet research before implementation can proceed.
