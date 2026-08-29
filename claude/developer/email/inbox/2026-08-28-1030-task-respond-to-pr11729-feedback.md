# Task Assignment: Respond to maintainer feedback on PR #11729

**Date:** 2026-08-28 10:30
**From:** Manager
**To:** Developer
**Project:** feature-canbus-errors-blackbox
**Priority:** HIGH
**Estimated Effort:** 0.5-1 hour

## Task

New review comment on `iNavFlight/inav#11729` from `sensei-hacker` (project maintainer), posted 2026-08-28 04:00 UTC — not yet addressed. Review it and reply.

## Background

You already investigated and declined this exact suggestion once: on 2026-08-23, Qodo flagged that the new `droneCANBusOffCount` blackbox slow-frame field uses `PREDICT(0)` instead of `PREDICT(PREVIOUS)`. You traced both real decoders (`blackbox-tools`/`blackbox_decode`'s `parser.c` and the JS `flightlog_parser.js`) and found `PREDICT(PREVIOUS)` is a no-op for S-frame fields in both (they pass `previous = NULL`), and that INAV's encoder never actually delta-encodes any S-frame field regardless of declared predictor — so the change would have been cosmetic only. You posted a detailed technical reply to that effect: https://github.com/iNavFlight/inav/pull/11729#discussion_r3839243425

Now, 2026-08-28, the maintainer `sensei-hacker` posted an independent top-level review comment raising the *same* point, without apparent reference to your earlier reply:

> Thanks for the PR — logging the cumulative DroneCAN bus-off count to the blackbox slow frame is a nice, small addition.
>
> While reviewing I noticed the Qodo finding and wanted to weigh in: the new field is declared with `PREDICT(0)`, which re-encodes the full cumulative count every slow frame. Since `dronecanGetBusOffCount()` increments monotonically, `PREDICT(PREVIOUS)` would keep the encoded values tiny (usually a 0/1 delta) and reduce blackbox log size/write bandwidth — the codebase already uses `PREDICT(PREVIOUS)` for slowly-changing fields in the same S-frame. Could you switch it to `PREDICT(PREVIOUS)`?
>
> One question from me: is the raw cumulative count what you want to log, or would a delta/rate also be useful for diagnosing bus-off events in the field? The cumulative count is great for "has this ever happened", but for "when is it happening" a per-frame delta in a faster frame might complement it. Happy to defer to your intent — just curious.
>
> Also: the PR targets `maintenance-10.x`, which is correct for a 10.0 enhancement.
>
> Other than the predictor question, this looks clean — +17/-1, no RAM/flash impact. Would you be able to make the `PREDICT(PREVIOUS)` change and push?

Also noted in the same PR thread: `sensei-hacker` posted a separate FYI (2026-08-16) that INAV 10.0 RC1 is targeted for 2026-09-01 — new features for 10.0 need to be ready by then, which this PR is close to.

## What to Do

1. Reply to the maintainer's comment on the PR thread. Point to your existing technical reply (the decoder-tracing analysis still stands — `PREDICT(PREVIOUS)` is genuinely a no-op today) but don't just repeat it verbatim; the maintainer is asking a direct question and deserves a direct answer, not a re-post.

2. Decide and state your recommendation: given the maintainer is explicitly asking for the declarative change (readability/consistency with other slowly-changing S-frame fields, and correctness of intent even though it's a no-op under the current encoder), is it worth making anyway despite being cosmetic? Your call — you have the technical context.

3. Answer the raw-cumulative-vs-delta/rate question. You have relevant context from the investigation — is a per-frame delta or rate field something worth adding now, later, or not at all for this use case (diagnosing bus-off events in the field)?

4. If you and the maintainer land on actually making the `PREDICT(PREVIOUS)` change (or adding a delta field): per project convention, DroneCAN code changes are user-written, not developer-written. Flag the specific line-level change needed and hand off to the user to make the commit — do not push firmware code changes yourself.

5. Keep the 2026-09-01 RC1 deadline in mind — this PR is close and small, worth not letting it stall on a review back-and-forth.

## Success Criteria

- [ ] Reply posted to the maintainer's PR comment addressing both the predictor question and the delta/rate question
- [ ] Clear recommendation given (change vs. no change, with reasoning)
- [ ] If a code change is warranted, specific diff described and handed to the user (not pushed by developer)
- [ ] Status report sent to manager

## Project Directory

`claude/projects/active/feature-canbus-errors-blackbox/`

---
**Manager**
