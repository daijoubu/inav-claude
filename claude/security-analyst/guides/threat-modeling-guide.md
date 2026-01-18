# Threat Modeling Guide

This guide covers how to create and maintain threat models for components and systems.

---

## What is Threat Modeling?

Threat modeling is a structured approach to:
- Identify potential security threats
- Prioritize risks
- Define mitigation strategies

**Use threat modeling for:**
- New features with security implications
- Components that handle sensitive data
- Network-facing code
- Cryptographic protocols

---

## Threat Modeling Process

### Step 1: System Decomposition

**Identify Assets:**
- What data or resources does this system protect?
- What is the value of each asset?

**Examples:**
- Encryption keys (HIGH VALUE)
- User credentials (HIGH VALUE)
- Private communications (HIGH VALUE)
- Configuration data (MEDIUM VALUE)
- Metadata (LOW-MEDIUM VALUE)

**Map Data Flows:**
```
[External Input] --> [Parser] --> [Validator] --> [Crypto Module] --> [Storage]
                         |              |               |
                    [Sanitizer]   [Auth Check]    [Key Manager]
```

**Identify Trust Boundaries:**
- Where does untrusted data enter the system?
- What components run with elevated privileges?
- What data crosses network boundaries?

**Document Entry Points:**
- Network interfaces
- File inputs
- User inputs
- API endpoints
- Hardware interfaces

---

### Step 2: Threat Identification (STRIDE)

Use the STRIDE framework to systematically identify threats:

**S - Spoofing Identity**
- Can an attacker impersonate a legitimate entity?
- Are authentication mechanisms strong enough?
- Can device identity be forged?

**T - Tampering with Data**
- Can data be modified in transit?
- Can stored data be altered?
- Are integrity checks in place?

**R - Repudiation**
- Can users deny their actions?
- Is there sufficient logging?
- Are logs tamper-proof?

**I - Information Disclosure**
- Can sensitive data be accessed by unauthorized parties?
- Are there side-channel leaks?
- Is data encrypted at rest and in transit?

**D - Denial of Service**
- Can the system be made unavailable?
- Are there resource exhaustion vulnerabilities?
- Is there rate limiting?

**E - Elevation of Privilege**
- Can users gain unauthorized access?
- Are privilege boundaries enforced?
- Can attackers escape sandboxes?

---

### Step 3: Vulnerability Analysis

**Map Threats to Vulnerabilities:**

| Threat | Component | Vulnerability | Exploitability |
|--------|-----------|---------------|----------------|
| T1: Message tampering | Crypto module | No MAC verification | High |
| T2: Key extraction | Key storage | Keys in plaintext | Medium |
| T3: DoS via flood | Network handler | No rate limiting | High |

**Assess Impact:**
- What happens if this threat is realized?
- How many users/devices affected?
- Can the system recover?

---

### Step 4: Risk Rating

**Calculate Risk:**

Risk = Likelihood × Impact

**Likelihood:**
- **High:** Easy to exploit, common attack vector
- **Medium:** Requires some skill or specific conditions
- **Low:** Difficult to exploit, uncommon scenario

**Impact:**
- **Critical:** Complete system compromise, key leakage, RCE
- **High:** Data breach, privilege escalation
- **Medium:** Information disclosure, DoS
- **Low:** Minor information leak, edge case

**Risk Levels:**
- **CRITICAL:** Immediate action required
- **HIGH:** Fix as soon as possible
- **MEDIUM:** Plan to fix
- **LOW:** Consider for future enhancement

---

### Step 5: Mitigation Recommendations

**For Each Threat:**

1. **Eliminate:** Remove the vulnerable component if possible
2. **Mitigate:** Add security controls to reduce risk
3. **Transfer:** Use trusted libraries or hardware
4. **Accept:** Document why risk is acceptable (rare for CRITICAL/HIGH)

**Example Mitigations:**

| Threat | Mitigation Strategy | Priority |
|--------|---------------------|----------|
| Message tampering | Add authenticated encryption (AES-GCM) | CRITICAL |
| Key extraction | Store keys in secure enclave | HIGH |
| DoS via flood | Add rate limiting and connection limits | MEDIUM |

---

## Creating a Threat Model Document

**Use this structure:**

```markdown
# Threat Model: [Component Name]

**Date:** YYYY-MM-DD
**Analyst:** Security Analyst
**Version:** 1.0

## System Overview
[Description of the component/system]

## Assets
**High Value:**
- Asset 1
- Asset 2

**Medium Value:**
- Asset 3

## Data Flow Diagram
[ASCII or description of data flows]

## Trust Boundaries
1. Boundary 1: [Description]
2. Boundary 2: [Description]

## Threats (STRIDE Analysis)

### Spoofing
- **T1:** [Threat description]
  - **Severity:** HIGH
  - **Mitigation:** [How to address]

### Tampering
- **T2:** [Threat description]
  - **Severity:** CRITICAL
  - **Mitigation:** [How to address]

[Continue for all STRIDE categories]

## Risk Assessment

| Threat ID | Likelihood | Impact | Risk | Priority |
|-----------|------------|--------|------|----------|
| T1 | Medium | High | HIGH | 1 |
| T2 | High | Critical | CRITICAL | 1 |

## Recommendations

1. [Immediate fix for CRITICAL/HIGH]
2. [Short-term improvement]
3. [Long-term architectural change]

---
**Security Analyst**
```

**Save to:** `claude/security-analyst/email/sent/YYYY-MM-DD-HHMM-threat-model-component.md`

---

## Reusable Threat Model Components

**Build a library of threat model components:**

```bash
# Save reusable STRIDE analysis templates
vim docs/threat-models/stride-template-wireless-protocol.md
vim docs/threat-models/stride-template-key-management.md
vim docs/threat-models/common-mitigations.md
```

**Next time you analyze a similar component, start with the template!**

---

## Tools for Threat Modeling

**Diagramming:**
- ASCII art for simple flows
- Use `mermaid` syntax if needed
- Hand-drawn diagrams are fine (describe in text)

**Analysis:**
- STRIDE framework (recommended)
- PASTA methodology
- Attack trees

**References:**
- Microsoft Threat Modeling Tool (for reference)
- OWASP Threat Modeling Cheat Sheet

---

## After Threat Modeling

**1. Share with Manager**

Use **email-manager** agent to send threat model to manager.

**2. Save Reusable Components**

Extract generic parts to `docs/threat-models/`:
```bash
# Example: STRIDE analysis for wireless protocols
cp workspace/current-analysis/wireless-stride.md \
   docs/threat-models/wireless-protocol-stride-template.md
```

**3. Update as System Evolves**

Threat models are living documents:
- Update when new features added
- Revise when threats are mitigated
- Add newly discovered threats

---

## Next Steps

After completing threat modeling:
- Proceed to vulnerability assessment if needed
- Or document findings and report to manager

See: `guides/findings-documentation.md`
