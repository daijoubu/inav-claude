# Project: Contribute DroneCAN Documentation to inavdocs

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Documentation
**Created:** 2026-08-21
**Estimated Time:** 4-8 hours (spread across multiple PRs, timed with firmware merges)

## Overview

Plan and begin contributing DroneCAN documentation to `iNavFlight/iNavFlight.github.io`
(the new Docusaurus-based docs site, `https://inavflight.github.io/`,
replacing the old GitHub wiki). Covers both a correctness gap in already-shipped
DroneCAN functionality and new content for the feature stack currently in
progress (`feature-dronecan-*` / `review-dronecan-gps-node-health` /
`fix-dronecan-cell-voltage-calculation` projects).

## Problem

User asked (2026-08-21) to add `robotgoat/inavdocs` to known repos and figure
out how to contribute updates describing the DroneCAN functionality being
released, "in the appropriate branches."

Investigation findings:

- `robotgoat/inavdocs` is **robotgoat's own fork** of
  `iNavFlight/iNavFlight.github.io` (the actual upstream), maintained by
  robotgoat (GitHub: TrailerParkPilot), who has authored nearly every merged
  PR against the site (#2, #4, #10, #11, #12, #13). It's a reference/example
  fork, not something we can push to — contributing means forking the
  upstream under our own account.
- **No branch-based versioning** — the repo has a single `master` branch
  (confirmed 2026-08-21 via `gh repo view`; robotgoat's fork happens to
  default to a branch it calls `main`, but that's just their own fork's
  naming, not upstream's).
  Versioning is directory-based (Docusaurus): unversioned `docs/` holds
  content for the unreleased "Next" version; `versioned_docs/version-X.X.X/`
  are frozen snapshots of past releases (currently 4.0.0 through 9.1.0),
  created via `npm run docusaurus docs:version x.y.z` at release time. So
  "the appropriate branch" for our purposes translates to "the appropriate
  docs directory" — since our DroneCAN work targets `maintenance-10.x`
  (unreleased), it belongs in unversioned `docs/`, not any `versioned_docs/`
  snapshot.
- **Existing gap found, independent of our new work:** `docs/03-getting-started/01-hardware-overview.mdx`
  currently states *"While INAV does not support any DroneCAN based sensors
  yet..."* — this is already stale. DroneCAN GPS/battery-monitor support
  shipped in earlier completed projects (`review-dronecan-battery-monitor`,
  completed 2026-06-10) well before the current PR stack. `docs/05-core-features/gps.mdx`
  and `docs/05-core-features/battery.mdx` have zero mention of DroneCAN as a
  data source either.
- **No CONTRIBUTING.md**; style rules live in the repo's own README: MDX
  format, one sentence per line, images under `/static/img/` referenced with
  absolute paths (`/img/...`), page links relative (`../category/page.mdx`).

## Objectives

1. Fork `iNavFlight/iNavFlight.github.io` under the project's own GitHub
   account (not robotgoat's fork) and clone/branch off `master`.
2. Fix the stale "no DroneCAN sensor support" claim and add DroneCAN as a
   documented option in `gps.mdx` and `battery.mdx` for functionality
   that's already shipped.
3. Add new documentation, in unversioned `docs/`, for the functionality
   landing via the current DroneCAN PR stack — scope depends on what
   actually merges and needs a per-feature pass, likely a new page (e.g.
   under `06-advanced-features/`) covering: node health guard/status,
   parameter get/set + node info via the configurator tab, DNA server,
   actuator/ESC control, RC input over CAN, and the CAN bus error blackbox
   fields (once `fix-dronecan-cell-voltage-calculation` resolves, note the
   correct/fixed cell-voltage behavior for a DroneCAN battery source too).
4. Open PR(s) against `iNavFlight/iNavFlight.github.io` `master`.

## Scope

**In Scope:**
- `inavdocs/docs/03-getting-started/01-hardware-overview.mdx` — correct the
  stale DroneCAN claim
- `inavdocs/docs/05-core-features/gps.mdx`, `battery.mdx` — add DroneCAN
  source documentation
- New page(s) under `inavdocs/docs/06-advanced-features/` for the DroneCAN
  feature stack (node management, DNA server, actuator/ESC/RC-input, CAN
  bus diagnostics)

**Out of Scope:**
- `versioned_docs/` — don't touch frozen release snapshots
- The old `inavwiki/` GitHub wiki — being superseded, not worth updating
  in parallel
- Documenting anything not yet merged/rebased in the firmware PR stack as
  if it were current behavior — hold each doc addition until its
  corresponding firmware PR is at least out of draft, to avoid documenting
  behavior that changes during review

## Implementation Steps

1. Fork `iNavFlight/iNavFlight.github.io`, clone locally, branch off `master`
   (see `.claude/skills/git-workflow/SKILL.md` decision table, now includes
   `inavdocs`).
2. Small first PR: fix the stale hardware-overview claim + add DroneCAN
   mentions to `gps.mdx`/`battery.mdx` for already-shipped functionality —
   low-risk, immediately mergeable, doesn't depend on the in-progress stack.
3. Per DroneCAN firmware PR (once each is out of draft / rebased): draft
   the corresponding user-facing docs section, timed with that PR's review
   rather than all at once.
4. `npm run build` locally before each PR to confirm the site builds
   cleanly (per repo README).

## Success Criteria

- [ ] Own fork of `iNavFlight/iNavFlight.github.io` created
- [ ] Stale "no DroneCAN sensor support" claim corrected
- [ ] `gps.mdx`/`battery.mdx` document DroneCAN as a supported source
- [ ] New DroneCAN feature-stack page(s) added to unversioned `docs/`,
      matching what's actually merged/mergeable at time of writing
- [ ] At least the first (correctness-fix) PR opened against
      `iNavFlight/iNavFlight.github.io`

## Estimated Time

4-8 hours, spread across multiple PRs timed with firmware merges rather
than one large batch

## Priority Justification

MEDIUM — not blocking any firmware work, but the current docs actively
misinform users that INAV has no DroneCAN sensor support at all, which is
already false today and will be more conspicuously wrong once the current
feature stack ships.
