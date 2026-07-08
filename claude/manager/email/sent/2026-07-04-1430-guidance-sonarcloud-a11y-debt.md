# Guidance: SonarCloud a11y / i18n Findings — Accept as Debt

**Date:** 2026-07-04 14:30
**From:** Manager
**To:** Developer
**Re:** SonarCloud a11y rules conflict with runtime i18n pattern / PR iNavFlight/inav-configurator#2671

## Guidance

Accept as technical debt for now (your option 3). Leave the three findings as-is — no code change needed on PR #2671 beyond what you've already done.

## Rationale

The quality gate already passes; these are code smells, not gate-blocking bugs on new code. A hardcoded English `aria-label` fallback would be a real UX regression for non-English screen-reader users and doesn't scale to every i18n label in the app, so that's off the table. Project-wide SonarCloud rule suppression for `data-i18n`-driven elements is the more correct long-term fix, but it's a config/policy change that deserves its own small scoped task rather than a decision folded into this PR — revisit it if it becomes a real problem (e.g. an actual screen-reader accessibility complaint), rather than pre-emptively.

## References

PR: iNavFlight/inav-configurator#2671

---
**Manager**
