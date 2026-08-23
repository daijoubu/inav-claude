# Project: Fix Email Outbox Not Cleared After Delivery

**Status:** 🚧 IN PROGRESS (implementation complete, pending manager review — see Success Criteria)
**Priority:** HIGH (raised from MEDIUM 2026-08-23 — see Second, More Severe Bug below)
**Type:** Bug Fix (harness tooling — internal email system)
**Created:** 2026-08-02
**Estimated Effort:** 1-2 hours (original scope) — re-estimate once the
silent non-delivery bug below is diagnosed; could be the same root cause
or a separate one

## Second, More Severe Bug Found 2026-08-23 — Silent Non-Delivery

While reading through `review-pr11553-vtol-transition` milestone reports
with Ray, found that 6 of 6 developer completion reports for that project
(milestones 1-6, sent 2026-08-21 through 2026-08-23, one containing a
flight-safety-CRITICAL finding) exist in
`claude/developer/email/sent/` but were **never delivered to the manager's
inbox at all** — not in `inbox/`, not in `inbox-archive/`. Unlike the
stale-outbox-duplicate bug below (delivery succeeded, cleanup didn't), this
is a case where delivery itself silently failed while the agent's own
`sent/` record made it look like it succeeded. `claude/developer/email/
outbox/` is empty, so there's no leftover draft to explain it either — the
file simply never reached the recipient. Manager project tracking
(`review-pr11553-vtol-transition` INDEX.md/todo.md) was stale for 2+ days
as a direct result — the M6 CRITICAL finding sat unseen the whole time.
**Needs its own root-cause investigation** — may share a cause with the
outbox-clearing bug (both point at the "Send Email" step in
`.claude/agents/email-manager.md`) or may be independent. Recovered this
time by reading the sender's `sent/` copies directly; that's a manual
workaround, not a fix.

**Directional clue found 2026-08-23:** swept all developer→manager sent/
mail from the last 4 days (25 messages) and found 4 total non-delivered
(the 2 DMA reports + these 2). Then swept the reverse direction —
manager→developer sent/ from the same window (14 messages) — and found
zero missing. **Caveat considered and checked (Ray):** presence alone
doesn't rule out a past gap that was silently patched by hand later, which
would look identical to a clean delivery. Checked mtimes instead —
every one of the 14 developer-inbox copies was written 3-28 seconds after
its `sent/` counterpart, consistent with the same automated tool-call
sequence, not a human noticing and backfilling a gap (which would show a
much larger delay). So: the asymmetry holds up under a timing check, not
just a presence check. The bug so far only reproduces in the
developer→manager direction. Worth checking whether it's sender-specific,
role-specific, or correlates with something else about how developer's
send step was invoked, rather than a blanket bug in the shared logic both
directions call.

## Scope Change 2026-08-23 (mid-implementation, live with Ray) — outbox/ removed entirely

While implementing `email_ops.py`'s `send`, Ray questioned whether
`outbox/` has any real function at all beyond causing confusion and bugs.
Investigated and agreed: `outbox/` modeled a real-email concept (delivery
that can be delayed or fail — network down, recipient's mail server
unreachable) that doesn't exist here, since delivery is just copying a
file into a local directory that always exists. Nothing was ever
legitimately staged there in practice (all 4 roles' `outbox/` folders were
already empty before this project touched them). Worse, an outbox-based
"check for undelivered mail" can only ever catch a message staged in
`outbox/` and mishandled from there — the more severe bug above never
touched `outbox/` at all, so that check design was structurally incapable
of catching it regardless of how well it was written.

**Decision:** removed `outbox/` entirely (all 4 roles' folders deleted,
confirmed empty first) and replaced `check-outbox` with
`email_ops.py audit`: for every message in a role's `sent/`, parse its
`**To:**` header and confirm a byte-identical copy exists anywhere in the
recipient's email tree. This catches both the original stale-duplicate
bug's shape and the more severe silent-non-delivery bug's shape, and
depends on nothing having been staged anywhere first.

**Added per Ray's request:** `audit-if-due`, self-triggered weekly via a
flag file (`claude/agents/email-manager/data/last-audit-timestamp.txt`,
timestamp stored in content, not relied on for mtime since git checkouts
reset mtimes). The email-manager agent now runs `audit-if-due` on every
invocation regardless of the requested action — a no-op 6 days out of 7.

**First real run found a live instance of the bug happening today
(2026-08-23), independent of the known 6 milestone reports:** two more
developer→manager messages — including a status update recommending PR
#11553 be held for merge, given the CRITICAL finding is now SITL-confirmed
— were also silently undelivered. Redelivered both immediately via
`email_ops.py send`, verified. The same first run also surfaced a backlog
of ~52 older undelivered messages dating back to 2025-11 across all
sender/recipient pairs — **deliberately NOT auto-fixed**: bulk-redelivering
old, possibly already-resolved messages into a live inbox as if new risks
recreating the exact 2026-08-02 incident this project exists to prevent.
Flagging this backlog to the manager for case-by-case triage rather than
resolving it unilaterally.

## Overview

The `email-manager` agent's "Send Email" workflow (`.claude/agents/email-manager.md`)
copies (`cp`) a drafted message from the sender's `sent/` folder to the recipient's
`inbox/`, but never removes the corresponding file from the sender's `outbox/`.
Every message ever sent therefore leaves a permanent orphaned copy in `outbox/`,
even though it has already been fully delivered, read, and archived.

## Problem

The agent's own "Check for Undelivered Mail" step is:

```bash
find claude/*/email/outbox/ -type f -name "*.md" 2>/dev/null
```

Any file found is reported as "stuck"/"undelivered," with no way to distinguish
a genuinely stuck draft from a stale leftover copy of an already-delivered,
already-archived message. This produced a false-positive incident on 2026-08-02:
an inbox check found 5 files in `claude/developer/email/outbox/` dated
2026-05-31 through 2026-06-23 and reported them as undelivered mail needing
manager action. All 5 were confirmed byte-identical to copies already sitting
in `claude/manager/email/archive/` or `inbox-archive/` — i.e., already
delivered, read, and processed weeks/months ago. A follow-up agent copied all
5 into the manager's inbox before the duplication was caught (by the user,
not the agent), which nearly caused already-merged/already-resolved items
(PR #2644, PR #11365, PR #2652, a stale-lock question) to be re-processed.

## Solution

**Scope decision 2026-08-23 (Ray), per manager recommendation:** replace the
manually-instructed multi-step "Send Email" / "Archive Message" sequences
with a deterministic script, `email_ops.py`, mirroring the pattern already
established by `claude/projects/project_ops.py` (built after two real
INDEX.md corruption incidents caused by an agent hand-editing state across
multiple steps — see that script's docstring and
`claude/manager/README.md`'s INDEX.md section). An LLM agent (this one runs
on Haiku) manually chaining `cp`/`rm`/`mv` across 2-4 filesystem locations,
with no atomicity and no verification, is exactly the failure shape that
produced *two independent* bugs in the same step: the original
stale-outbox-duplicate bug, and the more severe silent-non-delivery bug
found 2026-08-23 (see above — 6 completion reports, including one CRITICAL
finding, silently never reached the recipient inbox while `sent/` showed
delivery as successful).

1. Write `claude/projects/email_ops.py` (or an equivalent shared location —
   developer's call) with atomic operations:
   - `send <sender-role> <recipient-role> <file>` — writes to sender's
     `sent/`, copies to recipient's `inbox/`, and removes the file from
     sender's `outbox/` if it was staged there, as one operation. Verifies
     each write actually landed (re-read and compare, don't just trust the
     copy call returned success) before reporting success; raises loudly
     and leaves state unchanged/rolled back on any failure instead of
     silently completing a partial sequence.
   - `archive <role> <file>` — moves inbox → inbox-archive, verified.
   - `check-outbox` — folds in the existing
     `claude/agents/email-manager/scripts/check_outbox.py` byte-identical-
     duplicate check (already deterministic — keep/port that logic rather
     than rewriting it).
2. Update `.claude/agents/email-manager.md`'s "Send Email" and "Archive
   Processed Message" sections to call `email_ops.py` instead of issuing
   raw `cp`/`rm`/`mv` commands directly.
3. One-time cleanup: remove the 5 confirmed-stale duplicate files already
   sitting in `claude/developer/email/outbox/` (all verified byte-identical
   to already-archived copies — do not re-copy them anywhere, just delete):
   - `2026-05-31-1500-completed-fix-pwm-beeper-mode-regression.md`
   - `2026-05-31-1600-completed-fix-vtol-control-profile-sync.md`
   - `2026-05-31-1800-completed-resolve-merge-conflict-pr11365.md`
   - `2026-06-06-1100-completed-fix-cli-autocomplete-undefined.md`
   - `2026-06-23-1430-question-stale-lock.md`
4. Sweep all four roles' `outbox/` folders (`claude/{manager,developer,
   release-manager,security-analyst}/email/outbox/`) for the same kind of
   stale leftover and clean up any found, after confirming each is a
   byte-identical duplicate of an already-archived message (never delete
   an outbox file that doesn't have a matching archived copy — that would be
   a genuinely undelivered message).
5. Root-cause the silent-non-delivery bug specifically (distinct from the
   stale-outbox one) before assuming `email_ops.py` alone fixes it — worth
   understanding *how* the old manual step managed to skip the inbox copy
   while still recording `sent/` success, so the new script's verification
   step is designed against the actual failure mode, not a guess.

## Implementation

- New file: `claude/projects/email_ops.py` (deterministic script, pattern
  mirrors `claude/projects/project_ops.py`)
- File to update: `.claude/agents/email-manager.md` ("Common Operations" →
  "2. Send Email" and "3. Archive Processed Message" sections, calling the
  new script instead of raw shell commands)
- This is harness tooling, not INAV firmware/configurator source — no PR
  needed, direct commit to master (consistent with other harness-tooling
  projects, e.g. `harness-m07-hardware-debugger`).

## Success Criteria

- [x] `email_ops.py` written: atomic `send`, `archive`, `audit`,
      `audit-if-due` operations, each verified and fail-loud (not fail-silent)
- [x] Root cause of the silent-non-delivery bug investigated (no
      per-invocation command log exists to confirm the exact failed
      command, but the structural defect — no verification step existed to
      catch a failed/skipped copy before reporting success — is identified
      and closed regardless of mechanism; see summary and workspace notes)
- [x] `email-manager` agent's send/archive/audit workflow calls
      `email_ops.py` instead of raw `cp`/`rm`/`mv`
- [x] `outbox/` removed entirely from all 4 roles (confirmed empty first;
      superseded "remove 5 known-stale files" — they no longer existed by
      the time this ran) and from all docs/scripts referencing it
- [x] Delivery audit run for real: found and fixed 2 live undelivered
      messages from today; found (but deliberately did not bulk-fix) a
      ~52-message historical backlog — flagged to manager for triage
- [ ] Completion report sent to manager

## Related

- **Discovered:** 2026-08-02, manager inbox check false-positive incident (caught by user, not by either agent involved)
- **Assignment:** (pending — see `manager/email/sent/`)
