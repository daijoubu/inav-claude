# Security Analysis Methods Guide

This guide covers different types of security analysis you may be asked to perform.

---

## Code Security Review

### Objective
Identify vulnerabilities, insecure patterns, and security weaknesses in source code.

### Process

**1. Understand the Code**
- Read the code to understand its purpose
- Identify input sources and data flows
- Map trust boundaries
- Identify security-critical operations

**2. Apply Security Checklists**

Use the comprehensive checklist below, or use evolved checklists from `docs/checklists/`:

**Input Validation:**
- [ ] All external inputs validated and sanitized
- [ ] Buffer overflow protections in place
- [ ] Integer overflow/underflow checks
- [ ] Path traversal prevention
- [ ] Command injection prevention

**Cryptography:**
- [ ] Strong algorithms (AES-256, ChaCha20, etc.)
- [ ] Proper key sizes (128-bit minimum, 256-bit preferred)
- [ ] Secure random number generation
- [ ] No hardcoded keys or secrets
- [ ] Proper initialization vectors (random, unique)
- [ ] Authenticated encryption (GCM, Poly1305, etc.)

**Authentication & Authorization:**
- [ ] Strong authentication mechanisms
- [ ] Proper session management
- [ ] Access control enforcement
- [ ] Principle of least privilege
- [ ] Defense in depth

**Secure Communication:**
- [ ] TLS 1.2+ or equivalent
- [ ] Certificate validation
- [ ] Forward secrecy (ECDHE, DHE)
- [ ] Protection against replay attacks
- [ ] Message authentication codes (MAC)

**Memory Safety:**
- [ ] No use-after-free vulnerabilities
- [ ] No double-free vulnerabilities
- [ ] Proper bounds checking
- [ ] Memory cleared after use (for sensitive data)
- [ ] Safe string handling

**Error Handling:**
- [ ] No information leakage in errors
- [ ] Fail securely
- [ ] Proper exception handling
- [ ] Logging does not expose sensitive data

**3. Use Automated Tools**

Run automated security scanners from `scripts/scanning/`:

```bash
# General crypto security scan
./claude/security-analyst/scripts/scanning/scan-crypto-functions.sh PrivacyLRS/src

# Custom scans for specific patterns
grep -r "strcpy\|sprintf\|gets" PrivacyLRS/
grep -r "rand()\|srand()" PrivacyLRS/
grep -r "MD5\|SHA1\|DES\|RC4" PrivacyLRS/
```

**4. Manual Code Analysis**

Focus on high-risk areas:
- Cryptographic implementations
- Authentication/authorization code
- Input parsing and validation
- Network protocol handlers
- Key management

**5. Check for Known Patterns**

Review `docs/vulnerabilities/` for patterns previously found in this codebase:

```bash
ls claude/security-analyst/docs/vulnerabilities/
```

**6. Document Findings**

For each vulnerability found, document:
- **Location:** File, function, line numbers
- **Severity:** CRITICAL, HIGH, MEDIUM, LOW
- **Description:** What the vulnerability is
- **Impact:** What an attacker could achieve
- **Proof of Concept:** Demonstrate the issue
- **Recommendation:** How to fix it

---

## Vulnerability Assessment

### Objective
Analyze attack surfaces and identify potential exploit vectors.

### Process

**1. Identify Attack Surface**
- Network interfaces
- File inputs
- User inputs
- API endpoints
- Inter-process communication

**2. Map Attack Vectors**
- How could an attacker reach this code?
- What data can they control?
- What operations can they trigger?

**3. Analyze Exploitability**
- Can the vulnerability be triggered remotely?
- Does it require authentication?
- What are the prerequisites?
- How difficult is exploitation?

**4. Assess Impact**
- Confidentiality impact
- Integrity impact
- Availability impact
- Scope of damage

**5. Assign Risk Rating**

| Likelihood | Impact | Risk Rating |
|------------|--------|-------------|
| High | Critical | CRITICAL |
| High | High | HIGH |
| Medium | High | HIGH |
| Medium | Medium | MEDIUM |
| Low | High | MEDIUM |
| Low | Medium | LOW |

---

## Tools and Techniques

### Static Analysis Tools
- `grep`, `ripgrep` for pattern matching
- Custom scripts from `scripts/analysis/`
- Compiler warnings (`-Wall -Wextra`)

### Dynamic Analysis
- Use **test-privacylrs-hardware** skill for hardware testing
- Use **privacylrs-test-runner** skill for unit tests
- Manual testing with crafted inputs

### Code Review Techniques
- Trace data flow from input to sensitive operations
- Review error handling paths
- Check boundary conditions
- Look for race conditions
- Verify constant-time operations in crypto code

---

## After Analysis

**1. Update Knowledge Assets**

If you discovered new patterns:
```bash
# Document the pattern
vim docs/vulnerabilities/YYYY-MM-DD-pattern-name.md

# Update checklist if needed
vim docs/checklists/evolved-security-checklist.md
```

**2. Create Test Scripts**

If you wrote test code to validate findings:
```bash
# Save reusable test harnesses
cp workspace/current-analysis/test_timing.py scripts/testing/
```

**3. Proceed to Documentation**

See `guides/findings-documentation.md` for how to write your report.

---

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE Top 25: https://cwe.mitre.org/top25/
- SANS Top 25: https://www.sans.org/top25-software-errors/
- SEI CERT C Coding Standard: https://wiki.sei.cmu.edu/confluence/display/c/
