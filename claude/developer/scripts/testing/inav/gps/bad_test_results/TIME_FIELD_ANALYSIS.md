# Time Field P-Frame Encoding Analysis

## Problem Statement

In the 2-field minimal test (only loopIteration + time), 290 out of ~838 P-frames fail to decode, despite the encoding logic appearing mathematically correct.

## Field Definitions

From `/home/raymorris/Documents/planes/inavflight/inav/src/main/blackbox/blackbox.c` line 208:

```c
{"time", -1, UNSIGNED,
 .Ipredict = PREDICT(0),       .Iencode = ENCODING(UNSIGNED_VB),
 .Ppredict = PREDICT(STRAIGHT_LINE), .Pencode = ENCODING(SIGNED_VB),
 CONDITION(ALWAYS)
},
```

- **I-frame**: Write absolute time value using UNSIGNED_VB encoding
- **P-frame**: Use STRAIGHT_LINE prediction, write delta using SIGNED_VB encoding

## STRAIGHT_LINE Predictor Definition

From `/home/raymorris/Documents/planes/inavflight/inav/src/main/blackbox/blackbox_fielddefs.h` lines 119-120:

> "Predict that the slope between this field and the previous item is the same as that between the past two history items"

Mathematical formula:
```
predicted_value = 2 * previous - previous2
```

This is first-order linear extrapolation.

## Encoder Implementation

### P-Frame Write (blackbox.c line 909)

```c
blackboxWriteSignedVB((int32_t) (blackboxHistory[0]->time - 2 * blackboxHistory[1]->time + blackboxHistory[2]->time));
```

Where:
- `blackboxHistory[0]` = current frame being written
- `blackboxHistory[1]` = previous frame (t-1)
- `blackboxHistory[2]` = frame before previous (t-2)

This writes: `current - 2*prev + prev2`

Which can be rewritten as: `(current - prev) - (prev - prev2)` (second-order difference)

### Encoder History Buffer Rotation (blackbox.c lines 859-863, 1115-1117)

**After writing I-frame:**
```c
blackboxHistory[1] = blackboxHistory[0];  // Both history[1] and
blackboxHistory[2] = blackboxHistory[0];  // history[2] point to I-frame
blackboxHistory[0] = ((blackboxHistory[0] - blackboxHistoryRing + 1) % 3) + blackboxHistoryRing;
```

**After writing P-frame:**
```c
blackboxHistory[2] = blackboxHistory[1];
blackboxHistory[1] = blackboxHistory[0];
blackboxHistory[0] = ((blackboxHistory[0] - blackboxHistoryRing + 1) % 3) + blackboxHistoryRing;
```

## Decoder Implementation

### P-Frame Read (blackbox-tools/src/parser.c line 665)

```c
value += 2 * previous[fieldIndex] - previous2[fieldIndex];
```

Where:
- `value` = delta read from log (using SIGNED_VB decoding)
- `previous` = mainHistory[1] (previous frame)
- `previous2` = mainHistory[2] (frame before previous)

Reconstructed value: `delta + 2*previous - previous2`

### Decoder History Buffer Rotation (parser.c lines 1416-1422)

**After parsing P-frame:**
```c
private->mainHistory[2] = private->mainHistory[1];
private->mainHistory[1] = private->mainHistory[0];
private->mainHistory[0] += FLIGHT_LOG_MAX_FIELDS;
if (private->mainHistory[0] >= &private->blackboxHistoryRing[3][0])
    private->mainHistory[0] = &private->blackboxHistoryRing[0][0];
```

**After parsing I-frame (lines 1373-1374):**
```c
private->mainHistory[1] = private->mainHistory[0];  // Both point to
private->mainHistory[2] = private->mainHistory[0];  // I-frame
```

## Mathematical Verification

### Normal P-Frame (with 2+ history frames)

**Encoder writes:**
```
delta = current - 2*prev + prev2
```

**Decoder predicts:**
```
predicted = 2*prev - prev2
```

**Decoder reconstructs:**
```
reconstructed = delta + predicted
              = (current - 2*prev + prev2) + (2*prev - prev2)
              = current ✓ CORRECT
```

### First P-Frame After I-Frame

At this point, `prev == prev2 == I-frame`

**Encoder writes:**
```
delta = current - 2*I_time + I_time
      = current - I_time
```

**Decoder predicts:**
```
predicted = 2*I_time - I_time
          = I_time
```

**Decoder reconstructs:**
```
reconstructed = delta + predicted
              = (current - I_time) + I_time
              = current ✓ CORRECT
```

## Conclusion: Math is Correct

The STRAIGHT_LINE predictor formula is **identical** between encoder and decoder:
- Encoder writes: `current - 2*prev + prev2`
- Decoder expects: `delta + 2*prev - prev2`
- History buffer rotations match on both sides

**The encoding/decoding logic is mathematically correct and should work.**

## Possible Bug Locations

Since the math is correct, the bug must be in:

1. **SIGNED_VB encoding/decoding mismatch**
   - Encoder uses `blackboxWriteSignedVB()`
   - Decoder uses `streamReadSignedVB()` or equivalent
   - Check zigzag encoding: `(value << 1) ^ (value >> 31)`

2. **Time value overflow**
   - Time is declared as UNSIGNED but encoded as SIGNED (for deltas)
   - Check if time values exceed 31-bit range causing sign issues
   - Check if second-order differences create unexpected values

3. **Parser state machine desync**
   - After a failed P-frame, does decoder recover correctly?
   - Is `mainStreamIsValid` flag causing cascading failures?

4. **Decoder buffer addressing**
   - Check if `mainHistory[0] += FLIGHT_LOG_MAX_FIELDS` calculation is correct
   - Check if ring buffer wrap-around works properly

5. **Version mismatch between firmware and decoder**
   - Encoder might be from different 9.0.0-rc1 build than decoder
   - Check git commit hash of both

## Recommended Next Steps

1. **Examine time values in raw log**
   - Use hex editor to look at actual bytes written after 'P' marker
   - Manually decode first few SIGNED_VB values
   - Check if values match expected deltas

2. **Add debug output to decoder**
   - Print predicted value, delta read, and reconstructed value for time field
   - Identify at which P-frame number decoding first fails

3. **Compare encoder/decoder SIGNED_VB implementations**
   - Verify zigzag encoding formula matches
   - Check for endianness issues (unlikely on same platform)

4. **Test with constant time increments**
   - Modify firmware to write constant loop time (e.g., exactly 1000us)
   - Second-order difference should be exactly 0
   - Any non-zero delta indicates encoder bug

5. **Bisect INAV versions**
   - Test 8.0.0 stable (known working)
   - Test 9.0.0-rc1 (known broken)
   - Find exact commit where bug was introduced

## Files for Reference

- Encoder: `/home/raymorris/Documents/planes/inavflight/inav/src/main/blackbox/blackbox.c`
- Field definitions: `/home/raymorris/Documents/planes/inavflight/inav/src/main/blackbox/blackbox_fielddefs.h`
- Decoder: `/home/raymorris/Documents/planes/inavflight/blackbox-tools/src/parser.c`
- Predictor logic: `/home/raymorris/Documents/planes/inavflight/blackbox-tools/src/parser.c:630-700`
