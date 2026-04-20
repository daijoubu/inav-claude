# Todo: Fix H743 DFU Reboot Failure

**Status:** 📋 TODO
**Estimated Effort:** 4-6 hours

---

## Phase 1: Hardware Verification (1-2h)

### Test INAV 9.0.0

- [ ] Obtain H743 target board (DAKEFPVH743PRO or similar)
- [ ] Build INAV 9.0.0 for H743 target
- [ ] Flash firmware to board
- [ ] Connect via CLI (USB or serial)
- [ ] Run `dfu` command
- [ ] Observe reboot behavior
- [ ] Check if DFU device appears: `dfu-util -l` (Linux) or Device Manager (Windows)
- [ ] Document exact behavior

### Test INAV 8.0.0 for Comparison

- [ ] Check out INAV 8.0.0 tag
- [ ] Build firmware for same H743 target
- [ ] Flash to board
- [ ] Connect via CLI
- [ ] Run `dfu` command
- [ ] Check if DFU mode works correctly
- [ ] Document behavior

### Compare Results

- [ ] Document differences between 8.0.0 and 9.0.0
- [ ] Confirm if this is a regression (works in 8.0.0, breaks in 9.0.0)

---

## Phase 2: Code Location (30min)

### Use inav-architecture Agent

- [ ] Launch inav-architecture agent
- [ ] Query: "Find the rebootEx() function and related DFU reboot code for H743 targets"
- [ ] Get file locations for:
  - `rebootEx()` implementation
  - H743-specific system code
  - DFU mode entry logic
  - Boot register configuration

### Locate Key Files

- [ ] Find H7-specific system file (likely `system_stm32h7xx.c`)
- [ ] Find generic system code (`system.c`)
- [ ] Find CLI dfu command implementation (`cli.c`)
- [ ] Find MSP reboot handling (`msp.c`)
- [ ] Note relevant target configuration files

---

## Phase 3: Code Comparison (1h)

### Compare 8.0.0 vs 9.0.0

- [ ] **Checkout 8.0.0 tag**
  - [ ] Read `rebootEx()` implementation for H743
  - [ ] Note boot register configuration
  - [ ] Note bootloader address
  - [ ] Note reset sequence
  - [ ] Save relevant code snippets

- [ ] **Checkout maintenance-9.x**
  - [ ] Read `rebootEx()` implementation for H743
  - [ ] Note boot register configuration
  - [ ] Note bootloader address
  - [ ] Note reset sequence
  - [ ] Save relevant code snippets

- [ ] **Identify differences**
  - [ ] What changed in `rebootEx()`?
  - [ ] What changed in boot register handling?
  - [ ] What changed in H743-specific code?
  - [ ] Were new conditionals added?
  - [ ] Were addresses changed?

### Git History Analysis

- [ ] Use git log to find commits affecting rebootEx() between 8.0.0 and 9.0.0
- [ ] Check commit messages for H743 or DFU-related changes
- [ ] Review specific commits for context

---

## Phase 4: Root Cause Analysis (1h)

### Analyze Differences

- [ ] **Boot address hypothesis:**
  - [ ] Compare bootloader addresses between versions
  - [ ] Check if H743 uses correct address
  - [ ] Verify against STM32H743 datasheet/reference manual

- [ ] **Boot register hypothesis:**
  - [ ] Compare boot mode register setup
  - [ ] Check if H743-specific registers are set correctly
  - [ ] Verify register values against STM32 documentation

- [ ] **Reset sequence hypothesis:**
  - [ ] Compare reset sequences
  - [ ] Check if cache is flushed before reset
  - [ ] Verify memory barriers are present

- [ ] **Conditional logic hypothesis:**
  - [ ] Check if H743 is properly included/excluded in conditionals
  - [ ] Look for `#ifdef STM32H7` that might miss H743 variants

### Document Root Cause

- [ ] Write clear explanation of what's wrong
- [ ] Explain why it worked in 8.0.0
- [ ] Explain what broke in 9.0.0
- [ ] Include code references

---

## Phase 5: Fix Implementation (1-2h)

### Develop Fix

- [ ] Based on root cause, implement fix
- [ ] Ensure fix is H743-specific (don't break other targets)
- [ ] Follow existing code patterns
- [ ] Add comments explaining the fix

### Build and Test

- [ ] Build firmware for H743 target
- [ ] Flash to test board
- [ ] Test `dfu` command
- [ ] Verify board enters DFU mode
- [ ] Check: DFU device appears in `dfu-util -l`
- [ ] Test: Flash firmware via DFU to verify complete flow

---

## Phase 6: Regression Testing (30min-1h)

### Test Other Targets

- [ ] **F4 target:**
  - [ ] Build with fix
  - [ ] Test `dfu` command
  - [ ] Verify DFU mode still works

- [ ] **F7 target:**
  - [ ] Build with fix
  - [ ] Test `dfu` command
  - [ ] Verify DFU mode still works

- [ ] **Other H7 targets** (if available):
  - [ ] Test to ensure no regression

### Document Testing

- [ ] Record all test results
- [ ] Note any issues found
- [ ] Verify no regressions

---

## Phase 7: PR Creation

### Prepare PR

- [ ] Review code changes for quality
- [ ] Ensure consistent formatting
- [ ] Add/update comments
- [ ] Clean up any debug code

### Create PR

- [ ] Create branch from `maintenance-9.x`
- [ ] Commit changes with clear message
- [ ] Push to fork
- [ ] Create PR to upstream `maintenance-9.x`

### PR Description

Include:
- [ ] Summary of the bug
- [ ] Root cause explanation
- [ ] Description of fix
- [ ] Testing performed (9.0.0 broken, 8.0.0 working, fix verified)
- [ ] Hardware tested on
- [ ] Regression testing results

---

## Completion

- [ ] Root cause documented
- [ ] Fix implemented and tested
- [ ] No regressions on other targets
- [ ] PR created
- [ ] Send completion report to manager

---

**Key Files Reference:**
(Will be populated by inav-architecture agent)

- `src/main/drivers/system_stm32h7xx.c`
- `src/main/drivers/system.c`
- `src/main/fc/cli.c`
- `src/main/msp/msp.c`

---

**Estimated Time Breakdown:**
- Hardware verification: 1-2h
- Code location: 30min
- Code comparison: 1h
- Root cause analysis: 1h
- Fix implementation: 1-2h
- Regression testing: 30min-1h
- **Total: 4-6 hours**
