# Parameter Group (PG) Validation for Releases

## Overview

The Parameter Group validation system helps catch a critical class of EEPROM corruption bugs by verifying that struct size changes are accompanied by version increments.

**When to run:** During release preparation, before creating tags.

**What it checks:** Compares PG struct sizes against a reference target to detect unversioned changes.

**Limitations:** This validation uses a single reference target (SPEEDYBEEF745AIO) and cannot detect configuration-specific struct changes that don't affect that target.

## Why This Matters

INAV stores flight controller settings in EEPROM using the Parameter Group (PG) system. Each configuration struct has:
- A unique ID (pgn)
- A version number
- A compiled size

When loading settings, the firmware checks if the EEPROM version matches. If not, it resets to defaults.

**The risk:** If a developer modifies a struct (adding/removing fields) but forgets to increment the version, the firmware will try to load old EEPROM data into a differently-sized struct, causing memory corruption and crashes.

**Runtime protection:** The `pgLoad()` function compares versions and resets on mismatch.

**Build-time validation:** This system catches the mistake before the release is published.

## Validation Process

### 1. Prerequisites

Ensure you have:
- ARM toolchain installed (`arm-none-eabi-gcc`)
- INAV firmware repository checked out to the release tag
- Clean build directory

### 2. Run Validation

Use the provided helper script:

```bash
cd inav
./cmake/validate-pg-for-release.sh
```

This script will:
1. Build the reference target (SPEEDYBEEF745AIO)
2. Extract PG struct sizes from the binary
3. Compare against the reference database
4. Report any size changes without version increments

### 3. Interpret Results

#### ✅ All validations pass

```
🔍 Validating PG struct sizes for release...
Building reference target: SPEEDYBEEF745AIO...
Extracting PG struct sizes...
Comparing against reference database...

  ✓ systemConfig_t (40B)
  ✓ accelerometerConfig_t (20B)
  ✓ barometerConfig_t (8B)
  ...

✅ All PG struct sizes validated successfully
```

**Action:** Proceed with release.

#### ❌ Validation fails

```
🔍 Validating PG struct sizes for release...
...

  ❌ systemConfig_t: size changed 40B → 42B but version not incremented (still v7)

❌ PG STRUCT SIZE VALIDATION FAILED

The following structs changed size without version increments:
  • systemConfig_t: 40B → 42B (version 7 should be 8)

Fix: Increment PG version in PG_REGISTER for affected structs
```

**Action:**
1. **Do NOT proceed with release**
2. Identify which PRs changed the affected struct
3. Create a hotfix PR to increment the version:
   - Find the `PG_REGISTER` call for the struct (usually in the same file as the struct definition)
   - Increment the 4th parameter (version number)
   - Example: `PG_REGISTER(systemConfig_t, systemConfig, PGN_SYSTEM_CONFIG, 7)` → `8`
4. Merge the hotfix PR
5. Re-run validation

#### ✅ Version was incremented

```
  ✅ systemConfig_t: size changed 40B → 42B with version increment v7 → v8
```

**Action:**
- This is expected and correct
- The database will auto-update
- Proceed with release

#### ➕ New struct added

```
  ➕ New: gpsPresetConfig_t (12B, v1)
```

**Action:**
- This is normal for new features
- The database will auto-add
- Proceed with release

## How It Works

### Reference Target Approach

Due to conditional compilation (`#ifdef USE_I2C`, etc.), the same struct can have different sizes on different targets. A static database for all targets is not feasible.

**Solution:** We use a single well-featured reference target (SPEEDYBEEF745AIO) that enables most features. Size changes that affect this target will be caught.

**Trade-off:** Configuration-specific changes (e.g., fields only present when `USE_OBSCURE_FEATURE` is defined) may not be detected if SPEEDYBEEF745AIO doesn't enable that feature.

### Database Files

- **cmake/pg_struct_sizes.reference.db** - Reference sizes from SPEEDYBEEF745AIO
- Format: `struct_type  size  version` (space-separated, 3 columns)
- Auto-updated when versions are correctly incremented
- Committed to the repository

### Validation Logic

1. Build SPEEDYBEEF745AIO target
2. Extract `pgResetTemplate_<name>` symbol sizes from ELF binary using `nm`
3. Parse source code to find `PG_REGISTER` macros and extract versions
4. Compare each struct:
   - Size unchanged → ✓ Pass
   - Size changed, version incremented → ✓ Pass, update database
   - Size changed, version NOT incremented → ❌ Fail build
   - New struct → ➕ Add to database

## Troubleshooting

### Build fails unrelated to PG validation

The validation runs as a POST_BUILD step. If the build itself fails, fix the build first.

### False positive: Size changed but we didn't modify the struct

**Possible causes:**
1. **Compiler version changed** - Different toolchain versions may produce different alignments (rare)
2. **Platform dependency changed** - Size depends on `sizeof(int)` or pointer size (very rare)
3. **Database was for wrong target** - Ensure database was generated from SPEEDYBEEF745AIO

**Resolution:**
- Verify no actual struct changes in recent commits
- If confirmed false positive, increment version anyway (safer) or regenerate database

### Validation doesn't catch a bug

**Remember:** This only validates changes to SPEEDYBEEF745AIO configuration.

**If a struct only changes when a feature is disabled:**
- Example: Field only present when `USE_FEATURE` is NOT defined
- SPEEDYBEEF745AIO has `USE_FEATURE` enabled
- Size change won't be detected

**Mitigation:** Code review remains critical.

## Manual Validation

If the script fails or you need to validate a specific target:

```bash
# Build the target
cd inav/build
make YOURTARGET.elf

# Extract sizes
../cmake/extract-pg-sizes-nm.sh bin/YOURTARGET.elf > /tmp/current_sizes.txt

# Compare manually
diff ../cmake/pg_struct_sizes.reference.db /tmp/current_sizes.txt
```

Any differences in size for the same version indicate a problem.

## Updating the Database

The database auto-updates when:
- New structs are added (first build after PG_REGISTER added)
- Struct size changes AND version is incremented

**Manual update (not normally needed):**

```bash
# Regenerate entire database from current SPEEDYBEEF745AIO build
cd inav/build
make SPEEDYBEEF745AIO.elf
../cmake/extract-pg-sizes-nm.sh bin/SPEEDYBEEF745AIO.elf > ../cmake/pg_struct_sizes.reference.db
cd ..
git add cmake/pg_struct_sizes.reference.db
git commit -m "Update PG reference database"
```

## Integration with Release Workflow

Add to pre-release checklist:

**Before creating tags:**

```bash
cd inav
git checkout master && git pull
./cmake/validate-pg-for-release.sh
```

**If validation passes:**
- Proceed with tagging and release

**If validation fails:**
- Create hotfix PR to increment version(s)
- Merge to master
- Re-run validation
- Then proceed with release

## Related Documentation

- `docs/development/release-create.md` - Full release process
- `cmake/check-pg-struct-sizes.sh` - Core validation script
- `cmake/extract-pg-sizes-nm.sh` - Size extraction utility
- `src/main/config/parameter_group.h` - PG_REGISTER macros
- `src/main/config/parameter_group.c` - pgLoad() runtime validation

## Notes for Future Maintainers

### Why Not Validate All Targets?

We investigated using architecture-specific databases (ARM, x86_64) but discovered that struct sizes vary by build configuration, not just architecture. Same-architecture targets can have different sizes due to `#ifdef` directives.

Options considered:
- **Double-compilation** (build base + PR branches) - Too slow for CI
- **Per-target databases** - 300+ targets, configuration explosion
- **Reference target** (current approach) - Limited coverage but practical

### Why SPEEDYBEEF745AIO?

Criteria for reference target:
- Well-featured (enables most PG-affecting features)
- F7 platform (common, well-supported)
- Popular board (community testing)
- Stable target (unlikely to be removed)

### Changing Reference Target

If SPEEDYBEEF745AIO is removed or needs replacement:

1. Choose new reference (apply same criteria)
2. Build new target: `make NEWTARGET.elf`
3. Regenerate database: `cmake/extract-pg-sizes-nm.sh bin/NEWTARGET.elf > cmake/pg_struct_sizes.reference.db`
4. Update `cmake/validate-pg-for-release.sh` to build new target
5. Update this documentation
6. Commit changes

---

**Last updated:** 2026-01-23
**Reference target:** SPEEDYBEEF745AIO (F745, well-featured)
**Database:** cmake/pg_struct_sizes.reference.db
