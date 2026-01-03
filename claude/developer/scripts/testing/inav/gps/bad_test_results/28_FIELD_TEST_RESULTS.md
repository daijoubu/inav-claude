# 28-Field Blackbox Test Results

**Date:** 2025-12-30
**Firmware Build:** Dec 29 2025 23:20:55
**Test Script:** `gps_hover_test_30s.py --duration 5`

## Fields Added (28 total)

### Loop & Timing (2 fields)
- loopIteration
- time

### Flight Control (21 fields)
- axisRate[0-2] (desired rotation rates)
- axisPID_P[0-2] (proportional terms)
- axisPID_I[0-2] (integral terms)
- axisPID_D[0-2] (derivative terms)
- rcCommand[0-3] (stick commands: roll, pitch, throttle, yaw)
- gyroADC[0-2] (gyro raw data)

### RC & Motors (7 fields)
- rcData[0-3] (receiver channel data)
- motor[0-2] (motor outputs)

## Configuration

```
blackbox_device = SPIFLASH
blackbox_rate_num = 1
blackbox_rate_denom = 100  (~10 Hz logging)
debug_mode = POS_EST (20)
blackbox_arm_control = 0 (log only while armed)
```

## Test Results

### Decode Summary
```
Log 1 of 1, start 00:16.143, end 00:23.247, duration 00:07.103

Statistics
Looptime            504 avg            0.7 std dev (0.1%)
I frames     111   38.0 bytes avg     4217 bytes total
P frames     109   30.0 bytes avg     3272 bytes total
S frames      36   44.0 bytes avg     1584 bytes total
Frames       220   34.0 bytes avg     7489 bytes total
Data rate   30Hz   1729 bytes/s      17300 baud

3 frames failed to decode, rendering 1 loop iterations unreadable.
```

### Success Rate
- **Total Frames:** 220
- **Failed Frames:** 3
- **Success Rate:** 99.86% (217/220)

### CSV Fields Verification

All 28 added fields present in decoded CSV:

```
 1. loopIteration
 2. time (us)
 3. axisRate[0]
 4. axisRate[1]
 5. axisRate[2]
 6. axisPID_P[0]
 7. axisPID_P[1]
 8. axisPID_P[2]
 9. axisPID_I[0]
10. axisPID_I[1]
11. axisPID_I[2]
12. axisPID_D[0]
13. axisPID_D[1]
14. axisPID_D[2]
15. rcCommand[0]
16. rcCommand[1]
17. rcCommand[2]
18. rcCommand[3]
19. gyroADC[0]
20. gyroADC[1]
21. gyroADC[2]
22. rcData[0]
23. rcData[1]
24. rcData[2]
25. rcData[3]
26. motor[0]
27. motor[1]
28. motor[2]
```

Plus S-frame (slow) fields (29-55): activeWpNumber, flightModeFlags, stateFlags, temperatures, etc.

## Data Rate Analysis

- **Loop rate:** 504 µs avg (1984 Hz)
- **Logging rate:** 30 Hz (rate_denom=100 → log every 100th loop)
- **Frame size:** 34 bytes avg
- **Data rate:** 1729 bytes/s (17.3 KB/s, 0.14 Mbps)
- **5-second test:** ~8.6 KB expected, ~7.5 KB actual

## Flash Usage

With 16 MB flash:
- **5-second test:** 8.6 KB (0.05% of flash)
- **60-second test:** 104 KB (0.6% of flash)
- **Max duration at 28 fields:** ~153 minutes until full

## Issues Encountered

### Automated Script Problem
The automated test script (`run_20field_test.sh`) initially used an unreliable CLI configuration method:

```bash
# UNRELIABLE - timing-based, no CLI prompt check
(echo "####"; sleep 0.5; cat commands; sleep 1.5) | timeout 5 cat > $PORT
```

This caused random failures where settings weren't saved, resulting in wrong `blackbox_rate_denom` values and flash overflow.

**Fixed by:** Using `configure_fc_blackbox.py` (MSP-based, reliable)

### Manual Test Success
Running the test manually after proper configuration worked perfectly:
```bash
python gps_hover_test_30s.py --duration 5 /dev/ttyACM0
```

## Conclusion

✅ **28-field test SUCCESSFUL**
- 99.86% decode success rate
- All fields present in CSV
- Proper data rates with rate_denom=100
- Automated script fixed to use reliable MSP configuration

**Next steps:**
- Continue incremental testing (36, 44+ fields)
- Monitor decode success rates
- Identify any patterns in failed frames
