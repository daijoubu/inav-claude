# Question: SonarCloud a11y rules conflict with runtime i18n pattern

**Date:** 2026-07-04 10:00
**From:** Developer
**To:** Manager
**Re:** feature-dronecan-configurator-tab / PR iNavFlight/inav-configurator#2671

## Question

Should we hardcode fallback accessible text (e.g. `aria-label`) on i18n-driven `<label>`/`<th>` elements to satisfy SonarCloud's accessibility rules, or ask to suppress/waive those specific rules for this codebase's i18n pattern?

## Context

While fixing PR #2671's SonarQube quality gate failure, I added `for=` attributes linking the two config labels to their inputs, and added a `<thead>` with `<th>` elements to the previously-headerless detail table. That satisfied the DOM-association half of SonarCloud's rules (`Web:S6853`, `Web:InputWithoutLabelCheck`, `Web:S5256`).

However, those rules also require the label/header element to have non-empty *accessible text* in the static HTML. This codebase's entire i18n system works by shipping empty elements with a `data-i18n="key"` attribute in the raw HTML/JS, with the actual text injected by `i18n.localize()` at runtime in the browser. SonarCloud's static analyzer only sees the raw HTML file — it can't see JS-injected text — so it will flag this pattern as "label has no accessible text" for any i18n-driven label or header, everywhere in the app, not just this tab. I confirmed these three findings are still open after my fix and are not stale/mis-tracked (unlike some other findings I found this session), because they point at the actual `data-i18n`-only elements.

This isn't something I can cleanly fix at the code level for just this PR without picking one of:
1. Hardcode an English fallback string (e.g. `aria-label="Bus speed"` alongside `data-i18n`) on these specific elements — works for the a11y tooling and screen readers, but that hardcoded string won't get localized (a real UX regression for non-English users using a screen reader) and doesn't scale to every i18n label in the app.
2. Ask to suppress/waive these specific SonarCloud rules for i18n-driven elements project-wide (via SonarCloud's issue-resolution or rule-exclusion config) — the more correct long-term fix but a policy/config decision, not something I can decide unilaterally as a code change on this PR.
3. Leave as-is — it doesn't block the quality gate (the gate passed; these are code smells, not gate-failing bugs on new code), so this could just be accepted debt.

I didn't want to silently work around this with a hardcoded label patch without flagging the tradeoff, since it'd affect every future i18n-driven label in the app, not just these two. Let me know which direction you want, or if this should become its own small investigation/task.

---
**Developer**
