# Quick Start: Automatic Blackbox Rates

## What Changed?

The test suite now **automatically sets the optimal blackbox rate** for each test before running. No manual configuration needed!

---

## Common Usage

### Run baseline tests (Tests 1-6)
```bash
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.3.3
```
✓ Automatically uses 1/2 rate (70 KB/s) for all baseline tests

### Run 1-hour stability test (Test 9)
```bash
python sd_card_test.py /dev/ttyACM0 --test 9
```
✓ Automatically uses 1/2 rate (70 KB/s) for ≤60 min test

### Run 4-hour validation test (Test 9)
```bash
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 240
```
✓ Automatically uses 1/4 rate (35 KB/s) for 240 min test

### Run 12-hour overnight test (Test 9)
```bash
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 720
```
✓ Automatically uses 1/8 rate (17.5 KB/s) for 720 min test

### Force a specific rate (override automatic selection)
```bash
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 720 --test9-blackbox-rate 1/16
```
✓ Override automatic 1/8 selection with 1/16 rate for ultra-conservative space usage

---

## Automatic Rate Selection Table

| Test | Duration | Auto Rate | Data/Hour | Status |
|------|----------|-----------|-----------|--------|
| 1 | ~1 min | 1/2 | 252 MB | ✓ Full detail |
| 2 | ~1 min | 1/2 | 252 MB | ✓ Full detail |
| 3 | ~5 min | 1/2 | 252 MB | ✓ Full detail |
| 4 | ~1 min | 1/2 | 252 MB | ✓ Full detail |
| 6 | ~2 min | 1/2 | 252 MB | ✓ Full detail |
| 8 | ~1-2 min | 1/2 | 252 MB | ✓ Full detail |
| 9 | ≤60 min | 1/2 | 252 MB | ✓ Full detail |
| 9 | 61-240 min | 1/4 | 126 MB | ✓ Good detail |
| 9 | 241-480 min | 1/4 | 126 MB | ✓ Good detail |
| 9 | 481+ min | 1/8 | 63 MB | ✓ Conservative |
| 10 | ~10 min | 1/2 | 252 MB | ✓ Full detail |
| 11 | ~1-2 min | 1/2 | 252 MB | ✓ Full detail |

---

## What You'll See

When running a test, look for:

```
Setting blackbox rate: 1/4
  ✓ Blackbox rate set to 1/4
```

This means the automatic rate selection worked!

If it shows:
```
⚠ Failed to set blackbox rate, continuing with current rate
```

The test will continue with the rate that's already in the FC.

---

## Command-Line Reference

### `--duration-min MINUTES`

Set test duration for Test 9 (default: 60)

**Examples:**
```bash
--duration-min 60      # 1 hour (auto: 1/2 rate)
--duration-min 240     # 4 hours (auto: 1/4 rate)
--duration-min 480     # 8 hours (auto: 1/4 rate)
--duration-min 720     # 12 hours (auto: 1/8 rate)
```

### `--test9-blackbox-rate RATE`

Override automatic rate selection (Test 9 only)

**Format:** `1/N` where N is 2, 4, 8, or 16

**Examples:**
```bash
--test9-blackbox-rate 1/2      # Full rate (70 KB/s)
--test9-blackbox-rate 1/4      # Half rate (35 KB/s)
--test9-blackbox-rate 1/8      # Quarter rate (17.5 KB/s)
--test9-blackbox-rate 1/16     # Eighth rate (8.75 KB/s)
```

---

## Recommended Scenarios

### For HAL Upgrade Validation (Quick)
```bash
# 1-hour quick test at full rate
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.3.3
```
| Test | Count | Time | Rate | Space |
|------|-------|------|------|-------|
| Tests 1-6 | 6 | ~6 min | 1/2 | ~15 MB |

### For HAL Upgrade Validation (Extended)
```bash
# 1-hour stability test with periodic arm/disarm
python sd_card_test.py /dev/ttyACM0 --test 1,2,3,4,6,9 --duration-min 60 --hal-version 1.3.3
```
| Test | Count | Time | Rate | Space |
|------|-------|------|------|-------|
| Tests 1-6 | 6 | ~6 min | 1/2 | ~15 MB |
| Test 9 | 1 | 60 min | 1/2 | ~246 MB |
| **Total** | **7** | **~66 min** | **1/2** | **~261 MB** |

### For Pre-Release Validation (Thorough)
```bash
# 4-hour stability test
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 240 --hal-version 1.3.3 --verify-logs
```
| Test | Count | Time | Rate | Space |
|------|-------|------|------|-------|
| Test 9 | 1 | 240 min | 1/4 | ~246 MB |

### For Overnight Stress Test
```bash
# 12-hour overnight test
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 720 --hal-version 1.3.3 --verify-logs
```
| Test | Count | Time | Rate | Space |
|------|-------|------|------|-------|
| Test 9 | 1 | 720 min | 1/8 | ~369 MB |

### For Debugging with Lower Rate
```bash
# 4-hour test with conservative 1/8 rate
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 240 --test9-blackbox-rate 1/8 --verify-logs
```
| Test | Count | Time | Rate | Space |
|------|-------|------|------|-------|
| Test 9 | 1 | 240 min | 1/8 | ~123 MB |

---

## FAQ

### Q: Why do tests automatically set the rate?
**A:** To ensure safe operation without overflow, with appropriate data granularity. Tests adjust rate based on duration to maintain the sweet spot.

### Q: Can I disable automatic rate setting?
**A:** Not currently. But you can use `--test9-blackbox-rate` to override. Rate is set via CLI command, so worst case, you can change it manually and re-run.

### Q: What if the automatic rate is wrong for my use case?
**A:** Use `--test9-blackbox-rate` to override:
```bash
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 240 --test9-blackbox-rate 1/2
```

### Q: How do I verify the rate was applied?
**A:** Look at the logs. You should see:
```
Setting blackbox rate: 1/4
  ✓ Blackbox rate set to 1/4
```

Or verify manually via INAV Configurator CLI:
```
> get blackbox_rate
blackbox_rate = 1/4
```

### Q: What if rate setting fails?
**A:** The test continues with whatever rate is already configured in the FC. Check serial connection and try again.

### Q: Can I use different rates for different tests in one run?
**A:** Each test gets the rate optimal for IT. Tests 1-6 get 1/2, Test 9 gets duration-based rate. If you need a specific rate for all tests, set it manually before running.

---

## For More Details

See **BLACKBOX_RATE_AUTOMATION.md** for complete documentation including:
- Detailed rate selection logic
- Space calculations
- Implementation details
- Troubleshooting guide
- How to extend the feature

---

**Last Updated:** 2026-02-22
**Status:** Ready to use
