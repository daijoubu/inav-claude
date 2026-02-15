# Investigation: DShot Sends Incorrect 0048 Value After Reverse

**Issue:** [#10648](https://github.com/iNavFlight/inav/issues/10648)
**Status:** CONFIRMED BUG - Ready for Investigation
**Priority:** Medium
**Severity:** Code Bug - Incorrect motor direction signal
**Created:** 2026-02-01
**Assigned To:** Developer

---

## Problem Description

✅ **CONFIRMED BUG (2026-02-01):** This is definitely a bug in the mixer state machine.

INAV rover is sending a **DShot value of 0048** (minimum reverse) when RC stick transitions from neutral to forward **after** being in reverse.

**Why This Is Wrong:**

In bidirectional (3D) mode, the RC stick operates as:
- **Stick BELOW center** = Reverse (48-1047, where 1047 is max reverse at stick bottom)
- **Stick AT center** = Neutral (0)
- **Stick ABOVE center** = Forward (1048-2047, where 2047 is max forward at stick top)

When the user moves stick **upward from center** (forward direction), the system should send **forward values (≥1048)**, but instead it sends **0048 which is a REVERSE value**.

**Impact:** Motor briefly tries to spin **backward** before the next update corrects to forward, causing:
- Unexpected motor behavior
- Mechanical stress on drivetrain
- Potential control instability

### Correct Behavior
- First non-zero command when transitioning from neutral to forward should be **≥1048**
- This works correctly when:
  - Initial transition from neutral to forward (first arming)
  - Transition to forward when prior non-neutral command was forward

### Incorrect Behavior
- When transitioning from neutral to forward **after being in reverse**, first value is **0048**
- This value should not exist in the DShot protocol for normal motor control
- Appears to be mixing reverse and forward values incorrectly

---

## Reproduction Steps

From issue #10648, the sequence is:

```
Count | DShot | Action
------|-------|-------
6561  | 0000  | Armed neutral
76    | 1048  | Transition forward ✓ CORRECT
3     | 1050  | Increase forward
...   | ...   | Continue forward
22    | 1048  | Decrease forward
54    | 0000  | Transition to neutral
3     | 0107  | Transition to reverse ✓ CORRECT
3     | 0114  | Increase reverse
...   | ...   | Continue reverse
3     | 0116  | Decrease reverse
11362 | 0000  | Transition to neutral
41    | 0048  | ❌ WRONG - Transition forward (should be ≥1048)
3     | 1052  | Increase forward ✓ (now correct)
```

**Key Pattern:**
- Only happens after reverse → neutral → forward sequence
- Does NOT happen on forward → neutral → forward sequence

---

## Technical Context

### DShot Protocol Values

DShot uses 11-bit values (0-2047):

| Range | Meaning |
|-------|---------|
| 0000 | Motor stop / disarmed |
| 0001-0047 | **RESERVED / Special commands** |
| 0048-1047 | **REVERSE** (reverse throttle range) |
| 1048-2047 | **FORWARD** (forward throttle range) |

**The value 0048 is the boundary between special commands and reverse range.**

Sending **0048** when intending **forward** motion (≥1048) suggests:
- Bit corruption or truncation (upper bits lost?)
- Incorrect value calculation in mixer
- State machine not clearing reverse mode flag
- Bidirectional DShot mode confusion

---

## Suspected Root Cause

Based on the value pattern, likely causes:

1. **Mixer State Machine Bug**
   - Reverse mode flag not clearing properly
   - Next forward command incorrectly offset into reverse range

2. **Value Calculation Error**
   - Integer overflow/underflow when transitioning from reverse offset
   - Incorrect base offset applied (should add 1000 to get 1048, adding 0 gives 0048)

3. **Bidirectional DShot Logic**
   - Reverse throttle uses 48-1047 range
   - Forward throttle uses 1048-2047 range
   - Boundary condition not handled correctly

---

## Investigation Tasks

- [ ] **Locate DShot mixer code**
  - Find where DShot values are calculated for rovers
  - Identify bidirectional DShot handling
  - Check state machine for reverse/forward transitions

- [ ] **Identify value calculation bug**
  - Trace where 0048 is generated vs 1048
  - Check offset calculations when switching from reverse
  - Verify state clearing on neutral transitions

- [ ] **Reproduce in SITL**
  - Configure SITL as rover with bidirectional DShot
  - Follow exact reproduction sequence
  - Capture DShot output values
  - Confirm bug exists in current master

- [ ] **Develop fix**
  - Clear reverse mode state on neutral transition
  - Ensure forward offset (1000) applied correctly
  - Add boundary checks for value range

- [ ] **Test fix**
  - Verify forward-neutral-forward still works
  - Verify reverse-neutral-forward now correct
  - Test edge cases (rapid direction changes)
  - Hardware test if possible

---

## Files to Investigate

Likely locations in INAV codebase:

```
inav/src/main/flight/mixer.c          # Main mixer logic
inav/src/main/drivers/dshot.c         # DShot driver
inav/src/main/drivers/pwm_output.c    # PWM/DShot output
inav/src/main/fc/rc_controls.c        # RC input processing
```

Search for:
- Bidirectional DShot handling
- Reverse throttle calculations
- Rover mixer specific code
- Value offset application (1000 offset for forward)

---

## Configuration

From issue reporter (INAV 8.0.0):

```
FC: MATEKF722MINI
Firmware: INAV 8.0.0 (Jan 21 2025)
Platform: Rover
Motors: Bidirectional DShot
```

CLI dump: [INAV_8.0.0_cli_MAXX_20250126_084307.txt](https://github.com/user-attachments/files/18550669/INAV_8.0.0_cli_MAXX_20250126_084307.txt)

---

## Expected Deliverables

1. Root cause analysis document
2. Code fix (PR-ready)
3. Test results (SITL + hardware if available)
4. Regression test to prevent recurrence

---

## Priority Justification

**Medium priority** because:
- ✅ Clear reproduction steps
- ✅ Isolated to specific sequence (reverse → forward)
- ✅ Affects rover platform specifically
- ⚠️ Could cause unexpected motor behavior
- ⚠️ Not critical safety issue (0048 is low throttle, not full)
- ⚠️ Workaround exists (pause at neutral before direction change)

**Lower than #10913** (motors spinning after disarm) but **higher than enhancements**.

---

## Related Issues

- #10913 - DShot erroneous signal after disarm (fixed by PR #11260)
- #9441 - DShot ESCs reboot on save
- #10865 - Motor/Servo wrong direction on disarm

Pattern: Multiple DShot-related edge case bugs suggest DShot driver needs careful review.

---

## References

- Issue: https://github.com/iNavFlight/inav/issues/10648
- Reporter: pitts-mo
- Created: 2025-01-26
- Comments: 2
