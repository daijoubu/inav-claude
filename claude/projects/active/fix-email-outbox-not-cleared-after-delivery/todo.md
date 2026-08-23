# Todo: Fix Email Outbox Not Cleared After Delivery

## Phase 0: Root-Cause the Silent Non-Delivery Bug (added 2026-08-23)

- [x] Investigated how the manual "Send Email" step produced a `sent/`
      copy but no `inbox/` copy for 6 messages. No per-invocation command
      log exists to replay the exact failed command. Ruled out (checked,
      not assumed) a "wrong cwd silently wrote elsewhere" mechanism:
      `inav/claude`, `inav2/claude`, `inav3/claude` are root-owned/
      non-writable by design, and a filesystem-wide search for all 6+2
      missing filenames found zero stray copies anywhere. Structural
      conclusion: the real defect is that no step ever verified the
      `inbox/` write landed before reporting success — closed by
      `email_ops.py`'s read-back+hash verification regardless of the
      exact per-incident mechanism. See workspace notes.md for full
      writeup.
- [x] Determined: same step (`cp` in "Send Email"), different symptom —
      treated as the same underlying failure *class* (unverified
      hand-chained multi-step filesystem edits by an LLM agent), which
      `email_ops.py` closes as a whole rather than patching symptom by
      symptom.

## Phase 1: Build `email_ops.py` (deterministic script, scope decided 2026-08-23 per Ray)

- [x] Read `.claude/agents/email-manager.md` and `project_ops.py` as the pattern to mirror
- [x] Wrote `claude/projects/email_ops.py` with atomic, verified `send`/`archive` operations
- [x] Each operation verifies its own result (re-read and hash-compare) and raises loudly on any failure
- [x] Updated `.claude/agents/email-manager.md`'s Send Email / Archive Processed Message sections to call `email_ops.py`
- [x] Re-read the doc for self-consistency

### Phase 1b: outbox/ removed entirely (scope change 2026-08-23, live with Ray — see summary.md)

- [x] Confirmed `outbox/` models nothing real in a same-filesystem mail
      system and an outbox-based check structurally cannot catch the more
      severe bug (it never touched `outbox/`)
- [x] Removed `outbox/` from all 4 roles (confirmed empty first), deleted
      `check_outbox.py` (logic superseded, not ported — the new check is
      a different, better-targeted design)
- [x] Replaced `check-outbox` with `email_ops.py audit`/`audit-if-due`:
      parses each sent message's `**To:**` header and confirms delivery
      anywhere in the recipient's email tree (catches both bug shapes;
      depends on nothing being staged anywhere first)
- [x] Added the weekly self-triggering flag file
      (`claude/agents/email-manager/data/last-audit-timestamp.txt`,
      7-day interval, timestamp in content not mtime)
- [x] Swept the whole repo for every remaining `outbox` reference (role
      READMEs, install.sh/INSTALL.md, manager/email/README.md +
      COMMUNICATION.md, skills, onboarding hook, presentation outline) and
      updated each

## Phase 2: Cleanup

- [x] The 5 originally-known-stale files no longer existed in
      `claude/developer/email/outbox/` by the time this ran (already gone
      — confirmed via the audit/check before deletion, nothing to clean)
- [x] Swept all 4 roles' `outbox/` folders — all already empty, confirmed
      before deleting the folders themselves
- [x] N/A — nothing found in the Phase 2 sweep requiring the
      identical-copy-before-delete judgment call

## Completion

- [x] Fix verified end-to-end: sent + archived a test message via
      `email_ops.py`, confirmed byte-identical delivery, confirmed
      idempotent re-send, confirmed the outbox-draft-recovery fallback
      path (later removed along with `outbox/` itself)
- [x] Verified against the silent-non-delivery failure mode specifically:
      ran `email_ops.py audit` for real, which found and fixed 2 messages
      from today that were silently undelivered by the *current* (partially
      pre-fix) workflow — direct evidence the audit catches exactly this
      failure mode, not just the original stale-outbox symptom
- [ ] Send completion report to manager (includes flagging the ~52-message
      historical backlog for manager triage — deliberately not auto-fixed,
      see summary.md)
