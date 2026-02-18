# GPS Rate Optimization Research Summary

**Project:** Enable Galileo & Optimize GPS Rate
**Date:** 2026-01-16
**Status:** Research Complete, Ready for Implementation

---

## Research Documents

All detailed research documents are located in:
`claude/projects/active/enable-galileo-optimize-gps-rate/`

### Core Implementation Documents

1. **IMPLEMENTATION-PLAN-constellation-aware.md**
   - Complete implementation plan
   - Constellation-aware rate algorithm
   - Code changes required
   - Settings modifications

2. **jetrell-testing-data.md**
   - Field testing that validates the problem
   - M9/M10 testing with 4 constellations
   - Shows 10Hz causes issues, 6Hz works well

### Hardware Analysis

3. **m9-channel-limitation-analysis.md**
   - M9 has hardware limit: 16 satellites at ≥10Hz
   - Not configurable - it's a processing constraint
   - Recommendation: Keep M9 at 10Hz (current default)

4. **cturvey-implementation-analysis.md**
   - Expert code review from u-blox specialist
   - OTP programming patterns
   - M9 channel configuration
   - Safe implementation approaches

### Advanced Topics

5. **adaptive-gps-rate-analysis.md**
   - Speed-based dynamic rate adjustment analysis
   - Error budget comparison (temporal lag vs HDOP)
   - **CRITICAL:** INAV's predictive positioning changes the math
   - Conclusion: Don't implement adaptive rates (not worth complexity)

---

## Key Findings

### The Problem (Jetrell's Testing)

**M10 with 4 constellations at 10Hz:**
- Wild HDOP fluctuations (2-5)
- Poor satellite tracking (13-17 sats)
- Unstable GPS performance

**M10 with 4 constellations at 6-9Hz:**
- Stable HDOP (1.3)
- +8-10 more satellites
- Excellent GPS performance

**Root Cause:** M10 default CPU clock mode has processing limits.

### M10 CPU Clock Modes (CRITICAL Discovery)

**Two modes exist:**

1. **Default Clock** (most M10 modules ship with this)
   - 4 constellations: 4-6 Hz max
   - 3 constellations: 6-8 Hz max
   - 2 constellations: 10 Hz max

2. **High-Performance Clock** (OTP programmed, rare)
   - 4 constellations: 10 Hz
   - 3 constellations: 12-16 Hz
   - 2 constellations: 20 Hz
   - **Permanent configuration** - cannot be changed at runtime
   - Requires specific OTP byte sequences

### M9 Behavior

**M9 at ≥10Hz:**
- Automatically limits to 16 satellites (hardware processing constraint)
- Cannot be overridden by configuration
- Trade-off: fast updates OR many satellites, not both

**Recommendation:** Keep M9 at 10Hz (current default is fine)

---

## Solution: Constellation-Aware Rates

### Algorithm

```c
static uint8_t calculateSafeGPSRate(void)
{
    int constellationCount = 1; // GPS always enabled

    if (gpsState.gpsConfig->ubloxUseGalileo) constellationCount++;
    if (gpsState.gpsConfig->ubloxUseGlonass) constellationCount++;
    if (gpsState.gpsConfig->ubloxUseBeidou) constellationCount++;

    if (gpsState.hwVersion >= UBX_HW_VERSION_UBLOX10) {
        // M10: Assume default CPU clock (most common)
        switch (constellationCount) {
            case 4: return 6;   // Conservative for 4 constellations
            case 3: return 8;   // Good balance for 3 constellations
            default: return 10; // Full speed for 1-2 constellations
        }
    } else if (gpsState.hwVersion >= UBX_HW_VERSION_UBLOX9) {
        return 10; // M9: Can handle 10Hz with all configurations
    }
    return 10; // M8 and earlier
}
```

### Changes Required

1. **inav/src/main/fc/settings.yaml**
   - `gps_ublox_use_galileo`: Change default from `OFF` to `ON`
   - `gps_ublox_nav_hz`: Change default from `10` to `0` (auto)

2. **inav/src/main/io/gps_ublox.c**
   - Add `calculateSafeGPSRate()` function
   - Modify `gpsConfigure()` to use auto rate when setting is 0

3. **Documentation**
   - Explain constellation-aware behavior
   - Document manual override option
   - Explain M10 clock modes

---

## Why NOT Adaptive Rates

### Initial Analysis Showed Promise

At 100 MPH:
- 10Hz: 4.5m temporal lag
- 5Hz: 9m temporal lag
- Difference: 4.5 meters favors 10Hz

### But INAV Has Predictive Positioning

**INAV extrapolates using velocity:**
```c
predicted_position = last_gps_position + (gps_velocity × time_since_update)
```

**Revised analysis WITH prediction:**
- Temporal lag mostly eliminated by prediction
- HDOP difference dominates (5Hz better: 1.0-1.3m vs 10Hz: 2.0-2.5m)
- **5Hz is actually better** when prediction works (most scenarios)

**Adaptive rates only help during:**
- Very rapid maneuvering (prediction fails)
- Combat/racing with violent direction changes
- Rare in typical INAV use cases

**Conclusion:** Not worth the complexity.

---

## Diagnostic Tools Created

### Query Script: `claude/developer/scripts/testing/query_m10_clock_config.py`

**Purpose:** Safely detect M10 CPU clock mode (default vs high-performance)

**Usage:**
```bash
python3 query_m10_clock_config.py /dev/ttyUSB0
```

**Output:**
```
RESULT: CPU Clock Mode = DEFAULT
RESULT: CPU Clock Mode = HIGH_PERFORMANCE
```

**Features:**
- Read-only (safe, no writes)
- Uses UBX-CFG-VALGET to query config keys
- Compares against known high-performance values
- Helps gather field data

---

## Implementation Status

### Completed
- ✅ Comprehensive research
- ✅ Field testing analysis
- ✅ Hardware capability mapping
- ✅ Expert code review
- ✅ Diagnostic tool creation
- ✅ Implementation plan

### Ready for Implementation
- ⏳ Code changes to gps_ublox.c
- ⏳ Settings.yaml modifications
- ⏳ Build and test
- ⏳ User documentation
- ⏳ Pull request

---

## Recommendations

### Phase 1: Implement Constellation-Aware Rates (NOW)

**Priority:** HIGH
**Risk:** LOW
**Benefit:** Fixes Jetrell's reported issue

**Changes:**
1. Enable Galileo by default
2. Implement constellation-aware rate calculation
3. Default setting: 0 (auto)
4. Allow manual override

### Phase 2: Monitor Field Data (ONGOING)

**Use query script to gather statistics:**
- What % of M10 modules have high-performance mode?
- Do users request OTP programming feature?
- Any issues with constellation-aware rates?

### Phase 3: Optional Enhancements (FUTURE)

**Only if users request:**
- OTP programming feature (with safety checks)
- Speed-based adaptive rates for M9
- Flight mode-aware rates

---

## References

**Official Documentation:**
- MAX-M10S Integration Manual (UBX-20053088-R04)
- MAX-M10S Datasheet (UBX-20035208-R07)
- M10 SPG 5.10 Interface Description (UBX-21035062-R03)
- NEO-M9N Datasheet (UBX-19014285)

**Expert Code:**
- cturvey's RandomNinjaChef repository
- https://github.com/cturvey/RandomNinjaChef

**Community Testing:**
- ArduPilot M9 channel limitation discussion
- PX4 M9 satellite count issues

**Field Testing:**
- Jetrell's M9/M10 rate testing data
- HDOP and satellite count measurements

---

**Research Status:** ✅ Complete
**Next Step:** Begin implementation
**Last Updated:** 2026-01-16
