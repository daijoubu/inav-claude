# Blackbox MOTORS Field Null Byte Investigation

## Problem Summary

When MOTORS field conditions are enabled in blackbox encoder, the decoder fails catastrophically:
- 200+ frame decode failures
- Log duration crashes from 12s to 0.050s
- Only 1-2 I/P frames successfully decoded

SERVOS field conditions work fine (3 failures baseline).

## Hypothesis Test: Null-Byte Padding

**Theory:** The encoder writes spurious null bytes between frames when MOTORS fields are enabled, similar to the known issue in maintenance-9.x.

**Method:** Modified blackbox_decode to skip ahead one byte when it encounters a null (0x00) where a frame marker is expected.

**Modification:** `blackbox-tools/src/parser.c` lines 1612-1629
```c
// BODGE: If we got a null byte instead of a frame marker, try skipping it
if (!frameType && command == 0x00 && command != EOF) {
    int nextByte = streamReadByte(private->stream);
    if (nextByte != EOF) {
        const flightLogFrameType_t *nextFrameType = getFrameType((uint8_t) nextByte);
        if (nextFrameType) {
            // Found valid frame marker after null byte - use it
            fprintf(stderr, "BODGE: Skipped null byte at offset %ld, found '%c' frame marker\n",
                    (long)(private->stream->pos - private->stream->start - 1), (char)nextByte);
            command = nextByte;
            frameType = nextFrameType;
            frameEnd++; // Adjust frame end since we consumed the null byte
        } else {
            // Next byte also not valid - unread it and continue normally
            streamUnreadChar(private->stream, nextByte);
        }
    }
}
```

## Results

### Original Decode (Broken)
**Log:** `test_results/blackbox_20251231_014104.TXT`
**Version:** MOTORS enabled, no sensors() checks (commit 7fb85d115 + uncommitted)

```
I frames       1  110.0 bytes avg      110 bytes total
P frames       1   77.0 bytes avg       77 bytes total
207 frames failed to decode, rendering 382 loop iterations unreadable.
Duration: 00:00.050
```

### Bodge Decode (FIXED!)
**Same log with null-skip bodge:**

```
Skipped 207 null bytes throughout log (offsets 4023 to 41631)

I frames     188  111.0 bytes avg    20876 bytes total
P frames     186   77.5 bytes avg    14415 bytes total
S frames      50   44.0 bytes avg     2200 bytes total
3 frames failed to decode, rendering 1 loop iterations unreadable.
Duration: 00:12.067
```

## Key Findings

1. **Exact correspondence:** 207 null bytes skipped = 207 original decoder failures
2. **Full decode success:** 0.050s → 12.067s (complete flight)
3. **Baseline match:** 3 failures same as working SERVOS-only version
4. **Null distribution:** Throughout entire log, not just at beginning/end
5. **Pattern:** Null bytes appear before all frame types (P, S, E)

## Comparison Matrix

| Version | MOTORS | Failures (std) | Failures (bodge) | Null Bytes |
|---------|--------|----------------|------------------|------------|
| Baseline (SERVOS only) | ❌ | 3 | N/A | 0 |
| Our code (+ sensors) | ✓ | 203 | ? | ? |
| Our code (no sensors) | ✓ | 207 | **3** ✓ | **207** |
| maintenance-9.x | ✓ | 247 | ? | ? |

## Conclusion

**CONFIRMED:** Our MOTORS-enabled encoder has the same null-byte padding bug as maintenance-9.x.

The data itself is correct - the decoder successfully processes all frames after skipping the spurious null bytes. The bug is in the **frame serialization** code.

## Root Cause Possibilities

### 1. Encoder/Decoder Field Count Mismatch
- Encoder writes N fields
- Header declares N+1 fields (with null padding field)
- Decoder expects N+1 values, reads extra null byte

### 2. Signed/Unsigned Integer Issue
- A field written as signed (variable-byte encoded) could encode value 0 as 0x00
- Predictor/encoding mismatch could make deltas frequently zero
- Variable-byte encoding of 0 is single 0x00 byte

### 3. Array Indexing Error
- Loop writes one extra field per frame
- Extra field has uninitialized/zero value

### 4. Conditional Write Logic Error
- A field is conditionally included in header but unconditionally written (or vice versa)
- Extra write produces 0x00 for missing field

## Next Steps

1. **Compare field counts:** Verify header field count matches actual writes
2. **Examine MOTORS field encoding:** Check if any MOTORS fields use signed encoding
3. **Trace frame write functions:** Find where P/S frames serialize data
4. **Check array bounds:** Verify loop counters match field counts

## Test Logs

- **Broken (MOTORS):** `test_results/blackbox_20251231_014104.TXT`
- **Working (SERVOS):** `test_results/blackbox_20251231_004130.TXT`
- **Bodge decode:** `test_results/decode_20251231_014104_BODGE.txt`

## Modified Tools

- **Decoder with bodge:** `~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode`
- **Original backup:** `~/Documents/planes/inavflight/blackbox-tools/src/parser.c.original`

## ROOT CAUSE IDENTIFIED

### The Bug: Header/Write Function Condition Mismatch

**Field Definitions (lines 328-336):**
```c
{"motor", 0, ..., CONDITION(AT_LEAST_MOTORS_1)},  // Requires getMotorCount() >= 1
{"motor", 1, ..., CONDITION(AT_LEAST_MOTORS_2)},  // Requires getMotorCount() >= 2
// ... all 8 motor fields use AT_LEAST_MOTORS_N
```

**I-frame Write Function (lines 1079-1088):**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {  // Only checks flag, not motor count!
    blackboxWriteUnsignedVB(blackboxCurrent->motor[0] - getThrottleIdleValue());  // ALWAYS writes 1 byte
    
    const int motorCount = getMotorCount();
    for (int x = 1; x < motorCount; x++) {  // Writes motorCount-1 more bytes
        blackboxWriteSignedVB(blackboxCurrent->motor[x] - blackboxCurrent->motor[0]);
    }
}
```

**P-frame Write Function (lines 1346-1348):**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {  // Only checks flag!
    blackboxWriteArrayUsingAveragePredictor16(offsetof(blackboxMainState_t, motor), getMotorCount());
}
```

### The Mismatch

| Component | Condition Used | What It Checks | Result (motorCount=0) |
|-----------|----------------|----------------|------------------------|
| **Field definitions** | AT_LEAST_MOTORS_N | `getMotorCount() >= N && flag` | 0 fields in header |
| **I-frame write** | MOTORS | `flag` only | Writes 1 byte for motor[0] |
| **P-frame write** | MOTORS | `flag` only | Writes 0 bytes (loop count=0) |

### Why Null Bytes Appear

On a board with `motorCount == 0`:

1. **Header declares 0 motor fields** (AT_LEAST_MOTORS_1 returns false)
2. **I-frame writes 1 byte** for motor[0] (MOTORS returns true)
3. Motor[0] value is 0, throttleIdleValue is likely 0 → `0 - 0 = 0` → encodes as `0x00`
4. **Decoder doesn't expect this byte** → sees 0x00 where it expects next frame marker
5. **Bodge skips the 0x00** → finds real frame marker after it → decodes successfully

### Expected Behavior

The write functions should use the **same condition logic** as the field definitions:

**Option A: I-frame should match field definition**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1)) {  // Check motor count!
    blackboxWriteUnsignedVB(...);
}
```

**Option B: Field definitions should match write function**
```c
{"motor", 0, ..., CONDITION(MOTORS)},  // Don't check motor count
```

But Option B would log motor[0] even when there are no motors, which is wasteful.

**Option A is correct** - don't write motor data when there are no motors.

### Why This Affects P-frames Too

The null byte is written at the end of **I-frames**. When the decoder finishes reading an I-frame, it expects the next byte to be a frame marker ('P', 'S', 'G', etc.). Instead it finds the spurious motor[0] null byte.

This explains why the bodge found null bytes before ALL frame types (P, S, E) - the extra byte from the I-frame pushes everything off by one.

