# Documentation Issues

Documentation fixes or improvements needed.

---

## Issues

### #10778 - Unclear documentation regarding fw_d_level

**Created:** 2024-10-15
**Labels:** documentation
**URL:** https://github.com/iNavFlight/inav/issues/10778

**Problem:**
Documentation for the `fw_d_level` parameter is unclear or confusing.

**What's Needed:**
- Clarify what the parameter does
- Provide usage examples
- Update wiki documentation

**Notes:**
Documentation-only change, no code modifications.

---

### inav #11672 - Request for private security disclosure channel

**Created:** 2026-06-29
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/11672

**Problem:** Reporter asks for a private/security disclosure channel (e.g. `SECURITY.md`, a security contact, or GitHub private vulnerability reporting) rather than requiring security issues to be filed publicly.

**What's Needed:** Add a `SECURITY.md` documenting a disclosure process (contact email/Discord DM to a core dev, or enable GitHub's private vulnerability reporting feature for the repo), and reference it from `CONTRIBUTING.md`/README.

**Notes:** Process/policy documentation, no firmware code changes. Worth prioritizing given #11209 (CRSF MSP integer overflow, security-relevant) shows this repo does get real security reports filed as public issues today.

**2026-08-11:** the thread evolved past the original SECURITY.md ask into a real technical report (6 flagged MSP SET handlers, potential bounds-checking gaps). Ray (maintainer) replied directly with Discord contact info and reframed it as a reliability concern rather than a security vuln — the original documentation-framing ask is effectively answered/closeable. The reliability follow-up is tracked separately: `active/audit-msp-set-handler-bounds-checking/`.
