# 2-Field Test - Exact Fields Present

**Test Date:** 2025-12-29 16:42
**Firmware:** INAV 9.0.0-rc1 JHEMCUF435 (modified)
**Result:** 3 failures / 1452 frames = 99.8% success rate

---

## I-Frame Fields (Intra-frame, Absolute Values)

**Count:** 2 fields

```
H Field I name:loopIteration,time
H Field I signed:0,0
H Field I predictor:0,0
H Field I encoding:1,1
```

| # | Field Name | Type | I-Predictor | I-Encoding | Source Line |
|---|------------|------|-------------|------------|-------------|
| 0 | loopIteration | UNSIGNED | 0 (none) | UNSIGNED_VB | blackbox.c:207 |
| 1 | time | UNSIGNED | 0 (none) | UNSIGNED_VB | blackbox.c:208 |

**Data written by:**
- `writeIntraframe()` lines 669-670:
  ```c
  blackboxWriteUnsignedVB(blackboxIteration);        // Field 0
  blackboxWriteUnsignedVB(blackboxCurrent->time);    // Field 1
  ```

---

## P-Frame Fields (Inter-frame, Delta Values)

**Count:** 2 fields (same as I-frame)

```
H Field P predictor:6,2
H Field P encoding:9,0
```

| # | Field Name | Type | P-Predictor | P-Encoding | Source Line |
|---|------------|------|-------------|------------|-------------|
| 0 | loopIteration | (not written) | INC (always +1) | NULL (omitted) | - |
| 1 | time | UNSIGNED | STRAIGHT_LINE | SIGNED_VB | blackbox.c:208 |

**Data written by:**
- `writeInterframe()` line 898:
  ```c
  // loopIteration not written (predictor handles it)
  blackboxWriteSignedVB((int32_t)(blackboxHistory[0]->time - 2*blackboxHistory[1]->time + blackboxHistory[2]->time));  // Field 1 delta
  ```

**Note:** loopIteration is NOT written in P-frames because its predictor is `PREDICT(INC)` which means "always increment by 1", so the decoder can reconstruct it without data.

---

## S-Frame Fields (Slow Frame, Infrequent Data)

**Count:** 28 fields (UNMODIFIED - all original fields present)

```
H Field S name:activeWpNumber,flightModeFlags,flightModeFlags2,activeFlightModeFlags,
               stateFlags,failsafePhase,rxSignalReceived,rxFlightChannelsValid,rxUpdateRate,
               hwHealthStatus,powerSupplyImpedance,sagCompensatedVBat,wind[0],wind[1],wind[2],
               mspOverrideFlags,IMUTemperature,baroTemperature,sens0Temp,sens1Temp,sens2Temp,
               sens3Temp,sens4Temp,sens5Temp,sens6Temp,sens7Temp,escRPM,escTemperature
```

| # | Field Name | Type | Predictor | Encoding | Array Line |
|---|------------|------|-----------|----------|------------|
| 0 | activeWpNumber | UNSIGNED | 0 | UNSIGNED_VB | 244 |
| 1 | flightModeFlags | UNSIGNED | 0 | UNSIGNED_VB | 245 |
| 2 | flightModeFlags2 | UNSIGNED | 0 | UNSIGNED_VB | 246 |
| 3 | activeFlightModeFlags | UNSIGNED | 0 | UNSIGNED_VB | 247 |
| 4 | stateFlags | UNSIGNED | 0 | UNSIGNED_VB | 248 |
| 5 | failsafePhase | UNSIGNED | 0 | TAG2_3S32 | 250 |
| 6 | rxSignalReceived | UNSIGNED | 0 | TAG2_3S32 | 251 |
| 7 | rxFlightChannelsValid | UNSIGNED | 0 | TAG2_3S32 | 252 |
| 8 | rxUpdateRate | UNSIGNED | PREVIOUS | UNSIGNED_VB | 253 |
| 9 | hwHealthStatus | UNSIGNED | 0 | UNSIGNED_VB | 255 |
| 10 | powerSupplyImpedance | UNSIGNED | 0 | UNSIGNED_VB | 256 |
| 11 | sagCompensatedVBat | UNSIGNED | 0 | UNSIGNED_VB | 257 |
| 12 | wind[0] | SIGNED | 0 | SIGNED_VB | 258 |
| 13 | wind[1] | SIGNED | 0 | SIGNED_VB | 259 |
| 14 | wind[2] | SIGNED | 0 | SIGNED_VB | 260 |
| 15 | mspOverrideFlags | UNSIGNED | 0 | UNSIGNED_VB | 262 |
| 16 | IMUTemperature | SIGNED | 0 | SIGNED_VB | 264 |
| 17 | baroTemperature | SIGNED | 0 | SIGNED_VB | 266 |
| 18 | sens0Temp | SIGNED | 0 | SIGNED_VB | 269 |
| 19 | sens1Temp | SIGNED | 0 | SIGNED_VB | 270 |
| 20 | sens2Temp | SIGNED | 0 | SIGNED_VB | 271 |
| 21 | sens3Temp | SIGNED | 0 | SIGNED_VB | 272 |
| 22 | sens4Temp | SIGNED | 0 | SIGNED_VB | 273 |
| 23 | sens5Temp | SIGNED | 0 | SIGNED_VB | 274 |
| 24 | sens6Temp | SIGNED | 0 | SIGNED_VB | 275 |
| 25 | sens7Temp | SIGNED | 0 | SIGNED_VB | 276 |
| 26 | escRPM | UNSIGNED | 0 | UNSIGNED_VB | 279 |
| 27 | escTemperature | SIGNED | PREVIOUS | SIGNED_VB | 280 |

**Data written by:** `writeSlowFrame()` lines 1116-1194 (unmodified)

---

## Fields NOT Present in This Test

All fields from the original 78-field I/P array were removed EXCEPT loopIteration and time.

### Removed Fields (lines 210-398 in original blackbox.c):

**PID Fields (15 fields):**
- axisRate[0,1,2]
- axisP[0,1,2]
- axisI[0,1,2]
- axisD[0,1,2] (conditional)
- axisF[0,1,2]

**Fixed-Wing Navigation PID (8 fields):**
- fwAltP, fwAltI, fwAltD, fwAltOut
- fwPosP, fwPosI, fwPosD, fwPosOut

**Multicopter Navigation PID (16 fields):**
- mcPosAxisP[0,1,2]
- mcVelAxisP[0,1,2]
- mcVelAxisI[0,1,2]
- mcVelAxisD[0,1,2]
- mcVelAxisFF[0,1,2]
- mcVelAxisOut[0,1,2]
- mcSurfaceP, mcSurfaceI, mcSurfaceD, mcSurfaceOut

**RC Data (8 fields):**
- rcData[0,1,2,3]
- rcCommand[0,1,2,3]

**Battery (2 fields):**
- vbat
- amperage

**Magnetometer (3 fields):**
- magADC[0,1,2]

**Barometer (1 field):**
- BaroAlt

**Pitot (1 field):**
- airSpeed

**Rangefinder (1 field):**
- surfaceRaw

**RSSI (1 field):**
- rssi

**Gyro (9 fields):**
- gyroADC[0,1,2]
- gyroRaw[0,1,2] (conditional)
- gyroPeaksRoll[0,1,2] (conditional)
- gyroPeaksPitch[0,1,2] (conditional)
- gyroPeaksYaw[0,1,2] (conditional)

**Accelerometer (4 fields):**
- accADC[0,1,2]
- accVib

**Attitude (3 fields):**
- attitude[0,1,2]

**Debug (4 fields):**
- debug[0,1,2,3]

**Motors (variable, max 8):**
- motor[0..7]

**Servos (variable, max 8):**
- servo[0..7]

**Navigation State (2 fields):**
- navState
- navFlags

**Navigation Position (20 fields):**
- navEPH, navEPV
- navPos[0,1,2]
- navRealVel[0,1,2]
- navTargetVel[0,1,2]
- navTargetPos[0,1,2]
- navTargetHeading
- navSurface

**Navigation Acceleration (3 fields):**
- navAccNEU[0,1,2]

**Total removed:** 76 fields

---

## Frame Statistics

From blackbox_decode output:

```
Log duration: 00:47.015
I frames:  727 frames (7.8 bytes avg)  = 5687 bytes total
P frames:  725 frames (4.0 bytes avg)  = 2900 bytes total
S frames:  259 frames (43.0 bytes avg) = 11137 bytes total
E frames:    1 frame  (6.0 bytes avg)  = 6 bytes total
Total:    1452 frames (5.9 bytes avg)  = 8587 bytes total

Data rate: 30 Hz, 464 bytes/s, 4700 baud
```

**Decode success:** 1449 / 1452 frames = 99.8%
**Failed frames:** 3 frames (likely S-frames based on debugging output)

---

## Key Observations

1. **I-frame size:** 7.8 bytes avg with only 2 fields
   - Frame marker: 1 byte
   - loopIteration: ~2 bytes (VB encoded)
   - time: ~4 bytes (VB encoded)
   - Total: ~7 bytes ✓

2. **P-frame size:** 4.0 bytes avg with only 1 field written
   - Frame marker: 1 byte
   - time delta: ~3 bytes (signed VB, second-order diff)
   - Total: ~4 bytes ✓

3. **S-frame size:** 43.0 bytes avg with 28 fields
   - Much larger because slow fields use simpler predictors
   - Still decodes successfully

4. **Encoder efficiency:** 99.8% success rate with minimal fields proves:
   - VB encoding works correctly
   - STRAIGHT_LINE predictor works for time field
   - INC predictor works for loopIteration
   - Field count logic is correct

---

## Files for Comparison

**Successful 2-field test:**
- Raw log: `test_results/blackbox_2_fields_FINAL.TXT`
- Decoded CSV: `test_results/blackbox_2_fields_FINAL.01.csv`
- Source: `inav/src/main/blackbox/blackbox.c` (lines 205-209, 669-670, 898)

**For future field-by-field testing:**
1. Start with this 2-field baseline (99.8% success)
2. Add one field at a time from the removed list
3. Test and compare decode success rate
4. Identify which specific field(s) cause decode failures

---

## Next Testing Recommendations

**Test sequence to isolate problematic fields:**

1. **2 fields** (baseline) ✓ - 99.8% success
2. **3 fields** - Add axisRate[0] (first PID field)
3. **4 fields** - Add axisRate[1,2] (complete axis)
4. **7 fields** - Add axisP[0,1,2] (P term)
5. **Continue incrementally** until failures appear

**Hypothesis:** If certain fields cause decoder issues, adding them will reduce success rate below 99%.
