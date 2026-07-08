# Task Assignment: Open Draft PR for DroneCAN GPS Health Guard

**Date:** 2026-07-05 09:00
**From:** Manager
**To:** Developer
**Project:** review-dronecan-gps-node-health
**Priority:** MEDIUM-HIGH
**Estimated Effort:** Small — PR submission only, no new code

## Task

Open a draft PR for branch `fix/dronecan-gps-health-guard` against `maintenance-10.x`.

## Background

This project's code has been complete and build-matrix-clean since it was rebased onto `feature/dronecan-param-getset` and re-verified 2026-07-04. It was intentionally held back from opening a PR until it could go out alongside `feature-dronecan-dna-server`, per its original holding condition ("both to be reviewed and merged together"). `feature-dronecan-dna-server`'s draft PRs (firmware #11688, configurator #2672) opened 2026-07-04, so that condition is now satisfied — go ahead and open this one too.

## What to Do

1. Open a draft PR from `fix/dronecan-gps-health-guard` against `maintenance-10.x` (draft, matching the pattern used for #11683/#11688/#2672 — stacked/dependent PRs opened as drafts while prerequisites are still unmerged)
2. Cross-link it with #11688 and #11683 in the PR description, same as the other stacked DroneCAN PRs
3. Confirm CI is green on the PR
4. Reply with the PR number once opened so tracking can be updated

## Success Criteria

- [ ] Draft PR opened against `maintenance-10.x`
- [ ] CI green
- [ ] Cross-linked with related stacked PRs (#11683, #11688)
- [ ] PR number reported back

## Project Directory

`claude/projects/active/review-dronecan-gps-node-health/`

---
**Manager**
