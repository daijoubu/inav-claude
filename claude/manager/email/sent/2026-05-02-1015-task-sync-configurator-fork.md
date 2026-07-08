# Task Assignment: Sync Configurator Fork with Upstream

**Date:** 2026-05-02 10:15
**From:** Manager
**To:** Developer
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 30 minutes

## Task

Bring the personal inav-configurator fork up to date with `inavflight/inav-configurator` — all branches and tags — in preparation for starting `feature-dronecan-configurator-tab`.

## What to Do

1. In `inav-configurator/`, fetch all branches and tags from upstream:
   ```
   git fetch upstream --prune --tags
   ```
2. For each key branch (`master`, `maintenance-9.x`, `maintenance-10.x`), fast-forward and push to origin:
   ```
   git checkout <branch>
   git merge --ff-only upstream/<branch>
   git push origin <branch>
   ```
3. Push all fetched tags to origin:
   ```
   git push origin --tags
   ```
4. Verify: confirm origin is at the same commits as upstream for all three branches.
5. Send completion report to manager.

## Context

`feature-dronecan-configurator-tab` targets `maintenance-10.x` in inav-configurator. The fork needs to be current before a feature branch is cut from it.

## Success Criteria

- [ ] `origin/master`, `origin/maintenance-9.x`, `origin/maintenance-10.x` match upstream
- [ ] All upstream tags present on origin
- [ ] Completion report sent to manager

---
**Manager**
