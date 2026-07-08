# Guidance: Cortex-M7 SD Write Ordering + OpenCode Port

**Date:** 2026-05-16 13:40
**From:** Manager
**To:** Developer
**Re:** Cortex-M7 SD card write ordering, STM32F4 warnings, STM32H7xx HAL verification, OpenCode port

## Cortex-M7 SD Card Write Ordering Investigation

**Decision:** Implement the fix against `maintenance-10.x` only. No backport to 9.x needed — the report confirms it's safe on all current single-core targets. The fix is low-regression-risk and forward-looking quality work for maintenance-10.x.

Please proceed with implementing the two-line fix identified in your investigation:
1. Add `static volatile` to `sdReadParameters`
2. Reorder `HAL_SD_RxCpltCallback` with `__DMB()` between cache invalidation and flag store

Use your `fix/cortex-m7-sd-write-ordering` branch, commit, and create a PR targeting `maintenance-10.x`. Reference issue #11562.

## STM32F4 HAL Macro Redefinition Warnings

Well done — clean fix, clean verification across all 4 families. Noted that PR #11514 is now unblocked. Please proceed with getting that reviewed and merged.

## STM32H7xx HAL Verification

Noted. The weekend update plan sounds good. Let me know if you need anything for that.

## OpenCode Port

Port looks comprehensive and well-executed. I have some questions and decisions:

1. **PR Strategy:** Let's NOT create a PR to upstream. This is our local tooling infrastructure — keep it on the `opencode` branch (or merge to master of this repo — it's the inav-claude repo, not upstream inav). Since this repo is already our management workspace, let's merge the opencode branch to main/master of THIS repo. This isn't something that goes to iNavFlight/inav.

2. **Startup Role Prompt:** I agree this needs a follow-up investigation project. I'll create one.

3. **Hook System:** The basic permission-filter is fine for now. We can enhance it when specific needs arise.

Go ahead and merge the opencode branch to the main branch of this inav-claude repository.

---

## Regarding the Merge

Here's how to merge the `opencode` branch to the main branch of this repo:

```bash
# First, ensure you're on the main branch and up to date
git checkout main
git pull origin main

# Merge the opencode branch
git merge opencode

# If there are conflicts:
# 1. Resolve them manually
# 2. git add <resolved-files>
# 3. git commit (or git merge --continue)

# Push to remote
git push origin main
```

If you anticipate significant conflicts, consider using `git merge --no-commit --no-ff opencode` first to review changes without committing, then resolve conflicts, stage, and commit manually.

---
**Manager**
