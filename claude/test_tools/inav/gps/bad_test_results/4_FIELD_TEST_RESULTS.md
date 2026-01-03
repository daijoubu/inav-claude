# INAV Blackbox 4-Field Test Results

**Date:** 2025-12-29
**Test:** Incremental field testing (4 fields)
**Firmware:** INAV 9.0.0 JHEMCUF435 (modified)
**Decoder:** blackbox_decode 9.0.0-rc1 030eebf

## Fields Tested

**Main fields (I/P frames):**
1. `loopIteration` - UNSIGNED, predictor: 0 → INC, encoding: UNSIGNED_VB → NULL
2. `time` - UNSIGNED, predictor: 0 → STRAIGHT_LINE, encoding: UNSIGNED_VB → SIGNED_VB
3. `axisRate[0]` - SIGNED, predictor: 0 → PREVIOUS, encoding: SIGNED_VB → SIGNED_VB
4. `axisRate[1]` - SIGNED, predictor: 0 → PREVIOUS, encoding: SIGNED_VB → SIGNED_VB

**Source:** `axisPID_Setpoint[]` array (contains axisRate values)

## Test Data

- **Duration:** 32.084 seconds (00:16.129 to 00:48.213)
- **Total frames:** 994 (498 I-frames, 496 P-frames, 119 S-frames)
- **Data rate:** 30Hz, 474 bytes/s (4800 baud)
- **Flash used:** 15,239 bytes (14.9 KB)
- **Logging rate:** 1/100 (blackbox_rate setting)

## Decode Results

### Success Rate
- **Failed frames:** 3 out of 994 total frames
- **Success rate:** 99.7%
- **Loop iterations unreadable:** 1
- **Missing time:** 0ms (0.00%)

### Statistics
```
Looptime            503 avg            0.5 std dev (0.1%)
I frames     498    9.7 bytes avg     4851 bytes total
P frames     496    6.0 bytes avg     2976 bytes total
S frames     119   44.0 bytes avg     5236 bytes total
Frames       994    7.9 bytes avg     7827 bytes total
Data rate   30Hz    474 bytes/s       4800 baud
```

## CSV Output Sample

```csv
loopIteration,time (us),axisRate[0],axisRate[1],...
0,16129008,0,0,...
100,16179455,0,0,...
128,16193579,0,0,...
228,16244026,0,0,...
```

**Note:** Additional S-frame fields (slow data) are present but not part of this test.

## Field Values

- **loopIteration:** Increments properly (0, 100, 128, 228...)
- **time (us):** Increments properly (16129008, 16179455, 16193579...)
- **axisRate[0]:** All zeros (expected - FC stationary on bench)
- **axisRate[1]:** All zeros (expected - FC stationary on bench)

## Comparison with 2-Field Test

| Metric | 2-Field Test | 4-Field Test | Change |
|--------|--------------|--------------|--------|
| Success rate | 99.8% | 99.7% | -0.1% |
| Failed frames | 3 | 3 | Same |
| Total frames | ~1000 | 994 | Similar |
| Duration | ~30s | 32s | Similar |

**Conclusion:** Adding 2 more fields (axisRate[0] and axisRate[1]) did not introduce new decode failures. The 3 frame failures appear to be consistent across tests and unrelated to the specific fields being logged.

## Firmware Modifications

### Field Definitions (blackbox.c lines 205-211)
```c
static const blackboxDeltaFieldDefinition_t blackboxMainFields[] = {
    /* 4-FIELD TEST - loopIteration, time, axisRate[0], axisRate[1] */
    {"loopIteration",-1, UNSIGNED, .Ipredict = PREDICT(0),     .Iencode = ENCODING(UNSIGNED_VB), .Ppredict = PREDICT(INC),           .Pencode = FLIGHT_LOG_FIELD_ENCODING_NULL, CONDITION(ALWAYS)},
    {"time",       -1, UNSIGNED, .Ipredict = PREDICT(0),       .Iencode = ENCODING(UNSIGNED_VB), .Ppredict = PREDICT(STRAIGHT_LINE), .Pencode = ENCODING(SIGNED_VB), CONDITION(ALWAYS)},
    {"axisRate",    0, SIGNED,   .Ipredict = PREDICT(0),       .Iencode = ENCODING(SIGNED_VB),   .Ppredict = PREDICT(PREVIOUS),      .Pencode = ENCODING(SIGNED_VB), CONDITION(ALWAYS)},
    {"axisRate",    1, SIGNED,   .Ipredict = PREDICT(0),       .Iencode = ENCODING(SIGNED_VB),   .Ppredict = PREDICT(PREVIOUS),      .Pencode = ENCODING(SIGNED_VB), CONDITION(ALWAYS)},
};
```

### I-frame writes (blackbox.c line 675)
```c
// *** 4-FIELD TEST: axisRate[0,1] (axisPID_Setpoint) ***
blackboxWriteSignedVBArray(blackboxCurrent->axisPID_Setpoint, 2);  // Only write 2 elements
```

### P-frame delta writes (blackbox.c lines 906-908)
```c
// *** 4-FIELD TEST: axisRate[0,1] delta (axisPID_Setpoint) ***
int32_t deltas[8];
arraySubInt32(deltas, blackboxCurrent->axisPID_Setpoint, blackboxLast->axisPID_Setpoint, 2);  // Only 2 elements
blackboxWriteSignedVBArray(deltas, 2);
```

## Test Environment

- **Hardware:** JHEMCU F435 flight controller
- **Build:** `make JHEMCUF435` (clean rebuild)
- **Flash method:** DFU (dfu-util)
- **Test script:** `gps_hover_test_30s.py` (killed after 20s for 15s of data)
- **Download method:** MSP (download_blackbox_from_fc.py)
- **Blackbox flash:** Erased before test to ensure clean data

## Files

- **Firmware:** `inav/build/inav_9.0.0_JHEMCUF435.hex`
- **Raw log:** `claude/test_tools/inav/gps/test_results/blackbox_4_fields.TXT` (15,239 bytes)
- **Decoded CSV:** `claude/test_tools/inav/gps/test_results/blackbox_4_fields.01.csv`

## Next Steps

Continue incremental testing by adding more fields to identify the full set of fields that decode successfully.

**Candidates for next test:**
- axisRate[2] (yaw)
- axisPID_P[0,1,2] (PID P terms)
- axisPID_I[0,1,2] (PID I terms)
- axisPID_D[0,1,2] (PID D terms)
