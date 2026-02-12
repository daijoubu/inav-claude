# PG Version Rollover - Quick Findings Summary

**Date:** 2026-01-23
**Status:** Analysis Complete - Ready for Decision

---

## 🚨 Critical Finding

**`osdConfig_t` is at version 15 (maximum)** - The next OSD feature change will force a rollover to v0.

### What Happens at Rollover?

**Short-term (v15→v0):**
- ✅ **SAFE** - Settings are discarded, reset to defaults
- ⚠️ **INCONVENIENT** - Users lose all OSD configuration
- Users must reconfigure from scratch

**Long-term (old v0 → new v0, after 16+ versions):**
- 🔴 **DANGEROUS** - Ancient v0 data could load into completely different v0 struct
- 🔴 **DATA CORRUPTION** - Fields misaligned, wrong types, invalid values
- 🔴 **POTENTIAL CRASHES** - Undefined behavior

---

## 📊 At-Risk Parameter Groups

| PG Name | Current Version | Risk Level | Changes Left |
|---------|----------------|------------|--------------|
| `osdConfig_t` | **15** | 🔴 CRITICAL | 0 |
| `rxConfig_t` | 13 | 🟡 HIGH | 2 |
| `gyroConfig_t` | 12 | 🟡 MEDIUM | 3 |
| `motorConfig_t` | 11 | 🟢 MEDIUM-LOW | 4 |
| `pidProfile_t` | 11 | 🟢 MEDIUM-LOW | 4 |

---

## 🔍 Root Cause

```c
// parameter_group.c:90
void pgLoad(..., int version) {
    pgReset(reg, profileIndex);  // Always reset to defaults first

    if (version == pgVersion(reg)) {  // Simple equality check
        memcpy(...);  // Load EEPROM data
    }
    // Else: keep defaults
}
```

**Problem:** No cycle tracking - Cannot distinguish:
- v0 from 2020 (first cycle)
- v0 from 2028 (after 16 versions, second cycle)

Both would pass the `version == 0` check, but structs could be completely different!

---

## ✅ Recommended Solution

**Hybrid: Skip v15 + Rollover Detection**

### Implementation

```c
#define PG_VERSION_MAX 14  // Reserve v15 for rollover marker

void pgLoad(const pgRegistry_t* reg, int profileIndex, const void *from, int size, int version)
{
    pgReset(reg, profileIndex);
    uint8_t current_version = pgVersion(reg);

    // Detect rollover scenarios
    bool rollover_detected = (version == 15) ||  // v15 always resets
                            (version >= 12 && current_version <= 2);  // v14→v0 transition

    if (version == current_version && !rollover_detected) {
        const int take = MIN(size, pgSize(reg));
        memcpy(pgOffset(reg, profileIndex), from, take);
    }
}
```

### Benefits

- ✅ Minimal code changes (10-15 lines)
- ✅ No EEPROM format change
- ✅ No forced configuration reset for all users
- ✅ Handles immediate `osdConfig_t` risk
- ✅ Safe rollover behavior (settings reset, not corruption)
- ✅ Buys time for better long-term solution

### Trade-offs

- ⚠️ Loses one version number (14 usable instead of 15)
- ⚠️ Settings reset needed when crossing v14→v0
- ⚠️ Still limited to 15 versions total per PG

---

## 🔮 Long-Term Solution (INAV 10.0+)

**Expand to 8-bit versions (0-255):**

```
Current:  [version(4 bits) | pgn(12 bits)]
Proposed: [version(8 bits) | pgn(8 bits)]
```

**Benefits:**
- 255 versions instead of 15 (17x increase)
- ~85-100 years per cycle at current change rate
- Essentially unlimited for project lifetime

**Cost:**
- Breaking EEPROM format change
- Reduces PG ID space from 4096→256 (still plenty - we use 48)
- Requires full configuration reset for all users
- Should wait for major version release

---

## 📈 Version Growth Rates

Based on historical data:

| PG | Versions/Year | Time to Cycle (14 versions) |
|----|---------------|----------------------------|
| `osdConfig_t` | ~3.0 | ~4.6 years |
| `rxConfig_t` | ~2.6 | ~5.4 years |
| `gyroConfig_t` | ~2.4 | ~5.8 years |

**Conclusion:** Short-term fix (skip v15) buys 4-5 years; long-term fix (8-bit) provides ~100 years.

---

## 🧪 Testing Requirements

If implementing the recommended solution:

1. **Version Match** - Settings load correctly (normal case)
2. **Version Mismatch** - Settings reset (version upgrade)
3. **Rollover Detection** - Settings reset when v14→v0 detected
4. **Reserved v15** - Settings always reset from v15
5. **EEPROM Integrity** - No corruption or crashes

---

## 📋 Next Steps

### For Manager/Tech Lead:

1. **Review findings** in ANALYSIS.md
2. **Decide on solution approach:**
   - Recommended: Skip v15 + rollover detection
   - Alternative: Other options in Section 7 of ANALYSIS.md
3. **Assign implementation** if approved
4. **Schedule for release:**
   - Before next `osdConfig_t` change
   - Consider for INAV 9.x maintenance release

### For Developer (if assigned):

1. Implement changes to `parameter_group.c` and `parameter_group.h`
2. Add `#define PG_VERSION_MAX 14`
3. Update `pgLoad()` with rollover detection logic
4. Write unit tests for rollover scenarios
5. Test on SITL and hardware
6. Update developer documentation
7. Create PR with clear explanation

---

## 📚 Documentation

- **Full Analysis:** `ANALYSIS.md` (59 sections, 550+ lines)
- **Code Locations:**
  - Version storage: `src/main/config/parameter_group.h:57`
  - Version check: `src/main/config/parameter_group.c:90`
  - PG versions: `cmake/pg_struct_sizes.arm.db`

---

## ❓ Quick Q&A

**Q: Is this urgent?**
A: MEDIUM-HIGH. `osdConfig_t` is at v15 NOW. Next OSD feature will force rollover.

**Q: Will users lose data?**
A: With mitigation: Settings reset (inconvenient, safe). Without: Potential corruption (dangerous).

**Q: Can we just expand to 8-bit now?**
A: Not recommended - forces all users to reset configs. Better for major version (INAV 10.0).

**Q: How long to implement?**
A: ~4-6 hours including testing. Minimal risk, well-contained change.

**Q: What if we do nothing?**
A: Next `osdConfig_t` change → forced rollover → user confusion → settings reset. Long-term: corruption risk.

---

**For complete technical details, see ANALYSIS.md**
