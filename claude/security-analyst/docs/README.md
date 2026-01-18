# Security Analysis Documentation Library

This directory contains security knowledge accumulated across analysis sessions.

## Directory Structure

- **vulnerabilities/** - Common vulnerability patterns discovered in this codebase
- **threat-models/** - Reusable threat model components and templates
- **checklists/** - Evolved security review checklists
- **lessons-learned/** - Analysis insights, effective techniques, and patterns

## Purpose

Build institutional knowledge so each security analysis session benefits from previous work.

## Guidelines

**When adding documentation:**

1. Use descriptive filenames with dates: `YYYY-MM-DD-description.md`
2. Include code examples where relevant
3. Reference specific files/functions in findings
4. Document both the problem and the remediation
5. Cross-reference related findings

**Examples:**

- `vulnerabilities/timing-attacks-in-mac-verification.md`
- `threat-models/wireless-protocol-stride-analysis.md`
- `lessons-learned/effective-embedded-crypto-testing.md`
- `checklists/esp32-specific-security-review.md`

## Evolution

These documents should evolve over time:
- Add new patterns as they're discovered
- Update checklists based on findings
- Refine threat models with new attack vectors
- Document what works and what doesn't
