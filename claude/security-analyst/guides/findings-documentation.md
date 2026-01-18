# Security Findings Documentation Guide

This guide covers how to document and report security findings.

---

## Types of Security Reports

1. **Security Findings Report** - Vulnerability discoveries
2. **Threat Model Document** - STRIDE analysis and risk assessment
3. **Cryptographic Protocol Review** - Crypto implementation analysis
4. **Security Audit Report** - Comprehensive security assessment

---

## Security Findings Report

**When to use:** When you've discovered vulnerabilities during code review or analysis.

### Report Structure

```markdown
# Security Analysis Findings: [Component/Feature]

**Date:** YYYY-MM-DD HH:MM
**Analyst:** Security Analyst
**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**Status:** New | Confirmed | Mitigated

---

## Executive Summary

[2-3 sentence overview of what was analyzed and key findings]

Example:
"Analyzed the authentication module in PrivacyLRS v2.0. Found 2 HIGH severity
vulnerabilities related to timing attacks and 1 MEDIUM severity issue with
error message disclosure. All vulnerabilities are remotely exploitable."

## Scope

**Analyzed:**
- Files: `src/auth/verify.c`, `src/auth/session.c`
- Components: Authentication, Session Management
- Attack Surface: Network, API endpoints
- Lines of code: ~450 LOC

**Out of Scope:**
- Cryptographic primitives (reviewed separately)
- Network transport layer

## Findings

### Finding 1: [Vulnerability Title]

**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**CWE:** CWE-XXX (if applicable)
**Location:**
- File: `path/to/file.c`
- Function: `functionName()`
- Lines: 123-145

**Description:**

[Detailed technical description of the vulnerability. Include:]
- What the vulnerable code does
- Why it's vulnerable
- Under what conditions it can be exploited

**Vulnerable Code:**
```c
// Show the actual vulnerable code
if (memcmp(user_mac, expected_mac, 16) == 0) {
    return AUTH_SUCCESS;  // Early exit reveals timing info
}
return AUTH_FAILED;
```

**Impact:**

[What an attacker could achieve by exploiting this]

Examples:
- "Remote attacker can bypass authentication by measuring response times"
- "Leads to complete system compromise and private key extraction"
- "Allows privilege escalation from user to admin"

**Attack Scenario:**
1. Attacker sends authentication request with guessed MAC
2. Measures response time
3. Iteratively refines guess based on timing differences
4. Recovers valid MAC after ~2^20 attempts (~1 hour)

**Proof of Concept:**

[Code or steps to demonstrate the vulnerability]

```python
import time

def timing_attack_poc():
    correct_mac = [0x12, 0x34, 0x56, ...]

    for byte_pos in range(16):
        for guess in range(256):
            test_mac = wrong_mac[:]
            test_mac[byte_pos] = guess

            start = time.time()
            response = send_auth_request(test_mac)
            elapsed = time.time() - start

            if elapsed > threshold:
                correct_mac[byte_pos] = guess
                break
```

**Recommendation:**

[Specific, actionable fix]

```c
// Use constant-time comparison
if (sodium_memcmp(user_mac, expected_mac, 16) == 0) {
    return AUTH_SUCCESS;
}
return AUTH_FAILED;
```

**Additional Context:**
- Also consider using a MAC with built-in constant-time verification
- Implement rate limiting to slow down attacks
- Add logging for authentication failures

**References:**
- CWE-208: Observable Timing Discrepancy
- https://owasp.org/www-community/vulnerabilities/Timing_attack
- "Remote Timing Attacks are Practical" (Brumley & Boneh, 2003)

---

### Finding 2: [Next Vulnerability]

[Repeat structure]

---

## Summary of Recommendations

**CRITICAL (Fix Immediately):**
1. Finding 1: Use constant-time MAC verification
2. [Other critical fixes]

**HIGH (Fix Soon):**
1. Finding 3: [Description]
2. [Other high priority fixes]

**MEDIUM (Plan to Fix):**
1. Finding 5: [Description]

**LOW (Consider):**
1. Finding 7: [Enhancement]

## Risk Assessment

| Finding | Likelihood | Impact | Risk | Exploitability |
|---------|------------|--------|------|----------------|
| #1 | High | Critical | CRITICAL | Remote |
| #2 | Medium | High | HIGH | Local |
| #3 | High | Medium | MEDIUM | Remote |

## Next Steps

- [ ] Developer review and prioritization
- [ ] Fix implementation for CRITICAL/HIGH items
- [ ] Verification testing after fixes
- [ ] Re-audit after mitigation

---
**Security Analyst**
YYYY-MM-DD HH:MM
```

### Filename Convention

`YYYY-MM-DD-HHMM-findings-brief-description.md`

Examples:
- `2026-01-18-1430-findings-auth-timing-attacks.md`
- `2026-01-20-0900-findings-key-management-issues.md`

---

## Severity Ratings

Use consistent severity levels:

### CRITICAL
- Remote code execution (RCE)
- Authentication bypass
- Cryptographic key compromise
- Complete system compromise

**Examples:**
- Buffer overflow leading to RCE
- Hardcoded master encryption key
- SQL injection in authentication

### HIGH
- Privilege escalation
- Data exfiltration
- Weak cryptographic implementation
- Significant information disclosure

**Examples:**
- Timing attack on MAC verification
- Session fixation vulnerability
- Use of MD5 for password hashing

### MEDIUM
- Information disclosure (limited scope)
- Denial of Service
- Implementation weakness
- Missing security controls

**Examples:**
- Detailed error messages exposing paths
- Resource exhaustion DoS
- Missing input validation (non-critical)

### LOW
- Minor information leaks
- Edge case vulnerabilities
- Defense-in-depth improvements
- Best practice violations

**Examples:**
- Stack trace in error messages
- Missing security headers
- Verbose logging

---

## Threat Model Documents

See: `guides/threat-modeling-guide.md` for detailed structure.

**Quick reference:**
- Use STRIDE framework
- Include data flow diagrams
- Create risk assessment table
- Provide specific mitigations

---

## Cryptographic Protocol Reviews

See: `guides/crypto-review-guide.md` for detailed structure.

**Quick reference:**
- Document protocol flow
- Analyze each cryptographic primitive
- Check for common crypto vulnerabilities
- Include test results

---

## Sending Reports to Manager

**Use the email-manager agent:**

1. Save report to `claude/security-analyst/email/sent/`
2. Use email-manager to send:

```
Task tool with subagent_type="email-manager"
Prompt: "Send security findings report to manager. Report file: claude/security-analyst/email/sent/2026-01-18-1430-findings-auth-timing-attacks.md"
```

---

## Building Documentation Assets

**After creating a findings report:**

### 1. Extract Vulnerability Patterns

If you found a new pattern, document it:

```bash
vim docs/vulnerabilities/YYYY-MM-DD-timing-attacks-in-auth.md
```

Include:
- Pattern description
- Code examples (good and bad)
- Detection methods
- Remediation approaches
- References

### 2. Update Checklists

Add items to your security checklist:

```bash
vim docs/checklists/evolved-security-checklist.md
```

Add:
- [ ] Check for constant-time comparisons in auth code
- [ ] Verify MAC verification is timing-safe

### 3. Save Test Scripts

If you wrote tests to verify the finding:

```bash
cp workspace/current-analysis/test_timing_attack.py \
   scripts/testing/test_timing_attacks.py
```

### 4. Document Lessons Learned

```bash
vim docs/lessons-learned/YYYY-MM-DD-effective-timing-analysis.md
```

What worked well:
- Timing measurement approach
- Tools used
- Analysis technique

---

## Quality Checklist for Reports

Before sending a report, verify:

- [ ] **Clear severity ratings** - Each finding has CRITICAL/HIGH/MEDIUM/LOW
- [ ] **Specific locations** - File paths, function names, line numbers
- [ ] **Actionable recommendations** - Developer knows exactly what to fix
- [ ] **Impact described** - Explains what attacker can achieve
- [ ] **Proof of concept** - Demonstrates the vulnerability (if possible)
- [ ] **References included** - Links to CWE, OWASP, papers
- [ ] **Executive summary** - Manager can understand at a glance
- [ ] **No duplication** - Each finding listed once
- [ ] **Consistent formatting** - Follows template structure

---

## Common Mistakes to Avoid

❌ **Don't:**
- Use vague descriptions ("code is insecure")
- Skip proof of concept when exploitable
- Mix multiple unrelated findings into one
- Forget to include line numbers
- Use inconsistent severity ratings
- Recommend "fix the bug" without specifics

✅ **Do:**
- Be specific and technical
- Provide code examples
- Separate distinct findings
- Include precise locations
- Use standard severity levels
- Give actionable, specific fixes

---

## After Sending Report

1. **Archive the assignment:**

Use email-manager agent:
```
Prompt: "Archive completed assignment. Current role: security-analyst"
```

2. **Update knowledge base:**

Ensure all reusable assets extracted to `docs/` and `scripts/`

3. **Clean workspace:**

```bash
# Optional: Archive or remove workspace files
mv workspace/2026-01-18-auth-analysis/ workspace/archive/
```

---

## Next Steps

After documentation:
- Report sent to manager ✅
- Knowledge assets saved ✅
- Assignment archived ✅

Ready for next security analysis task!
