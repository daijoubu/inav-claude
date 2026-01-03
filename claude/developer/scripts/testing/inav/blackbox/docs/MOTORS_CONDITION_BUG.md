# Blackbox MOTORS Condition Bug - Complete Analysis

## Executive Summary

**Bug:** I-frame motor write function uses wrong condition, causing header/data mismatch when `BLACKBOX_FEATURE_MOTORS` is enabled but `getMotorCount() == 0`.

**Impact:** Decoder fails catastrophically (200+ frame failures) on aircraft with no motors (fixed-wing with servos only).

**Root Cause:** Inconsistent condition checks between field definitions and write functions.

**Fix:** Change I-frame write condition from `FLIGHT_LOG_FIELD_CONDITION_MOTORS` to `FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1`.

---

## The Bug in Detail

### Field Definitions vs Write Functions

**File:** `inav/src/main/blackbox/blackbox.c`

**Field Definitions (lines 328-336):**
```c
static const blackboxDeltaFieldDefinition_t blackboxMainFields[] = {
    // ...
    {"motor", 0, UNSIGNED, .Ipredict = PREDICT(MINTHROTTLE), .Iencode = ENCODING(UNSIGNED_VB),
     .Ppredict = PREDICT(AVERAGE_2), .Pencode = ENCODING(SIGNED_VB),
     CONDITION(AT_LEAST_MOTORS_1)},  // ← Requires motorCount >= 1 AND flag

    {"motor", 1, UNSIGNED, .Ipredict = PREDICT(MOTOR_0), .Iencode = ENCODING(SIGNED_VB),
     .Ppredict = PREDICT(AVERAGE_2), .Pencode = ENCODING(SIGNED_VB),
     CONDITION(AT_LEAST_MOTORS_2)},  // ← Requires motorCount >= 2 AND flag

    // ... motors 2-7 all use AT_LEAST_MOTORS_N
};
```

**Condition Implementation (lines 652-662):**
```c
case FLIGHT_LOG_FIELD_CONDITION_MOTORS:
    return blackboxIncludeFlag(BLACKBOX_FEATURE_MOTORS);  // Only checks flag

case FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1:
case FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_2:
// ... through AT_LEAST_MOTORS_8:
    return (getMotorCount() >= condition - FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1 + 1)
           && blackboxIncludeFlag(BLACKBOX_FEATURE_MOTORS);  // Checks BOTH count AND flag
```

**I-frame Write Function (lines 1079-1088) - THE BUG:**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {  // ← Only checks flag!
    // This executes when flag is set, regardless of motor count
    blackboxWriteUnsignedVB(blackboxCurrent->motor[0] - getThrottleIdleValue());

    const int motorCount = getMotorCount();
    for (int x = 1; x < motorCount; x++) {
        blackboxWriteSignedVB(blackboxCurrent->motor[x] - blackboxCurrent->motor[0]);
    }
}
```

**P-frame Write Function (lines 1346-1348):**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {  // ← Only checks flag!
    // Loop count is motorCount, so happens to write 0 bytes when motorCount=0
    blackboxWriteArrayUsingAveragePredictor16(offsetof(blackboxMainState_t, motor), getMotorCount());
}
```

---

## The Failure Scenario

### Configuration
- **Hardware:** Flight controller with 0 motors (e.g., fixed-wing with servos only)
- **Software:** Default blackbox config has `BLACKBOX_FEATURE_MOTORS = true`
- **Runtime:** `getMotorCount() = 0`

### What Happens

| Step | Component | Condition | Check | Result |
|------|-----------|-----------|-------|--------|
| 1 | Field definition | AT_LEAST_MOTORS_1 | `(0 >= 1) && true` | **FALSE** → 0 motor fields |
| 2 | Header generation | Uses field count | ARRAYLEN filters FALSE conditions | **0 motor fields in header** |
| 3 | I-frame write | **MOTORS** | `true` only | **TRUE** → Executes write block |
| 4 | Motor[0] write | Unconditional | Always runs inside block | **Writes 1 byte** |
| 5 | Motor[1-N] loop | `for (x=1; x<0; x++)` | Loop never executes | **Writes 0 bytes** |
| 6 | **Total I-frame** | — | — | **Writes 1 spurious byte** |
| 7 | P-frame write | MOTORS | `true` only | TRUE → Executes write |
| 8 | Motor array write | Loop count = `getMotorCount()` | `count = 0` | **Writes 0 bytes** (correct by accident) |

### The Spurious Byte Value

```c
blackboxWriteUnsignedVB(blackboxCurrent->motor[0] - getThrottleIdleValue());
```

On a board with no motors:
- `motor[0]` is uninitialized or 0
- `getThrottleIdleValue()` returns 0 (no motors configured)
- `0 - 0 = 0`
- `blackboxWriteUnsignedVB(0)` encodes as `0x00` (single null byte)

---

## Decoder Impact

### Expected Frame Sequence
```
[I-frame data...] [next frame marker 'P']
```

### Actual Frame Sequence (with bug)
```
[I-frame data...] [spurious 0x00] [next frame marker 'P']
```

### Decoder Behavior
1. Finishes reading I-frame according to header field count
2. Expects next byte to be frame marker ('P', 'S', 'G', 'E', etc.)
3. Reads `0x00` instead
4. `0x00` is not a valid frame marker
5. Treats previous frame as corrupt
6. Attempts to resynchronize by scanning forward
7. Finds 'P' marker at wrong offset
8. All subsequent frames misaligned → catastrophic failure

### Observed Failure Pattern

**Without bodge (standard decoder):**
```
I frames       1  110.0 bytes avg      110 bytes total
P frames       1   77.0 bytes avg       77 bytes total
207 frames failed to decode, rendering 382 loop iterations unreadable.
Duration: 00:00.050 (should be 12s)
```

**With null-skip bodge:**
```
BODGE: Skipped null byte at offset 4023, found 'P' frame marker
BODGE: Skipped null byte at offset 4214, found 'P' frame marker
[... 207 total null bytes skipped ...]

I frames     188  111.0 bytes avg    20876 bytes total
P frames     186   77.5 bytes avg    14415 bytes total
S frames      50   44.0 bytes avg     2200 bytes total
3 frames failed to decode, rendering 1 loop iterations unreadable.
Duration: 00:12.067 ✓
```

**Bodge proves the bug:**
- 207 null bytes skipped = 207 original decoder failures
- All null bytes appear where frame markers are expected
- After skipping null bytes, decoder works perfectly
- 3 remaining failures match working baseline (unrelated issue)

---

## Why This Went Undetected

1. **Most users have motors** - Multirotors have 4+ motors, so AT_LEAST_MOTORS_1 returns true
2. **Fixed-wing users may disable MOTORS** - Users without motors might disable the feature
3. **Servos use correct condition** - SERVOS condition works correctly, masking the pattern
4. **Default config enables MOTORS** - Flag is on by default regardless of hardware

---

## Test Evidence

### Test Platform
- **Board:** JHEMCUF435 (AT32F43x)
- **Configuration:** Fixed-wing with servos, no motors
- **Motor count:** `getMotorCount() = 0`
- **MOTORS flag:** Enabled (default config line 113)

### Test Results Matrix

| Version | MOTORS Cond | Motor Count | Fields in Header | I-frame Writes | Failures |
|---------|-------------|-------------|------------------|----------------|----------|
| Baseline (SERVOS only) | Disabled | 0 | 0 | 0 bytes | 3 |
| Bug (MOTORS enabled) | Enabled | 0 | 0 | **1 byte (0x00)** | 207 |
| Bug + bodge | Enabled | 0 | 0 | 1 byte (skipped) | 3 |

### Logs
- **Working:** `test_results/blackbox_20251231_004130.TXT` (SERVOS only, 3 failures)
- **Broken:** `test_results/blackbox_20251231_014104.TXT` (MOTORS enabled, 207 failures)
- **Bodge decode:** `test_results/decode_20251231_014104_BODGE.txt` (skips 207 nulls, 3 failures)

---

## The Fix

### Option A: Fix Write Function (RECOMMENDED)

**File:** `inav/src/main/blackbox/blackbox.c`
**Line:** 1079

**Change from:**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {
    blackboxWriteUnsignedVB(blackboxCurrent->motor[0] - getThrottleIdleValue());

    const int motorCount = getMotorCount();
    for (int x = 1; x < motorCount; x++) {
        blackboxWriteSignedVB(blackboxCurrent->motor[x] - blackboxCurrent->motor[0]);
    }
}
```

**Change to:**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1)) {
    blackboxWriteUnsignedVB(blackboxCurrent->motor[0] - getThrottleIdleValue());

    const int motorCount = getMotorCount();
    for (int x = 1; x < motorCount; x++) {
        blackboxWriteSignedVB(blackboxCurrent->motor[x] - blackboxCurrent->motor[0]);
    }
}
```

**Rationale:**
- Matches field definition condition exactly
- Won't write motor[0] when motorCount < 1
- Consistent with SERVOS implementation (which works correctly)
- P-frame already uses correct loop bounds, so needs no change

### Option B: Fix Field Definitions (NOT RECOMMENDED)

Change all motor field definitions to use `CONDITION(MOTORS)` instead of `CONDITION(AT_LEAST_MOTORS_N)`.

**Why not:**
- Would log motor[0] even when no motors exist (waste of space)
- Would log uninitialized/zero motor values
- Inconsistent with SERVOS pattern
- Less flexible for users

---

## P-frame Analysis

**Why P-frame doesn't have the bug:**

```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {
    blackboxWriteArrayUsingAveragePredictor16(offsetof(blackboxMainState_t, motor), getMotorCount());
}
```

The function uses `getMotorCount()` as the loop count:
```c
static void blackboxWriteArrayUsingAveragePredictor16(int arrOffsetInHistory, int count)
{
    // ...
    for (int i = 0; i < count; i++) {  // When count=0, loop doesn't execute
        blackboxWriteSignedVB(curr[i] - predictor);
    }
}
```

When `motorCount = 0`, the loop doesn't execute → 0 bytes written → **accidentally correct**.

But it's still using the wrong condition - it should use `AT_LEAST_MOTORS_1` for consistency.

---

## SERVOS Comparison (Working Correctly)

**Field definitions (lines 339-346):**
```c
{"servo", 0, UNSIGNED, ..., CONDITION(AT_LEAST_SERVOS_1)},
{"servo", 1, UNSIGNED, ..., CONDITION(AT_LEAST_SERVOS_2)},
// ...
```

**I-frame write (lines 1090-1095):**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_SERVOS)) {  // ← Uses SERVOS, not AT_LEAST_SERVOS_1!
    const int servoCount = getServoCount();
    for (int x = 0; x < servoCount; x++) {
        blackboxWriteSignedVB(blackboxCurrent->servo[x] - 1500);
    }
}
```

**Wait - SERVOS has the same pattern!**

But SERVOS works because:
- The write is a **loop starting at 0**, not an unconditional write + loop starting at 1
- When `servoCount = 0`, loop doesn't execute → 0 bytes written → correct!

**MOTORS is different:**
- Unconditional write of motor[0] **outside the loop**
- Loop for motors 1-N
- When `motorCount = 0`, still writes motor[0] → **1 spurious byte**

This is the key difference!

---

## Why SERVOS Works But MOTORS Doesn't

### SERVOS (Correct)
```c
if (condition) {
    for (int x = 0; x < count; x++) {  // Starts at 0, no writes outside loop
        write(servo[x]);
    }
}
```
When count=0: Loop doesn't execute → 0 bytes → ✓

### MOTORS (Broken)
```c
if (condition) {
    write(motor[0]);  // ← UNCONDITIONAL write when condition is true!
    for (int x = 1; x < count; x++) {  // Starts at 1, motor[0] already written
        write(motor[x]);
    }
}
```
When count=0: Writes motor[0] → 1 byte → ✗

---

## Complete Fix Verification

### Before Fix
```c
// Field definitions - lines 328-336
{"motor", 0, ..., CONDITION(AT_LEAST_MOTORS_1)},  // count >= 1 AND flag

// I-frame write - line 1079
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {  // flag only ← BUG
    blackboxWriteUnsignedVB(motor[0] - idle);  // Writes even when count=0
    for (int x = 1; x < motorCount; x++) { ... }
}

// P-frame write - line 1346
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {  // flag only ← BUG
    blackboxWriteArray(..., getMotorCount());  // Works by accident
}
```

**Result when motorCount=0, flag=true:**
- Header: 0 fields
- I-frame: 1 byte
- P-frame: 0 bytes
- **MISMATCH** → decoder fails

### After Fix
```c
// Field definitions - unchanged
{"motor", 0, ..., CONDITION(AT_LEAST_MOTORS_1)},  // count >= 1 AND flag

// I-frame write - line 1079
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1)) {  // count >= 1 AND flag ← FIXED
    blackboxWriteUnsignedVB(motor[0] - idle);
    for (int x = 1; x < motorCount; x++) { ... }
}

// P-frame write - line 1346 (optional consistency fix)
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1)) {  // count >= 1 AND flag ← FIXED
    blackboxWriteArray(..., getMotorCount());
}
```

**Result when motorCount=0, flag=true:**
- Header: 0 fields
- I-frame: 0 bytes
- P-frame: 0 bytes
- **MATCH** → decoder works ✓

---

## Implementation Notes

1. **Only I-frame strictly needs the fix** - P-frame works by accident due to loop starting at 0
2. **Both should be fixed for consistency** - Makes code maintainable
3. **No need to change field definitions** - They are already correct
4. **No need to change P-frame array write** - Already has implicit count check via loop
5. **Verify with same test case** - Flash fixed firmware, test on JHEMCUF435 with motorCount=0

---

## Related Code Locations

**File:** `inav/src/main/blackbox/blackbox.c`

| Line | Component | Current Condition | Should Be |
|------|-----------|-------------------|-----------|
| 328-336 | Field definitions | AT_LEAST_MOTORS_N | ✓ Correct |
| 652 | MOTORS condition impl | flag only | ✓ Correct (used elsewhere) |
| 662 | AT_LEAST_MOTORS impl | count + flag | ✓ Correct |
| 1079 | I-frame write | **MOTORS** | **AT_LEAST_MOTORS_1** ← FIX |
| 1346 | P-frame write | **MOTORS** | AT_LEAST_MOTORS_1 (optional) |

**Decoder bodge:** `blackbox-tools/src/parser.c:1612-1629`

---

## Affected Versions

- **INAV 9.x maintenance-9.x branch** - Confirmed broken (247 failures)
- **Our testing branch** - Confirmed broken (207 failures without sensors() checks, 203 with)
- **Upstream INAV master** - Likely affected (same pattern exists)

The 40-failure difference (247 vs 207) suggests there are other unrelated differences between maintenance-9.x and our branch, but the null-byte issue is the primary cause.

---

## Conclusion

This is a **clear encoder bug** with:
- ✓ Root cause identified (wrong condition in I-frame write)
- ✓ Mechanism understood (unconditional motor[0] write)
- ✓ Proof of concept (bodge decoder skips 207 null bytes)
- ✓ Simple fix (change one condition check)
- ✓ No decoder changes needed

The bug has existed for a long time but only affects users with:
1. `BLACKBOX_FEATURE_MOTORS` enabled AND
2. `getMotorCount() == 0`

This is a relatively rare combination (mostly fixed-wing with servos only), which explains why it went undetected.
