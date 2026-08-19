# ⚠️ CRITICAL CHECKLIST - Read Before Creating Pull Request

**STOP! Complete this checklist before running `gh pr create` or `/create-pr`:**

**Use a task list tool to track each step as you complete it.**

---

## Prerequisites

- ✅ Code written and tested
- ✅ Changes committed (following `CRITICAL-BEFORE-COMMIT.md`)
- ✅ Working on feature branch (NOT master/main/maintenance-*)

---

## 🚨 TESTING IS MANDATORY

**NEVER create a pull request without testing the code.**

### Required Testing Steps

1. **Code Must Compile**
   - Use **inav-builder** agent to verify build succeeds

2. **Code Must Actually Run**
   - Don't just verify it compiles
   - Actually execute and test the functionality
   - Use **test-engineer** agent or SITL for firmware changes

3. **Feature Must Work**
   - Test the specific feature/fix works as expected
   - Verify expected behavior occurs

4. **Test Edge Cases**
   - Try invalid inputs
   - Test with empty data
   - Test boundary conditions

5. **Verify No Regressions**
   - Check that existing functionality still works
   - Run related tests

### If Testing Isn't Possible

If you genuinely cannot test (no hardware, blocked dependencies):
1. **Be explicit in PR description** - state what you couldn't test and why
2. **Request testing** - ask for someone with hardware/setup to test
3. **Never claim "tested" if you didn't actually test**

**Remember:** Untested code can brick expensive flight hardware.

---

## 🚨 CODE REVIEW IS MANDATORY

**Use the `inav-code-review` agent before creating your PR.**

```
Task tool with subagent_type="inav-code-review"
Prompt: "Review changes in [files] - [brief description]"
```

**What the review checks:**
- Coding standards compliance
- Embedded systems safety (ISR safety, memory constraints, stack usage)
- INAV-specific patterns (PG system, scheduler, hardware abstraction)
- Common pitfalls (integer overflow, volatile misuse, race conditions)
- Over-engineering and unnecessary complexity
- Flight-critical code path safety

**Address issues found:**
- Fix CRITICAL issues (must fix before merge)
- Fix IMPORTANT issues (should fix before merge)
- Consider MINOR issues (nice to have)

---

## 🔍 Finalize End-User Documentation

**If you drafted user documentation before coding (see CRITICAL-BEFORE-CODE.md step 4):**

1. **Update the draft** in `claude/developer/workspace/[task-name]/draft-user-docs.md`
   - Verify it matches the actual implementation
   - Update examples and configuration steps if they changed
   - Ensure CLI/settings changes are accurate

2. **Add documentation to the codebase:**
   - Technical docs → `inav/docs/` (committed with PR)
   - End-user guides → `inavwiki/` (separate PR to wiki repo if needed)

3. **Mention in PR description:**
   - List which documentation files were added/updated
   - Or note "Documentation not needed (bug fix/target/refactor)"

---

## 🔍 Check for Upstream Changes Since Work Started

**Before creating the PR, check whether the upstream base branch has moved:**

```bash
git fetch upstream
git log HEAD..upstream/maintenance-10.x --oneline   # or maintenance-9.x
```

**If there are new upstream commits: STOP. Do not rebase automatically.**

Show the commits to the user and ask for advice:
- The upstream may have already merged a fix for the same issue — duplicating it would be wrong.
- The upstream may have introduced a conflict that needs human judgment to resolve correctly.
- The upstream may be unrelated and a rebase is safe — but that decision belongs to the user.

Present the new commits and ask: *"Upstream has N new commits since we branched. Would you like to rebase, check if any overlap with our changes, or proceed as-is?"*

---

## Creating the Pull Request

### 1. Review Changes

Determine your base branch from `.claude/skills/git-workflow/SKILL.md` ("Creating
Branches") — it's the single authority and includes any active temporary override.
**Never PR to master.**

Then review (substitute the base branch you actually branched from):
```bash
git status
git diff <base-branch>...HEAD
git log <base-branch>..HEAD
```

### 2. Verify All Changes Committed
```bash
git status  # Should show "nothing to commit, working tree clean"
```

If uncommitted changes exist, commit them first (see `CRITICAL-BEFORE-COMMIT.md`).

### 3. Push to Remote
```bash
git push -u origin branch-name
```

Plain `git push` to origin is safe and approved — never force-push. If the push fails
with "Network is unreachable" or "Connection refused", that's the sandbox blocking the
operation — NOT a network outage. Retry once (`github.com` and `ssh.github.com` are
allowlisted). If the sandbox still blocks this specific push, it is an approved
exception: retry with `dangerouslyDisableSandbox: true`. Do not generalize this to
other operations (see "Sandbox Restrictions" in the git-workflow skill).

### 4. Create PR

**⚠️ First, unset `GITHUB_TOKEN`/`GH_TOKEN` for this step only.** If either is set in the
environment, `gh` always prefers it over the credential from `gh auth login` — and the
`GITHUB_TOKEN` commonly present in this environment is a fine-grained PAT scoped to
specific repos/permissions, which typically lacks `Pull requests: write` on
`iNavFlight/inav` (you're a contributor there, not a maintainer). This produces
`GraphQL: Resource not accessible by personal access token (createPullRequest)`.
The default logged-in `gh auth login` credential (classic PAT, broader `repo`/`workflow`
scope) can create the PR. Unset just for this command, then restore for everything else
(releases, other API calls may rely on the fine-grained PAT's specific grants):

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh pr create --title "Title" --body "Description"
```

Use `/create-pr` skill or the command above.
IMPORTANT **Never open a pull request to the master branch**

**Set the milestone (and any applicable category label, e.g. "New target") when creating the PR** — see "Choosing Labels and Milestone" in `.claude/skills/create-pr/INAV-PR.md` for the current mapping.

**PR Description Requirements:**

**Include:**
- Summary of changes
- Testing performed (be specific - what did you test and what were the results)
- Code review performed (mention using inav-code-review agent)
- Related issue number (if applicable)

**Do NOT mention:**
- Claude or AI assistance
- "Generated by" statements

**Example:**
```markdown
## Summary
Fixes blackbox corruption when no motors are defined in the mixer.

## Changes
- Added motor count validation in blackbox logger
- Return early if motor count is zero

## Testing
- Built SITL target successfully
- Tested with custom mixer with 0 motors - no corruption
- Tested with standard quad mixer - blackbox works normally
- Verified existing blackbox functionality unchanged

## Code Review
Reviewed with inav-code-review agent - no critical issues found.

Fixes #1234
```

If `gh pr create` fails with network errors, that's the sandbox blocking an unapproved
network operation — NOT a network outage. Do not disable the sandbox. Ask the user to
approve the operation or run it manually (see "Sandbox Restrictions" in the git-workflow
skill).

---

## After Creating PR

**This is step 10 in the workflow. See `/check-builds` skill or `check-pr-bots` agent.**

Quick summary:
1. Wait 3 minutes for bots to analyze
2. Use **check-pr-bots** agent or **/check-builds** skill
3. Review and address bot suggestions

---

## Self-Improvement: Lessons Learned

When you discover something important about PR CREATION AND TESTING that will likely help in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future PR creation, not one-off situations
- **About PRs/testing** - testing requirements, PR workflow, bot checking, CI/CD
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

- **Test all code paths, not just the happy path**: When refactoring code from one module to another, you must drive every branch of the extracted code — not just the path you happened to exercise. In the PR #2603 refactor, the backup path was tested but the entire post-flash restore flow (onFlashComplete, port polling, executeRestore, error dialog) was untested until we actually flashed the hardware FC. Static analysis (Qodo) caught four bugs in those untested paths that live testing missed.
- **Test before push, not after**: All five testing checklist items must be complete before `git push` and `gh pr create` — not during or after PR creation. Creating a PR signals the work is ready for review.
- **Fix conflicts in the existing PR's branch, don't create a duplicate PR**: When asked to fix merge conflicts in an existing PR, resolve them by pushing to that PR's head branch — not by creating a new branch and a new PR. A link to `/pull/NNNN/conflicts` means fix *that* PR.
- **`gh pr create` needs the default credential, not `GITHUB_TOKEN`**: if `GITHUB_TOKEN`/`GH_TOKEN` is set to a fine-grained PAT, unset it for just the `gh pr create` command (`env -u GITHUB_TOKEN -u GH_TOKEN gh pr create ...`) — see the note above this section for why. The same credential precedence can affect a plain `git push` to that same remote too, not just `gh pr create`. **Ask the user for explicit authorization before unsetting `GITHUB_TOKEN`/`GH_TOKEN` for any command, every time** — never do it unilaterally just because a prior turn approved it; approval doesn't carry forward.
- **A unit test proving one race is closed doesn't prove the symptom is gone**: a bug's reported symptom can have more than one independent root cause producing the identical output. After fixing and unit-testing the race the manager's analysis identified (`fix-cli-tab-msp-polling-leak`), live-testing on real hardware reproduced the same garbage anyway — a second, unrelated bug (a retry loop that never re-checked the same guard condition) was the other contributor. Live-test the actual reported symptom end-to-end before declaring a race-condition fix complete, even when an isolated unit test already passes.
- **Pushing to a contributor's fork can 403 even with `maintainer_can_modify: true`**: resolving conflicts in someone else's PR (e.g. PR #2593) and pushing the fix directly to their fork branch can fail with 403 even though the PR shows maintainer-edit access is enabled and the base-repo permission is admin-level — likely because the active `gh`/git credential is a fine-grained PAT whose scope doesn't cover third-party forks. Don't switch `gh auth` accounts to work around this (too invasive without explicit permission); instead push the resolved branch to `origin` (your own fork) and open a fresh PR referencing the original, then ask the user how to handle the now-superseded original PR.
<!-- Add new lessons above this line -->
