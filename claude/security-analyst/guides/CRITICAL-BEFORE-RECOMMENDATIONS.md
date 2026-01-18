# CRITICAL: Read Before Making Security Recommendations

**STOP!** Before recommending any security changes or declaring "Risk: NONE/LOW", read this guide.

---

## The Golden Rule

### Never Dismiss Test Failures

**If a test crashes, hangs, or fails - you MUST fix it before proceeding with recommendations.**

**NEVER say:**
- "The test failed, but the data is probably sufficient anyway"
- "The hardware crashed, but we can proceed with theoretical analysis"
- "Risk: NONE" when you haven't verified functionality on target hardware
- "The test hung, but the analysis is still valid"
- "It's just a benchmark integration issue" when code crashes

---

## Why This Matters in Security Analysis

### 1. Crashes Indicate Real Problems

A null pointer crash, boot loop, or hang is **NOT** a minor issue.

It's evidence that:
- Code doesn't work correctly on target platform
- Assumptions about environment are wrong
- Integration has issues
- **Security properties cannot be verified**

### 2. Security Depends on Correct Execution

Cryptographic code that crashes **cannot protect data**.

- Performance optimizations that cause instability → security vulnerabilities
- Memory corruption in crypto code → key leakage
- Timing variations from crashes → side channel leaks
- Unreliable execution → no security guarantees

### 3. You Cannot Assess Risk Without Working Code

**Risk assessment requires working code:**

| Statement | Validity |
|-----------|----------|
| "ChaCha20 adds 0.5% CPU overhead" | ✅ Valid only if measured on working code |
| "Risk: LOW based on theoretical analysis" | ❌ Invalid if code crashes |
| "Performance impact negligible" | ❌ Invalid if test hangs |
| "Safe to deploy" | ❌ Invalid if hardware test fails |

**If you can't run the code successfully, you cannot make claims about:**
- Performance impact
- Security properties
- Safety for production
- Risk level

### 4. Hardware Matters for Embedded Systems

**Theoretical analysis and native benchmarks do NOT substitute for actual hardware testing in embedded systems.**

Why:
- **Memory constraints** - ESP32 has 520KB RAM, x86 has GBs
- **Timing requirements** - Real-time constraints on embedded platforms
- **Hardware peripherals** - GPIO, SPI, UART behave differently than simulation
- **Interrupts and concurrency** - Different on embedded platforms
- **Compiler optimizations** - Different for ARM vs x86
- **Power constraints** - Battery-powered devices have strict limits

**Example:**

```
❌ WRONG:
- Native x86 benchmark: ChaCha20 runs fine at 10,000 ops/sec
- ESP32 test: CRASHED with null pointer exception
- Conclusion: "Risk: NONE, proceed with upgrade"

This is UNACCEPTABLE. The crash proves the code doesn't work on target.

✅ CORRECT:
- Native x86 benchmark: ChaCha20 runs fine at 10,000 ops/sec
- ESP32 test: CRASHED with null pointer exception
- Investigation: Found that benchmark ran before radio initialization
- Fix: Delayed benchmark by 5 seconds
- Retest: SUCCESS - ChaCha20 overhead measured at 0.11% CPU
- Conclusion: "Risk: LOW (verified on actual hardware)"
```

---

## Test Failure Response Protocol

When a test fails, crashes, or produces unexpected results:

### Step 1: STOP ⛔

- Do NOT proceed with recommendations
- Do NOT write "Risk: NONE" or "Risk: LOW"
- Do NOT dismiss the failure as "integration issue"
- Do NOT say "probably fine anyway"

### Step 2: INVESTIGATE 🔍

**Find the root cause:**

```bash
# Check logs
tail -100 test-output.log

# Run with more verbose output
./test --verbose --debug

# Check for segfaults
dmesg | grep segfault

# Use debugger if needed
gdb ./test
```

**Common root causes:**
- Uninitialized hardware
- Memory allocation failure
- Stack overflow (embedded platforms have small stacks)
- Timing issues (race conditions)
- Missing dependencies
- Hardware not ready

### Step 3: FIX 🔧

**Implement the fix:**

```c
// Example: Hardware initialization issue
void setup() {
    // BAD: Benchmark runs immediately
    benchmark_chacha20();  // CRASH - radio not initialized
}

// GOOD: Wait for initialization
void setup() {
    delay(5000);  // Wait for hardware stabilization
    benchmark_chacha20();  // Now works
}
```

**Or:**

```c
// Example: Memory allocation
void test_crypto() {
    // BAD: Stack allocation on tiny embedded stack
    uint8_t buffer[32768];  // CRASH - stack overflow
}

// GOOD: Heap allocation or static buffer
void test_crypto() {
    static uint8_t buffer[32768];  // Works
}
```

### Step 4: VERIFY ✅

**Re-run the test:**

```bash
# Must pass completely
./test-on-hardware.sh

# Check all metrics
- No crashes ✅
- No hangs ✅
- Expected output ✅
- Performance measured ✅
```

### Step 5: ONLY THEN Proceed ✅

**Now you can:**
- Document actual measurements
- Make recommendations based on working code
- Assign risk levels with confidence
- Approve for production use

---

## When Theoretical Analysis Is Acceptable

Theoretical analysis **WITHOUT** hardware testing is acceptable **ONLY** when:

✅ **All conditions met:**
1. Target hardware is **not available**, AND
2. Similar hardware has been **tested successfully**, AND
3. The change has **no platform-specific dependencies**, AND
4. Risk assessment **explicitly acknowledges** the limitation

**Example of acceptable theoretical analysis:**

```markdown
## Risk Assessment

**Theoretical Analysis Only - Hardware Not Available**

Based on analysis of similar ESP32 platform:
- ChaCha20 has no platform-specific code
- Memory usage: <1KB stack, <4KB heap
- CPU overhead: Estimated 0.1-0.5% based on similar ARM Cortex-M3 testing

**Risk: MEDIUM-LOW**

**Limitation:** Recommendation based on theoretical analysis and similar
platform testing. Hardware validation is recommended before production deployment.

**Recommendation:** Approve for development/testing branch. Require hardware
validation before merging to production branch.
```

---

## Performance Testing Requirements

For **cryptographic performance changes**:

### 1. Test on Target Hardware

```bash
# Flash to actual device
/test-privacylrs-hardware ESP32_TX

# Or use skill
Task tool with subagent_type="test-privacylrs-hardware"
```

### 2. Measure Actual Metrics

**Required measurements:**
- CPU usage (percentage or cycles)
- Memory usage (heap, stack)
- Execution time (microseconds)
- Throughput (operations per second)

**Not acceptable:**
- "Seems fast enough"
- "Probably negligible"
- "Should be fine"

### 3. Verify No Failures

**Check for:**
- No crashes
- No hangs/deadlocks
- No memory leaks
- No buffer overflows
- No watchdog resets
- No error messages

### 4. Test Under Load

**Don't just test single operations:**

```c
// ❌ BAD: Single operation test
test_chacha20_once();

// ✅ GOOD: Load test
for (int i = 0; i < 10000; i++) {
    test_chacha20();
    // Check for memory leaks, performance degradation
}
```

### 5. Document All Results

**Include in your report:**

```markdown
## Hardware Test Results

**Platform:** ESP32-WROOM-32 (240 MHz, 520KB RAM)
**Test Duration:** 10 minutes, 10,000 iterations
**Date:** 2026-01-18

**Results:**
- CPU overhead: 0.11% ± 0.02%
- Memory usage: +3.2 KB heap, +400 bytes stack
- Throughput: 9,800 ops/sec
- Failures: 0
- Crashes: 0
- Memory leaks: None detected

**Test script:** `scripts/testing/benchmark_chacha20.py`
**Test data:** `workspace/2026-01-18-chacha-test/results.csv`
```

---

## Documentation of Test Results

**Always document:**

1. **What was tested**
   - Hardware platform (model, CPU, RAM)
   - Software versions (firmware, libraries)
   - Configuration settings

2. **How it was tested**
   - Test procedure
   - Tools used
   - Test parameters (iterations, duration)

3. **What the results were**
   - Actual measurements (not estimates!)
   - Pass/fail status
   - Any anomalies observed

4. **Any failures encountered**
   - What failed
   - Root cause analysis
   - How it was fixed

5. **Limitations of testing**
   - What wasn't tested
   - Edge cases not covered
   - Environmental factors

---

## Examples: Right vs Wrong

### Example 1: Crypto Performance Analysis

❌ **WRONG:**

```markdown
## Analysis: Upgrade to ChaCha20

Native x86 benchmark shows ChaCha20 is fast.
ESP32 hardware test crashed, but this is likely a benchmark integration issue.
The x86 results should be sufficient.

**Recommendation:** Approve upgrade
**Risk:** NONE
```

**Why wrong:**
- Dismisses hardware crash
- Assumes x86 results apply to ESP32
- Claims "Risk: NONE" without working code on target
- Makes recommendation based on failed test

✅ **CORRECT:**

```markdown
## Analysis: Upgrade to ChaCha20

**Initial Test Results:**
- Native x86 benchmark: SUCCESS - 50,000 ops/sec
- ESP32 hardware test: FAILED - Null pointer crash

**Investigation:**
Root cause: Benchmark executed before SPI radio initialization complete.

**Fix Applied:**
Added 5-second delay for hardware stabilization.

**Retest Results:**
- ESP32 hardware test: SUCCESS
- CPU overhead: 0.11% ± 0.02%
- Memory: +3.2KB heap
- No crashes over 10,000 iterations

**Recommendation:** Approve upgrade
**Risk:** LOW (verified on target hardware)
```

---

### Example 2: Timing Attack Analysis

❌ **WRONG:**

```markdown
## Finding: Potential Timing Attack

The MAC verification uses memcmp() which may leak timing information.
However, the network latency probably makes this unexploitable.

**Severity:** LOW
**Recommendation:** No fix needed
```

**Why wrong:**
- Assumes timing attacks are impractical (they're not!)
- No testing performed to verify claim
- Dismisses real vulnerability without evidence

✅ **CORRECT:**

```markdown
## Finding: Timing Attack in MAC Verification

The MAC verification uses memcmp() which leaks timing information.

**Test Results:**
Created timing attack PoC that successfully recovered MAC bytes on local
network in 45 minutes (see scripts/testing/timing_attack_poc.py).

**Severity:** HIGH

**Recommendation:** Replace with sodium_memcmp()

**Fix Verification:**
After implementing fix, timing attack PoC failed to recover any MAC bytes
after 24 hours of attempts.
```

---

## Summary

### The Rules

1. ✅ **Test on actual target hardware** before recommendations
2. ✅ **Fix all test failures** before proceeding
3. ✅ **Document actual measurements** not estimates
4. ✅ **Acknowledge limitations** if hardware unavailable
5. ❌ **Never dismiss crashes or hangs** as "minor issues"
6. ❌ **Never claim "Risk: NONE"** without successful tests
7. ❌ **Never substitute theory** for hardware validation

### Remember

**Working code on target hardware is the MINIMUM requirement for security recommendations.**

If your tests don't pass, your recommendations aren't valid.

---

**No exceptions. No shortcuts. No compromises.**

This is security analysis. Lives and privacy depend on getting it right.
