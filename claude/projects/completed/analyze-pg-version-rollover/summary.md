# Project: Analyze PG Version Rollover Impact

**Status:** ✅ ANALYSIS COMPLETE
**Priority:** MEDIUM-HIGH
**Type:** Investigation / Risk Analysis
**Created:** 2026-01-22
**Completed:** 2026-01-23
**Actual Effort:** 2 hours
**Related To:** document-parameter-group-system

## Overview

Analyze what happens when parameter group version numbers roll over from 15 to 0. PG versions are stored in a 4-bit field, and some parameter groups like `osdConfig_t` are approaching version 15.

## Problem

Parameter group versions use only 4 bits (range 0-15). As parameter groups are modified over time, their versions increment. Some PGs are close to version 15 and will soon need to roll over to 0.

**Questions to answer:**
- What happens when a PG version rolls from 15 to 0?
- Does `pgLoad()` handle this correctly?
- Will users with version 15 settings be able to load version 0 firmware?
- Is there version comparison logic that might break?
- Do we need a mitigation strategy?

**Known PGs near rollover:**
- `osdConfig_t` - approaching version 15
- Others TBD (need to identify)

## Solution

Conduct thorough code analysis to understand version rollover behavior and recommend a solution if issues are found.

## Implementation

### Phase 1: Identify Current Versions (1 hour)

- Find all PG registrations and their current versions
- Identify which PGs are at high version numbers (12+)
- Document PGs at risk of rollover
- Check `cmake/*pg*` files in `pg-version-check-action` branch for struct sizes and versions

**Reference:** `cmake/*pg*` in the `pg-version-check-action` branch contains PG struct sizes and version information.

### Phase 2: Code Analysis (1-2 hours)

- Study `pgLoad()` implementation
- Understand version comparison logic
- Trace through what happens on version mismatch
- Test rollover scenario: stored_version=15, current_version=0
- Check if comparison is signed/unsigned
- Look for any assumptions about version ordering

### Phase 3: Impact Assessment (30-60 min)

**Determine:**
- Does rollover cause settings to load incorrectly?
- Does rollover trigger default reset (safe but inconvenient)?
- Does rollover fail silently (dangerous)?
- Are there any edge cases or special handling?

### Phase 4: Recommendations (30 min)

**If rollover is handled correctly:**
- Document the behavior
- No code changes needed

**If rollover causes issues:**
- Propose mitigation strategies:
  - Skip version 15, jump to 1?
  - Special rollover detection logic?
  - Alternative versioning scheme?
  - Migration plan for affected PGs?

## Success Criteria

- [ ] Current PG versions documented (especially those near 15)
- [ ] Version rollover behavior clearly understood
- [ ] Impact on users clearly assessed
- [ ] Code paths for rollover scenario traced
- [ ] Recommendations provided
- [ ] Findings documented for parameter group documentation

## Related

- **Related Project:** document-parameter-group-system
- **Key Files:**
  - `src/main/config/parameter_group.h` - Version storage and extraction
  - `src/main/config/parameter_group.c` - pgLoad() implementation
  - `cmake/*pg*` in `pg-version-check-action` branch - Struct sizes and versions
- **Version Storage:** Top 4 bits of pgn field (`pgVersion = (pgn >> 12) & 0xF`)

## Findings Summary

### ✅ REVISED: Rollover is Safe - No Code Changes Needed

**Initial Assessment:** Theoretical corruption risk at rollover
**Revised Assessment:** Safe in practice due to upgrade procedures

**Key Insight:**
- `osdConfig_t` was v3 by INAV 2.0 (8 years ago)
- Any v0-2 EEPROM is from INAV 1.x (pre-2018)
- Major version upgrades **require full flash erase** per instructions
- Theoretical corruption scenario won't happen in practice

### Rollover Behavior (Working as Intended)

**When v15 → v0 rollover occurs:**
- ✅ **SAFE** - Settings reset to defaults (same as any version change)
- ⚠️ **INCONVENIENT** - Users must reconfigure (expected for PG changes)
- 📋 **DOCUMENTED** - Standard behavior for version mismatch

### Parameter Group Versions (For Reference)

1. `osdConfig_t` - v15 (will rollover to v0 on next change)
2. `rxConfig_t` - v13 (2 changes until rollover)
3. `gyroConfig_t` - v12 (3 changes until rollover)
4. `motorConfig_t` - v11 (4 changes until rollover)
5. `pidProfile_t` - v11 (4 changes until rollover)

### Version Comparison Logic

Simple equality check is **appropriate and sufficient**:

```c
void pgLoad(..., int version) {
    pgReset(reg, profileIndex);  // Reset to defaults

    if (version == pgVersion(reg)) {  // Exact match only
        memcpy(...);  // Load EEPROM
    }
    // Mismatch: keep defaults (safe)
}
```

**Why this works:**
- Version mismatch → settings reset (safe, documented)
- Major upgrades → flash erase required (prevents old EEPROM)
- No practical path for corruption

### Recommended Actions

**DOCUMENTATION ONLY - No Code Changes:**

1. ✅ Document rollover behavior in PG system guide
2. ✅ Confirm upgrade guides mention flash erase for major versions
3. ✅ Add rollover comments to PG registration macros
4. ✅ Close investigation as "working as intended"

**No PR needed** - system is safe as-is.

**See:**
- `ANALYSIS.md` - Complete technical analysis (original assessment)
- `REVISED-CONCLUSION.md` - Updated assessment with practical considerations

## Notes

This analysis should feed into the parameter group documentation project, specifically the versioning rules section that covers the 4-bit version limitation and wraparound behavior.
