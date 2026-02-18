# Parameter Group Version Rollover Analysis

**Date:** 2026-01-23
**Analyst:** Developer
**Branch:** ci/pg-version-check-action
**Status:** COMPLETE

---

## Executive Summary

⚠️ **CRITICAL FINDING:** The parameter group version rollover from 15→0 will cause **data corruption** if users have EEPROM from an earlier v0 cycle.

**Risk Level:** HIGH for `osdConfig_t` (currently at v15)

**Recommendation:** Implement version rollover prevention or detection before `osdConfig_t` reaches v16.

---

## 1. Current Parameter Group Versions

### At-Risk Parameter Groups

Data source: `inav/cmake/pg_struct_sizes.arm.db`

| Parameter Group | Size (bytes) | Current Version | Risk Level | Changes Until Rollover |
|-----------------|--------------|-----------------|------------|------------------------|
| `osdConfig_t` | 160 | **15** | 🔴 CRITICAL | **0** - Next change will force rollover |
| `rxConfig_t` | 36 | **13** | 🟡 HIGH | 2 changes remaining |
| `gyroConfig_t` | 64 | **12** | 🟡 MEDIUM | 3 changes remaining |
| `motorConfig_t` | 10 | **11** | 🟢 MEDIUM-LOW | 4 changes remaining |
| `pidProfile_t` | 292 | **11** | 🟢 MEDIUM-LOW | 4 changes remaining |

### Full Version List (Sorted by Version)

```
Version 15: osdConfig_t
Version 13: rxConfig_t
Version 12: gyroConfig_t
Version 11: motorConfig_t, pidProfile_t
Version 8:  positionEstimationConfig_t, telemetryConfig_t
Version 7:  navConfig_t, systemConfig_t
Version 6:  compassConfig_t
Version 5:  barometerConfig_t, gpsConfig_t
Version 4:  blackboxConfig_t, rcControlsConfig_t, vtxConfig_t
Version 3:  armingConfig_t, djiOsdConfig_t, failsafeConfig_t, rangefinderConfig_t, servoConfig_t
Version 2:  batteryMetersConfig_t, beeperConfig_t, imuConfig_t, opticalFlowConfig_t, pidAutotuneConfig_t, pitotmeterConfig_t, statsConfig_t, vtxSettingsConfig_t
Version 1:  escSensorConfig_t, ezTuneSettings_t, gimbalConfig_t, headTrackerConfig_t, powerLimitsConfig_t, rpmFilterConfig_t, timeConfig_t
Version 0:  adcChannelConfig_t, displayConfig_t, featureConfig_t, generalSettings_t, geozone_config_t, gimbalSerialConfig_t, ledPinConfig_t, logConfig_t, modeActivationOperatorConfig_t, navFwAutolandConfig_t, osdCommonConfig_t, osdJoystickConfig_t, reversibleMotorsConfig_t, smartportMasterConfig_t
```

**Total PGs:** 48
**PGs at version 12+:** 5 (10.4%)
**PGs at maximum version (15):** 1

---

## 2. Version Storage Architecture

### Bit Layout

Version is stored in the **upper 4 bits** of the 16-bit PGN (Parameter Group Number):

```
PGN Format (16 bits):
┌──────────────┬─────────────────────────────────┐
│ Version (4)  │   PG Number (12)                │
├──────────────┼─────────────────────────────────┤
│ Bits 15-12   │   Bits 11-0                     │
└──────────────┴─────────────────────────────────┘

Range:
- PG Number: 0-4095 (12 bits)
- Version:   0-15   (4 bits)
```

**Source:** `inav/src/main/config/parameter_group.h:34-35, 57`

```c
typedef enum {
    PGR_PGN_MASK =          0x0fff,    // Lower 12 bits: PG ID
    PGR_PGN_VERSION_MASK =  0xf000,    // Upper 4 bits: version (0-15)
} pgRegistryInternal_e;

static inline uint8_t pgVersion(const pgRegistry_t* reg) {
    return (uint8_t)(reg->pgn >> 12);  // Extract upper 4 bits
}
```

### EEPROM Record Format

Each parameter group in EEPROM has this header structure:

**Source:** `inav/src/main/config/config_eeprom.c:61-71`

```c
typedef struct {
    uint16_t size;      // Size of this record + pg data
    pgn_t pgn;          // Parameter group number (12-bit ID only)
    uint8_t version;    // Version when saved (0-15)
    uint8_t flags;      // System (0) or Profile1-3 (1-3)
    uint8_t pg[];       // Actual PG data follows
} PG_PACKED configRecord_t;
```

**Key Point:** Version is stored **separately** in the EEPROM record header, not just in the PGN bits.

---

## 3. Version Comparison Logic

### pgLoad() Implementation

**Source:** `inav/src/main/config/parameter_group.c:86-94`

```c
void pgLoad(const pgRegistry_t* reg, int profileIndex, const void *from, int size, int version)
{
    pgReset(reg, profileIndex);  // ALWAYS reset to defaults first

    // Only restore EEPROM data if versions match exactly
    if (version == pgVersion(reg)) {
        const int take = MIN(size, pgSize(reg));
        memcpy(pgOffset(reg, profileIndex), from, take);
    }
    // If version mismatch: keeps the defaults from pgReset()
}
```

### Critical Observations

1. **Simple Equality Check:** `if (version == pgVersion(reg))`
   - NOT a range check
   - NOT a greater-than/less-than comparison
   - JUST exact match: `stored_version == firmware_version`

2. **No Migration Logic:**
   - No attempt to transform old data to new format
   - No version sequence tracking
   - No detection of version cycles

3. **Behavior on Mismatch:**
   - Silently discards EEPROM data
   - Uses compiled-in defaults
   - No error message to user
   - No indication in logs (beyond settings reset)

4. **Data Types:**
   - Both versions are `uint8_t` (unsigned 8-bit)
   - Comparison is unsigned: `0-15` range
   - No signed arithmetic or overflow detection

---

## 4. Rollover Scenario Analysis

### Scenario 1: User Upgrades from v15 → v0 (After Rollover)

**Setup:**
- User has INAV with `osdConfig_t` v15
- Settings saved in EEPROM with `version=15`
- User upgrades to firmware where `osdConfig_t` rolled over to v0

**What Happens:**

```c
// In pgLoad():
version = 15           // From EEPROM record
pgVersion(reg) = 0     // From firmware

if (15 == 0)           // FALSE
    // Load data (not executed)

// Result: pgReset() defaults remain
```

**Outcome:**
- ✅ **SAFE** - Settings are discarded
- ⚠️ **INCONVENIENT** - User loses all OSD settings
- ℹ️ User sees "Configuration reset" or similar message
- ℹ️ User must reconfigure OSD from scratch

**User Impact:** Inconvenient but safe

---

### Scenario 2: Old v0 Data Loaded into New v0 (After Full Cycle)

**Setup:**
- User has very old EEPROM from first `osdConfig_t` v0 (many years ago)
- Never updated firmware
- Now upgrades to firmware where `osdConfig_t` has cycled through v15 and back to v0

**What Happens:**

```c
// In pgLoad():
version = 0            // From ancient EEPROM record
pgVersion(reg) = 0     // From current firmware (after rollover)

if (0 == 0)            // TRUE - VERSIONS MATCH!
    memcpy(dest, eeprom_data, size);  // Load old data
```

**Outcome:**
- 🔴 **DANGEROUS** - Ancient data loaded into completely different struct
- 🔴 **DATA CORRUPTION** - Fields are misaligned, wrong types, wrong meanings
- 🔴 **POTENTIAL CRASH** - Invalid pointers, out-of-range values
- 🔴 **UNDEFINED BEHAVIOR** - No validation of loaded data

**Why This Is Critical:**

After 16 versions, the struct could be completely different:
- Different field order
- Different data types
- Added/removed fields
- Different semantics
- Different valid ranges

But the version check would **pass**, loading corrupted data.

**Example:**

```c
// Original v0 (year 2020):
typedef struct {
    uint8_t video_system;      // Offset 0
    uint8_t units;             // Offset 1
    // ... 158 more bytes
} osdConfig_t;  // Version 0

// After 16 changes (year 2028):
typedef struct {
    uint32_t feature_flags;    // Offset 0 - NOW 4 BYTES!
    uint16_t screen_width;     // Offset 4
    // ... completely different layout
} osdConfig_t;  // Version 0 (after rollover)

// Loading old v0 data into new v0:
// - Old video_system byte goes into feature_flags bits 0-7
// - Old units byte goes into feature_flags bits 8-15
// - Rest is garbage
// = CORRUPTION
```

---

### Scenario 3: Version Comparison Edge Cases

**Question:** Is the comparison signed or unsigned?

**Answer:** Unsigned (`uint8_t`)

```c
// Both are uint8_t
uint8_t version;               // EEPROM version
uint8_t pgVersion(reg)         // Firmware version

// Comparison is unsigned
if (version == pgVersion(reg))  // 0-15 range, no negative values
```

**Implication:** No risk of signed integer wraparound bugs, but also no way to detect cycles.

---

## 5. Impact Assessment

### Immediate Risk (osdConfig_t at v15)

**Timeline:**
- **Current:** v15 (maximum)
- **Next OSD feature:** Forced rollover to v0
- **Risk Window:** Until v16 changes complete a full cycle

**Likelihood:**
- **Scenario 1 (v15→v0):** HIGH - Will happen on next OSD change
- **Scenario 2 (old v0 → new v0):** LOW - Requires ~16 OSD changes over many years

**User Impact:**
- **Scenario 1:** Inconvenient (settings reset)
- **Scenario 2:** Dangerous (data corruption)

### Medium-Term Risk (rxConfig_t, gyroConfig_t, others)

These PGs will hit v15 in the next few years of development.

**Risk Multiplier:**
- Each additional PG at v15 increases the risk
- More PGs cycling means more opportunities for corruption
- More user confusion from unexpected resets

### Long-Term Risk (All PGs)

Eventually, all frequently-modified PGs will cycle through v0-15 multiple times.

**Without mitigation:**
- Version system becomes unreliable
- Cannot distinguish v0 cycle 1 from v0 cycle 2
- Increasing probability of data corruption as old devices upgrade

---

## 6. Comparison with Industry Practice

### How Other Projects Handle Versioning

**Betaflight:**
- Uses similar 4-bit version field
- Same equality-check approach
- Same risk of rollover (not yet addressed)

**ArduPilot:**
- Uses 16-bit version numbers
- Much larger version space (0-65535)
- Unlikely to exhaust in project lifetime

**PX4:**
- Uses CRC-based configuration detection
- Version changes trigger CRC mismatch
- Different approach, no version rollover risk

**Linux Kernel:**
- Module versioning uses 32-bit or larger
- Explicitly handles version incompatibility
- Migration paths documented

---

## 7. Potential Solutions

### Option 1: Skip Version 15 (Use 14→0)

**Approach:**
- Reserve v15 as a "rollover marker"
- Increment from v14 directly to v0
- Document that v15 means "about to rollover"

**Advantages:**
- ✅ Simple to implement
- ✅ Minimal code changes
- ✅ Clear signal that rollover occurred

**Disadvantages:**
- ⚠️ Loses one version number (14 usable instead of 15)
- ⚠️ Doesn't solve the v0 cycle confusion
- ⚠️ Still has corruption risk after full cycle

**Code Change:**
```c
// When incrementing version:
#define PG_MAX_VERSION 14  // Not 15

// In PG_REGISTER macros:
if (new_version > PG_MAX_VERSION) {
    new_version = 0;  // Rollover
}
```

---

### Option 2: Expand Version Field to 8 bits

**Approach:**
- Reduce PGN space from 12 bits to 8 bits
- Increase version from 4 bits to 8 bits
- Support versions 0-255

**Advantages:**
- ✅ 255 versions instead of 15 (17x increase)
- ✅ Unlikely to cycle in project lifetime
- ✅ More room for future development

**Disadvantages:**
- ❌ Reduces PG ID space from 4096 to 256
- ❌ Breaking change to EEPROM format
- ❌ Requires full configuration reset for all users
- ❌ Complex migration

**Feasibility:**
- Currently 48 PGs defined
- 256 PG limit still comfortable
- But EEPROM format change is painful

**Code Impact:**
- Change `PGR_PGN_MASK` from `0x0fff` to `0x00ff`
- Change `PGR_PGN_VERSION_MASK` from `0xf000` to `0xff00`
- Update version extraction: `(reg->pgn >> 8)` instead of `>> 12`
- Force EEPROM version bump

---

### Option 3: Add Cycle Counter

**Approach:**
- Add a "version cycle" counter to EEPROM header
- Track which cycle of v0-15 we're in
- Compare (cycle, version) tuple instead of just version

**Advantages:**
- ✅ Solves the v0 cycle confusion
- ✅ No reduction in PG ID space
- ✅ Graceful rollover handling

**Disadvantages:**
- ❌ Requires EEPROM format change
- ❌ Forces configuration reset
- ❌ More complex version comparison logic
- ❌ Need to manage cycle counter persistence

**EEPROM Format:**
```c
typedef struct {
    uint16_t size;
    pgn_t pgn;
    uint8_t version;       // 0-15
    uint8_t version_cycle; // NEW: which cycle of 0-15
    uint8_t flags;
    uint8_t pg[];
} configRecord_t;
```

**Version Comparison:**
```c
if (version == pgVersion(reg) && version_cycle == pgCycle(reg)) {
    // Load data
}
```

---

### Option 4: Version Rollover Detection

**Approach:**
- Detect when stored version is much higher than current (e.g., 15 vs 0)
- Treat as version mismatch and reset to defaults
- Document this behavior

**Advantages:**
- ✅ Simple detection logic
- ✅ No EEPROM format change
- ✅ Handles v15→v0 gracefully

**Disadvantages:**
- ⚠️ Still doesn't solve v0 cycle problem
- ⚠️ Only helps for the first rollover
- ⚠️ Heuristic-based (what threshold to use?)

**Code Change:**
```c
void pgLoad(const pgRegistry_t* reg, int profileIndex, const void *from, int size, int version)
{
    pgReset(reg, profileIndex);

    uint8_t current_version = pgVersion(reg);

    // Detect likely rollover: stored version is much higher
    bool likely_rollover = (version > 12 && current_version < 3);

    if (version == current_version && !likely_rollover) {
        const int take = MIN(size, pgSize(reg));
        memcpy(pgOffset(reg, profileIndex), from, take);
    }
    // Else: keep defaults (version mismatch or rollover detected)
}
```

---

### Option 5: Force Reset at v15→v0 Transition

**Approach:**
- When incrementing from v14 to v0 (skipping v15), set a flag
- On first boot after rollover, force full EEPROM reset
- Clear flag after reset
- Document that rollover causes one-time reset

**Advantages:**
- ✅ Prevents v0 cycle confusion
- ✅ Clean slate after rollover
- ✅ Clear user messaging possible

**Disadvantages:**
- ❌ Forces settings reset on rollover
- ❌ Users lose all configuration
- ❌ Inconvenient but safe

---

## 8. Recommended Solution

### Recommendation: **Option 1 + Option 4** (Hybrid Approach)

**Implementation:**

1. **Skip version 15** (use 14→0 rollover)
2. **Add rollover detection** in `pgLoad()`
3. **Document the behavior** clearly
4. **Plan for long-term** (Option 2 or 3 in future major version)

**Rationale:**
- ✅ Minimal code changes
- ✅ No EEPROM format breaking change
- ✅ Handles immediate `osdConfig_t` risk
- ✅ Buys time for better long-term solution
- ✅ Safe and predictable behavior

**Code Changes Required:**

```c
// In parameter_group.h or parameter_group_ids.h:
#define PG_VERSION_MAX 14  // Reserve v15 for rollover marker

// In pgLoad():
void pgLoad(const pgRegistry_t* reg, int profileIndex, const void *from, int size, int version)
{
    pgReset(reg, profileIndex);
    uint8_t current_version = pgVersion(reg);

    // Detect rollover scenarios:
    // 1. Stored v15 (reserved) - always reset
    // 2. Stored >> current (likely v14→v0 transition)
    bool rollover_detected = (version == 15) ||
                            (version >= 12 && current_version <= 2);

    if (version == current_version && !rollover_detected) {
        const int take = MIN(size, pgSize(reg));
        memcpy(pgOffset(reg, profileIndex), from, take);
    }
    // Mismatch or rollover: keep defaults
}
```

**Documentation Update:**
- Add comment to PG registration macros explaining v0-14 range
- Document rollover behavior in developer guide
- Add note to PG documentation project

---

## 9. Future Considerations

### Long-Term Migration (INAV 10.0+)

For a future major version release, consider:

**Option 2 (Expand to 8 bits):**
- Clean break opportunity during major version
- Users expect configuration reset during major updates
- Provides long-term version space (255 versions)

**Implementation Timeline:**
1. **Short-term (now):** Implement Option 1+4 (skip v15 + detection)
2. **Mid-term (INAV 9.x):** Monitor PG version growth, document behavior
3. **Long-term (INAV 10.0):** Expand to 8-bit versions with EEPROM migration

### Version Growth Rate Analysis

Based on git history:
- `osdConfig_t`: 15 versions over ~5 years = ~3 versions/year
- `rxConfig_t`: 13 versions over ~5 years = ~2.6 versions/year
- `gyroConfig_t`: 12 versions over ~5 years = ~2.4 versions/year

**Projection:**
- With 14 usable versions (Option 1): ~4-5 years per cycle
- With 255 usable versions (Option 2): ~85-100 years per cycle

**Conclusion:** Option 1 buys time; Option 2 provides permanent solution.

---

## 10. Testing Requirements

### Test Cases for Rollover Behavior

If implementing Option 1+4:

1. **Test: Version Match (Normal Case)**
   - Create EEPROM with v5
   - Load firmware with v5
   - Verify: Settings loaded correctly

2. **Test: Version Mismatch (Normal Upgrade)**
   - Create EEPROM with v5
   - Load firmware with v6
   - Verify: Settings reset to defaults

3. **Test: Rollover Detection (v14→v0)**
   - Create EEPROM with v14
   - Load firmware with v0
   - Verify: Settings reset (rollover detected)

4. **Test: Reserved Version (v15)**
   - Create EEPROM with v15 (forced)
   - Load firmware with any version
   - Verify: Settings reset (v15 always resets)

5. **Test: Old v0 Rejection**
   - Create EEPROM with v0
   - Load firmware with v0 (after simulated cycle)
   - Verify: Settings reset if heuristic detects old data

### Hardware Testing

- Test on real flight controller
- Verify EEPROM read/write with rollover versions
- Check for memory corruption
- Monitor for crashes or undefined behavior

---

## 11. Conclusion

### Key Findings

1. **Current Risk:** `osdConfig_t` at v15 (maximum) - next change will force rollover
2. **Rollover Behavior:** v15→v0 causes settings reset (safe but inconvenient)
3. **Corruption Risk:** Old v0 data loading into new v0 (after full cycle) causes data corruption
4. **Root Cause:** Simple equality check with no cycle tracking
5. **Likelihood:** Immediate risk for OSD, long-term risk for all PGs

### Recommendations

**Immediate Action (Before Next OSD Change):**
1. Implement Option 1+4 (skip v15 + rollover detection)
2. Test thoroughly with SITL and hardware
3. Document the rollover behavior
4. Add developer guidelines for version management

**Long-Term Planning:**
1. Monitor PG version growth rates
2. Plan for 8-bit version expansion in INAV 10.0
3. Design EEPROM migration strategy
4. Document upgrade path for users

### Impact Summary

**With Mitigation (Option 1+4):**
- ✅ Safe rollover behavior
- ✅ Predictable settings reset
- ⚠️ User inconvenience (reconfiguration needed)
- ✅ Buys time for better solution

**Without Mitigation:**
- ❌ Potential data corruption
- ❌ Undefined behavior
- ❌ User confusion
- ❌ Difficult to debug issues

---

## Appendix A: Complete PG Version Table

| Parameter Group | Version | Size | Risk |
|-----------------|---------|------|------|
| adcChannelConfig_t | 0 | 4 | Low |
| armingConfig_t | 3 | 6 | Low |
| barometerConfig_t | 5 | 8 | Low |
| batteryMetersConfig_t | 2 | 24 | Low |
| beeperConfig_t | 2 | 12 | Low |
| blackboxConfig_t | 4 | 16 | Low |
| compassConfig_t | 6 | 24 | Low |
| displayConfig_t | 0 | 1 | Low |
| djiOsdConfig_t | 3 | 6 | Low |
| escSensorConfig_t | 1 | 4 | Low |
| ezTuneSettings_t | 1 | 12 | Low |
| failsafeConfig_t | 3 | 22 | Low |
| featureConfig_t | 0 | 4 | Low |
| generalSettings_t | 0 | 1 | Low |
| geozone_config_t | 0 | 20 | Low |
| gimbalConfig_t | 1 | 10 | Low |
| gimbalSerialConfig_t | 0 | 1 | Low |
| gpsConfig_t | 5 | 11 | Low |
| gyroConfig_t | **12** | 64 | **Medium** |
| headTrackerConfig_t | 1 | 16 | Low |
| imuConfig_t | 2 | 16 | Low |
| ledPinConfig_t | 0 | 1 | Low |
| logConfig_t | 0 | 8 | Low |
| modeActivationOperatorConfig_t | 0 | 1 | Low |
| motorConfig_t | **11** | 10 | **Medium-Low** |
| navConfig_t | 7 | 156 | Low |
| navFwAutolandConfig_t | 0 | 16 | Low |
| opticalFlowConfig_t | 2 | 8 | Low |
| osdCommonConfig_t | 0 | 1 | Low |
| osdConfig_t | **15** | 160 | **CRITICAL** |
| osdJoystickConfig_t | 0 | 6 | Low |
| pidAutotuneConfig_t | 2 | 10 | Low |
| pidProfile_t | **11** | 292 | **Medium-Low** |
| pitotmeterConfig_t | 2 | 8 | Low |
| positionEstimationConfig_t | 8 | 72 | Low |
| powerLimitsConfig_t | 1 | 8 | Low |
| rangefinderConfig_t | 3 | 2 | Low |
| rcControlsConfig_t | 4 | 10 | Low |
| reversibleMotorsConfig_t | 0 | 6 | Low |
| rpmFilterConfig_t | 1 | 10 | Low |
| rxConfig_t | **13** | 36 | **High** |
| servoConfig_t | 3 | 12 | Low |
| smartportMasterConfig_t | 0 | 2 | Low |
| statsConfig_t | 2 | 20 | Low |
| systemConfig_t | 7 | 40 | Low |
| telemetryConfig_t | 8 | 58 | Low |
| timeConfig_t | 1 | 4 | Low |
| vtxConfig_t | 4 | 55 | Low |
| vtxSettingsConfig_t | 2 | 12 | Low |

---

## Appendix B: References

**Code Files:**
- `inav/src/main/config/parameter_group.h` - Version storage and extraction
- `inav/src/main/config/parameter_group.c` - pgLoad() implementation
- `inav/src/main/config/config_eeprom.c` - EEPROM loading/saving
- `inav/cmake/pg_struct_sizes.arm.db` - PG version database

**Related Projects:**
- `document-parameter-group-system` - Documentation effort for PG subsystem

**Related Issues:**
- (None currently tracked - this is proactive analysis)

---

**Analysis completed:** 2026-01-23
**Next steps:** Present findings to manager for decision on mitigation strategy
