---
description: Walk through open PRs scored by merge-readiness, suggesting merge/comment/label/approve for each
triggers:
  - pr scorecard triage
  - triage scorecards
  - review ready prs
  - which prs are ready
  - scorecard triage
  - walk through prs
  - pr review session
---

# PR Scorecard Triage

Walk through open PRs in merge-readiness order — highest-scoring first — and
take action on each: merge, approve, comment, label, or skip.
This is NOT code review. It is a disposition session based on readiness signals.

## Usage

```
/pr-scorecard-triage [inav|configurator|both] [--after YYYY-MM-DD]
```

Default: both repos (inav first), PRs from the last 6 months.
Pass `--after` to override the date window, e.g. `--after 2025-10-01`.

---

## How It Differs from /pr-triage

| `/pr-triage` | `/pr-scorecard-triage` |
|---|---|
| Assigns milestones | Takes merge actions |
| Oldest-first order | Highest-score first |
| Asks: which milestone? | Asks: merge/approve/comment/label? |
| No scoring | Full scorecard per PR |

---

## Preparation

```bash
mkdir -p /tmp/claude
touch /tmp/claude/skip-scorecard-inav.txt
touch /tmp/claude/skip-scorecard-configurator.txt
```

---

## Main Loop

### Step 1 — Get Next PR + Prefetch the One After

```bash
# Fetch current PR (foreground) — default window is 6 months
bash claude/developer/scripts/triage/scorecard-triage.sh \
    iNavFlight/inav \
    /tmp/claude/skip-scorecard-inav.txt

# Or with explicit date window:
bash claude/developer/scripts/triage/scorecard-triage.sh \
    iNavFlight/inav \
    /tmp/claude/skip-scorecard-inav.txt \
    --after 2025-10-01

# Immediately prefetch next in background
bash claude/developer/scripts/triage/scorecard-triage.sh \
    iNavFlight/inav \
    /tmp/claude/skip-scorecard-inav.txt \
    --offset 1 \
    --output /tmp/claude/prefetch-scorecard.txt
```

Use `run_in_background: true` on the prefetch call.

If output is `NO_MORE_PRS`: that repo is exhausted, move to the other repo or stop.

---

### Step 2 — Run the Scorecard

Check the `CACHE_STATUS` line in the scorecard-triage output:

**If `CACHE_STATUS=fresh`:**
Run pr-scorecard.sh to get the cached result instantly:
```bash
bash claude/developer/scripts/triage/pr-scorecard.sh iNavFlight/inav <PR_NUMBER>
```
Output will contain `CACHE_HIT=true` — use the cached score and label directly.
**Do NOT re-run pr-scorecard-record.sh** — the entry already exists.

**If `CACHE_STATUS=unscored` or `CACHE_STATUS=expired`:**
Fetch fresh data:
```bash
bash claude/developer/scripts/triage/pr-scorecard.sh iNavFlight/inav <PR_NUMBER>
# (add --force if status was expired)
```
Apply the scoring rubric from `/pr-scorecard` SKILL.md to compute a score.
Then record it immediately:
```bash
bash claude/developer/scripts/triage/pr-scorecard-record.sh \
    iNavFlight/inav <PR_NUMBER> <SCORE> "<LABEL>" "<TITLE>" "<URL>"
```

---

### Step 3 — Check Milestone

Check the `MILESTONE CHECK` section in the scorecard output. If the milestone is
wrong or missing, flag it with `⚠` in KEY SIGNALS and include setting the correct
milestone in the suggested action.

**Current milestone policy (April 2026):**

| Base branch | Expected milestone |
|-------------|-------------------|
| `maintenance-9.x` | **9.1** (9.0.1 shipped Jan 2026; 9.1 target Jun/Jul 2026) |
| `maintenance-10.x` | **10.0** or **10.1** |

A wrong/missing milestone is NOT a hard blocker but should be fixed before merge.
When suggesting an action that includes merging or approving, also add: set milestone
to the correct value.

---

### Step 4 — Generate Suggested Disposition

Based on the score and blockers, suggest one clear action. Use this table:

| Condition | Suggested Action |
|-----------|-----------------|
| Hard blocker: draft | Skip — not ready |
| Hard blocker: merge conflicts | Comment: ask author to rebase |
| Hard blocker: CI failing | Comment: point to failing check |
| Hard blocker: changes requested | Comment: ask author to address review |
| Score 0–25 (Not Ready) | Comment: explain what's missing |
| Score 26–45 (Needs Work) | Comment: specific asks (testing, review, docs) |
| Score 46–65 (Promising) | Label `needs testing` OR comment requesting a tester |
| Score 66–80 (Looking Good) | Ask for one final confirmation, then it's merge-ready |
| Score 81–90 (Merge Candidate) | **Merge** (or Approve if you're not a maintainer) |
| Score 91–100 (Ready to Merge) | **Merge** |

For comment suggestions, be specific. Examples:
- "Could someone with the relevant hardware test this?"
- "Two open review threads need resolution before merge."
- "CI check `Build MATEKF405` is failing — please fix."
- "Looks good! I'll merge once the open review thread is closed."

---

### Step 5 — Present to User

Format each PR like this:

```
============================================================
PR #11220: Fix waypoint navigation calculation   [74/100 — Looking Good]
============================================================
https://github.com/iNavFlight/inav/pull/11220

Author: contributor123 (CONTRIBUTOR) | 52 days old
Labels: none | Base: maintenance-9.x

BLOCKERS: None

KEY SIGNALS
  ✓ CI: 12/12 checks passing
  ✓ Review: 1 member approval (sensei-hacker: APPROVED)
  ✓ Testing: 1 non-author confirmed testing
  ⚠ 2 open review threads not yet resolved
  ~ Scope: 180 lines, touches navigation subsystem

SUGGESTED: Comment asking reviewer to close the 2 open threads, then merge.

------------------------------------------------------------
[m]erge   [a]pprove   [c]omment   [l]abel   [r]eview   [s]kip   [q]uit
```

Key/symbol guide for KEY SIGNALS:
- `✓` = positive signal
- `⚠` = concern or soft blocker
- `✗` = hard blocker
- `~` = neutral/informational

**Always print the URL on its own line** so it's clickable in the terminal.

---

### Step 6 — Wait for User Decision

Wait for one of:

| Input | Action |
|-------|--------|
| `m` or `merge` | Merge the PR (see below) |
| `a` or `approve` | Approve the PR |
| `c` or `comment <text>` | Post a comment (use suggested text if no text given) |
| `l` or `label <name>` | Add a label |
| `r` or `review` | Run bot check + code review (see below) |
| `s`, `n`, or `skip` | Skip this PR for this session |
| `q` or `done` | End the session |

If the user types just `c` or `l` without text, prompt for the text/label.

---

### Step 7 — Execute the Action

#### Merge
```bash
gh pr merge <PR_NUMBER> --repo iNavFlight/inav --squash --auto
```
Ask the user for merge strategy if not obvious: `--squash` (default), `--merge`, or `--rebase`.

#### Approve
```bash
gh pr review <PR_NUMBER> --repo iNavFlight/inav --approve -b "Looks good to merge."
```

#### Comment
```bash
gh pr comment <PR_NUMBER> --repo iNavFlight/inav --body "Your comment here."
```

#### Label
```bash
gh api repos/iNavFlight/inav/issues/<PR_NUMBER>/labels \
    --method POST --field 'labels[]=needs testing'
```

#### Hardware register verification (proactive — use before Review)

When a PR touches `src/main/drivers/` with platform-specific register access
(GPIO toggle, DMA stream control, timer implementations, MCU-specific HAL/StdPeriph),
proactively invoke the `target-developer` agent to verify correctness against
hardware docs **before** deciding to merge or request review:

```
Agent(target-developer): "Verify hardware register usage in PR #<N> in <REPO>.
Fetch the diff with: gh pr diff <N> --repo <REPO>
Check register names, field access patterns, and logic against docs in
claude/developer/docs/targets/<mcu>/
Return: is the register usage correct per the hardware docs?"
```

This caught a GPIO toggle correctness issue in PR #11228 (AT32 LED fix) before merge.

#### Review (bot check → then code review)

These run **sequentially** — the code review agent reads the bot comments file.

**Step 1:** Run check-pr-bots agent first:
```
Agent(check-pr-bots): "Fetch all bot comments on PR #<N> in <REPO>.
Save full formatted output to /tmp/claude/pr-<N>-bot-comments.txt.
Return the content in your response."
```

**Step 2:** Once bot comments are saved, run inav-code-review:
```
Agent(inav-code-review): "Review PR #<N> in <REPO>.
Fetch the diff with: gh pr diff <N> --repo <REPO>
Bot comments file is at /tmp/claude/pr-<N>-bot-comments.txt — read it and
assess whether each bot concern is valid, already addressed, or invalid.
Return: categorized findings by severity, and suggested comment text."
```

After both agents return:
- Present the combined findings to the user
- Suggest a comment either confirming the bot findings or refuting them
- Ask the user: post the comment, or take a different action?

**Proactive trigger:** If the scorecard data showed bot review comments
(visible in the CODE REVIEW section), offer `[r]eview` as the suggested
action rather than waiting for the user to ask.

#### Skip (no GitHub action — just add to session skip file)
```bash
echo "<PR_NUMBER>" >> /tmp/claude/skip-scorecard-inav.txt
```

---

### Step 8 — Advance to Next PR

After any action (including skip):

1. Invalidate the PR list cache so merges/labels are reflected:
   ```bash
   rm -f /tmp/claude/scorecard-pr-cache-*.json
   ```

2. Read the prefetched output (already running in background):
   ```bash
   # Use the Read tool on the prefetch file — do NOT use Bash cat
   # Read: /tmp/claude/prefetch-scorecard.txt
   ```

3. From the prefetch output, start fetching the scorecard for THAT PR:
   ```bash
   bash claude/developer/scripts/triage/pr-scorecard.sh \
       iNavFlight/inav <NEXT_PR_NUMBER> \
       --output /tmp/claude/prefetch-scorecard-data.txt
   ```
   Use `run_in_background: true`.

4. While that runs, present the current prefetched PR to the user (go to Step 4).

5. Kick off the next `scorecard-triage.sh --offset 1` prefetch for the one after that.

---

### Step 9 — Loop

Continue until:
- User says `q` or `done`
- `NO_MORE_PRS` from scorecard-triage.sh
- Switching repos

---

## Configurator Repo

Replace `iNavFlight/inav` with `iNavFlight/inav-configurator` throughout.
Use separate skip file: `/tmp/claude/skip-scorecard-configurator.txt`.

---

## Example Session

```
> /pr-scorecard-triage inav

============================================================
PR #11220: Fix waypoint navigation calculation   [74/100 — Looking Good]
============================================================
https://github.com/iNavFlight/inav/pull/11220

Author: contributor123 (CONTRIBUTOR) | 52 days old
Labels: none | Base: maintenance-9.x

BLOCKERS: None

KEY SIGNALS
  ✓ CI: 12/12 checks passing
  ✓ Review: 1 member approval (sensei-hacker: APPROVED)
  ✓ Testing: 1 non-author confirmed testing ("works on MATEKF405")
  ⚠ 2 open review threads not yet resolved
  ~ Scope: 180 lines, touches navigation subsystem

SUGGESTED: Comment asking the reviewer to close the 2 open threads.
           "Looks good! Once the 2 open review threads are closed this is merge-ready."

[m]erge  [a]pprove  [c]omment  [l]abel  [s]kip  [q]uit

> c

[Using suggested comment text]
Posted comment on PR #11220. Moving to next PR...

============================================================
PR #11189: Add new MATEKF405SE target   [91/100 — Ready to Merge]
...
SUGGESTED: Merge

[m]erge  [a]pprove  [c]omment  [l]abel  [s]kip  [q]uit

> m

Merging PR #11189 (squash)... Done.
Moving to next PR...
```

---

## Notes

- GitHub API calls may need `dangerouslyDisableSandbox: true`
- `CACHE_STATUS=fresh` means use cached score — no re-fetch, no re-record
- `CACHE_STATUS=unscored` or `expired` means fetch fresh and record
- The prefetch model keeps you from waiting between PRs
- Use `/pr-scorecard <N>` for the full detailed scorecard on any individual PR
- Default date window is **6 months**; pass `--after YYYY-MM-DD` to override

### Score Calibration

**"Needs Work" does not mean "don't merge."** The score reflects how many
readiness signals are present — it is a floor for discussion, not a hard gate.

A COLLABORATOR's 2-day-old bugfix with perfect CI can legitimately score 30/100
(no maturity, no approvals yet) and still be the right call to merge. The score
helps surface *what's missing* — the maintainer decides whether that matters.

Use the score to guide questions:
- Low maturity + trusted author → fine to merge if the fix is obvious
- Low testing + core subsystem → wait for hardware confirmation
- Active unresolved review discussion → resolve before merging
- Low score across all categories → needs more time and engagement

---

## Related Skills

- **pr-scorecard** — Score a single PR in detail
- **pr-triage** — Assign milestones to PRs
- **pr-review** — Full code review (checkout, test, review bots)
- **check-builds** — Deep-dive CI failure investigation
