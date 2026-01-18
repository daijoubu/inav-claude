# Example: Timing Side Channel Vulnerabilities

**Pattern Category:** Side Channel Attacks
**Severity:** HIGH to CRITICAL (depending on context)
**Common in:** Cryptographic implementations, authentication code

---

## Description

Timing side channels occur when the execution time of a function leaks information about secret data. This is especially critical in cryptographic code where timing differences can reveal:
- Keys or key bits
- Password characters
- Authentication tokens
- Encrypted data

---

## Vulnerability Pattern

### Non-Constant-Time Comparison

**Vulnerable code pattern:**
```c
// BAD: Early exit reveals information
bool verify_mac(uint8_t *received, uint8_t *expected, size_t len) {
    for (size_t i = 0; i < len; i++) {
        if (received[i] != expected[i]) {
            return false;  // ❌ Early exit - timing leak!
        }
    }
    return true;
}
```

**Why it's vulnerable:**
- Function returns immediately when first byte differs
- Attacker can measure timing to guess MAC byte-by-byte
- Enables practical attacks even over network

### Non-Constant-Time Conditional

**Vulnerable code pattern:**
```c
// BAD: Branch timing depends on secret data
if (key[i] & 0x80) {
    // Different execution path reveals key bit
    perform_operation();
}
```

---

## Exploitation

**Attack scenario:**
1. Attacker sends messages with guessed MAC values
2. Measures response time for each guess
3. Longer response time = more correct bytes
4. Iteratively recovers full MAC byte-by-byte

**Real-world impact:**
- Remote timing attacks demonstrated over LAN/WAN
- Can recover AES keys, MAC values, passwords
- Especially effective in embedded systems with predictable timing

---

## Remediation

### Use Constant-Time Comparison

```c
// GOOD: Constant-time comparison
bool verify_mac_secure(const uint8_t *received, const uint8_t *expected, size_t len) {
    volatile uint8_t diff = 0;

    for (size_t i = 0; i < len; i++) {
        diff |= received[i] ^ expected[i];
    }

    return diff == 0;
}
```

**Key features:**
- Always processes all bytes
- No early exit
- Uses `volatile` to prevent compiler optimization
- Constant execution time regardless of input

### Use Cryptographic Libraries

```c
// GOOD: Use trusted constant-time functions
#include <sodium.h>

bool verify_mac_libsodium(const uint8_t *received, const uint8_t *expected, size_t len) {
    return sodium_memcmp(received, expected, len) == 0;
}
```

---

## Detection Methods

### Manual Code Review

Search for:
```bash
# Find potential timing leaks
grep -r "memcmp\|strcmp" src/crypto/
grep -r "if.*==" src/auth/
grep -r "return.*!=" src/verify/
```

### Automated Testing

Create timing measurement test:
```python
def test_timing_leak():
    correct_mac = bytes([0x12, 0x34, 0x56, 0x78])

    # Test with all wrong bytes
    wrong_mac = bytes([0xFF, 0xFF, 0xFF, 0xFF])
    time1 = measure_time(verify_mac, wrong_mac)

    # Test with first byte correct
    partial_mac = bytes([0x12, 0xFF, 0xFF, 0xFF])
    time2 = measure_time(verify_mac, partial_mac)

    # If timing differs significantly, leak detected
    assert abs(time1 - time2) < THRESHOLD
```

---

## References

- **Paper:** "Remote Timing Attacks are Practical" (Brumley & Boneh, 2003)
- **CWE-208:** Observable Timing Discrepancy
- **OWASP:** https://owasp.org/www-community/vulnerabilities/Timing_attack

---

## Observations in This Codebase

*This section should be updated as timing vulnerabilities are discovered in the actual codebase.*

**Example findings:**
- ✅ ChaCha20 implementation uses constant-time operations
- ✅ MAC verification in `crypto.c` uses `sodium_memcmp()`
- ⚠️ Custom comparison in `auth_check()` line 234 may leak timing

---

**Last Updated:** 2026-01-18
**Security Analyst**
