# Cryptographic Protocol Review Guide

This guide covers how to analyze cryptographic protocols and implementations for security.

**Reference textbook:** `claude/developer/docs/encryption/applied_cryptography-BonehShoup_0_4.pdf`

---

## When to Perform Crypto Review

- New cryptographic protocol implementations
- Changes to existing crypto code
- Integration of third-party crypto libraries
- Performance optimizations in crypto code
- Security upgrade proposals (e.g., AES → ChaCha20)

---

## Cryptographic Review Process

### Step 1: Understand the Protocol

**Document the protocol flow:**

```
Alice                           Bob
  |                              |
  |--- ClientHello (nonce_A) --->|
  |                              |
  |<-- ServerHello (nonce_B) ----|
  |                              |
  |--- KeyExchange (DH_pub) ---->|
  |                              |
  |<-- Encrypted(session_key) ---|
```

**Identify cryptographic primitives:**
- Encryption algorithms (AES, ChaCha20, etc.)
- Key derivation functions (HKDF, PBKDF2, etc.)
- Message authentication codes (HMAC, Poly1305, etc.)
- Digital signatures (Ed25519, ECDSA, etc.)
- Random number generators
- Hash functions

**Map key lifecycle:**
- How are keys generated?
- How are keys stored?
- How are keys derived?
- When are keys rotated?
- How are keys destroyed?

---

### Step 2: Verify Security Properties

**Check for required security properties:**

**Confidentiality:**
- [ ] Strong encryption algorithm (AES-256, ChaCha20)
- [ ] Proper key size (≥128 bits, prefer 256)
- [ ] Secure mode of operation (not ECB!)
- [ ] Unique IVs/nonces for each message

**Integrity:**
- [ ] Message authentication code (MAC) or authenticated encryption
- [ ] MAC verification before decryption
- [ ] MAC covers all relevant data (no truncation)

**Authentication:**
- [ ] Entity authentication (mutual if needed)
- [ ] Resistance to impersonation
- [ ] Binding between identity and keys

**Forward Secrecy:**
- [ ] Session keys are ephemeral
- [ ] Compromise of long-term key doesn't compromise past sessions
- [ ] Uses ECDHE or DHE key exchange

**Replay Protection:**
- [ ] Nonces or sequence numbers
- [ ] Timestamp validation
- [ ] Protection against message replay

**Non-repudiation (if required):**
- [ ] Digital signatures
- [ ] Audit logging
- [ ] Timestamp verification

---

### Step 3: Analyze Cryptographic Primitives

**For Each Primitive:**

**1. Algorithm Selection**
```
✅ RECOMMENDED:
- Encryption: AES-256-GCM, ChaCha20-Poly1305
- Hash: SHA-256, SHA-512, Blake2
- MAC: HMAC-SHA256, Poly1305
- KDF: HKDF-SHA256, Argon2
- Signatures: Ed25519, ECDSA-P256

❌ AVOID:
- MD5, SHA-1 (broken)
- DES, 3DES, RC4 (weak)
- ECB mode (insecure)
- Custom crypto (high risk)
```

**2. Parameter Selection**
- **Key sizes:** ≥128 bits (prefer 256)
- **Nonce sizes:** 96-128 bits (never reuse!)
- **Salt sizes:** ≥128 bits
- **IV sizes:** Match block size

**3. Implementation Review**

Check for common mistakes:
```c
// ❌ BAD: ECB mode
AES_encrypt(plaintext, key, ciphertext);

// ✅ GOOD: Authenticated encryption
chacha20_poly1305_encrypt(plaintext, key, nonce, aad, ciphertext, tag);
```

```c
// ❌ BAD: Reusing nonces
nonce = 0;
for (msg in messages) {
    encrypt(msg, key, nonce);  // Nonce reuse!
}

// ✅ GOOD: Unique nonces
nonce = random_bytes(12);
encrypt(msg, key, nonce);
```

```c
// ❌ BAD: Non-constant-time comparison
if (memcmp(received_mac, expected_mac, 16) == 0) {
    // Timing leak!
}

// ✅ GOOD: Constant-time comparison
if (sodium_memcmp(received_mac, expected_mac, 16) == 0) {
    // Safe
}
```

---

### Step 4: Analyze Side Channels

**Timing Attacks:**
- [ ] Constant-time comparisons for MACs/signatures
- [ ] Constant-time key operations
- [ ] No timing variation based on secret data

**Power Analysis:**
- [ ] Use hardware-accelerated crypto if available
- [ ] Consider masking for sensitive operations
- [ ] Limit exposure in power-constrained devices

**Cache Timing:**
- [ ] Table lookups don't depend on secret keys
- [ ] Consider using bitslicing
- [ ] Modern CPUs: Use AES-NI instructions

**Fault Injection:**
- [ ] Critical checks not bypassable
- [ ] Redundant security checks
- [ ] Hardware fault detection if available

---

### Step 5: Review Key Management

**Key Generation:**
- [ ] Cryptographically secure RNG
- [ ] Sufficient entropy
- [ ] Proper seeding

```c
// ❌ BAD: Insecure RNG
srand(time(NULL));
key = rand();

// ✅ GOOD: Cryptographic RNG
randombytes_buf(key, KEY_SIZE);  // libsodium
// or: getrandom(), /dev/urandom
```

**Key Storage:**
- [ ] Keys not in plaintext
- [ ] Use secure storage (hardware if available)
- [ ] Access controls on key material
- [ ] Keys cleared from memory after use

```c
// ✅ GOOD: Clear sensitive data
memset(key, 0, sizeof(key));
// Better: Use sodium_memzero() to prevent optimization
sodium_memzero(key, sizeof(key));
```

**Key Derivation:**
- [ ] Use proper KDF (HKDF, not just hash)
- [ ] Unique salt per key
- [ ] Domain separation

**Key Rotation:**
- [ ] Plan for key rotation
- [ ] Graceful key rollover
- [ ] Key version tracking

---

### Step 6: Protocol-Level Analysis

**Check for Protocol Vulnerabilities:**

**Downgrade Attacks:**
- [ ] Protocol version enforcement
- [ ] No fallback to weak crypto
- [ ] Version in authenticated portion

**Man-in-the-Middle:**
- [ ] Mutual authentication
- [ ] Certificate validation
- [ ] Public key pinning (if applicable)

**Replay Attacks:**
- [ ] Unique nonces/challenges
- [ ] Timestamp validation
- [ ] Sequence numbers

**Confused Deputy:**
- [ ] Clear protocol roles
- [ ] Role binding in messages
- [ ] No symmetric ambiguity

---

### Step 7: Test the Implementation

**Use available testing skills:**

```bash
# Run unit tests
/privacylrs-test-runner

# Test on actual hardware
/test-privacylrs-hardware
```

**Manual testing:**
- Test with invalid inputs
- Test with crafted messages
- Test key reuse scenarios
- Test boundary conditions

**CRITICAL:** See `guides/CRITICAL-BEFORE-RECOMMENDATIONS.md`
- Never recommend without successful tests
- Hardware testing is required for embedded systems
- Document all test results

---

## Creating a Crypto Review Report

**Structure:**

```markdown
# Cryptographic Protocol Review: [Protocol Name]

**Date:** YYYY-MM-DD
**Analyst:** Security Analyst
**Protocol Version:** X.Y

## Protocol Overview
[High-level description]

## Security Goals
- [x] Confidentiality
- [x] Integrity
- [x] Authentication
- [x] Forward Secrecy
- [x] Replay Protection
- [ ] Non-repudiation (not required)

## Protocol Flow
[Diagram or description]

## Cryptographic Primitives

**Encryption:**
- Algorithm: ChaCha20-Poly1305
- Key Size: 256 bits
- Mode: AEAD
- Assessment: ✅ Strong, appropriate

**Key Derivation:**
- Algorithm: HKDF-SHA256
- Salt: Random 32 bytes
- Info: Protocol constant
- Assessment: ✅ Strong, appropriate

[Continue for all primitives]

## Security Analysis

### Strengths
- Uses modern AEAD
- Forward secrecy via ephemeral keys
- Proper key derivation

### Weaknesses
- ⚠️ No key confirmation message
- ⚠️ Nonce counter could overflow

### Vulnerabilities
- **V1:** Nonce reuse possible after 2^64 messages
  - **Severity:** MEDIUM
  - **Mitigation:** Add key rotation at 2^48 messages

## Recommendations

**CRITICAL:** None

**HIGH:**
- Add key rotation mechanism
- Add key confirmation step

**MEDIUM:**
- Document security assumptions
- Add nonce overflow protection

**LOW:**
- Consider adding perfect forward secrecy for metadata

## Implementation Review

**File:** `src/crypto/protocol.c`

**Issues:**
- Line 234: [Issue description]
- Line 456: [Issue description]

## Test Results

[Document testing performed and results]

## Conclusion

[Overall assessment and go/no-go recommendation]

---
**Security Analyst**
```

**Save to:** `claude/security-analyst/email/sent/`

---

## Building Crypto Knowledge

**After each crypto review:**

**1. Document patterns:**
```bash
# Save crypto implementation patterns
vim docs/vulnerabilities/YYYY-MM-DD-nonce-reuse-pattern.md
```

**2. Update checklists:**
```bash
# Add protocol-specific items
vim docs/checklists/crypto-protocol-review-checklist.md
```

**3. Save test harnesses:**
```bash
# Reusable crypto tests
cp workspace/current/test_timing.py scripts/testing/
```

---

## Common Crypto Vulnerabilities

See `docs/vulnerabilities/` for detailed patterns:
- Timing attacks (constant-time violations)
- Nonce reuse
- Weak key derivation
- ECB mode usage
- Hardcoded keys
- Insecure RNG

---

## References

**Books:**
- Applied Cryptography (Boneh & Shoup) - in `claude/developer/docs/encryption/`
- Cryptography Engineering (Ferguson, Schneier, Kohno)

**RFCs:**
- RFC 5116: AEAD Interface
- RFC 5869: HKDF
- RFC 7539: ChaCha20-Poly1305
- RFC 8439: ChaCha20-Poly1305 AEAD

**Libraries:**
- libsodium: https://libsodium.gitbook.io/
- OpenSSL: https://www.openssl.org/docs/

---

## Next Steps

After crypto review:
1. Document findings
2. Test on hardware (if applicable)
3. Report to manager

See: `guides/findings-documentation.md`
