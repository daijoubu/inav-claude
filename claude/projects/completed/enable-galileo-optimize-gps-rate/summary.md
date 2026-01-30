# Project: Enable Galileo by Default and Optimize GPS Update Rate

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM
**Type:** Feature / Optimization
**Created:** 2025-12-31
**Updated:** 2026-01-16
**Estimated Effort:** 2-3 hours implementation (research complete)

## Overview

Implement constellation-aware GPS update rates to optimize M10 GPS performance and enable Galileo by default on M8+ receivers.

## Problem

Research revealed that M10 GPS modules have processing limitations that cause poor performance at high update rates with multiple GNSS constellations:

**Jetrell's Field Testing:**
- M10 with 4 constellations at 10Hz: Wild HDOP (2-5), poor satellite tracking
- M10 with 4 constellations at 6-9Hz: Stable HDOP (1.3), +8-10 more satellites

**Root Cause:** M10 default CPU clock mode has constellation-dependent update rate limits (not a bug, it's hardware design).

## Solution

**Constellation-Aware GPS Rates:**
- M10 with 4 constellations → 6Hz (safe, tested by Jetrell)
- M10 with 3 constellations → 8Hz (within datasheet limits)
- M10 with 1-2 constellations → 10Hz (full speed)
- M9 → 10Hz (more capable hardware)

**Enable Galileo by Default:**
- Clear benefit: +8 satellites, better HDOP, faster TTFF
- Supported since 2016 (M8N+)
- No downsides

## Implementation

### Code Changes

**1. inav/src/main/io/gps_ublox.c**

Add constellation-aware rate calculation:
```c
static uint8_t calculateSafeGPSRate(void)
{
    int constellationCount = 1; // GPS always enabled
    if (gpsState.gpsConfig->ubloxUseGalileo) constellationCount++;
    if (gpsState.gpsConfig->ubloxUseGlonass) constellationCount++;
    if (gpsState.gpsConfig->ubloxUseBeidou) constellationCount++;

    if (gpsState.hwVersion >= UBX_HW_VERSION_UBLOX10) {
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

Modify `gpsConfigure()`:
```c
if (gpsState.gpsConfig->ubloxNavHz == 0) {
    // Auto mode: use constellation-aware calculation
    navHz = calculateSafeGPSRate();
} else {
    // Manual override
    navHz = gpsState.gpsConfig->ubloxNavHz;
}
configureRATE(hz2rate(navHz));
```

**2. inav/src/main/fc/settings.yaml**

```yaml
- name: gps_ublox_use_galileo
  default_value: ON  # Changed from OFF

- name: gps_ublox_nav_hz
  default_value: 0  # Changed from 10 (0 = auto)
  min: 0  # Add 0 as valid (auto mode)
```

**3. Documentation**
- Explain constellation-aware behavior
- Document manual override capability
- Explain M10 clock modes

## Research Completed

All research documentation is in:
**`claude/developer/workspace/enable-galileo-optimize-gps-rate/`**

### Key Documents

1. **IMPLEMENTATION-PLAN-constellation-aware.md**
   - Complete implementation specification
   - Code examples and algorithms
   - Step-by-step implementation guide

2. **jetrell-testing-data.md**
   - Field testing evidence
   - HDOP and satellite count data
   - Validates constellation-aware approach

3. **m9-channel-limitation-analysis.md**
   - M9 hardware processing constraint
   - 16 satellite limit at ≥10Hz
   - Recommendation to keep M9 at 10Hz

4. **cturvey-implementation-analysis.md**
   - Expert code review from u-blox specialist
   - OTP programming patterns
   - Safe implementation approaches

5. **adaptive-gps-rate-analysis.md**
   - Speed-based dynamic rate analysis
   - Error budget comparison
   - Conclusion: Don't implement (not worth complexity)
   - INAV's predictive positioning changes the math

### M10 CPU Clock Modes Discovery

**CRITICAL Finding:**
- M10 has two CPU clock modes: Default and High-Performance
- **Default** (most common): Limited rates by constellation count
- **High-Performance** (OTP programmed, rare): Higher rates possible
- OTP = One-Time Programmable (permanent, cannot be reverted)

**Default Mode Limits** (from u-blox Integration Manual):
- 4 constellations: 4-6 Hz max
- 3 constellations: 6-8 Hz max
- 2 constellations: 10 Hz max

### Diagnostic Tool Created

**`claude/developer/scripts/testing/query_m10_clock_config.py`**
- READ-ONLY script to detect M10 clock mode
- Helps gather field data on module configurations
- Safe to run on any M10 module

## Success Criteria

- [x] Comprehensive research completed
- [x] M10 performance modes understood
- [x] M9 channel limitations documented
- [x] Implementation plan created
- [x] Diagnostic tool created
- [ ] Code changes implemented
- [ ] Build verification
- [ ] SITL testing
- [ ] Pull request created
- [ ] Community feedback gathered

## Value

**Benefits:**
- Fixes Jetrell's reported GPS performance issue
- Optimal rates for each hardware/constellation combination
- Improved accuracy with Galileo enabled
- Automatic optimization (no user configuration needed)
- Manual override available for advanced users

**Audience:**
- M10 GPS users (fixes current performance issues)
- M8/M9 GPS users (benefits from Galileo default)
- New users (better out-of-the-box experience)

## Priority Justification

MEDIUM priority because:
- Research complete, ready for implementation
- Clear evidence from field testing
- Low risk (backward compatible, manual override available)
- Significant performance improvement for M10 users
- Straightforward implementation

## Key Decisions

### ✅ Implement Constellation-Aware Rates
- Evidence: Jetrell's testing, datasheet limits, expert code review
- Approach: Auto-calculate based on enabled constellations
- Default: 0 (auto), allow manual override

### ✅ Enable Galileo by Default
- Clear benefit with no downsides
- Supported since 2016
- Backward compatible

### ❌ Don't Implement Adaptive Rates
- Initial analysis showed promise
- But INAV's predictive positioning eliminates temporal lag benefit
- Complexity not justified for small benefit
- Can revisit if users request it

### ❌ Don't Implement OTP Programming
- Too risky (permanent, cannot be reverted)
- Diagnostic tool sufficient for now
- Can add later if field data shows demand

## Next Steps

1. Implement code changes in gps_ublox.c
2. Modify settings.yaml defaults
3. Build and test with inav-builder agent
4. Create pull request with research documentation
5. Request community testing
6. Monitor field feedback

## Related

- **Branch:** `enable-galileo-gps-optimization`
- **Parent analysis:** document-ublox-gps-configuration (COMPLETED)
- **Research workspace:** `claude/developer/workspace/enable-galileo-optimize-gps-rate/`
- **Lock file:** `claude/locks/inav.lock` (ACQUIRED)
- **Assignment:** `claude/developer/email/inbox/2025-12-31-*-enable-galileo-optimize-gps-rate.md`
