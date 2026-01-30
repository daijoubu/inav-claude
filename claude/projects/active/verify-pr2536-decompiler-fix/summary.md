# Project: Check if PR #2536 Fixes Hoisting Bug

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Testing / Investigation
**Created:** 2026-01-26
**Estimated Effort:** 1 hour

## Overview

Check whether PR #2536 (fix/js-programming-decompiler-airspeed branch) happens to fix the hoisting bug that exists in maintenance-9.x when decompiling a specific set of logic conditions. **Note:** PR #2536 was not specifically intended to fix this bug, but we need to check if it fixes it as a side effect.

## Problem

The `maintenance-9.x` branch has a **hoisting bug** in the JavaScript decompiler. When decompiling certain logic conditions, the decompiler:

1. **Hoists** the condition (moves it to a variable declaration at the top)
2. **Keeps it inline** (also keeps the condition in its original location)
3. **Creates circular logic** - the condition becomes conditional on itself

This makes the decompiled JavaScript invalid/incorrect.

## Test Case

**Logic conditions to test:**
```
logic 0 1 -1 2 2 0 0 1000 0
logic 1 1 -1 47 4 0 0 0 0
logic 2 1 1 18 0 0 0 0 0
logic 3 1 -1 3 2 12 0 100 0
logic 4 1 3 19 0 0 0 1 0
logic 5 1 -1 1 2 17 0 0 0
logic 6 1 5 14 5 0 0 1 0
logic 7 1 5 18 0 1 4 6 0
```

These logic conditions trigger the hoisting bug in maintenance-9.x.

## Objectives

1. **Test maintenance-9.x (baseline):**
   - Checkout maintenance-9.x branch
   - Build configurator
   - Apply the logic conditions
   - Decompile to JavaScript
   - **Document the hoisting bug:**
     - Which condition gets hoisted AND kept inline?
     - What is the incorrect JavaScript output?
     - Show the circular dependency

2. **Test fix/js-programming-decompiler-airspeed (PR #2536):**
   - Checkout fix/js-programming-decompiler-airspeed branch
   - Build configurator
   - Apply the same logic conditions
   - Decompile to JavaScript
   - **Check if it's fixed:**
     - Does the hoisting bug still occur?
     - If not, what changed that fixed it?
     - Is the JavaScript output correct now?

3. **Compare results:**
   - Side-by-side comparison of decompiled code
   - Determine if the hoisting bug is fixed (YES/NO)
   - If fixed, identify what change in PR #2536 fixed it

## PR Information

**PR:** [#2536](https://github.com/iNavFlight/inav-configurator/pull/2536)
**Branch:** `fix/js-programming-decompiler-airspeed`
**Base:** `maintenance-9.x`
**Purpose:** Fix JavaScript decompiler issues (airspeed operand and others)
**Repository:** inav-configurator

**Note:** This PR was not specifically targeting the hoisting bug, but may fix it as a side effect.

## Testing Approach

### Option 1: SITL Testing (Recommended)
1. Build INAV SITL firmware
2. Start SITL
3. Connect configurator (maintenance-9.x) to SITL
4. Go to Programming tab
5. Paste logic conditions into CLI
6. Switch to JavaScript Programming tab
7. Click "Decompile"
8. Document the hoisting bug
9. Checkout PR #2536 branch
10. Rebuild configurator
11. Repeat decompile test
12. Compare results

### Option 2: Mock Testing (If SITL unavailable)
1. Review decompiler code changes in PR #2536
2. Create test with the logic conditions
3. Run decompiler directly on the test data
4. Compare maintenance-9.x vs fix branch behavior

## Expected Deliverables

**Investigation Report** including:

1. **Baseline (maintenance-9.x):**
   - Decompiled JavaScript output showing the bug
   - Identify which condition is hoisted AND kept inline
   - Show the circular dependency

2. **PR #2536 Branch:**
   - Decompiled JavaScript output
   - Does the hoisting bug still occur? YES/NO
   - If fixed, what is the correct output?

3. **Analysis:**
   - If fixed: Which change in PR #2536 likely fixed it?
   - If not fixed: The bug still exists, needs separate fix

4. **Conclusion:**
   - Clear answer: Does PR #2536 fix the hoisting bug? YES/NO

## Success Criteria

- [ ] maintenance-9.x tested with the logic conditions
- [ ] Hoisting bug demonstrated
- [ ] PR #2536 branch tested with same logic conditions
- [ ] Clear determination: bug fixed (YES) or still present (NO)
- [ ] If fixed: identify which change likely fixed it
- [ ] Side-by-side comparison provided
- [ ] Completion report sent to manager with clear answer

## Related

- **PR:** [#2536](https://github.com/iNavFlight/inav-configurator/pull/2536)
- **Branch:** `fix/js-programming-decompiler-airspeed`
- **Previous work:** `completed/fix-js-programming-decompiler-airspeed/`
- **Repository:** inav-configurator

---

**Last Updated:** 2026-01-26
