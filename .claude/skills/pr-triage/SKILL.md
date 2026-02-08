---
description: Triage open PRs by assigning milestones (9.0.1, 9.1, 10.0)
triggers:
  - triage prs
  - pr triage
  - milestone triage
  - assign milestones
  - pr milestones
---

# PR Milestone Triage Skill

Systematically triage open PRs by assigning milestones, working through them in date order (oldest first).

## Usage

```
/pr-triage [inav|configurator|both] [after-date]
```

- Default repo: both (inav first, then configurator)
- Default after-date: 12 months ago from today

## Script Locations

```
claude/developer/scripts/triage/fetch-next-pr.sh   # Fetch next PR for triage
claude/developer/scripts/triage/update-pr.sh        # Set milestone, branch, labels
```

**IMPORTANT:** You MUST use `update-pr.sh` for all PR updates (milestones, base branches, labels).
Do NOT call `gh api` or `gh issue edit` directly — the script handles API quirks reliably.

## Milestone Criteria

| Milestone | When to use |
|-----------|-------------|
| **9.0.1** | Straightforward bug fixes with very little risk. Minimal code change, obvious correctness, no behavior change beyond the fix. |
| **9.1** | Compatible fixes and features. Backward-compatible with Configurator 9.0.0 and firmware 9.0.0. |
| **10.0** | Breaking changes. Would break compatibility with Configurator 9.0.0 or firmware 9.0.0, or requires coordinated firmware+configurator changes. |
| **Future** | Good idea but not prioritized for any current release. Large scope or speculative. |
| **Skip** | Don't assign a milestone now (add to skip file for later). |

## Branch Validation

**After selecting a milestone, verify the PR targets the correct base branch.**

| Milestone | Expected Base Branch |
|-----------|---------------------|
| **9.0.1** | `maintenance-9.x` |
| **9.1** | `maintenance-9.x` |
| **10.0** | `maintenance-10.x` |
| **Future** | any (no change needed) |

If the PR targets the wrong branch:
1. **Flag it to the user** in your analysis
2. Include `--base CORRECT_BRANCH` in the `update-pr.sh` call when applying changes

## Milestone Numbers (for API calls)

### iNavFlight/inav
| Milestone | API Number |
|-----------|------------|
| 9.0.1 | 51 |
| 9.1 | 50 |
| 10.0 | 46 |
| Future | 18 |

### iNavFlight/inav-configurator
| Milestone | API Number |
|-----------|------------|
| 9.0.1 | 36 |
| 9.1 | 35 |
| 10.0 | 37 |
| Future | 5 |

### Refreshing Milestone Numbers
If milestones change, refresh with:
```bash
gh api repos/iNavFlight/inav/milestones --jq '.[] | "\(.number) \(.title)"'
gh api repos/iNavFlight/inav-configurator/milestones --jq '.[] | "\(.number) \(.title)"'
```

## Workflow

### Step 1: Initialize

Calculate the after-date (12 months ago or user-specified) and set up skip files:
```bash
mkdir -p /tmp/claude
touch /tmp/claude/skip-inav.txt
touch /tmp/claude/skip-configurator.txt
```

### Step 2: Fetch First PR + Prefetch Next

On the very first iteration, fetch the current PR and **immediately start prefetching the next one in the background**:

```bash
# Fetch current PR (foreground)
bash claude/developer/scripts/triage/fetch-next-pr.sh iNavFlight/inav YYYY-MM-DD /tmp/claude/skip-inav.txt

# Prefetch next PR in background (uses cached PR list, only fetches reviews/comments)
bash claude/developer/scripts/triage/fetch-next-pr.sh iNavFlight/inav YYYY-MM-DD /tmp/claude/skip-inav.txt --offset 1 --output /tmp/claude/prefetch-inav.txt
```

The script caches the PR list for 2 minutes, so the prefetch reuses it and only makes API calls for the next PR's reviews and comments.

Use the Bash tool with `run_in_background: true` for the prefetch call.

**IMPORTANT:** When reading prefetch results, use the Read tool on the `--output` file path (`/tmp/claude/prefetch-inav.txt` or `/tmp/claude/prefetch-configurator.txt`), NOT the task runner's output file. The script redirects all output to the `--output` file, so the task runner captures nothing.

### Step 3: Analyze and Suggest

After reading the script output, analyze:

1. **What the PR does** - bug fix, feature, refactor, breaking change?
2. **Risk level** - How much code changes? How confident is correctness?
3. **Compatibility** - Does it break existing behavior for firmware or configurator users?
4. **Base branch** - Does it target the right branch for the suggested milestone?
5. **Testing status**:
   - Is it labeled "needs testing" or "Testing Required"?
   - Do comments indicate testing by someone other than the author?
   - The PR description's testing section is NOT sufficient alone - external testing matters
6. **Review status** - Has it been reviewed? Approved?

Present your analysis concisely and suggest a milestone. Flag testing concerns and branch mismatches.

**Always include the PR URL** (e.g., `https://github.com/iNavFlight/inav/pull/NNNN`) so the user can quickly open it.

### Step 4: User Confirms or Changes

Wait for user to confirm the milestone choice or specify a different one.

### Step 5: Apply Changes with update-pr.sh

Use `update-pr.sh` to set milestone, fix base branch, and add labels **in a single call**.
Build the arguments based on what's needed:

```bash
# Example: milestone + branch fix + new target label
bash claude/developer/scripts/triage/update-pr.sh iNavFlight/inav PR_NUMBER \
    --milestone MILESTONE_NUMBER \
    --base CORRECT_BRANCH \
    --add-label "New target"

# Example: just milestone (branch already correct, no label needed)
bash claude/developer/scripts/triage/update-pr.sh iNavFlight/inav PR_NUMBER \
    --milestone MILESTONE_NUMBER
```

Auto-tag: If the PR adds a new hardware target but is NOT labeled "New target", include `--add-label "New target"`.

After applying changes, **invalidate the cache** so the next prefetch gets fresh data:
```bash
rm -f /tmp/claude/pr-cache-*.json
```

Then **immediately read the prefetched output** and present it to the user:
```bash
cat /tmp/claude/prefetch-inav.txt  # or prefetch-configurator.txt
```

While the user reads the prefetched PR, **start prefetching the one after that** in the background:
```bash
bash claude/developer/scripts/triage/fetch-next-pr.sh iNavFlight/inav YYYY-MM-DD /tmp/claude/skip-inav.txt --offset 1 --output /tmp/claude/prefetch-inav.txt
```

### Step 7: Handle Skip

If the user says "skip", add the PR number to the skip file:
```bash
echo "PR_NUMBER" >> /tmp/claude/skip-inav.txt
# or
echo "PR_NUMBER" >> /tmp/claude/skip-configurator.txt
```

Then invalidate cache and show prefetched PR as in Step 6.

### Step 8: Loop

Continue the cycle: show prefetched PR, prefetch next one, wait for user decision. Stop when:
- No more PRs to triage (script outputs `NO_MORE_PRS`)
- User says to stop
- Switching to the other repo

## Testing Status Assessment

When analyzing testing, report one of:
- **Tested by others** - Comments show someone besides the author tested it
- **Author-tested only** - Only the PR author reports testing
- **Needs testing** - Labeled "needs testing" / "Testing Required" or no testing evidence
- **Untested** - No testing mentioned at all

## Example Session

```
> /pr-triage inav

Fetching oldest untriaged PR for iNavFlight/inav (after 2025-02-07)...

============================================================
PR #11190: MSP: Add minimum power index to MSP_VTX_CONFIG
============================================================
URL:     https://github.com/iNavFlight/inav/pull/11190
Author:  sensei-hacker
Created: 2025-12-15
Base:    maintenance-9.x
Labels:  none
...

ANALYSIS:
- Adds one byte to MSP_VTX_CONFIG response
- Compatible change (older configurator ignores extra byte)
- Base branch: maintenance-9.x (correct for 9.1)
- Testing: Author-tested only, needs hardware VTX validation

SUGGESTION: 9.1
BRANCH: maintenance-9.x (correct)

> [user]: 9.1

Setting milestone 9.1 (50) on PR #11190... Done.
Fetching next PR...
```

## Notes

- PRs that already have a milestone are automatically excluded
- Draft PRs are automatically excluded
- PRs labeled "don't merge" (case-insensitive) are automatically excluded
- Once a milestone is set, the PR won't appear in subsequent fetches
- The skip file persists only for the current session (/tmp/claude/)
- Always verify milestone numbers are current before starting a session
