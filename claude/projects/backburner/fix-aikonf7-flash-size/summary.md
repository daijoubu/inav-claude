# Project: Fix AIKONF7 Target Flash Size Issue

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Investigation / Target Configuration Fix
**Created:** 2026-01-12
**Estimated Effort:** 4-6 hours

## Overview

Investigate and fix AIKONF7 target compilation issue where the compiled hex file exceeds available flash memory, causing the target to not work. Other F722 targets compile and work correctly.

## Problem

The AIKONF7 target currently doesn't work, suspected because:
- Compiled hex file size exceeds available flash memory on the target
- Other F722 targets (same MCU family) work fine
- Suggests target-specific configuration issue rather than general F722 problem

## Key Constraint

**⚠️ IMPORTANT:** The build directory is currently in use. Do not modify or clean the build directory during investigation.

## Investigation Strategy

### Phase 1: Compare Target Configurations (1-2 hours)

**Goal:** Understand what makes AIKONF7 different from working F722 targets

1. **Find all F722 targets:**
   ```bash
   grep -l "STM32F722" inav/src/main/target/*/target.h
   # or
   grep -l "F722" inav/src/main/target/*/target.mk
   ```

2. **Identify working F722 targets** to use as reference

3. **Compare AIKONF7 against working targets:**
   - Flash size definitions in `target.h`
   - Feature flags in `target.h` (enabled peripherals, sensors, etc.)
   - CMake configuration in `target.cmake`
   - Linker script settings
   - Default feature set

**Files to check:**
- `inav/src/main/target/AIKONF7/target.h`
- `inav/src/main/target/AIKONF7/target.cmake`
- `inav/src/main/target/AIKONF7/target.mk`
- Compare with working F722 targets (e.g., MATEKF722, SPEEDYBEEF7V2, etc.)

### Phase 2: Analyze Build Output (1 hour)

**Goal:** Confirm flash size issue and identify what's consuming space

1. **Check recent build logs** (if available without rebuilding):
   - Look for flash size warnings
   - Check final binary size vs flash capacity
   - Identify largest code sections

2. **Review flash capacity:**
   - STM32F722 typically has 512KB flash
   - Check if AIKONF7 target defines correct flash size
   - Verify linker script uses correct memory layout

3. **Compare binary sizes:**
   - Compare AIKONF7 binary size with working F722 targets
   - Identify if AIKONF7 is significantly larger

### Phase 3: Root Cause Analysis (1-2 hours)

**Common causes for target-specific flash overflow:**

1. **Too many features enabled:**
   - Unnecessary peripherals/sensors enabled
   - Extra protocols enabled (MSP, CLI extensions)
   - Excessive OSD elements
   - Debug features left enabled

2. **Incorrect flash size definition:**
   - target.h defines wrong flash capacity
   - Linker script has wrong memory regions

3. **Missing optimizations:**
   - LTO (Link Time Optimization) disabled
   - Wrong optimization level
   - Missing size reduction flags

4. **Unnecessary drivers:**
   - Extra sensor drivers included
   - Unused peripheral drivers
   - Legacy compatibility code

### Phase 4: Implementation (1-2 hours)

**Likely fixes:**

**Option A - Disable Unnecessary Features:**
- Disable unused sensors/peripherals in `target.h`
- Remove unnecessary default features
- Compare feature set with minimal working F722 target

**Option B - Fix Flash Configuration:**
- Correct `FLASH_SIZE` definition if wrong
- Fix linker script memory layout
- Ensure proper flash bank configuration

**Option C - Enable Size Optimizations:**
- Ensure LTO is enabled
- Check compiler optimization flags
- Add target-specific size reduction options

## Files to Investigate

### AIKONF7 Target Files
- `inav/src/main/target/AIKONF7/target.h` - Feature flags, flash size
- `inav/src/main/target/AIKONF7/target.cmake` - Build configuration
- `inav/src/main/target/AIKONF7/target.mk` - Makefile settings
- `inav/src/main/target/AIKONF7/config.c` - Default settings

### Reference Working F722 Targets
- `inav/src/main/target/MATEKF722/` - Popular F722 target
- `inav/src/main/target/SPEEDYBEEF7V2/` - Another F722 reference
- Or other known-working F722 targets

### Build System
- `inav/cmake/stm32f7.cmake` - F7 family build config
- Linker scripts in `inav/src/main/target/link/`

## Success Criteria

- [ ] Root cause identified and documented
- [ ] AIKONF7 target configuration fixed
- [ ] Firmware compiles successfully for AIKONF7
- [ ] Binary size is within flash capacity
- [ ] No features removed that are actually needed for the hardware
- [ ] PR created with fix
- [ ] Completion report sent to manager

## Recommended Workflow

### 1. Compare Target Configurations

Use Grep/Read to compare AIKONF7 with working F722 targets:
```
# Find all F722 targets
grep -r "STM32F722" inav/src/main/target/*/target.h

# Compare target.h files
Read: inav/src/main/target/AIKONF7/target.h
Read: inav/src/main/target/MATEKF722/target.h
```

### 2. Check Flash Size Definition

Look for:
- `#define FLASH_SIZE` or similar
- Memory region definitions
- Feature flags that consume significant flash

### 3. Use inav-architecture Agent

For understanding target structure:
```
Task tool: subagent_type="inav-architecture"
Prompt: "Explain INAV target configuration system. How are F7 targets
configured? Where is flash size defined? How do I compare target configurations?"
```

### 4. Build After Finding Fix

**Only after identifying the fix**, use **inav-builder** agent:
```
Task tool: subagent_type="inav-builder"
Prompt: "Build AIKONF7 target"
```

Check build output for:
- Binary size
- Flash utilization percentage
- Warning messages

### 5. Create PR

Use git-workflow skill:
```
/git-workflow "Create branch fix/aikonf7-flash-size from maintenance-9.x"
/git-workflow "Commit and create PR for AIKONF7 flash size fix"
```

## Notes

- **Do not modify build directory** - it's currently in use
- Focus on target configuration files only
- Compare with known-working F722 targets for reference
- F722 standard flash: 512KB
- Check if AIKONF7 hardware actually has 512KB or less

## Related

- **Issue:** TBD (check GitHub for AIKONF7 related issues)
- **Assignment:** `claude/manager/email/sent/2026-01-12-1525-task-fix-aikonf7-flash-size.md`
