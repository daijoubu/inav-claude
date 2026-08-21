# Task Assignment: Start DroneCAN Documentation on inavdocs

**Date:** 2026-08-21 10:00
**From:** Manager
**To:** Developer
**Project:** docs-dronecan-inavdocs-site
**Priority:** MEDIUM
**Estimated Effort:** 4-8 hours (spread across multiple PRs, not one batch)

## Task

Start contributing DroneCAN documentation to `iNavFlight/iNavFlight.github.io`,
the new Docusaurus-based INAV documentation site
(`https://inavflight.github.io/`) that's replacing the old GitHub wiki.

## IMPORTANT: Target the correct INAV release

This repo does not version docs by git branch — there's a single branch
(`master` upstream). Versioning is **directory-based**:

- Unversioned `docs/` = unreleased "Next" content — this is where anything
  tied to `maintenance-10.x` belongs, since that hasn't shipped yet. All of
  the current DroneCAN feature-stack documentation goes here.
- `versioned_docs/version-9.1.0/` (and older) = frozen snapshots of
  **already-released** versions. Do NOT add new/unreleased functionality
  there — 9.1.0 shipped before this DroneCAN work and doesn't have it.
  Only touch a `versioned_docs/` snapshot if you're fixing something that
  was actually true and wrong for that specific released version.

Getting this wrong would document unreleased behavior as if it already
shipped in 9.1.0, or bury next-release docs somewhere users on the current
stable won't see and won't be confused by — both are real support-ticket
generators, so double-check which directory you're editing before each
commit.

## Background

Manager reviewed the repo 2026-08-21 while researching how to contribute:

- `robotgoat/inavdocs` (the repo originally pointed at) is robotgoat's own
  fork of the real upstream, `iNavFlight/iNavFlight.github.io` — not
  writable by us. To contribute, fork the upstream under your own account.
- Confirmed upstream's default branch is `master` (not `main` — that's
  just robotgoat's own fork's branch name, an early mistake in our notes
  that's now corrected in CLAUDE.md and `.claude/skills/git-workflow/SKILL.md`).
- Found the current docs already stale independent of this project's new
  work: `docs/03-getting-started/01-hardware-overview.mdx` states "INAV
  does not support any DroneCAN based sensors yet" — false today, since
  DroneCAN battery/GPS support shipped back in June. `docs/05-core-features/gps.mdx`
  and `battery.mdx` don't mention DroneCAN as a source at all either.
- No CONTRIBUTING.md; style rules are in the repo's own README (MDX
  format, one sentence per line, images referenced with absolute paths
  under `/img/`, page links relative).

## What to Do

Full detail in `claude/projects/active/docs-dronecan-inavdocs-site/summary.md`
and `todo.md`. Suggested order:

1. Fork `iNavFlight/iNavFlight.github.io` under your own GitHub account,
   clone, `npm install`, confirm `npm run build` works.
2. **Phase 2 first (small, low-risk, immediately mergeable):** branch off
   `master`, fix the stale "no DroneCAN sensor support" claim in
   `hardware-overview.mdx`, add DroneCAN as a documented source in
   `gps.mdx` and `battery.mdx` — this describes functionality that's
   already shipped, so it's safe to land right away. Open a PR.
3. **Phase 3, per feature, only once each firmware PR is out of draft**
   (don't document behavior that might still change in review): node
   health guard, parameter get/set + configurator tab, DNA server,
   actuator/ESC/RC-input control, CAN bus error blackbox logging. All of
   this goes in unversioned `docs/`, likely a new page under
   `docs/06-advanced-features/`.

## Success Criteria

- [ ] Own fork of `iNavFlight/iNavFlight.github.io` created
- [ ] Stale "no DroneCAN sensor support" claim corrected
- [ ] `gps.mdx`/`battery.mdx` document DroneCAN as a supported source
- [ ] New DroneCAN feature-stack page(s) added to unversioned `docs/` only
      — nothing added to `versioned_docs/version-9.1.0/` or older for
      unreleased functionality
- [ ] At least the Phase 2 correctness-fix PR opened against
      `iNavFlight/iNavFlight.github.io` `master`

## Project Directory

`claude/projects/active/docs-dronecan-inavdocs-site/`

---
**Manager**
