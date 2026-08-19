# email-manager Agent Tools

**Purpose:** Permanent tools and scripts for the `email-manager` agent (`.claude/agents/email-manager.md`).

## Scripts

### scripts/check_outbox.py
**Purpose:** Distinguish genuinely undelivered mail from stale leftover copies
in `claude/{role}/email/outbox/`. A file in `outbox/` is only genuinely
undelivered if no byte-identical copy exists anywhere else in the email tree
(`sent/`, `inbox/`, `inbox-archive/`, `archive/`); otherwise it was already
delivered and the outbox copy is a stale leftover.

**Usage:**
```bash
# Report only (used by the agent's "Check for Undelivered Mail" step)
python3 claude/agents/email-manager/scripts/check_outbox.py

# Also delete confirmed-stale duplicates
python3 claude/agents/email-manager/scripts/check_outbox.py --clean
```

Exit code is `0` if no genuinely undelivered mail was found, `1` otherwise
(so it can be used as a CI-style check).

**Created:** 2026-08-02 — fixing `fix-email-outbox-not-cleared-after-delivery`.
The "Send Email" workflow used to copy a message into the recipient's
`inbox/` without ever removing the original from the sender's `outbox/`, so
every message ever sent left a permanent orphaned copy. The old undelivered-
mail check (`find claude/*/email/outbox/ -type f`) then reported all of these
as stuck mail, which nearly caused several already-resolved items to be
re-delivered. The Send Email workflow itself was also fixed (see
`.claude/agents/email-manager.md`, "Common Operations" → "2. Send Email") to
remove the file from `outbox/` after successful delivery — this script is a
defensive backstop in case an outbox file is ever created without going
through that path.
